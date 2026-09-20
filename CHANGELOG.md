# Changelog

## 0.2.0 — September 20, 2026 (experimental prerelease)

This release updates the translation data, not just the builder. It contains
518 patch targets, compared with 379 in 0.1.1. The game is **not fully translated**.

### Translation progress

- Completed the audited quest journal, rewards and quest-related NPC pass,
  including 2,038 reviewed NPC passages across 20 region archives. The final
  audited scope checked 4,255 dialogue references, 89 title references and
  621 journal/reward references with no Japanese remaining. This does not cover
  every unclassified story or party conversation.
- Translated 2,189 distinct Japanese battle messages across three checked battle
  tables (3,147 references), preserving dynamic substitutions.
- Updated 1,681 speaker-name references across 23 archives. Other speaker names
  and character dialogue still remain untranslated.
- Completed all 222 populated heading/body fields in the shared tutorial table
  (72 active pages), with 2D and 3D layout adjustments.
- Translated forge flourishes, prompts, commands and status text; corrected
  substitution order and redrew three forge text graphics in English.
- Includes recap translations and earlier battle-command, victory-message,
  tactics, equipment, statistics and menu-label fixes.

### Item and display corrections

- Audited all 2,845 item records against the original typed records; corrected
  or standardized 726 names. Leather Hat is no longer called Leather Armour,
  and Crimson Catsuit is no longer incorrectly named Trodain Togs.
- Restored 159 damaged numeric values across 158 items from the original data.
  All item gameplay metadata now matches the original records byte for byte.
- Applied item-screen text-fitting changes across 484 panes in nine UI archives,
  including names, detail buttons and descriptions.
- Corrected a subsequent readability experiment that caused overlapping letters:
  normal spacing is restored across 194 affected panes. Wider letters are retained
  only on applicable proportional-font panes.

### Still to do / known limitations

- Broader story/party dialogue, some speaker names and guidance, and some map or
  banner graphics remain Japanese. Completed audits are scoped, not game-wide proof.
- The latest monster-list spacing correction has passed file checks but still
  needs in-game confirmation. Some item names may remain too narrow; layout and
  readability are not considered finished.
- Tutorial, forge and item layouts need further in-game visual testing. Expect
  rough translations and other display issues.
- Older save-slot labels can retain Japanese text stored in the save itself.
  This patch does not rewrite saves.
- Real-hardware compatibility and a separate clean-Windows test remain unverified.

Use your own supported decrypted Japanese ROM. Back up saves, use a normal
in-game save rather than an old save state, and do not mix versions of mod files.
No ROM, full game archive, emulator or save is distributed.

## 0.1.1 — Builder compatibility fix

- Handle decrypted ROMs with stale encryption flags.
- Improve rebuild logging and verification tests.
