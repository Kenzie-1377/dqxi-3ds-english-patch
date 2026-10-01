# Release validation

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
