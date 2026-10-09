# Release validation

## 0.6.0 — October 9, 2026 (experimental regional dialogue and Memories update)

- Frozen current installed package: 787 active targets, consisting of 72 updated
  targets, 54 additions and 661 byte-identical retained payloads from 0.5.3.
  No earlier public target is removed. 551 quarantined old files are excluded.
  Original inputs and the entire installed inventory were pinned before and
  after preparing the separate snapshot; publication does not install anything.
- Manifest SHA-256:
  `ddcdc0cbc9b28b2b0e5cf93fcf373d9ea97ba84814c92b069e3da8c604c007a9`.
- Exact native Windows EXE: 3,757,056 bytes, SHA-256
  `86fc8424dfa761cfa519410a96e47581ae395fd2de66550c81bbcfb326d35431`.
- Three complete builds of that exact executable verified all 787 embedded
  payloads and all 787 output paths, sizes and hashes. Original input hashes
  were checked before and after each run. Each output matches the frozen
  installed snapshot. Builder changes are mechanical version, manifest-pin
  and target-count changes; codecs and runtime safety checks are retained.
- Independent embedded-resource inspection found exactly one ZIP resource,
  containing only the manifest and 787 source-bound patch payloads. All targets
  reconstructed correctly from matching originals. No complete game archives,
  original ROM, saves, keys, private reference CSV or quarantine files are bundled.
- Functional GUI build/cancellation and both checksum-pinned tool downloads
  passed, including cancelled download behavior. All 787 GUI output files were
  independently compared. Repository regression tests passed 37/37.
- Independent rebuilt-ROM verification checked all 21,250 RomFS files, three
  ExeFS files and content/IVFC integrity. The original ROM and unrelated
  cartridge partitions were preserved. Modified retail NCSD/NCCH signatures
  are expected invalid, not represented as Nintendo-valid signatures.
- The exact release EXE passed a scoped Defender file scan with no threats
  found; remediation was disabled and no security settings changed. This is
  not a security guarantee. The builder remains unsigned.
- All 941 referenced memory titles were independently read back from typed
  tables. No Japanese remains in those referenced title fields. Playback IDs,
  counts and unrelated bytes are preserved. Full PC titles are retained with
  explicit native-font typography conversions; list and prompt widths are
  checked for the maximum title. The user reports the latest Memories changes
  work. This is not verification of every replayed scene or every story state.
- Runtime page validation remains limited to reviewed consumers and individual
  player-tested interactions. School NPC/book/quest/party completion and wider
  regional audits remain unfinished. Newly reported 2D battle/map crashes are
  undiagnosed; no new crash fix, whole-game stability or hardware clearance is
  claimed. Earlier bridge and Church hardware passes are version/scope-specific.
- Existing release tags, bodies and assets are preserved. Only the builder EXE
  and SHA-256 checksum file are published as the new release's assets.

## 0.5.3 — October 7, 2026 (experimental dialogue, UI and rendering update)

- 733 targets: 42 changed, 691 byte-identical payloads retained from 0.5.2,
  with no added/removed targets. Scope is 38 cutscene packs, one existing-English
  script reflow, two UI archives and the shared graphics-layout repair. Eleven
  unrelated preexisting private overlays and six uninstalled fields are excluded.
- Fresh typed before/current reconciliation confirms 175 recent translated
  dialogue fields across 38 packs, raw CJK reduction 173 and two retained source
  heart glyphs. Eight older privately installed translations in one scene have
  separate source/installation lineage and are not counted in the recent 175.
  Existing-English quality corrections are separate. The broader town audit and
  full rendered-fit/runtime validation remain incomplete.
- Frozen manifest SHA-256:
  `f1265829a7c2e19e43723b1775b953aa92775f95adcaec3b7bb582ccd384adfa`.
- Exact Windows-native EXE: 3,524,096 bytes, SHA-256
  `cbef76ca68e3aa8ff0e2001e08a21882f58d92e210406750d0c2d3628545009b`.
- Three fresh complete matching-source builds passed GUI construction, 44 codec
  and 22 support checks, all 733 embedded payload checks, all 733 output
  path/size/hash checks and source-before/after checks. Native codecs and safety
  assertions are unchanged from 0.5.2; builder changes are version/manifest pins.
- Independent inspection of the sole embedded ZIP verified exactly the manifest
  and 733 patch payloads, independently reconstructed all targets and checked
  the 42-change/691-preserved scope. No original archives, ROMs, saves, private
  reference CSV or extra package files are embedded.
- Functional GUI build/cancellation and both pinned tool downloads passed;
  independent readback checked every GUI output. The first restricted-environment
  download attempt failed at TLS credentials after build/cancellation passed;
  a fresh exact-assembly permitted-network run passed all gates. No emulator,
  Windows policy, cache or decoder changes were used.
- The rebuilt cartridge passed independent readback of all 21,250 RomFS files,
  three ExeFS files, content hashes and three IVFC levels. Unrelated partitions
  and the original ROM were preserved. Modified Nintendo retail signatures are
  expected invalid; they are not claimed as valid signatures.
- The exact release asset passed a scoped Defender file scan with no threats
  detected. This is not a security guarantee; the builder remains unsigned.
- Shared archive repair restores the exact original graphics suffix/addresses
  while retaining every current payload. The player reports Octagonia and
  Heliodor rendering passes in Azahar. The internal graphics dependency is not
  diagnosed. The Church fix has a separate user-reported hardware pass on 0.5.2,
  not hardware validation of the new 0.5.3 archive. Whole-game, new-version
  hardware, all layouts and clean-host compatibility remain unverified.
- Historical 0.5.0, 0.5.1 and 0.5.2 release assets remain unchanged. The earlier
  Church-unresolved wording below reflects release-time evidence and is
  superseded by the later limited 0.5.2 user hardware confirmation above.

## 0.5.2 — October 4, 2026 (experimental Heliodor rendering repair)

**This version has not been tested on real hardware.** The player reports a
limited Azahar Heliodor rendering pass with the compact item-storage variant;
file verification is not gameplay or whole-game certification.

- 733 targets: only `syscmn.pack` changes relative to 0.5.1; the other 732
  payloads, eight-byte bridge repair and Veronica/Sylvando IPS are unchanged.
  The private newer dialogue overlays are not included.
- Manifest SHA-256:
  `875318786e3f69e4245bb2ad506e91f83b8d147ee986ba0c26aae490454ffb85`.
- Exact native Windows EXE: 3,511,296 bytes, SHA-256
  `b1e20b31762b2b8293f28c9fed2a1f3e48583a28bc65d63a1f718c1f55e138e6`.
- Three fresh normal-permission full builds each passed GUI construction,
  44 codec checks, 22 support checks, all 733 embedded payload checks and
  all 733 matching-source builds. Separate native readback checked every
  output path, size and hash, and each original input before and after.
- Typed item audit covers all 2,875 descriptors: all effective UTF-16 names
  and descriptions, ASCII resource strings, nullness and original gameplay
  metadata are preserved. The original text tail is fully accounted for by
  typed strings and alignment padding, and reconstructs byte-for-byte.
  Compact storage interns byte-identical same-encoding strings and changes
  pointer/storage topology; it does not establish an exact GPU or memory fault.
  The other 67 archive payloads and table/header metadata are preserved;
  original, legacy-translated and compact archive no-op rebuilds match exactly.
- The final EXE's exact release-asset file passed a native Microsoft Defender
  custom scan with no threats detected. This scoped scan is not a security
  guarantee; the unsigned executable is not represented as signed.
- Functional GUI success/cancellation, both pinned tool downloads and cancelled
  downloads passed. Independent readback verified all 733 GUI-built files.
- Independent extraction of the final builder's rebuilt ROM verified all
  21,250 RomFS files, three ExeFS files, content integrity and unchanged
  non-game partitions. The original ROM remained unchanged. These are file
  checks, not hardware gameplay validation.
- The sole embedded resource contains exactly the manifest and 733 verified
  patch payloads, with no extra files or private game/reference data.
- Earlier helper-path mistakes were held and corrected without changing the
  package: a nested output was safely rejected, and an independent harness
  initially selected the old manifest. Successful final-EXE repeats supersede
  these test-harness results; no runtime/decoder masking was used.
- Clean-host/Windows 8 compatibility, hardware Heliodor rendering, Church exit
  behavior, other reported crashes, full translation and rendered text fit
  remain unverified or unresolved. The previous Python execution-failure cause
  remains unknown. 0.5.0 and 0.5.1 release assets remain unchanged.

## 0.5.1 — October 4, 2026 (experimental hardware-crash hotfix)

- 733 targets, one changed and 732 unchanged relative to 0.5.0. Only the
  gamecmn delta/target changes; the IPS and all other payloads are identical.
  Four original enemy-category values are restored: exactly eight target bytes.
  No English text, archive layout or unrelated gameplay bytes change in this fix.
- Frozen manifest SHA-256:
  `f1219ec7990d2fa82eaee34df754f85b0282bf4a7e5a0069aa7655ea60cc1345`.
- Windows-native C#/.NET Framework 4.8 executable: 3,528,192 bytes, SHA-256
  `ede72bb014ecb38b9ae96cd8c0e1a47eab0001832b4096970e72bc45e424e305`.
  It does not bundle or execute Python. Its sole managed resource is a ZIP of
  exactly the manifest plus 733 hash-verified patch payloads; no originals,
  complete game archives, ROMs, saves or private reference data are embedded.
- Three fresh normal-permission trials constructed the GUI, checked all733
  embedded payloads and rebuilt all733 outputs from matching originals.
  Each passed 44 codec plus22 support/path/cancellation synthetic checks,
  with separate native output path/size/hash and source before/after checks.
- Functional GUI checks also passed under the production Windows message loop:
  successful build, cancellation, restored controls, and no cancelled output
  advertised as ready. Both pinned tool downloads and pre-cancelled download
  checks passed. The GUI-built mod passed independent checks of all 733 files.
- Microsoft Defender's custom file scan of this exact executable completed
  with no threats detected. This is a scoped scan, not a security guarantee.
- End-to-end cartridge extraction, patching and rebuilding passed. Independent
  CTRTool extraction checked every one of21,250 RomFS files and three ExeFS
  files against original/frozen expected bytes. Logo/exheader/ExeFS/RomFS and
  all three IVFC integrity levels passed; unrelated cartridge partitions were
  preserved, original ROM unchanged and only the private exheader code-compression
  bit cleared for uncompressed patched code. Modified NCSD/NCCH Nintendo retail
  signatures necessarily fail; these expected authentication failures are not
  represented as valid retail signatures or content-integrity failures.
- The rebuilt cartridge was byte-for-byte identical to the diagnostic the
  player reported passed the previously crashing hardware bridge/walking test.
  This is limited user-reported testing, not an independently observed full
  playthrough. Heliodor's possible rendering recurrence awaits a clean-install
  result; the Church exit crash is not established as fixed.
- The first native ROM trial stopped normally at3dstool's legacy261-character
  path limit. Shorter exclusive temporary paths and fail-closed path preflight
  were implemented, recompiled and checked in a fresh successful complete trial.
  No Windows policy, registry, emulator or PC settings were changed.
- Previous Python-based execution failures remain unexplained, including failures
  outside packaging. Replacing the builder is an authorized architecture change,
  not a diagnosed Python/PC/hardware fix. Clean-host and Windows8 compatibility,
  wider schemas, gameplay and rendered text fit remain unverified.

## 0.5.0 — October 2, 2026 (experimental prerelease)

- 733 frozen targets: 730 PACK deltas, two BCH deltas and one executable IPS;
  111 changed, 622 unchanged, no additions/removals relative to 0.4.0.
  See [0.5.0-target-changes.json](0.5.0-target-changes.json).
- Latest installation receipts were reconciled against live files before the
  freeze. Snapshot hashes stayed stable during copying and delta generation.
  The Veronica/Sylvando display-only IPS is unchanged.
- Candidate manifest SHA-256:
  `e9bef010e9444ef3e218be6d0ac5f883018a8e6d0452734eb60be47557b61871`.
- Source builder rebuilt all 733 targets from matching originals. Independent
  sizes/hashes/path-set checks matched every frozen output, with no extra files.
- All 24 repository regression tests passed with normal Windows permissions.
  A sandbox-restricted run encountered temporary-file permission errors; it
  is superseded by the complete successful normal-permissions run.
- Exact final Windows EXE: 15,436,543 bytes, SHA-256:
  `d689143cd33037d036db44a8239958cad259a52c0bb7dc289592962bea9aa14b`.
  At the player's request, three fresh full frozen-builder runs with normal
  Windows permissions each created the GUI, verified all 733 embedded payloads
  and rebuilt all 733 targets from matching originals. Separate native readback
  matched every output's size/hash and exact path set in all three runs, with
  no mismatches or extras. All 24 regression tests also passed again.
- Earlier attempts had intermittent failures in this EXE, the previously
  published builder and standalone Python; their root cause remains unknown.
  A sandbox-restricted evening startup also stalled and was stopped. These
  successful normal-permissions repeats establish scoped verification on this
  host, not proof of a diagnosed fix or clean-Windows reliability. No tracing,
  decoder masking or runtime/PC-setting workaround was added. The older
  `f08c625...` candidate success is historical, not the final-asset proof.
- The player reported the frozen candidate "good to go" after the requested
  limited in-game spot check. Specific screens were not individually enumerated,
  and the check was not independently observed. File verification does not
  establish all rendered fit or gameplay correctness. Clean-Windows, Windows 8
  and real-hardware execution remain unverified. Hardware bridge/Church 3D
  crashes are unresolved; this is not a stable or fully translated release.

## 0.4.0 — October 1, 2026 (experimental prerelease)

- Frozen from the working local installation after the player confirmed the
  corrected Veronica/Sylvando final-letter repair. All live target hashes were
  stable across delta generation; no failed comparison variants or held stages
  were substituted into this snapshot.
- 733 targets: 730 PACK deltas, two BCH image deltas and one executable IPS.
  Compared with the hash-pinned 0.3.2 manifest: 156 added targets, 56 changed
  targets, 521 unchanged, zero removed. The exact file list is in
  [0.4.0-target-changes.json](0.4.0-target-changes.json).
- Packaged Windows manifest SHA-256 (before Git line-ending normalization):
  `2aba70cd5ce2fc4191d30af6e9ac37e4df227574788c4df695c4d3ec9180008a`.
- All 24 repository tests passed. A separate source-builder run checked source
  hashes, rebuilt all 733 targets and independently matched all output hashes
  to the frozen snapshot, with zero extra files or mismatches.
- Exact final Windows EXE: 15,228,359 bytes, SHA-256
  `fbc7150913e537d9ba478fb996eaa1b02935a025852ba2bdab46cc6949d68901`.
  Its frozen self-test ran with normal Windows permissions, constructed its
  GUI, verified all 733 embedded payloads and rebuilt all 733 targets from
  matching originals. A separate hash comparison confirmed 733/733 and no extras.
- The corrected display-only name hook passed 62 actual ARM tests, including
  execution of the original singleton accessor. The first candidate failed
  the human test due to an extra pointer dereference; it is NOT packaged.
  The corrected version was player-confirmed. Existing IPS records and
  character/gameplay data are preserved; no save fields or name buffers expanded.
- These are structural/build and scoped player checks, not a complete gameplay
  audit. New 3DS 3D-mode bridge/Church crashes remain unresolved; 0.4.0 has not
  been hardware-tested. Clean-Windows/Windows 8, wider UI/story/side-world fit,
  Hotto's first-visit title and saved Tockle names remain open.

## 0.3.2 — September 30, 2026 (experimental; hardware crash confirmed)

- Generated 577 patch targets from the reviewed local installation: 575 PACK
  deltas, one standalone BCH delta, and one executable IPS. All 577 targets
  rebuilt against original inputs and independently matched installed hashes.
- Manifest SHA-256: `eb948e1cd2de1320aaf915112ab3cfa1b8c2de4818a6713fb36ad7225d494e52`.
- All 23 automated tests passed, including a standalone BCH release/builder
  roundtrip. The Windows EXE packaged successfully (14,942,937 bytes; SHA-256
  `8bb4772ccc1622ed5b2d8c72b33ed3a3c5dbf9937eb8253a95bcd1d9923702b6`).
  A later frozen runtime self-test with normal Windows permissions created the
  GUI, verified 577 embedded payloads and rebuilt all 577 mod targets from
  matching originals. Independent output hashes matched **577/577**. A first
  sandbox-restricted attempt did not finish; clean-Windows execution remains
  unverified.
- A New 3DS tester confirms that the exact 0.3.2 build still crashes at the
  bridge toward Heliodor and when leaving the Church of Guidance. The tester
  reports that the earlier Heliodor rendering error is no longer visible;
  broader validation remains open. Hotto first-visit image and saved Tockle-name
  checks remain open. The 8,708
  Japanese-field covered audit omits secondary references. A corrected later
  scan finds 8,328 Japanese regional secondary candidates after excluding 270
  false refs embedded within decoded strings. Neither number is a complete
  count of active untranslated dialogue; local work after 0.3.2 affects the
  newer candidate count.
- A patch-only 0.3.2 original-data control was added after the hardware crash
  report. Its reverse delta was checked against exact 0.3.2 and original PACK
  hashes; the reconstructed output matched the original byte for byte. All 24
  repository tests passed. This is a diagnostic, **not** a fix or a new release.

## 0.3.1 — September 29, 2026 (experimental; hardware unverified)

- Built 575 patch targets from the last validated installed mod: 574 archive
  deltas and one executable IPS payload. All payload hashes and delta
  reconstructions passed; all 575 original source hashes and rebuilt output
  hashes matched the installed snapshot, with zero extras or mismatches.
- The manifest SHA-256 before publication is
  `61387080d95c567d5fabf182536b737cc12aa567340c11278b4e225be0bf0345`.
- The 0.3.0/0.2.0 New 3DS 3D-mode bridge-to-Heliodor crash and possible
  first-visit rendering corruption remain unresolved. This release is **not**
  a validated fix. Hardware A/B diagnostic results are still needed.
- All 22 automated tests passed. The frozen Windows builder self-test created
  its GUI, verified 575 embedded payloads, and built 575 mod targets from
  matching originals; independent output hashes matched 575/575.
- The Windows EXE is 14,924,117 bytes, SHA-256
  `1631a9ea467362fa0a1cdf1bb986cb34ca6b799a43bc229355506192aecb144e`.
  A clean-Windows test and real-hardware gameplay validation remain pending.

## 0.3.0 — September 29, 2026

- Built 566 patch targets from the current mod: 565 archive deltas and one
  executable IPS payload. All deltas reconstructed their targets byte for byte.
- Independently compared every target hash against the current mod: 566/566
  matched. A separate extracted-input build checked all 566 original source
  hashes and verified all 566 output files.
- All 21 automated tests passed. Restricted test runs initially failed to
  create Windows temporary directories; the same tests passed outside that
  restriction without code changes.
- A fresh effective-overlay BXON/BFLYT scan found 12,472 Japanese-containing
  fields and zero parse errors. This is evidence of incompleteness, not a
  comprehensive image/executable-text or gameplay audit.
- The release payloads and manifest total 2,662,326 bytes and contain no ROM,
  complete game archive or save. All 567 files exactly match the validated
  release candidate.
- The rebuilt standalone Windows EXE is 14,765,221 bytes, SHA-256
  `16e4af1147e64d7e666a83cfb70f17aa6f0651f61a45444d1962d38ee376c66f`.
  Its frozen self-test created the GUI, verified all 566 embedded payloads,
  and built a mod from extracted originals with output verification.
- Broader in-game testing of this exact release and a clean-Windows test remain
  pending; structural checks do not establish that every screen fits.

## 0.2.0 — September 20, 2026

- Regenerated the release from the current installed mod, including the final
  normal-spacing correction rather than the superseded overlapping-text experiment.
- 518 patch targets: 517 archive deltas and one executable IPS payload.
- Every archive delta reconstructed its target byte for byte. All 518 target
  hashes were independently compared with the installed mod after packaging.
- Release payloads and manifest total 2,079,129 bytes.
- All 21 automated tests passed. Initial sandboxed runs hit Windows temporary-folder
  permission errors; rerunning outside that restriction passed without code changes.
- The frozen Windows executable instantiated its GUI, verified all 518 embedded
  payload hashes, and completed an extracted-input-to-mod build with mandatory
  output hash and size verification.
- The unsigned Windows EXE is 14,195,512 bytes. Its SHA-256 is
  `3fa7d4677e039491f671f0e2ba14a69009e421b274fdb69b62ac25cf997a6415`.
- The same frozen executable completed a decrypted `.3ds` input-to-output build,
  checking rebuilt partition/header hashes and preservation of non-game partitions.
  An initial attempt used an incorrect local tool path; the corrected-path retry
  completed successfully. Test ROMs and extracted files remain private.

The [changelog](../CHANGELOG.md) distinguishes completed text audits from remaining
translation and visual checks. In particular, the newest monster-list spacing fix
has not yet been confirmed in game. These checks do not establish full translation,
all-screen readability, or real-hardware compatibility.

## Historical initial player-build validation

Validated September 16, 2026:

- 14 synthetic unit tests passed.
- The pinned Windows x64 CTRTool v1.3.0 download matched its recorded SHA-256.
- A decrypted game application (`.app`) was extracted through the player builder.
- All source-file checks passed against the release manifest.
- All 379 generated mod files matched the active development mod byte for byte.
- Release deltas and manifest total 955,089 bytes (about 0.96 MB).
- The release tree contains only deltas, a small executable patch payload, and
  a hash/path manifest. It does not contain a ROM, full game archive, or save.

These checks establish reproducibility of the current incomplete mod, not that
the game has been fully translated or every scene has been tested. The original
game and saved progress were not changed. The new builder's `.cci`, `.3ds`, and
`.cxi` container paths have not all received end-to-end tests. Their extracted
files must pass the same mandatory hash checks.

## Standalone Windows application

The Windows x64 windowed EXE bundles Python 3.13, Tcl/Tk, and the 379 patch
payloads. It does not require users to install Python. It downloads the pinned
extractor with consent, or accepts an existing extractor.

- 16 automated tests passed, including cancellation before I/O and rejection of
  incorrect inputs without creating output.
- The frozen executable successfully created its graphical interface and verified
  all embedded payload hashes in a hidden startup smoke test.
- The frozen executable completed both extracted-input and decrypted `.app`
  ROM-to-mod builds. The final ROM-to-mod build's 379 output hashes matched the
  release manifest.
- The bundled-file inventory contained no ROM, extracted PACK archive, or save.
- Runtime license notices are bundled. The executable is unsigned.

The UI was instantiated in the smoke test; interactive clicking and all Windows
display-scaling configurations have not been exhaustively tested. Automated tests
were run on a development machine; a separate clean Windows machine test remains
recommended before promoting the release as stable.

## Single .3ds output

The GUI now defaults to a translated `.3ds` cartridge output; mod folders remain
an option. Validation completed September 16, 2026:

- 19 unit tests passed, including IPS literal/run records and malformed-patch rejection.
- The pinned official 3dstool v1.2.6 download was checksum-verified.
- A full decrypted NCSD cartridge was rebuilt to a separate `.3ds`.
- The original non-game partitions were preserved and verified by SHA-256.
- Rebuilt NCCH extended-header, ExeFS, and RomFS header hashes passed verification.
- Re-extraction of the rebuilt cartridge reproduced all 378 translated archive
  hashes and the expected IPS-patched executable bytes.
- The packaged EXE independently completed a full `.3ds` input-to-output build,
  without an external Python interpreter.

The generated image is decrypted and unsigned. These are structural and content
checks, not a full emulator gameplay test or a real-hardware compatibility claim.
The input cartridge and saves were not modified. Generated ROMs and intermediate
files remain private and must not be uploaded to the public repository.
