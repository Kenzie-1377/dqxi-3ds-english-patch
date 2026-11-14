"""Read and rebuild a decrypted CIA while retaining its non-game contents.

Modified CIA signatures require a compatible custom-firmware installation.
Original ticket/certificate/footer bytes are retained; no keys are supplied.
"""
import hashlib
import struct
from pathlib import Path

TITLE = 0x0004000000199200
def align(n, boundary=64): return (n + boundary - 1) // boundary * boundary
def digest_range(path, start, size):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        f.seek(start)
        while size:
            b = f.read(min(size, 1024*1024))
            if not b: raise ValueError('Truncated CIA content')
            h.update(b); size -= len(b)
    return h.digest()

def read(path):
    path = Path(path)
    with path.open('rb') as f:
        h = f.read(0x2020)
        if len(h) != 0x2020 or struct.unpack_from('<IHH', h) != (0x2020, 0, 0):
            raise ValueError('Unsupported or truncated CIA header')
        cert_size, ticket_size, tmd_size, meta_size, content_size = struct.unpack_from('<IIIIQ', h, 8)
        if tmd_size > 4*1024*1024 or cert_size > 4*1024*1024 or ticket_size > 1024*1024 or meta_size > 16*1024*1024:
            raise ValueError('Oversized CIA metadata')
        offset = align(len(h)); sections = {}
        for name, size in [('cert',cert_size),('ticket',ticket_size),('tmd',tmd_size),('content',content_size),('meta',meta_size)]:
            if offset + size > path.stat().st_size: raise ValueError('CIA section exceeds input')
            sections[name] = (offset,size); offset = align(offset+size)
        def section(name):
            off,size=sections[name]; f.seek(off);return f.read(size)
        t = section('tmd')
        if len(t)<0xb04 or struct.unpack_from('>I',t)[0]!=0x10004 or t[0x180]!=1:
            raise ValueError('Unsupported CIA TMD signature/layout')
        if struct.unpack_from('>Q',t,0x18c)[0]!=TITLE: raise ValueError('CIA is not the supported Japanese DQXI title')
        count,boot=struct.unpack_from('>HH',t,0x1de)
        if not 1<=count<=65535 or len(t)!=0xb04+count*48:raise ValueError('Invalid CIA content count')
        if hashlib.sha256(t[0x204:0xb04]).digest()!=t[0x1e4:0x204]:raise ValueError('CIA content-info hash mismatch')
        covered=set()
        for i in range(64):
            p=0x204+i*36;start,n=struct.unpack_from('>HH',t,p)
            if not n:continue
            indices=set(range(start,start+n))
            if start+n>count or indices&covered:raise ValueError('CIA content-info range is invalid')
            covered|=indices
            if hashlib.sha256(t[0xb04+start*48:0xb04+(start+n)*48]).digest()!=t[p+4:p+36]:raise ValueError('CIA content-info group hash mismatch')
        if covered!=set(range(count)):raise ValueError('CIA content-info coverage incomplete')
        contents=[];at=sections['content'][0];seen=set()
        for i in range(count):
            p=0xb04+i*48;cid,index,kind,size=struct.unpack_from('>IHHQ',t,p)
            if index in seen:raise ValueError('Duplicate CIA content index')
            seen.add(index)
            if h[0x20+index//8] & (0x80>>(index%8)):
                if at+align(size,16)>sum(sections['content']):raise ValueError('CIA content exceeds section')
                contents.append(dict(row=p,id=cid,index=index,kind=kind,size=size,offset=at,hash=t[p+16:p+48]));at+=align(size,16)
        if at!=sum(sections['content']):raise ValueError('CIA content size does not match TMD')
        present={c['index']for c in contents}
        if any(h[0x20+i//8]&(0x80>>(i%8))for i in range(65536)if i not in present):raise ValueError('CIA bitmap contains an unknown content')
        game=next((c for c in contents if c['index']==boot),None)
        if game is None:raise ValueError('CIA boot content missing')
        f.seek(game['offset']);ncch=f.read(512)
        if len(ncch)!=512 or ncch[256:260]!=b'NCCH' or struct.unpack_from('<Q',ncch,0x118)[0]!=TITLE:
            raise ValueError('CIA game content is encrypted or incompatible; provide a decrypted CIA')
        if digest_range(path,game['offset'],game['size'])!=game['hash']:raise ValueError('CIA game content hash mismatch; encrypted or damaged input')
        return dict(header=h,cert=section('cert'),ticket=section('ticket'),tmd=t,meta=section('meta'),contents=contents,game=game)

def copy_range(source,out,start,size,cancel=None):
    with Path(source).open('rb') as f:
        f.seek(start)
        while size:
            if cancel is not None and cancel.is_set():raise ValueError('CIA build cancelled')
            b=f.read(min(size,1024*1024))
            if not b:raise ValueError('Truncated CIA copy')
            out.write(b);size-=len(b)

def extract_game(source,destination):
    j=read(source)
    with Path(destination).open('xb')as out:copy_range(source,out,j['game']['offset'],j['game']['size'])
    return Path(destination)

def write_replacement(source,game,destination,cancel=None):
    source,game,destination=map(Path,(source,game,destination));j=read(source);t=bytearray(j['tmd']);row=j['game']['row'];newsize=game.stat().st_size
    with game.open('rb')as f:ncch=f.read(512)
    if ncch[256:260]!=b'NCCH' or struct.unpack_from('<Q',ncch,0x118)[0]!=TITLE:raise ValueError('Rebuilt game title mismatch')
    struct.pack_into('>H',t,row+6,j['game']['kind']&~1);struct.pack_into('>Q',t,row+8,newsize);t[row+16:row+48]=digest_range(game,0,newsize)
    for i in range(64):
        p=0x204+36*i;start,n=struct.unpack_from('>HH',t,p)
        if n:t[p+4:p+36]=hashlib.sha256(t[0xb04+start*48:0xb04+(start+n)*48]).digest()
    t[0x1e4:0x204]=hashlib.sha256(t[0x204:0xb04]).digest();h=bytearray(j['header']);content_size=sum(align(newsize if c['index']==j['game']['index']else c['size'],16)for c in j['contents']);struct.pack_into('<Q',h,0x18,content_size)
    with destination.open('xb')as out:
        def pad(boundary=64):out.write(bytes(align(out.tell(),boundary)-out.tell()))
        for data in(h,j['cert'],j['ticket'],t):out.write(data);pad()
        for c in j['contents']:
            selected=c['index']==j['game']['index'];size=newsize if selected else c['size'];copy_range(game if selected else source,out,0 if selected else c['offset'],size,cancel);pad(16)
        pad();out.write(j['meta'])
    rebuilt=read(destination)
    for key in('cert','ticket','meta'):assert rebuilt[key]==j[key]
    for old,new in zip(j['contents'],rebuilt['contents']):
        assert old['id']==new['id']and old['index']==new['index']
        expected=t[row+16:row+48]if old['index']==j['game']['index']else digest_range(source,old['offset'],old['size'])
        if digest_range(destination,new['offset'],new['size'])!=expected:raise ValueError('Rebuilt CIA content verification failed')
    return destination
