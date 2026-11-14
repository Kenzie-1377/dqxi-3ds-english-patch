# Version 1.0 validation and testing

## Version 1.0 release

[Version 1.0](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/releases/tag/1.0)
packages the frozen 1,256-target patch set with Windows and Linux builders and
SHA-256 checksums. Version 0.8.10 downloads represent the older snapshot.

## Translation verification

- The active 1,256-file installation was independently read back after the latest
  equipment-badge texture repair. Saves and emulator settings were unchanged.
- The final formatting scan checked 64,662 text entries. Actual font metrics,
  display-specific bounds, and conservative name/number substitutions were used.
- Seven movie-caption corrections passed 126 native text checks; all 97 movie
  captions fit the checked two-line subtitle layout without timing changes.
- The final party-formatting batch passed 42 native 2D/3D/2D descriptor checks,
  preserving 2D text and archive sizes.
- Both localized title textures passed 13 native layout-construction checks.
  Nine changing background layouts, 92 animation files, and five effect textures
  were retained unchanged. The player confirmed the title-screen result.
- All 56 equipped-character labels and 132 native selection cases passed.
  Layout transparency alone did not remove the original badge in gameplay;
  the final repair cleared eight badge textures. The player then confirmed
  that the Japanese badges were gone.
- Targeted player tests confirmed the Heliodor repair and revised 3D spacing.

These checks have different scopes. Native resource, text-flow, and geometry
checks do not emulate a complete physical GPU playthrough. Player confirmation
applies to the screens and interactions actually reported.

## Release-package verification

The frozen patch manifest, all 1,256 patch payloads and target hashes, both
release-asset checksums, all 1,274 Linux archive entries, and page image files
were checked before publication. The source suite passed all 44 tests.

The final Windows executable has passed clean-recipe compilation, GUI/payload self-tests,
all 1,256 reconstructed-output checks, and an embedded patch-only audit.
The full source suite has 44 passing tests. CIA-container and Windows full-rebuild
checks passed; real-console installation and actual Linux runtime checks remain open.
A local installation pass does not certify an older published builder or a
future rebuilt executable.

## New builder feature test limits

CIA tests preserve certificates, tickets, metadata, content indices, and unrelated
contents. Native/Python synthetic rebuilt containers match byte for byte. The
full Windows CIA test used real supported game content in synthetic CIA outer
metadata. The native Windows and shared Python engines produced byte-identical full CIAs
from the real-game-content fixture. A normal retail CIA and real-console install
have not been verified.
CIAs must be decrypted and match the expected Japanese game. Rebuilt CIAs are
modified and require a compatible custom-firmware installation workflow.

Linux tool archives and ELF64 x86_64 binaries were inspected and checksummed.
The shared Python engine reconstructed all 1,256 targets on Windows. No Linux
host is available in this session, so Linux execution remains a separate test.

## Gameplay limits

A full story playthrough, all quest/choice outcomes and return states, movie
pacing, all emulator settings, and comprehensive real-hardware compatibility
remain unverified. Use a fresh launch and a normal save when retesting.

Historical release-specific tests and reports are retained in the
[validation archive](archive/validation-through-0.8.10.md).
