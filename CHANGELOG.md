# Changelog

## 0.3.1 — September 29, 2026 (experimental, hardware-unverified prerelease)

This is a **translation-progress update, not a crash fix**. It has **575 patch
targets** (574 archive deltas and one executable IPS payload), versus 566 in
0.3.0. It was built from the last validated installed translation snapshot.
Pending bridge-test variants, uninstalled party-talk work and uninstalled title
assets are not included.

### Changes since 0.3.0

- Added carefully reviewed story and party dialogue, regional conversations,
  Tickington and book-world follow-ups, battle/UI text fixes, and screen-fit
  revisions. The installed-work ledger records 3,877 BXON text update events,
  874 layout-pane update events, one image, and six hidden raw-pool corrections
  since 0.3.0; these are work events, not a count of distinct game lines.
- Rebuilt all 575 patch targets from matching original inputs and independently
  matched all 575 outputs to the validated installed snapshot. This structural
  check does not establish real-hardware stability or visual fit.

### Critical known issue and remaining work

**The New 3DS 3D-mode crash while crossing the bridge toward Heliodor is
unresolved.** It was reported with 0.2.0 and 0.3.0; 0.3.1 has **not** been
tested on hardware or shown to fix it. The translated `gamecmn.pack` is a
leading suspect, and first-visit Heliodor graphics corruption has also been
reported. See [issue #1](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/issues/1)
and the [diagnostic tests](diagnostics/bridge_0_3_0/README.md). Back up saves
and mod files before testing. This release is not recommended as a way to get
past that bridge.

The latest effective-overlay text audit still finds 9,031 Japanese-containing
records in its covered archive formats, with zero parse errors. That audit has
known blind spots: top-level archives, embedded images, executable text and
runtime visibility are not comprehensively resolved. Tickington and wider
gameplay/fit checks remain open. No ROM, complete game archive or save is
distributed.

## 0.3.0 — September 29, 2026 (experimental prerelease)

This patch has **566 targets** (565 archive deltas and one executable IPS
payload), up from 518 in 0.2.0. It is still a partial translation.

### Changes since 0.2.0

- Translated and reviewed the Tickington opening, its book-world cutscenes and
  party talk, and ordinary Tickington NPC and book dialogue in the covered text
  archives. Twenty identical internal dummy-label fields were deliberately left
  untouched; they are not ordinary dialogue.
- Added reviewed story, regional NPC, book and party conversations across the
  main game, including previously missing cutscenes and scripts. All 314
  cutscene fields missed because their archives were absent from the earlier mod
  overlay are now English in the covered text audit.
- Shortened and reflowed accolade titles and descriptions, including the
  "You Shall Not Escape Me!" screen. Adjusted campfire time labels, Pep Power
  selection and descriptions, and several battle lower-screen labels to fit
  their boxes. The player confirmed the latest Pep/battle follow-up looked good.
- Preserved original game logic and control tokens in reviewed replacements;
  rebuilt archive entries and installed hashes were checked before packaging.

### Remaining work and limitations

- A fresh effective-overlay audit finds **12,472 Japanese-containing text
  fields** in the covered BXON/BFLYT formats: 7,526 in modded packs and 4,946
  in original packs not yet overlaid. The largest groups are party talk (5,376),
  UI layout text (4,524), other scenario/cutscene text (2,434), scripts (116),
  and region fields (22, including the 20 dummy labels). These are audit hits,
  not a claim that every field is independently player-visible.
- Image-embedded and executable text have not had a comprehensive audit.
  Untranslated text may therefore exist outside those counts.
- The Tickington, accolade and later story changes still need wider in-game
  visual testing. Text wrapping, display transitions, names cached in saves,
  translation accuracy and real-hardware compatibility remain open checks.
- The old bulk machine-translation draft was not included because spot checks
  found serious errors. This release is not a promise of full-game English.

Use your own supported decrypted Japanese game. Back up saves and load a normal
in-game save instead of an old save state. No ROM, complete game archive,
emulator or save is distributed.

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
