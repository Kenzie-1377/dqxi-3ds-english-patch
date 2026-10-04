#!/usr/bin/env python3
"""Export and import translatable Dragon Quest XI (3DS) BXON text."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path


MARKER = b"&&&&"
TEXT_BLOCK_CLASS = "TextBlock"
CHARACTER_IE_CLASS = "CharacterIEData"


@dataclass
class TextRecord:
    index: int
    key: int
    descriptor_offset: int
    pointer_offset: int
    target_offset: int
    block_start: int
    string_end: int
    block_end: int
    text: str


@dataclass
class MarkerTextRecord:
    index: int
    marker_offset: int
    target_offset: int
    string_end: int
    text: str
    references: list[int]


def _class_name(blob: bytes) -> str:
    if blob[:4] != b"BXON":
        raise ValueError("not a BXON file")
    end = blob.index(0, 0xC)
    return blob[0xC:end].decode("ascii")


def _aligned_utf16(text: str, original_size: int) -> bytes:
    data = text.encode("utf-16le") + b"\0\0"
    while len(data) % 4 != original_size % 4:
        data += b"\0\0"
    return data


def _write_separate(source: Path, output: Path, data: bytes) -> None:
    if output.resolve() == source.resolve():
        raise ValueError("output must differ from the source")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(data)


def parse_text_block(blob: bytes) -> list[TextRecord]:
    class_name = _class_name(blob)
    if class_name != TEXT_BLOCK_CLASS:
        raise ValueError(f"unsupported BXON class {class_name!r}; expected {TEXT_BLOCK_CLASS!r}")
    if len(blob) < 0x38 or blob[0x28:0x2C] != MARKER:
        raise ValueError("unexpected TextBlock header layout")

    count = struct.unpack_from("<I", blob, 0x2C)[0]
    if count == 0:
        return []
    if len(blob) < 0x3C or blob[0x38:0x3C] != MARKER:
        raise ValueError("unexpected non-empty TextBlock descriptor layout")
    descriptor_start = 0x40
    descriptor_size = 0x1C
    pointers: list[tuple[int, int, int, int]] = []
    for index in range(count):
        offset = descriptor_start + index * descriptor_size
        if offset + descriptor_size > len(blob):
            raise ValueError("TextBlock descriptor table exceeds file size")
        key = struct.unpack_from("<I", blob, offset + 8)[0]
        pointer_offset = offset + 0x10
        relative = struct.unpack_from("<I", blob, pointer_offset)[0]
        target = pointer_offset + relative
        block_start = target - len(MARKER)
        if block_start < 0 or blob[block_start:target] != MARKER:
            raise ValueError(f"record {index} does not point to an &&&& text block")
        pointers.append((index, key, offset, target))

    targets = [item[3] for item in pointers]
    if targets != sorted(targets) or len(targets) != len(set(targets)):
        raise ValueError("TextBlock string targets are not strictly increasing")

    records: list[TextRecord] = []
    for position, (index, key, descriptor_offset, target) in enumerate(pointers):
        terminator = -1
        cursor = target
        while cursor + 1 < len(blob):
            if blob[cursor:cursor + 2] == b"\0\0":
                terminator = cursor
                break
            cursor += 2
        if terminator < 0:
            raise ValueError(f"record {index} has no UTF-16 terminator")
        block_end = targets[position + 1] - len(MARKER) if position + 1 < len(targets) else len(blob)
        if terminator + 2 > block_end:
            raise ValueError(f"record {index} string overlaps the next block")
        text = blob[target:terminator].decode("utf-16le")
        records.append(
            TextRecord(
                index=index,
                key=key,
                descriptor_offset=descriptor_offset,
                pointer_offset=descriptor_offset + 0x10,
                target_offset=target,
                block_start=target - len(MARKER),
                string_end=terminator + 2,
                block_end=block_end,
                text=text,
            )
        )
    return records


def _marker_references(blob: bytes) -> tuple[list[int], dict[int, list[int]]]:
    """Find arithmetic candidates for READ-ONLY discovery, never pointer proof.

    Numeric fields can coincide with marker offsets. EnemyBaseParam category
    20/flags 1 at 0xB08 was one such collision and was corrupted by relocation.
    Neither this function nor exported references authorizes a write.
    """
    markers: list[int] = []
    cursor = 0
    while True:
        marker = blob.find(MARKER, cursor)
        if marker < 0:
            break
        markers.append(marker)
        cursor = marker + len(MARKER)
    references: dict[int, list[int]] = {marker + 4: [] for marker in markers}
    for pointer_offset in range(0, len(blob) - 3, 4):
        relative = struct.unpack_from("<I", blob, pointer_offset)[0]
        target = pointer_offset + relative
        if relative and target in references:
            references[target].append(pointer_offset)
    return markers, references


def _decode_marker_text(blob: bytes, target: int) -> tuple[str, int] | None:
    units: list[int] = []
    cursor = target
    while cursor + 1 < len(blob) and len(units) < 0x10000:
        unit = struct.unpack_from("<H", blob, cursor)[0]
        cursor += 2
        if unit == 0:
            break
        units.append(unit)
    else:
        return None
    if not units:
        return None

    def allowed(unit: int) -> bool:
        return (
            1 <= unit <= 0x0D
            or 0x20 <= unit <= 0x7E
            or 0x2000 <= unit <= 0x206F
            or 0x3000 <= unit <= 0x30FF
            or 0x3400 <= unit <= 0x9FFF
            or 0xF900 <= unit <= 0xFAFF
            or 0xFF00 <= unit <= 0xFFEF
        )

    if not all(allowed(unit) for unit in units):
        return None
    # Reject binary descriptor blocks which happen to begin with small integers.
    if not any(
        0x21 <= unit <= 0x7E
        or 0x2000 <= unit <= 0x206F
        or 0x3000 <= unit <= 0x30FF
        or 0x3400 <= unit <= 0x9FFF
        or 0xF900 <= unit <= 0xFAFF
        or 0xFF00 <= unit <= 0xFFEF
        for unit in units
    ):
        return None
    return bytes(struct.pack("<" + "H" * len(units), *units)).decode("utf-16le"), cursor


def parse_marker_text(blob: bytes, expected_class: str | None = None) -> list[MarkerTextRecord]:
    """Heuristic inventory only; references may include non-pointer fields."""
    class_name = _class_name(blob)
    if expected_class is not None and class_name != expected_class:
        raise ValueError(f"unsupported BXON class; expected {expected_class!r}")
    markers, references = _marker_references(blob)
    records: list[MarkerTextRecord] = []
    for marker in markers:
        target = marker + 4
        if not references[target]:
            continue
        decoded = _decode_marker_text(blob, target)
        if decoded is None:
            continue
        value, string_end = decoded
        records.append(MarkerTextRecord(
            index=len(records), marker_offset=marker, target_offset=target,
            string_end=string_end, text=value, references=references[target]
        ))
    return records


def parse_character_ie(blob: bytes) -> list[MarkerTextRecord]:
    return parse_marker_text(blob, CHARACTER_IE_CLASS)


def export_marker_bxon(source: Path, output: Path) -> None:
    blob = source.read_bytes()
    class_name = _class_name(blob)
    records = parse_marker_text(blob)
    payload = {
        "format": "dq11-3ds-marker-text-v1",
        "source": str(source),
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "class": class_name,
        "references_kind": "heuristic-candidates-not-schema-proof",
        "entries": [
            {"id": f"{record.marker_offset:08X}", "offset": record.marker_offset,
             "references": record.references, "source": record.text, "translation": ""}
            for record in records
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_marker_bxon(source: Path, translation: Path, output: Path) -> None:
    if output.resolve() == translation.resolve():
        raise ValueError("output must differ from the manifest")
    payload = json.loads(translation.read_text(encoding="utf-8"))
    if payload.get("format") != "dq11-3ds-marker-text-v1":
        raise ValueError("unsupported marker-text translation JSON format")
    if payload.get("class") != _class_name(source.read_bytes()):
        raise ValueError("translation manifest class does not match the BXON file")
    _import_marker_records(source, payload, output)


def _import_marker_records(source: Path, payload: dict, output: Path) -> None:
    blob = source.read_bytes()
    if payload.get("source_sha256") != hashlib.sha256(blob).hexdigest():
        raise ValueError("source hash mismatch; no changes made")
    if payload.get("class") != _class_name(blob):
        raise ValueError("translation manifest class does not match the BXON file")
    records = parse_marker_text(blob)
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) != len(records):
        raise ValueError("translation entry count does not match the BXON file")
    changed = False
    for record, entry in zip(records, entries):
        expected_id = f"{record.marker_offset:08X}"
        if entry.get("id") != expected_id or entry.get("source") != record.text:
            raise ValueError(f"translation entry mismatch at {expected_id}")
        translated = entry.get("translation")
        if translated is None or translated == "":
            translated = record.text
        if not isinstance(translated, str):
            raise ValueError(f"translation for {expected_id} must be a string")
        changed |= translated != record.text
    if changed:
        raise ValueError(
            "unsafe heuristic marker import disabled: class-specific, typed "
            "pointer schema required; exported references are not proof. "
            "For TextBlock dialogue use the descriptor-based import command."
        )
    # A no-op must retain every byte, including padding and pointer lookalikes.
    # Unsupported schemas are intentionally not 'fixed' by ignoring bad bytes,
    # accepting same-size edits, or appending text through guessed references.
    _write_separate(source, output, blob)


def export_character_ie(source: Path, output: Path) -> None:
    blob = source.read_bytes()
    records = parse_character_ie(blob)
    payload = {
        "format": "dq11-3ds-character-ie-v1",
        "source": str(source),
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "class": CHARACTER_IE_CLASS,
        "references_kind": "heuristic-candidates-not-schema-proof",
        "entries": [
            {
                "id": f"{record.marker_offset:08X}",
                "offset": record.marker_offset,
                "references": record.references,
                "source": record.text,
                "translation": "",
            }
            for record in records
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_character_ie(source: Path, translation: Path, output: Path) -> None:
    if output.resolve() == translation.resolve():
        raise ValueError("output must differ from the manifest")
    payload = json.loads(translation.read_text(encoding="utf-8"))
    if payload.get("format") != "dq11-3ds-character-ie-v1":
        raise ValueError("unsupported CharacterIEData translation JSON format")
    if payload.get("class") != CHARACTER_IE_CLASS:
        raise ValueError("expected CharacterIEData manifest class")
    _import_marker_records(source, payload, output)


def export_text_block(source: Path, output: Path) -> None:
    blob = source.read_bytes()
    records = parse_text_block(blob)
    payload = {
        "format": "dq11-3ds-textblock-v1",
        "source": str(source),
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "class": TEXT_BLOCK_CLASS,
        "entries": [
            {
                "id": f"{record.key:08X}:{record.index:04d}",
                "key": record.key,
                "index": record.index,
                "source": record.text,
                "translation": "",
            }
            for record in records
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_text_block(source: Path, translation: Path, output: Path) -> None:
    if output.resolve() == translation.resolve():
        raise ValueError("output must differ from the manifest")
    blob = source.read_bytes()
    records = parse_text_block(blob)
    payload = json.loads(translation.read_text(encoding="utf-8"))
    if payload.get("format") != "dq11-3ds-textblock-v1":
        raise ValueError("unsupported translation JSON format")
    if payload.get("source_sha256") != hashlib.sha256(blob).hexdigest():
        raise ValueError("source hash mismatch; no changes made")
    if payload.get("class") != TEXT_BLOCK_CLASS:
        raise ValueError("expected TextBlock manifest class")
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) != len(records):
        raise ValueError("translation entry count does not match the BXON file")
    no_op = True
    for record, entry in zip(records, entries):
        if entry.get("id") != f"{record.key:08X}:{record.index:04d}" or entry.get("source") != record.text:
            raise ValueError("translation entry mismatch")
        value = entry.get("translation")
        if value is None or value == "":
            value = record.text
        if not isinstance(value, str):
            raise ValueError("translation must be a string")
        if "\0" in value:
            raise ValueError("embedded NUL in translation")
        no_op &= value == record.text
    if no_op:
        _write_separate(source, output, blob)
        return

    first_block = records[0].block_start if records else len(blob)
    rebuilt = bytearray(blob[:first_block])
    new_targets: list[int] = []
    resized_strings: list[tuple[int, int, int]] = []
    for record, entry in zip(records, entries):
        expected_id = f"{record.key:08X}:{record.index:04d}"
        if entry.get("id") != expected_id or entry.get("source") != record.text:
            raise ValueError(f"translation entry mismatch at {expected_id}")
        translated = entry.get("translation")
        if translated is None or translated == "":
            translated = record.text
        if not isinstance(translated, str):
            raise ValueError(f"translation for {expected_id} must be a string")

        rebuilt.extend(MARKER)
        new_targets.append(len(rebuilt))
        encoded = _aligned_utf16(translated, record.string_end - record.target_offset)
        rebuilt.extend(encoded)
        resized_strings.append((record.target_offset, record.string_end, len(encoded)))
        rebuilt.extend(blob[record.string_end:record.block_end])

    for record, new_target in zip(records, new_targets):
        relative = new_target - record.pointer_offset
        if relative < 0 or relative > 0xFFFFFFFF:
            raise ValueError(f"rebuilt pointer for record {record.index} is out of range")
        struct.pack_into("<I", rebuilt, record.pointer_offset, relative)

    # TextBlock has a separate speaker-name pointer at descriptor + 0x0C.
    # Names are interleaved with dialogue, so resizing dialogue relocates them
    # too. Leaving these pointers untouched makes name boxes display dialogue.
    for record in records:
        pointer = record.descriptor_offset + 0x0C
        relative = struct.unpack_from("<I", blob, pointer)[0]
        if not relative:
            continue
        target = pointer + relative
        if blob[target - 4:target] != MARKER:
            raise ValueError(f"record {record.index} has an invalid speaker pointer; repair from the original first")
        delta = 0
        for start, end, length in resized_strings:
            if target < start:
                break
            if target < end:
                raise ValueError("speaker pointer unexpectedly targets dialogue")
            delta += length - (end - start)
        struct.pack_into("<I", rebuilt, pointer, target + delta - pointer)

    _write_separate(source, output, bytes(rebuilt))


def command_info(args: argparse.Namespace) -> None:
    blob = args.source.read_bytes()
    records = parse_text_block(blob)
    print(f"class: {TEXT_BLOCK_CLASS}")
    print(f"records: {len(records)}")
    print(f"characters: {sum(len(record.text) for record in records)}")


def command_export(args: argparse.Namespace) -> None:
    export_text_block(args.source, args.output)


def command_import(args: argparse.Namespace) -> None:
    import_text_block(args.source, args.translation, args.output)


def command_character_export(args: argparse.Namespace) -> None:
    export_character_ie(args.source, args.output)


def command_character_import(args: argparse.Namespace) -> None:
    import_character_ie(args.source, args.translation, args.output)


def command_marker_export(args: argparse.Namespace) -> None:
    export_marker_bxon(args.source, args.output)


def command_marker_import(args: argparse.Namespace) -> None:
    import_marker_bxon(args.source, args.translation, args.output)


def command_marker_bulk_export(args: argparse.Namespace) -> None:
    file_count = record_count = character_count = 0
    errors = []
    for source in sorted(args.root.rglob("*.bxon")):
        try:
            records = parse_marker_text(source.read_bytes())
            if not records:
                continue
            relative = source.relative_to(args.root).with_suffix(".json")
            export_marker_bxon(source, args.output / relative)
            file_count += 1
            record_count += len(records)
            character_count += sum(len(record.text) for record in records)
        except (OSError, ValueError, UnicodeError, struct.error) as exc:
            errors.append({"source": str(source), "error": str(exc)})
    report = {"format": "dq11-3ds-marker-text-export-report-v1", "files": file_count,
              "records": record_count, "characters": character_count, "errors": errors}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"files: {file_count}")
    print(f"records: {record_count}")
    print(f"characters: {character_count}")
    print(f"errors: {len(errors)}")


def command_character_bulk_export(args: argparse.Namespace) -> None:
    file_count = record_count = character_count = 0
    errors = []
    for source in sorted(args.root.rglob("*.bxon")):
        try:
            blob = source.read_bytes()
            if _class_name(blob) != CHARACTER_IE_CLASS:
                continue
            records = parse_character_ie(blob)
            relative = source.relative_to(args.root).with_suffix(".json")
            export_character_ie(source, args.output / relative)
            file_count += 1
            record_count += len(records)
            character_count += sum(len(record.text) for record in records)
        except (OSError, ValueError, UnicodeError, struct.error) as exc:
            errors.append({"source": str(source), "error": str(exc)})
    report = {
        "format": "dq11-3ds-character-ie-export-report-v1",
        "files": file_count, "records": record_count,
        "characters": character_count, "errors": errors,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"files: {file_count}")
    print(f"records: {record_count}")
    print(f"characters: {character_count}")
    print(f"errors: {len(errors)}")


def command_bulk_export(args: argparse.Namespace) -> None:
    file_count = 0
    record_count = 0
    character_count = 0
    errors = []
    for source in sorted(args.root.rglob("*.bxon")):
        blob = source.read_bytes()
        try:
            if _class_name(blob) != TEXT_BLOCK_CLASS:
                continue
            records = parse_text_block(blob)
            relative = source.relative_to(args.root).with_suffix(".json")
            export_text_block(source, args.output / relative)
            file_count += 1
            record_count += len(records)
            character_count += sum(len(record.text) for record in records)
        except (OSError, ValueError, UnicodeError, struct.error) as exc:
            errors.append({"source": str(source), "error": str(exc)})

    report = {
        "format": "dq11-3ds-textblock-export-report-v1",
        "files": file_count,
        "records": record_count,
        "characters": character_count,
        "errors": errors,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"files: {file_count}")
    print(f"records: {record_count}")
    print(f"characters: {character_count}")
    print(f"errors: {len(errors)}")


def command_markers(args: argparse.Namespace) -> None:
    blob = args.source.read_bytes()
    markers = []
    cursor = 0
    while True:
        marker = blob.find(MARKER, cursor)
        if marker < 0:
            break
        markers.append(marker)
        cursor = marker + 4

    references: dict[int, list[int]] = {marker: [] for marker in markers}
    marker_targets = {marker + 4: marker for marker in markers}
    for pointer_offset in range(0, len(blob) - 3, 4):
        relative = struct.unpack_from("<I", blob, pointer_offset)[0]
        target = pointer_offset + relative
        marker = marker_targets.get(target)
        if marker is not None and relative:
            references[marker].append(pointer_offset)

    print(f"class: {_class_name(blob)}")
    print(f"markers: {len(markers)}")
    for marker in markers:
        target = marker + 4
        preview_units = []
        for offset in range(target, min(target + 80, len(blob) - 1), 2):
            unit = struct.unpack_from("<H", blob, offset)[0]
            if unit == 0:
                break
            if unit < 0x20:
                preview_units.append(f"<{unit:02X}>")
            elif 0x20 <= unit <= 0x7E or 0x3000 <= unit <= 0x9FFF or 0xFF00 <= unit <= 0xFFEF:
                preview_units.append(chr(unit))
            else:
                preview_units.append("·")
        refs = ",".join(f"0x{value:X}" for value in references[marker]) or "-"
        print(f"0x{marker:08X} refs={refs:20s} {''.join(preview_units)}")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="inspect a TextBlock BXON")
    info_parser.add_argument("source", type=Path)
    info_parser.set_defaults(func=command_info)

    export_parser = subparsers.add_parser("export", help="export TextBlock records to JSON")
    export_parser.add_argument("source", type=Path)
    export_parser.add_argument("output", type=Path)
    export_parser.set_defaults(func=command_export)

    import_parser = subparsers.add_parser("import", help="import TextBlock JSON into a rebuilt BXON")
    import_parser.add_argument("source", type=Path)
    import_parser.add_argument("translation", type=Path)
    import_parser.add_argument("output", type=Path)
    import_parser.set_defaults(func=command_import)

    character_export = subparsers.add_parser("character-export", help="export NPC/book CharacterIEData text")
    character_export.add_argument("source", type=Path)
    character_export.add_argument("output", type=Path)
    character_export.set_defaults(func=command_character_export)

    character_import = subparsers.add_parser("character-import", help="import NPC/book CharacterIEData text")
    character_import.add_argument("source", type=Path)
    character_import.add_argument("translation", type=Path)
    character_import.add_argument("output", type=Path)
    character_import.set_defaults(func=command_character_import)

    marker_export = subparsers.add_parser("marker-export", help="export marker-style text from any BXON class")
    marker_export.add_argument("source", type=Path)
    marker_export.add_argument("output", type=Path)
    marker_export.set_defaults(func=command_marker_export)

    marker_import = subparsers.add_parser("marker-import", help="import marker-style BXON text")
    marker_import.add_argument("source", type=Path)
    marker_import.add_argument("translation", type=Path)
    marker_import.add_argument("output", type=Path)
    marker_import.set_defaults(func=command_marker_import)

    marker_bulk = subparsers.add_parser("marker-bulk-export", help="export marker text from every BXON below a root")
    marker_bulk.add_argument("root", type=Path)
    marker_bulk.add_argument("output", type=Path)
    marker_bulk.set_defaults(func=command_marker_bulk_export)

    character_bulk = subparsers.add_parser("character-bulk-export", help="export all CharacterIEData text")
    character_bulk.add_argument("root", type=Path)
    character_bulk.add_argument("output", type=Path)
    character_bulk.set_defaults(func=command_character_bulk_export)

    bulk_export_parser = subparsers.add_parser("bulk-export", help="export every TextBlock below a BXON root")
    bulk_export_parser.add_argument("root", type=Path)
    bulk_export_parser.add_argument("output", type=Path)
    bulk_export_parser.set_defaults(func=command_bulk_export)

    markers_parser = subparsers.add_parser("markers", help="diagnose marker blocks and relative references")
    markers_parser.add_argument("source", type=Path)
    markers_parser.set_defaults(func=command_markers)

    return parser


def main() -> None:
    args = make_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
