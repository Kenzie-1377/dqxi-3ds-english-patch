# Version 1.0 status

The maintainer considers the translation substantially complete. Current work
focuses on broader community testing and fixes for reported problems.
Please [report game-breaking issues on GitHub](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/issues/new/choose),
especially crashes, progression blockers, broken quests, or choices that stop
progress. This status does not claim that every gameplay path has been tested.

## Public download

The latest release is **[1.0](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/releases/tag/1.0)**,
with Windows and Linux builders, matching checksums, and the 1,256-target patch set.
Version 0.8.10 remains available as a historical release.

## Version 1.0 build

The version 1.0 build has **1,256 independently verified installed files**.
This is an inventory count, not a translation-completion percentage or a count
of public release assets.

Recent work covers additional dialogue and UI corrections, six-pixel 3D word
spacing with matching wrapping, party and cutscene formatting, seven movie
caption repairs, a restored shop-dialogue display flag, English title artwork,
and equipped-character badge cleanup. The Heliodor regional-pack repair is
retained. Targeted Azahar tests confirmed the Heliodor repair, word-spacing
changes, title screens, and final removal of Japanese equipment badges.

The formatting audit checked 64,662 regional, script, cutscene, and party text
entries with no remaining geometry leads in that scope after repairs. Original
password tokens are preserved. One native temporary placeholder is skipped by
its checked current quest-completion path; it was not replaced with invented
wording. These checks do not prove every possible scene or display path.

## Builder verification

The Windows 1.0 executable compiled from the isolated public source recipe and
reconstructed all 1,256 targets with independent hash readback. Seven additional
CIA/platform tests pass alongside the existing suite (44 tests total). The native
and Python CIA container implementations produced identical synthetic outputs.
A full Windows CIA rebuild was verified using real original game content in a
synthetic outer container; that is not a console-installation test.

The Linux command-line package includes the same patch set and verified official
x86_64 tool-download pins. Actual Linux runtime testing remains pending. The
Windows-hosted shared-engine checks do not substitute for that platform test.

The frozen patch set, exact Windows executable, Linux archive contents, and
matching checksums passed the release-package checks. All 44 automated tests pass.

## Remaining testing

Broader normal-save gameplay in both modes, story/quest choices and return
states, movie-caption pacing, uncommon layouts, and real-hardware behavior
still need coverage. Reported historical crashes are not universally declared
fixed by the recent targeted Azahar tests.

See [validation](release-validation.md), [the main page](../README.md), and the
[historical completion notes](archive/completion-through-0.8.10.md).
