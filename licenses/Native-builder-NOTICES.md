# Native builder notices

The 0.5.1 release builder is the repository's MIT-licensed C# source in
`tools/native/`. It uses the user's installed Microsoft .NET Framework 4.8;
Microsoft runtime binaries are not bundled in this release executable.

Pinned CTRTool and 3dstool are optionally downloaded from their official
upstream releases and checked by SHA-256. They retain their upstream licenses;
they are not relicensed by this repository. Neither tool, its optional key
databases, nor game originals are embedded in the release builder.

The Python, Tk and PyInstaller notices retained in this directory describe the
historical Python builders, not bundled components of the 0.5.1 native EXE.
