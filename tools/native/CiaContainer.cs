using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Threading;

// Decrypted CIA preservation/reconstruction. Modified signatures require CFW.
public static class CiaContainer {
 const ulong Title=0x0004000000199200UL;
 public sealed class Content {public int Row,Index,Kind;public uint Id;public long Offset,Size;public byte[] Hash;}
 public sealed class Info {public byte[] Header,Cert,Ticket,Tmd,Meta;public List<Content> Contents=new List<Content>();public Content Game;}
 static Exception Bad(string s){return new InvalidDataException(s);}
 static long Align(long n,int a){return checked((n+a-1)/a*a);}
 static uint LE32(byte[] b,int p){return (uint)(b[p]|b[p+1]<<8|b[p+2]<<16|b[p+3]<<24);}
 static ulong LE64(byte[] b,int p){return LE32(b,p)|((ulong)LE32(b,p+4)<<32);}
 static ulong BE(byte[] b,int p,int n){ulong v=0;for(int i=0;i<n;i++)v=(v<<8)|b[p+i];return v;}
 static void PutBE(byte[] b,int p,int n,ulong v){for(int i=n-1;i>=0;i--){b[p+i]=(byte)v;v>>=8;}}
 static byte[] Slice(byte[] b,int p,int n){byte[] r=new byte[n];Array.Copy(b,p,r,0,n);return r;}
 static byte[] ReadAt(FileStream f,long p,int n){if(p<0||n<0||p>f.Length-n)throw Bad("CIA section bounds");f.Position=p;byte[] b=new byte[n];int at=0;while(at<n){int x=f.Read(b,at,n-at);if(x==0)throw Bad("CIA truncated");at+=x;}return b;}
 static byte[] Hash(byte[] b,int p,int n){using(var h=SHA256.Create())return h.ComputeHash(b,p,n);}
 static bool Equal(byte[] a,byte[] b){if(a.Length!=b.Length)return false;int d=0;for(int i=0;i<a.Length;i++)d|=a[i]^b[i];return d==0;}
 static byte[] FileHash(string p,long start,long size,CancellationToken cancel){using(var f=File.OpenRead(p))using(var h=SHA256.Create()){if(start<0||size<0||start>f.Length-size)throw Bad("CIA hash bounds");f.Position=start;byte[] b=new byte[1048576];while(size>0){cancel.ThrowIfCancellationRequested();int n=f.Read(b,0,(int)Math.Min(size,b.Length));if(n==0)throw Bad("CIA truncated");h.TransformBlock(b,0,n,b,0);size-=n;}h.TransformFinalBlock(new byte[0],0,0);return h.Hash;}}
 static void TitleCheck(byte[] b){if(b.Length<512||b[256]!='N'||b[257]!='C'||b[258]!='C'||b[259]!='H'||LE64(b,0x118)!=Title)throw Bad("Provide a decrypted CIA of the supported Japanese DQXI game");}
 public static Info Read(string path,CancellationToken cancel){
  BuildSupport.NoReparse(path);var j=new Info();using(var f=File.OpenRead(path)){
   j.Header=ReadAt(f,0,0x2020);var h=j.Header;if(LE32(h,0)!=0x2020||LE32(h,4)!=0)throw Bad("Unsupported CIA header");
   int cert=checked((int)LE32(h,8)),ticket=checked((int)LE32(h,12)),tmd=checked((int)LE32(h,16)),meta=checked((int)LE32(h,20));long cs=checked((long)LE64(h,24));
   if(cert>4194304||ticket>1048576||tmd>4194304||meta>16777216)throw Bad("CIA metadata too large");
   long at=Align(h.Length,64);j.Cert=ReadAt(f,at,cert);at=Align(at+cert,64);j.Ticket=ReadAt(f,at,ticket);at=Align(at+ticket,64);j.Tmd=ReadAt(f,at,tmd);at=Align(at+tmd,64);long contentAt=at;if(cs<0||at>f.Length-cs)throw Bad("CIA content section bounds");j.Meta=ReadAt(f,Align(at+cs,64),meta);
   byte[] t=j.Tmd;if(t.Length<0xb04||BE(t,0,4)!=0x10004||t[0x180]!=1||BE(t,0x18c,8)!=Title)throw Bad("CIA TMD is incompatible");
   int count=(int)BE(t,0x1de,2),boot=(int)BE(t,0x1e0,2);if(count<1||t.Length!=0xb04+count*48)throw Bad("CIA TMD content count");
   if(!Equal(Hash(t,0x204,0x900),Slice(t,0x1e4,32)))throw Bad("CIA content-info checksum");var covered=new HashSet<int>();
   for(int i=0;i<64;i++){int p=0x204+i*36,start=(int)BE(t,p,2),n=(int)BE(t,p+2,2);if(n==0)continue;if(start+n>count)throw Bad("CIA content-info range");for(int k=start;k<start+n;k++)if(!covered.Add(k))throw Bad("CIA overlapping content-info ranges");if(!Equal(Hash(t,0xb04+start*48,n*48),Slice(t,p+4,32)))throw Bad("CIA content group checksum");}
   if(covered.Count!=count)throw Bad("CIA content-info coverage");var seen=new HashSet<int>();var present=new HashSet<int>();
   for(int i=0;i<count;i++){int p=0xb04+i*48,index=(int)BE(t,p+4,2);if(!seen.Add(index))throw Bad("Duplicate CIA content index");if((h[0x20+index/8]&(0x80>>(index%8)))==0)continue;long size=checked((long)BE(t,p+8,8));if(size<0||at>contentAt+cs-Align(size,16))throw Bad("CIA content range");var c=new Content{Row=p,Index=index,Id=(uint)BE(t,p,4),Kind=(int)BE(t,p+6,2),Size=size,Offset=at,Hash=Slice(t,p+16,32)};j.Contents.Add(c);present.Add(index);if(index==boot)j.Game=c;at=checked(at+Align(size,16));}
   if(at!=contentAt+cs)throw Bad("CIA content size mismatch");for(int i=0;i<65536;i++)if((h[0x20+i/8]&(0x80>>(i%8)))!=0&&!present.Contains(i))throw Bad("CIA unknown bitmap content");
   if(j.Game==null)throw Bad("CIA boot content missing");TitleCheck(ReadAt(f,j.Game.Offset,512));
  }
  if(!Equal(FileHash(path,j.Game.Offset,j.Game.Size,cancel),j.Game.Hash))throw Bad("CIA game content encrypted or damaged");return j;
 }
 static void Copy(string source,FileStream output,long start,long size,CancellationToken cancel){using(var f=File.OpenRead(source)){if(start<0||size<0||start>f.Length-size)throw Bad("CIA copy bounds");f.Position=start;byte[] b=new byte[1048576];while(size>0){cancel.ThrowIfCancellationRequested();int n=f.Read(b,0,(int)Math.Min(size,b.Length));if(n==0)throw Bad("CIA truncated");output.Write(b,0,n);size-=n;}}}
 public static string ExtractGame(string source,string destination,CancellationToken cancel){var j=Read(source,cancel);BuildSupport.NoReparse(destination);using(var f=new FileStream(destination,FileMode.CreateNew,FileAccess.Write))Copy(source,f,j.Game.Offset,j.Game.Size,cancel);return destination;}
 static void Pad(FileStream f,int a){int n=(int)(Align(f.Position,a)-f.Position);f.Write(new byte[n],0,n);}
 public static void WriteReplacement(string source,string game,string output,CancellationToken cancel){
  var j=Read(source,cancel);byte[] t=(byte[])j.Tmd.Clone(),h=(byte[])j.Header.Clone();long size=new FileInfo(game).Length;using(var f=File.OpenRead(game))TitleCheck(ReadAt(f,0,512));int p=j.Game.Row;
  PutBE(t,p+6,2,(ulong)(j.Game.Kind&~1));PutBE(t,p+8,8,(ulong)size);byte[] gh=FileHash(game,0,size,cancel);Array.Copy(gh,0,t,p+16,32);
  for(int i=0;i<64;i++){int q=0x204+i*36,start=(int)BE(t,q,2),n=(int)BE(t,q+2,2);if(n!=0)Array.Copy(Hash(t,0xb04+start*48,n*48),0,t,q+4,32);}Array.Copy(Hash(t,0x204,0x900),0,t,0x1e4,32);
  long contentSize=0;foreach(var c in j.Contents)contentSize=checked(contentSize+Align(c.Index==j.Game.Index?size:c.Size,16));ulong v=(ulong)contentSize;for(int i=0;i<8;i++){h[24+i]=(byte)v;v>>=8;}
  BuildSupport.NoReparse(output);using(var f=new FileStream(output,FileMode.CreateNew,FileAccess.Write)){foreach(byte[] data in new byte[][]{h,j.Cert,j.Ticket,t}){f.Write(data,0,data.Length);Pad(f,64);}foreach(var c in j.Contents){bool selected=c.Index==j.Game.Index;Copy(selected?game:source,f,selected?0:c.Offset,selected?size:c.Size,cancel);Pad(f,16);}Pad(f,64);f.Write(j.Meta,0,j.Meta.Length);}
  var result=Read(output,cancel);if(!Equal(result.Cert,j.Cert)||!Equal(result.Ticket,j.Ticket)||!Equal(result.Meta,j.Meta)||result.Contents.Count!=j.Contents.Count)throw Bad("CIA metadata was not preserved");
  for(int i=0;i<j.Contents.Count;i++){var a=j.Contents[i];var b=result.Contents[i];if(a.Index!=b.Index||a.Id!=b.Id||!Equal(FileHash(output,b.Offset,b.Size,cancel),a.Index==j.Game.Index?gh:FileHash(source,a.Offset,a.Size,cancel)))throw Bad("CIA content readback mismatch");}
 }
}
