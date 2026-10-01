# Scoped completion checklist — 0.4.0

This checklist distinguishes reviewed implementation from player testing.
"Complete" below applies only to the stated audited scope, never the whole game.

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
- Held 19-field letter and one quest instruction pending canonical-name review.
- New 3DS 3D-mode Heliodor-bridge/Church-exit crashes; 0.4.0 is hardware-untested.
- Intermittent battle-entry atlas flash: reproduced unpatched in Azahar;
  emulator cause unconfirmed, no repair claimed.
- Hotto first-visit location title and saved Tockle-name behavior.
- Clean-Windows/Windows 8 testing and broad accuracy/regression playthroughs.

## How to read the counts

733 packaged targets are patched files, not unique lines. The latest regional
secondary inventory has 7,944 candidates across 26 packs; another broad inventory
has 5,588 candidates in a different scope. They overlap and include inactive or
duplicate resources, and neither covers every image/executable/runtime string.
They are not additive and cannot establish a percentage translated.

The latest away batch's 155 enemy fields, 161 scene/NPC fields, 18 speaker fields
and 93 map/UI panes are a documented subset of 0.4.0, not the entire release delta.
See CHANGELOG.md and the machine-readable target changes for exact file coverage.
