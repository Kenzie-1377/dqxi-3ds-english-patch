# 0.3.2 bridge and Church of Guidance diagnostic control

**0.3.2 still crashes on New 3DS hardware** when crossing the bridge toward
Heliodor; a tester also reports a crash on leaving the Church of Guidance.
The earlier Heliodor top-screen rendering problem appears improved in that
test, but this does not establish a general fix.

This is a **test-only, original-data `gamecmn.pack` control**, not a new
translation release or a permanent workaround. It may restore Japanese text.
It helps determine whether both 0.3.2 crash locations respond to replacing
only the common-data archive. It does not edit saves. **Do not use the older
0.3.0 diagnostic builder with a 0.3.2 file; it rejects that version.**

Only a reverse delta is included here, not an original game archive. Supply
your own exact 0.3.2 mod `romfs/gamecmn.pack`, SHA-256
`eeb7dbd02c304c71c2b3b552fd4265c25f847220c63743f70050aad94bfb9ea1`.
From the repository root, run with Python 3.10 or newer:

```sh
python tools/build_bridge_control_0_3_2.py "PATH_TO_YOUR_0.3.2_MOD/romfs/gamecmn.pack" --output "NEW_TEST_FOLDER"
```

The output `NEW_TEST_FOLDER/gamecmn.pack` is the exact original-data expanded
PACK, SHA-256 `26bf97310438c16e400b3bb36253c9f5c45eca787b216029bd65bf4f8e1b9ceb`.
The builder rejects wrong source hashes and existing output folders, and
verifies the reconstructed bytes. Keep the generated full archive private.

For a hardware test, make a **separate copy** of your 0.3.2 mod and back up
its `romfs/gamecmn.pack`. With the game completely closed, replace only that
file in the test copy with the generated control. Use the same normal in-game
test save, not an emulator load state; do not edit or delete the save. In 3D
mode, check the bridge and the Church exit separately. Record crash yes/no,
whether the Church exit loads the same outdoor route, and whether Heliodor's
top screen renders normally. Close the game before restoring the translated
file. One successful crossing or exit does not prove the mod stable elsewhere.
