# Scoped completion checklist — 0.6.0

This checklist distinguishes reviewed implementation from player testing.
"Complete" below applies only to the stated audited scope, never the whole game.

## New scoped work packaged in 0.6.0

- Memories title tables: all 888 nested display fields and 53 chapter headings
  reviewed in English, using exact PC matches wherever available. No referenced
  Japanese titles remain. Full wording and original playback identities are
  preserved. Menu headers, confirmation/mode choices and prompts are English;
  the player reports that the latest update works in Azahar. This does not
  certify every memory's playback, dialogue or alternate state.
- Regional dialogue and extra-page consumer repairs since 0.5.3 are included,
  as are school/map/quest/records/mini-medal/equipment UI and area-title artwork
  improvements. Tests remain interaction-specific. Puerto Valor, Lonalulu,
  Nautica, L'Académie and the overall game are not certified fully complete.
- School NPC, book, quest and party/alternate-path work is still unfinished.
  Reported 2D battle/map crashes are undiagnosed. Brollyminator and other long
  battle-target names still need a wrapping repair. This release does not claim
  to fix these outstanding issues or provide real-hardware validation.
- Package/build scope: 787 targets, 72 updates, 54 additions, 661 unchanged
  payloads from 0.5.3. All787 matching-source outputs and complete rebuilt-ROM
  contents were verified; those checks are not gameplay certification.

## New file-verified implementation in 0.5.0

- Regional pass: 7,588 Japanese display fields translated and locally installed
  (6,302 dialogue, 1,286 speaker labels); five English-only corrections separate.
- Original structured membership, controls, gameplay bytes, archive metadata,
  untouched entries, rebuilds and source/output hashes checked for approved batches.
- Conservative static dialogue/caption fit checked; broader rendered fit unverified.
- Fresh regional inventory: 356 candidates, including unsupported structures and
  numeric pointer lookalikes. No full-region/game/dialogue completion claim.
- Frozen package: 733 targets, 111 changed and 622 unchanged from 0.4.0.
- Source and packaged builders independently rebuilt all 733 targets successfully.
  The player reported the frozen candidate good to go after the requested limited
  spot check; this is not comprehensive or independently observed gameplay testing.

The remaining sections retain earlier scoped achievements and limitations;
historical audit counts below are not the fresh 0.5.0 remaining count.

## Completed scoped work retained from earlier releases

- Audited quest journal/rewards and the covered quest-NPC pass: 4,255 dialogue
  references, 89 title references and 621 journal/reward references in that pass.
  Unclassified story/party conversations are outside its scope.
- Shared tutorial table: 222 populated heading/body fields across 72 active pages;
  layouts still need wider visual coverage.
- Reviewed battle-template banks: main/dungeon templates and player
  names/descriptions/status bank have no Japanese in the latest proven-table
  audit. Enemy-special-action names are a separate unfinished bank.
- Item metadata pass: 2,845 records checked against originals; previously damaged
  numeric fields restored. Names and visual fit remain subject to further review.
- Reviewed Tickington opening, covered NPC/book-world dialogue and party talk
  included in earlier releases. **Tickington as a whole is not complete.**

## Implemented and player-confirmed in 0.4.0

- Veronica/Sylvando missing final letters repaired on the player's tested
  screens. Display-only repair; no save/name-field expansion. Hardware and all
  specialized consumers have not been comprehensively tested.

## Implemented, file-verified, requiring broader gameplay/visual checks

- Additional enemy actions and summon labels; actor-token repairs.
- Selected spell/skill, inventory/equipment/statistics, Line-Up and field status
  text-fit/readability corrections.
- Tockle sort/profile labels and value positions; this does not rewrite Japanese
  names already saved in older saves.
- Zoom destination names/prompts, guidance, signposts, profile titles,
  title/records captions, map labels and selected location artwork.
- Added story scenes, regional dialogue and party-talk archives. Controls,
  original archive metadata and non-target data validated in reviewed stages.

## Not complete / known issues

- Main-game dialogue, party talk, Tickington/other side-world coverage.
- Remaining Japanese enemy-special-action names (282 fields in the last audit).
- Comprehensive image/executable-text audit and every menu's rendered fit.
- The previously held 19-field letter needs canonical review. The older held
  quest-instruction inventory must be reconciled against newer regional receipts;
  it is not an additional confirmed remaining field count.
- New 3DS 3D-mode Heliodor-bridge/Church-exit crashes; 0.5.0 is hardware-untested.
- Intermittent battle-entry atlas flash: reproduced unpatched in Azahar;
  emulator cause unconfirmed, no repair claimed.
- Hotto first-visit location title and saved Tockle-name behavior.
- Clean-Windows/Windows 8 testing and broad accuracy/regression playthroughs.

## How to read the counts

733 packaged targets are patched files, not unique lines. The fresh 0.5.0 regional
inventory has 356 candidates across 26 packs. Historical inventories recorded
7,944 regional candidates and 5,588 candidates in a different broad scope;
these are superseded or differently scoped counts. They overlap and include inactive or
duplicate resources, and neither covers every image/executable/runtime string.
They are not additive and cannot establish a percentage translated.

The earlier 0.4.0 away batch's 155 enemy fields, 161 scene/NPC fields, 18 speaker fields
and 93 map/UI panes are a documented subset of 0.4.0, not the entire release delta.
See CHANGELOG.md and the machine-readable target changes for exact file coverage.
