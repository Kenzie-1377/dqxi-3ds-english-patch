# Heliodor bridge diagnostic archives (0.3.0 only)

These are **temporary diagnostic variants, not a release or a finished fix**.
They help isolate a reported 3D-mode bridge crash on New 3DS-family hardware.
Only patch data and local builders are distributed here. They require the exact translated
`romfs/gamecmn.pack` from the 0.3.0 release build; no complete game archive is
included. No tool in this folder edits saves.

## Round-two test after the first hardware report

The tester reported that `original_pack_control` crosses the bridge and shows
Heliodor normally, while **both** `story_a010_original` and
`scenario_guide_original` still crash and corrupt the scene. This makes the
uncompressed PACK format alone an unlikely explanation, but does **not**
identify a safe translated archive. Each single-entry test retained the
other 43 translated entries.

Please test `group_a_only` and `group_b_only` next, one at a time, using the
same new/test save and the same bridge route. They contain complementary
sets of the 44 entries changed in 0.3.0: A retains five translated entries
(`achievement`, `passive_skill`, `enemy_base`, `quest_ui_param`, `ui_text`)
and B retains the other 39. All remaining entries in each are exact original
data. Each archive is about 103 KB larger than the original, versus 206 KB
for the full 0.3.0 archive. This split tests whether one group causes the
problem or whether combined changes/size may matter. It is **not** a fix.

Report separately for A and B: bridge crash **yes/no**, first-visit Heliodor
top-screen corruption **yes/no**, device model, and whether you booted normally
rather than loading an emulator save state. If both work, the combined edits
or archive size may be relevant; if one fails, its retained entries deserve
closer investigation; if both fail, more than one cause or a lower size
threshold is possible. None of those observations alone proves causation.

### Windows: one-click builder

For the new two-group test, download
[DQXI-Bridge-Diagnostics-Round2.exe](DQXI-Bridge-Diagnostics-Round2.exe).
The older [first-round builder](DQXI-Bridge-Diagnostics-0.3.0.exe) only creates
the original three tests. The round-two EXE creates all five. Run it on a
Windows PC and choose the exact **0.3.0**
`romfs/gamecmn.pack` from your own patch installation, then choose a folder
for the test files. No Python or command line is needed. The program
rejects the 0.3.1 PACK, never installs anything, and never touches saves.
The EXE was built on Windows 11; Windows 8 compatibility has not been tested.
It is unsigned; if Windows warns about it, you can instead use
the auditable Python method below. The round-two EXE SHA-256 is
`92788badae9078dfdc4f9ff2b989542198165925d67f615424eef1286b97df85`.
The older first-round EXE SHA-256 is
`ebb99639952a11d0fde63b14faa4a7f67bca3cc6b7e87734560ef6c194c31a45`.

### Python method

Run from the repository root, using Python 3.10 or newer:

```sh
python tools/build_bridge_diagnostics.py "PATH_TO_0.3.0_MOD/romfs/gamecmn.pack" --output "NEW_DIAGNOSTIC_FOLDER"
```

The input must have SHA-256
`493b95fad71a6a06da99a7c70b589cf0169c93307624476b69c114773b31c79a`.
The script refuses a different input or an existing output folder, verifies
each delta and reconstructed file, and leaves the input untouched. It creates
five subfolders, each containing a `gamecmn.pack`. The generated archives
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
4. `group_a_only`: retain only the five group-A translated entries.
5. `group_b_only`: retain only the other 39 translated entries.

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
| `group_a_only` | `2a6c044562ae8de9fdfb16447d905ec0a4d71b2914041fb7f8eeb20b7c51ec01` |
| `group_b_only` | `28193915d3e142cc3ed18ac69f82030da47e73e571e47fc3699a9dddc12f166f` |
