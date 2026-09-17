# Reviewed text patches

Use a separate local input and output. The command refuses to overwrite existing
output files. Do not publish generated archives or manifests containing game text.

```sh
python tools/text_patch.py input/example.bxon private/edits.json output/example.bxon
```

The local manifest format is:

```json
{
  "format": "reviewed-text-pointers-v1",
  "input_sha256": "REPLACE_WITH_EXACT_SHA256_OF_LOCAL_INPUT",
  "edits": [
    {"pointer": 80, "old": "Synthetic sample", "new": "Revised sample"}
  ]
}
```

The offset above is illustrative, not an offset for a specific game version.
Offsets must be obtained from a validated structural parser or manual format
review, not an unrestricted search for pointer-shaped integers.

The patcher verifies the input hash and old strings, appends new marked UTF-16
strings, and updates only the listed four-byte relative pointers. Other existing
bytes remain unchanged. It does not establish that the supplied offsets belong
to dialogue: the manifest author must verify that separately.

Substitution tokens and other non-layout controls must stay in the same order.
Word wrapping is a separate function, `wrap_text`, and never truncates messages.
It cannot validate pagination, font metrics, event behavior, or save compatibility.

Before testing generated files, back up your own inputs and saves. Do not replace
live files while a game is writing data. No save editor or automatic deployment
script is included in this source release.
