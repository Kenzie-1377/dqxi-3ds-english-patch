# FPS experiment on hold — 0.8.7

0.8.7 uses standard timing only. No 60 FPS addon is provided or supported for
this version after uneven menu/movement timing was reported in Azahar.
Do not apply an older FPS patch: it can overwrite newer cumulative code fixes,
including the integrated Tickington lute crash fix. Build fresh 0.8.7 output
instead of layering old patches over it. Historical releases remain unchanged.

## Historical optional experimental FPS addon — 0.8.6 only

The standard builder does **not** enable this experiment. Use the separate
`DQXI-0.8.6-Optional-Experimental-60FPS.zip` release asset with matching 0.8.6
Azahar mod output only. Keep all other translation files installed.

The addon changes two timing literals: the main update step from approximately
1/30 to 1/60 second and the minimum pre-refresh wait from 24,999 to 8,333
microseconds. Other effective executable bytes, including prior code fixes,
remain identical to standard 0.8.6. No new hooks, memory pools or code caves
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
2. Build and install standard 0.8.6 using your own original Japanese game.
3. Back up the translation mod's `exefs/code.ips`.
4. Copy the addon's `60fps/exefs/code.ips` over
   `user/load/mods/0004000000199200/exefs/code.ips`.
5. Use **100% emulator speed**, load an in-game save (not a save state), and
   initially avoid saving. Check FPS alongside normal movement, battles,
   dialogue, sound and transitions. Report issues with the game mode and area.

## Revert

Fully close Azahar and replace that file with `standard/exefs/code.ips` from
the addon, or your matching standard 0.8.6 backup. All translation, font,
rendering and crash repairs stay installed. Do not mix this cumulative IPS
with a different release version. No original game code, saves or ROMs are
distributed, and real-hardware suitability is not claimed.
## Validation unchanged since 0.8.5

Use `DQXI-0.8.6-Optional-Experimental-60FPS.zip` only with the matching 0.8.6
Azahar mod output. This release retains standard timing by default. The addon
contains the unchanged experimental FPS patch and standard-timing rollback.
No new numeric FPS, exhaustive animation/cutscene timing, full-playthrough or
hardware validation is claimed. Back up saves, use 100% emulator speed and
revert if timing or game speed is abnormal. The evidence above originated
with the 0.8.5 experiment; no new FPS/timing validation is claimed for 0.8.6.

