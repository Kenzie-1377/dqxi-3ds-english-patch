# Heliodor bridge diagnostic archives (0.3.0 only)

These are **temporary diagnostic variants, not a release or a finished fix**.
They help isolate a reported 3D-mode bridge crash on New 3DS-family hardware.
Only small delta files are distributed here. They require the exact translated
`romfs/gamecmn.pack` from the 0.3.0 release build; no complete game archive is
included. No tool in this folder edits saves.

Run from the repository root, using Python 3.10 or newer:

```sh
python tools/build_bridge_diagnostics.py "PATH_TO_0.3.0_MOD/romfs/gamecmn.pack" --output "NEW_DIAGNOSTIC_FOLDER"
```

The input must have SHA-256
`493b95fad71a6a06da99a7c70b589cf0169c93307624476b69c114773b31c79a`.
The script refuses a different input or an existing output folder, verifies
each delta and reconstructed file, and leaves the input untouched. It creates
three subfolders, each containing a `gamecmn.pack`. The generated archives
contain game data; keep them private and do not distribute them.

With the game completely closed, back up the installed mod's
`romfs/gamecmn.pack`. On a **test copy of the 0.3.0 mod**, copy only one
candidate to that path. Boot normally, use a new or expendable test save in 3D
mode, cross the same bridge, and note whether it crashes and whether graphics
and textures appear normal. Close the game before changing candidates. Restore
the original mod file after testing. Do not edit or delete saves, and do not
combine candidates.

Test in this order:

1. `original_pack_control`: the original game data in uncompressed PACK form.
   If this crashes while no `gamecmn.pack` overlay crosses safely, the PACK
   format or loading path may be involved independently of translated text.
2. `story_a010_original`: 0.3.0 content with only `story_a010.bxon` restored to
   original. If the control works and this works, that entry is a suspect.
3. `scenario_guide_original`: 0.3.0 content with only `scenario_guide.bxon`
   restored to original. This isolates another large edited entry.

If both single-entry variants crash while the control works, other edits or
aggregate archive growth remain possible. A successful crossing is only one
observation; it does not establish that a variant is safe throughout the game.
The two single-entry variants temporarily lose English in their restored entry.
These files have been reconstructed and hash-checked, but runtime behavior
still requires hardware testing.

| Variant | Reconstructed SHA-256 |
| --- | --- |
| `original_pack_control` | `26bf97310438c16e400b3bb36253c9f5c45eca787b216029bd65bf4f8e1b9ceb` |
| `story_a010_original` | `f269740cfe5e87e837f63d9c7e4126d6bc31fb9f7183c1bda587629e418feb29` |
| `scenario_guide_original` | `1bbff5f6c67424655ddb1a1316efe7dbe9af8ab8645b0c96ace1ad773e56469d` |
