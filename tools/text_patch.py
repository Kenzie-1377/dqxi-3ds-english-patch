"""Apply reviewed relative UTF-16 pointer edits to an exact local input."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

TOKEN = re.compile(r'\x04[\s\S]')


def wrap_text(text, limit=24, player_width=6, other_width=20):
    """Wrap whole words, preserving substitution codes and blank paragraphs."""
    if min(limit, player_width, other_width) < 1:
        raise ValueError('Widths must be positive')
    if re.search('[\ue000-\ue0ff]', text):
        raise ValueError('Reserved placeholder character in input')
    if any(ord(m[1]) > 255 for m in TOKEN.findall(text)):
        raise ValueError('Unsupported substitution code')
    protected = TOKEN.sub(lambda m: chr(0xe000 + ord(m[0][1])), text)

    def width(word):
        return sum(player_width if c == '\ue001' else other_width
                   if 0xe000 <= ord(c) <= 0xe0ff else 1 for c in word)

    result = []
    for paragraph in re.split(r'\n[ \t]*\n', protected.replace('\r\n', '\n')):
        lines, line = [], ''
        for word in re.split(r'[ \t\r\n]+', paragraph.strip(' \t\r\n')):
            if width(word) > limit:
                raise ValueError('A word or substitution exceeds the line limit')
            candidate = line + ' ' + word if line else word
            if line and width(candidate) > limit:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        result.append('\n'.join(lines))
    return re.sub('[\ue000-\ue0ff]', lambda m: '\x04' + chr(ord(m[0]) - 0xe000),
                  '\n\n'.join(result))


def read_text(blob, pointer):
    if pointer < 0 or pointer % 4 or pointer + 4 > len(blob):
        raise ValueError('Invalid pointer offset')
    relative = struct.unpack_from('<I', blob, pointer)[0]
    target = pointer + relative
    if not relative or target < 4 or target % 2 or blob[target-4:target] != b'&&&&':
        raise ValueError('Pointer does not reference a marked UTF-16 string')
    end = target
    while end + 2 <= len(blob):
        if blob[end:end+2] == b'\0\0':
            return blob[target:end].decode('utf-16le')
        end += 2
    raise ValueError('Unterminated text')


def apply_patch(blob, manifest):
    if manifest.get('format') != 'reviewed-text-pointers-v1':
        raise ValueError('Unsupported manifest format')
    if hashlib.sha256(blob).hexdigest() != manifest.get('input_sha256'):
        raise ValueError('Input hash mismatch; no changes made')
    edits = manifest['edits']
    seen = set()
    for edit in edits:
        p, old, new = edit['pointer'], edit['old'], edit['new']
        if p in seen or read_text(blob, p) != old:
            raise ValueError('Duplicate pointer or unexpected current text')
        seen.add(p)
        if '\0' in new or TOKEN.findall(old) != TOKEN.findall(new):
            raise ValueError('NUL or changed substitution sequence')
        # Preserve all controls except line/paragraph whitespace.
        control = lambda t: re.findall('[\x01-\x09\x0b\x0c\x0e-\x1f]', t)
        if control(old) != control(new):
            raise ValueError('Non-layout control codes changed')
    result = bytearray(blob)
    for edit in edits:
        result.extend(b'\0' * (-len(result) % 4) + b'&&&&')
        target = len(result)
        result.extend((edit['new'] + '\0').encode('utf-16le'))
        struct.pack_into('<I', result, edit['pointer'], target - edit['pointer'])
    allowed = {i for p in seen for i in range(p, p + 4)}
    if any(a != b and i not in allowed for i, (a, b) in enumerate(zip(blob, result))):
        raise ValueError('Unexpected change outside text pointers')
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.resolve() in {args.input.resolve(), args.manifest.resolve()}:
        parser.error('Output must differ from input and manifest')
    result = apply_patch(args.input.read_bytes(), json.loads(args.manifest.read_text(encoding='utf8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(result)
    print('Created a separate patched output. Original input unchanged.')


if __name__ == '__main__':
    main()
