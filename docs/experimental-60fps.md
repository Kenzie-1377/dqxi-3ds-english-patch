# Optional experimental FPS addon — 0.8.5

The standard builder does **not** enable this experiment. Use the separate
`DQXI-0.8.5-Optional-Experimental-60FPS.zip` release asset with matching 0.8.5
Azahar mod output only. Keep all other translation files installed.

The addon changes two timing literals: the main update step from approximately
1/30 to 1/60 second and the minimum pre-refresh wait from 24,999 to 8,333
microseconds. Other effective executable bytes, including prior code fixes,
remain identical to standard 0.8.5. No new hooks, memory pools or code caves
are introduced. It is not an emulator speed-limit increase.

The bounded native checks cover the affected pacer under supplied OS/GPU
boundaries and confirm the main update-step literal. They do not prove actual
60 FPS, correct timing of every frame-dependent consumer or GPU output.

One player reported that the separate Azahar test worked great. It was then
installed in normal Azahar, but no separate post-promotion test report or
numerical FPS measurement was supplied. Whole-game play, all animations,
cutscenes, sound synchronization and real hardware remain unverified. Revert
if game speed, events, animation timing or stability are abnormal.

## Install in Azahar

1. Back up saves and fully close Azahar.
2. Build and install standard 0.8.5 using your own original Japanese game.
3. Back up the translation mod's `exefs/code.ips`.
4. Copy the addon's `60fps/exefs/code.ips` over
   `user/load/mods/0004000000199200/exefs/code.ips`.
5. Use **100% emulator speed**, load an in-game save (not a save state), and
   initially avoid saving. Check FPS alongside normal movement, battles,
   dialogue, sound and transitions. Report issues with the game mode and area.

## Revert

Fully close Azahar and replace that file with `standard/exefs/code.ips` from
the addon, or your matching standard 0.8.5 backup. All translation, font,
rendering and crash repairs stay installed. Do not mix this cumulative IPS
with a different release version. No original game code, saves or ROMs are
distributed, and real-hardware suitability is not claimed.
