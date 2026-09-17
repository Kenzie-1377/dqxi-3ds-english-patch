# Contributing

Please submit small, reviewable changes and run the synthetic test suite:

```sh
python -m unittest discover -s tests -v
```

Do not commit ROMs, extracted files, game scripts, saves, encryption keys,
credentials, emulator binaries, personal paths, or compiled mod archives.
Ignore rules are a convenience, not a security check: review the staged diff.

The `release/` directory is the exception for reviewed, generated delta patches
and their hash manifest. Never replace those deltas with complete game archives.
Rebuild them with `tools/make_release.py`, test reconstruction against your own
inputs, and review the release inventory before committing.

Use synthetic examples when reporting parser bugs. For layout issues, describe
the screen, font settings, input length, and observed wrapping without uploading
large portions of game dialogue. Include whether a normal save or a save state
was loaded when investigating cached names or text.

Contributions of original code/documentation are offered under this repository's
MIT license. Identify third-party source and its license before proposing reuse.
Do not copy walkthroughs or official scripts into this repository.
