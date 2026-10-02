# Changelog

## 0.5.0 — October 2, 2026 (experimental prerelease)

Not fully translated, not stable, and not a hardware-crash repair. The frozen
candidate passed packaged-builder verification; the player reported it was
good to go after the requested limited in-game spot check. This is not an
independently observed or comprehensive gameplay/visual validation.

### Completed implementation and file-verified scope

- The regional secondary-display translation pass converted and locally
  installed **7,588 Japanese fields: 6,302 dialogue and 1,286 speaker labels**.
  Counts include repeated fields; these are not unique conversations or a
  whole-game completion percentage. Five English-only quality corrections
  are recorded separately and do not reduce the Japanese backlog.
- Covered work includes regional NPC conversations, story-related exchanges,
  party/book-entry dialogue, quest instructions and canonical speaker captions.
  Original 3DS directions and mechanics were retained where XI S differs.
- Each approved batch checked whole original display-field membership,
  original/current source equality, ordered dynamic controls, unchanged gameplay
  bytes, archive metadata and non-target entries, no-op rebuilds and exact hashes.
  Local installation used closed-emulator checks and exact recoverable backups.
- Dialogue was checked at a conservative 24 cells by three lines, reserving
  eight cells per player-name substitution. Captions received separate length
  checks. These are static checks, not proof of every rendered layout.
- The frozen release contains **733 targets: 111 updated, 622 unchanged,
  no additions and no removals** relative to 0.4.0. Previously included battle,
  map/UI, tutorial, item and character-name work is retained. The verified
  Veronica/Sylvando display-only IPS is unchanged; saves are not rewritten.

### Unverified layouts and gameplay

- New dialogue, captions and map/UI layouts need broader in-game visual testing.
  A release spot check is a limited regression check, not a full playthrough.
- Comprehensive image-embedded and executable-text audits remain unfinished.
  Whole-game, all-dialogue and all-Tickington completion are not claimed.
- Clean-Windows/Windows 8 execution and real-hardware compatibility remain
  unverified. Builder results on this Windows host must not be generalized.

### Ambiguous or remaining text

- A fresh broad regional inventory reports **356 Japanese candidates across
  26 packs**. It includes unsupported fields, duplicates and numeric values
  that resemble pointers, not 356 confirmed visible conversations.
- A separate structural investigation identified alternate-layout prose and
  numeric pointer lookalikes. Unsupported numeric fields and unproven alternate
  text were left untouched; false candidates are not counted as translations.
- Other text inventories have different scopes and can overlap; do not add them
  together. Remaining enemy-action text and held letters/instructions documented
  in 0.4.0 are not implicitly completed by this regional pass.

### Unresolved crashes and rendering issues

- Reported New 3DS 3D-mode crashes at the Heliodor bridge and Church of Guidance
  exit remain unresolved. 0.5.0 is not a crash fix and is hardware-untested.
- The intermittent battle-entry atlas flash also reproduced fully unpatched in
  Azahar. Its cause is unconfirmed; no renderer/settings/cache repair is claimed.
- Existing patch-only hardware diagnostic controls are separate from this release.

## 0.4.0 — October 1, 2026 (experimental prerelease)

Translation progress, UI improvements and character-name repair. **This is
not a complete translation or a hardware-crash repair.** The frozen package
contains **733 patch targets**, versus 577 in 0.3.2: 156 added targets, 56 updated
targets and 521 unchanged targets. No previous target was removed. Target counts
are files, not dialogue lines or a completion percentage.

### Character-name repair — player confirmed

- Restored the final letters of Veronica and Sylvando on the player's tested
  menu/battle screens. The original runtime name field stores only seven UTF-16
  characters; increasing it would overwrite adjacent level data. The repair
  supplies separately terminated full names on the shared display paths instead.
- The corrected patch passed 62 offline ARM tests, including the original
  manager accessor, register/flags/stack preservation, unrelated/null pointers
  and unchanged character data. The player confirmed the corrected build fixed
  the problem. This is not an exhaustive test of every consumer or real hardware.
- Saves and stored character-name fields are not rewritten.

### Battle text, menus and readability

- Added reviewed enemy action names, songs, dances, breath attacks, physical
  attacks and summon labels. Repaired two damaged actor substitutions; preserved
  dynamic controls and gameplay metadata in the reviewed replacements.
- Reworked selected spell/action descriptions, spell-list readability, required
  equipment labels, enemy targeting text and the monster-mount message.
- Corrected selected inventory Cancel/Filter labels, item ownership messages,
  equipment statistics, party stat labels, profile titles and field status text.
- Improved Line-Up name/stat layouts, Tockle sorting and profile labels/value
  placement, Zoom destinations, adventure guidance and selected title/records
  captions. Added further reviewed map labels and location artwork.
- These changes have file-level validation; most still need broader rendered
  fit and gameplay testing. They are not claims that every battle/menu is complete.

### Story, party talk and regional dialogue

- Added reviewed party-talk archives and story/NPC follow-ups, including Hotto,
  Gallopolis/Faris, Michelle's farewell, Rab-related dialogue, Sniflheim and
  Arboria scenes. Existing quest, tutorial, forge and covered Tickington work
  from earlier versions is retained.
- The latest October 1 away-work batch alone installed 155 enemy display fields,
  161 scene/NPC dialogue fields, 18 speaker-name fields and 93 map/UI panes across
  21 archives. These are scoped field/pane counts, not unique conversations,
  and do not represent the entire change list since 0.3.2.
- A held 19-field letter and a quest instruction with unresolved canonical names
  were excluded. Unreviewed bulk machine-translation drafts are not included.

### Remaining work and critical warnings

- **New 3DS 3D-mode crashes at the Heliodor bridge and Church of Guidance exit
  remain unresolved.** They were confirmed on 0.3.2; 0.4.0 is not hardware-validated
  and must not be presented as a fix. See [issue #1](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/issues/1).
- An intermittent battle-entry texture/atlas flash was also reproduced in a
  repeated unpatched Azahar comparison. Emulator involvement is suspected,
  not confirmed; this release does not claim to fix it or change renderer settings.
- The latest separate inventories find 282 Japanese enemy-action fields,
  7,944 regional secondary candidates and 5,588 broad structured/layout candidates.
  These are different, overlapping scopes with blind spots and inactive/duplicate
  records. **Do not add them together or derive a completion percentage.**
- Regional dialogue, party talk, Tickington/book worlds, image/executable text,
  names retained in older saves, translation accuracy and screen fit still need
  further review and in-game coverage. Hotto's first-visit title remains unverified.
- Clean-Windows/Windows 8 compatibility and the new name repair on hardware are
  untested. Back up saves/mods; use a normal game save rather than an old save state.

See [the scoped completion checklist](docs/completion-status.md) and
[validation evidence](docs/release-validation.md). Use your own supported
decrypted Japanese game. No ROM, full game archives, saves, keys or emulator
are distributed. This unsigned builder produces a new ROM or mod folder;
it does not modify your original ROM or saves.

## 0.3.2 — September 30, 2026 (experimental; hardware crash confirmed)

This updates the public builder to the latest locally installed translation
snapshot: **577 patch targets** (575 archive deltas, one Hotto location-image
delta, and one executable IPS payload). It adds reviewed Hotto and party dialogue,
restored 2D camp/forge and other UI text, selected Tickington name/menu fixes,
and screenshot-led corrections. The builder now includes standalone `.bch` image
patches. All targets rebuilt from matching original inputs and matched the local
installed files by SHA-256.

**This is not a bridge-crash repair or a complete translation.** A New 3DS
tester confirms that 0.3.2 still crashes when crossing the bridge toward
Heliodor, and also crashes when leaving the Church of Guidance. The tester
reports that the earlier Heliodor rendering error is no longer visible, but
that improvement needs broader validation. A previous compact variant crossed
the bridge in Azahar; emulator success did not predict hardware stability.
The Hotto title's first-visit appearance and saved Tockle-name behavior are
untested. The covered text audit still finds 8,708 Japanese fields with zero
parse errors; a corrected later scan identified 8,328 Japanese secondary
candidate references outside that audit after excluding 270 false pointers
embedded in other strings. This newer scan includes local work after 0.3.2;
the counts are not confirmed active dialogue. Keep backups of saves and mod files.

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
