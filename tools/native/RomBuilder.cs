using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Threading;

// Private, decrypted DQXI cartridge reconstruction. Inputs are never modified.
// A completed output is promoted only after partition and filesystem readback.
public static class RomBuilder
{
    const string ToolUrl = "https://github.com/dnasdw/3dstool/releases/download/v1.2.6/3dstool.zip";
    const string ToolZipSha = "481e20f445eb2f0f506d0d88cd750385bc8377670d681d6f66f584a176027806";
    const string ToolExeSha = "967fd5ec6476df1fa6a01da0df5a1fea339aa488c10be218d38e07f4b8143b7e";
    const string OriginalCodeSha = "dfcd1b7ad170eab3932abfaa702b694e6673dc0a8744bfc070765cc8c8cc24d8";
    const ulong TitleId = 0x0004000000199200UL;

    sealed class Part { public long Offset; public long Size; }

    public static void ValidateCartridge(string path)
    {
        ReadPartitions(Path.GetFullPath(path));
    }

    static uint U32(byte[] b, int p)
    {
        return (uint)(b[p] | b[p + 1] << 8 | b[p + 2] << 16 | b[p + 3] << 24);
    }

    static ulong U64(byte[] b, int p)
    {
        return U32(b, p) | ((ulong)U32(b, p + 4) << 32);
    }

    static bool Magic(byte[] b, int p, string text)
    {
        if (b.Length < p + text.Length) return false;
        for (int i = 0; i < text.Length; i++) if (b[p + i] != (byte)text[i]) return false;
        return true;
    }

    static byte[] ReadExactly(Stream s, int size)
    {
        byte[] b = new byte[size];
        int p = 0;
        while (p < size) { int n = s.Read(b, p, size - p); if (n == 0) throw new InvalidDataException("Unexpected end of cartridge."); p += n; }
        return b;
    }

    static void CheckRange(long offset, long size, long length, string label)
    {
        if (offset < 0 || size < 0 || offset > length || size > length - offset)
            throw new InvalidDataException(label + " exceeds file bounds.");
    }

    static SortedDictionary<int, Part> ReadPartitions(string path)
    {
        var result = new SortedDictionary<int, Part>();
        using (var s = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            byte[] h = ReadExactly(s, 512);
            if (!Magic(h, 256, "NCSD")) throw new InvalidDataException("Single-ROM output requires a decrypted .3ds/.cci cartridge, not an .app/.cxi.");
            for (int i = 0; i < 8; i++)
            {
                long offset = (long)U32(h, 0x120 + i * 8) * 512;
                long size = (long)U32(h, 0x124 + i * 8) * 512;
                if (size == 0) { if (offset != 0) throw new InvalidDataException("Empty cartridge partition has an offset."); continue; }
                if (offset < 512 || size < 512) throw new InvalidDataException("Invalid cartridge partition.");
                CheckRange(offset, size, s.Length, "Cartridge partition");
                foreach (Part other in result.Values)
                    if (offset < other.Offset + other.Size && other.Offset < offset + size)
                        throw new InvalidDataException("Cartridge partitions overlap.");
                result.Add(i, new Part { Offset = offset, Size = size });
            }
            if (!result.ContainsKey(0)) throw new InvalidDataException("Cartridge has no game partition.");
            s.Position = result[0].Offset;
            byte[] game = ReadExactly(s, 512);
            if (!Magic(game, 256, "NCCH") || U64(game, 0x118) != TitleId)
                throw new InvalidDataException("This is not the supported Japanese DQXI cartridge.");
        }
        return result;
    }

    static byte[] HashRange(string path, long offset, long size, CancellationToken cancel)
    {
        using (var s = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        using (var sha = SHA256.Create())
        {
            CheckRange(offset, size, s.Length, "Hash range"); s.Position = offset;
            byte[] buffer = new byte[1024 * 1024];
            while (size > 0)
            {
                cancel.ThrowIfCancellationRequested();
                int n = s.Read(buffer, 0, (int)Math.Min(size, buffer.Length));
                if (n == 0) throw new InvalidDataException("Unexpected end of cartridge while hashing.");
                sha.TransformBlock(buffer, 0, n, buffer, 0); size -= n;
            }
            sha.TransformFinalBlock(new byte[0], 0, 0); return sha.Hash;
        }
    }

    static bool Equal(byte[] a, byte[] b)
    {
        if (a.Length != b.Length) return false;
        int different = 0; for (int i = 0; i < a.Length; i++) different |= a[i] ^ b[i];
        return different == 0;
    }

    static string Hex(byte[] hash) { return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant(); }
    static string FileHash(string path, CancellationToken cancel) { return Hex(HashRange(path, 0, new FileInfo(path).Length, cancel)); }

    static void MatchHeaderDigest(string path, byte[] header, long offset, long size, int expected, CancellationToken cancel)
    {
        byte[] digest = new byte[32]; Buffer.BlockCopy(header, expected, digest, 0, 32);
        if (!Equal(HashRange(path, offset, size, cancel), digest))
            throw new InvalidDataException("NCCH plaintext region hash verification failed.");
    }

    static void VerifyNcch(string path, bool requireDecrypted, CancellationToken cancel)
    {
        byte[] h;
        long length;
        using (var s = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        { length = s.Length; h = ReadExactly(s, 512); }
        if (!Magic(h, 256, "NCCH") || U64(h, 0x118) != TitleId || (requireDecrypted && (h[0x18f] & 4) == 0))
            throw new InvalidDataException("Game partition is not a supported decrypted NCCH.");
        // This implementation deliberately supports only the established 512-byte media units.
        if (h[0x18e] != 0) throw new InvalidDataException("Unsupported NCCH media-unit size.");
        long declared = (long)U32(h, 0x104) * 512;
        if (declared != length) throw new InvalidDataException("NCCH declared size differs from partition size.");
        uint extendedSize = U32(h, 0x180);
        if (extendedSize == 0) throw new InvalidDataException("Game extended header is missing.");
        CheckRange(512, extendedSize, length, "Extended header");
        MatchHeaderDigest(path, h, 512, extendedSize, 0x160, cancel);
        foreach (int start in new int[] { 0x1a0, 0x1b0 })
        {
            long offset = (long)U32(h, start) * 512;
            long size = (long)U32(h, start + 4) * 512;
            long hashSize = (long)U32(h, start + 8) * 512;
            if (offset < 512 || size == 0 || hashSize == 0 || hashSize > size)
                throw new InvalidDataException("Invalid filesystem hash-region bounds.");
            CheckRange(offset, size, length, "NCCH filesystem");
            MatchHeaderDigest(path, h, offset, hashSize, start == 0x1a0 ? 0x1c0 : 0x1e0, cancel);
        }
    }

    static bool NormalizePrivateHeader(string path, CancellationToken cancel)
    {
        // Plaintext checks must pass BEFORE any encryption flag is modified.
        VerifyNcch(path, false, cancel);
        using (var s = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.None))
        {
            s.Position = 0x18f; int flags = s.ReadByte();
            if ((flags & 4) != 0) return false;
            s.Position = 0x18f; s.WriteByte((byte)(flags | 4)); s.Flush();
        }
        VerifyNcch(path, true, cancel); return true;
    }

    static void VerifyEmbeddedFiles(string game, string folder, CancellationToken cancel)
    {
        byte[] h;
        using (var s = new FileStream(game, FileMode.Open, FileAccess.Read, FileShare.Read)) h = ReadExactly(s, 512);
        foreach (var row in new KeyValuePair<int, string>[] {
            new KeyValuePair<int, string>(0x1a0, "new-exefs.bin"),
            new KeyValuePair<int, string>(0x1b0, "new-romfs.bin") })
        {
            string expected = Path.Combine(folder, row.Value);
            long offset = (long)U32(h, row.Key) * 512; long size = (long)U32(h, row.Key + 4) * 512;
            long expectedSize = new FileInfo(expected).Length;
            if (size != expectedSize || !Equal(HashRange(game, offset, size, cancel), HashRange(expected, 0, expectedSize, cancel)))
                throw new InvalidDataException("NCCH does not contain the exact newly built filesystem.");
        }
        string extended = Path.Combine(folder, "exheader.bin"); long extendedLength = new FileInfo(extended).Length;
        if (!Equal(HashRange(game, 512, extendedLength, cancel), HashRange(extended, 0, extendedLength, cancel)))
            throw new InvalidDataException("Rebuilt extended header does not match its private source.");
        foreach (var row in new KeyValuePair<int, string>[] {
            new KeyValuePair<int, string>(0x198, "logo.bin"),
            new KeyValuePair<int, string>(0x190, "plain.bin") })
        {
            string expected = Path.Combine(folder, row.Value);
            long offset = (long)U32(h, row.Key) * 512; long size = (long)U32(h, row.Key + 4) * 512;
            if (size == 0) { if (File.Exists(expected) && new FileInfo(expected).Length != 0) throw new InvalidDataException("Original NCCH resource was dropped."); continue; }
            if (!File.Exists(expected) || size != new FileInfo(expected).Length || !Equal(HashRange(game, offset, size, cancel), HashRange(expected, 0, size, cancel)))
                throw new InvalidDataException("Original NCCH resource changed.");
        }
    }

    static string Root(string path)
    {
        return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
    }

    static void RejectLinks(string path)
    {
        if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
            throw new InvalidDataException("Linked filesystem paths are not permitted: " + path);
    }

    static void CheckAncestors(string path)
    {
        string at = Path.GetFullPath(path);
        while (!String.IsNullOrEmpty(at))
        {
            if (Directory.Exists(at) || File.Exists(at)) RejectLinks(at);
            string parent = Path.GetDirectoryName(at);
            if (String.Equals(parent, at, StringComparison.OrdinalIgnoreCase)) break;
            at = parent;
        }
    }

    static Dictionary<string, string> Inventory(string folder, CancellationToken cancel)
    {
        string root = Root(folder); CheckAncestors(folder);
        if (!Directory.Exists(folder)) throw new DirectoryNotFoundException(folder);
        var files = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var pending = new Stack<string>(); pending.Push(Path.GetFullPath(folder));
        while (pending.Count != 0)
        {
            cancel.ThrowIfCancellationRequested(); string dir = pending.Pop(); RejectLinks(dir);
            foreach (string child in Directory.GetDirectories(dir)) { RejectLinks(child); pending.Push(child); }
            foreach (string file in Directory.GetFiles(dir))
            {
                RejectLinks(file); string absolute = Path.GetFullPath(file);
                if (!absolute.StartsWith(root, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Filesystem path escaped its root.");
                string relative = absolute.Substring(root.Length);
                if (relative.IndexOf(':') >= 0 || relative.IndexOf('\0') >= 0 || files.ContainsKey(relative))
                    throw new InvalidDataException("Unsafe or duplicate filesystem path.");
                files.Add(relative, absolute);
            }
        }
        return files;
    }

    static void CopyTree(string input, string output, CancellationToken cancel)
    {
        foreach (var pair in Inventory(input, cancel))
        {
            cancel.ThrowIfCancellationRequested(); string dest = Path.Combine(output, pair.Key);
            Directory.CreateDirectory(Path.GetDirectoryName(dest)); File.Copy(pair.Value, dest, false);
            if (FileHash(pair.Value, cancel) != FileHash(dest, cancel)) throw new IOException("Private input copy verification failed.");
        }
    }

    static void VerifyTree(string expected, string actual, CancellationToken cancel)
    {
        var a = Inventory(expected, cancel); var b = Inventory(actual, cancel);
        if (a.Count != b.Count) throw new InvalidDataException("Rebuilt filesystem path set differs.");
        foreach (var pair in a)
        {
            cancel.ThrowIfCancellationRequested(); string target;
            if (!b.TryGetValue(pair.Key, out target) || FileHash(pair.Value, cancel) != FileHash(target, cancel))
                throw new InvalidDataException("Rebuilt filesystem does not match staged bytes: " + pair.Key);
            if(!String.Equals(pair.Key, Path.GetFullPath(target).Substring(Root(actual).Length), StringComparison.Ordinal))
                throw new InvalidDataException("Rebuilt filesystem path casing changed: " + pair.Key);
        }
    }

    static void VerifyExeFsNonCode(string original, string staged, CancellationToken cancel)
    {
        var a = Inventory(original, cancel); var b = Inventory(staged, cancel);
        if (!a.Remove("code.bin") || !b.Remove("code.bin")) throw new InvalidDataException("Original ExeFS code is missing.");
        if (a.Count != b.Count) throw new InvalidDataException("Original ExeFS path set differs.");
        foreach (var pair in a)
        {
            string target;
            if (!b.TryGetValue(pair.Key, out target) || FileHash(pair.Value, cancel) != FileHash(target, cancel))
                throw new InvalidDataException("A non-code executable resource differs from the cartridge: " + pair.Key);
        }
    }

    static bool Overlap(string a, string b)
    {
        return Root(a).StartsWith(Root(b), StringComparison.OrdinalIgnoreCase) || Root(b).StartsWith(Root(a), StringComparison.OrdinalIgnoreCase);
    }

    static void AliasExeFs(string folder, string input, string output, CancellationToken cancel)
    {
        string source = Path.Combine(folder, input); string target = Path.Combine(folder, output);
        if (!File.Exists(source)) return;
        if (File.Exists(target))
        {
            if (FileHash(source, cancel) != FileHash(target, cancel)) throw new InvalidDataException("Conflicting ExeFS filenames.");
            File.Delete(source); // This is solely the fresh private copy, never an input file.
        }
        else File.Move(source, target);
    }

    public static string Build(string rom, string extracted, string mod, Action<string, int> notify, CancellationToken cancel, string tool)
    {
        rom = Path.GetFullPath(rom); extracted = Path.GetFullPath(extracted); mod = Path.GetFullPath(mod);
        CheckAncestors(rom); CheckAncestors(extracted); CheckAncestors(mod);
        if (!Directory.Exists(extracted) || !Directory.Exists(mod)) throw new DirectoryNotFoundException("Extraction or mod folder does not exist.");
        if (Overlap(extracted, mod) || rom.StartsWith(Root(extracted), StringComparison.OrdinalIgnoreCase) || rom.StartsWith(Root(mod), StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("ROM input, extraction, and output paths must not overlap.");
        string final = Path.Combine(mod, "DQXI-English.3ds"); string partial = final + ".partial";
        if (File.Exists(final) || File.Exists(partial)) throw new IOException("ROM output already exists; choose a fresh output folder.");
        // A read-only share lock prevents input-ROM mutation for the entire reconstruction.
        using (var inputLock = new FileStream(rom, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            string inputRomHash = FileHash(rom, cancel);
            var originalParts = ReadPartitions(rom);
            string folder = Path.Combine(extracted, "r-" + Guid.NewGuid().ToString("N").Substring(0,12));
            BuildSupport.CreateExclusiveDirectory(folder); string log = Path.Combine(folder, "rebuild.log");
            // Pinned 3dstool uses legacy file APIs. Reject long paths before extraction,
            // without modifying Windows policy or relaxing filesystem verification.
            if(partial.Length>=260 || rom.Length>=260 || folder.Length+32>=260)
                throw new IOException("Choose a shorter output parent path for the ROM rebuilding tool.");
            foreach(var file in Inventory(Path.Combine(extracted,"romfs"),cancel))
                if(Path.Combine(folder,"verify-romfs",file.Key).Length>=260)
                    throw new IOException("Choose a shorter output parent path; a game file exceeds the rebuilding tool's path limit.");
            string privateRomfs = Path.Combine(folder, "romfs"); string privateExefs = Path.Combine(folder, "exefs");
            Action<string, int> progress = notify ?? delegate { };
            Action<string[]> run = delegate(string[] toolArguments)
            {
                cancel.ThrowIfCancellationRequested();
                BuildSupport.RunTool(tool, toolArguments, folder, log, cancel);
                cancel.ThrowIfCancellationRequested();
            };
            progress("Preparing the ROM rebuilding tool...", 66);
            if (String.IsNullOrEmpty(tool)) tool = BuildSupport.FetchTool(ToolUrl, ToolZipSha, "3dstool.exe", Path.Combine(folder, "tool"), cancel);
            tool = Path.GetFullPath(tool); CheckAncestors(tool);
            if (FileHash(tool, cancel) != ToolExeSha) throw new InvalidDataException("ROM rebuilding tool checksum mismatch.");
            var parts = new SortedDictionary<int, string>();
            var args = new List<string> { "-x", "-t", "cci", "-f", rom, "--header", Path.Combine(folder, "ncsd.bin") };
            foreach (int i in originalParts.Keys)
            { parts.Add(i, Path.Combine(folder, "partition" + i + ".bin")); args.Add("--partition" + i); args.Add(parts[i]); }
            progress("Preserving the original cartridge partitions...", 69); run(args.ToArray());
            // Verify all external extraction results before private flag normalization.
            foreach (var pair in originalParts)
                if (new FileInfo(parts[pair.Key]).Length != pair.Value.Size || !Equal(HashRange(rom, pair.Value.Offset, pair.Value.Size, cancel), HashRange(parts[pair.Key], 0, pair.Value.Size, cancel)))
                    throw new InvalidDataException("Original cartridge partition extraction failed verification.");
            if (NormalizePrivateHeader(parts[0], cancel)) progress("Corrected a verified plaintext flag in the private working copy.", 71);
            run(new string[] { "-x", "-t", "cxi", "-f", parts[0], "--header", Path.Combine(folder, "ncch.bin"), "--exh", Path.Combine(folder, "exheader.bin"), "--logo", Path.Combine(folder, "logo.bin"), "--plain", Path.Combine(folder, "plain.bin"), "--exefs", Path.Combine(folder, "original-exefs.bin"), "--romfs", Path.Combine(folder, "original-romfs.bin") });
            string originalExefs = Path.Combine(folder, "original-exefs");
            run(new string[] { "-x", "-t", "exefs", "-f", Path.Combine(folder, "original-exefs.bin"), "--header", Path.Combine(folder, "exefs-header.bin"), "--exefs-dir", originalExefs });
            run(new string[] { "-x", "-t", "romfs", "-f", Path.Combine(folder, "original-romfs.bin"), "--romfs-dir", privateRomfs });
            VerifyTree(Path.Combine(extracted, "romfs"), privateRomfs, cancel);
            progress("Copying the private game files and applying the translation...", 73);
            CopyTree(Path.Combine(extracted, "exefs"), privateExefs, cancel);
            AliasExeFs(privateExefs, "banner.bin", "banner.bnr", cancel); AliasExeFs(privateExefs, "icon.bin", "icon.icn", cancel);
            AliasExeFs(originalExefs, "banner.bin", "banner.bnr", cancel); AliasExeFs(originalExefs, "icon.bin", "icon.icn", cancel);
            VerifyExeFsNonCode(originalExefs, privateExefs, cancel);
            var sourceFiles = Inventory(privateRomfs, cancel);
            foreach (var replacement in Inventory(Path.Combine(mod, "romfs"), cancel))
            {
                cancel.ThrowIfCancellationRequested(); string dest;
                if (!sourceFiles.TryGetValue(replacement.Key, out dest)) throw new InvalidDataException("Replacement adds an unknown original path: " + replacement.Key);
                File.Copy(replacement.Value, dest, true);
                if (FileHash(replacement.Value, cancel) != FileHash(dest, cancel)) throw new IOException("Translation copy verification failed.");
            }
            string code = Path.Combine(privateExefs, "code.bin");
            if (FileHash(code, cancel) != OriginalCodeSha) throw new InvalidDataException("Original executable is not the supported uncompressed DQXI code.");
            byte[] patched = NativeCodecs.ApplyIps(File.ReadAllBytes(code), File.ReadAllBytes(Path.Combine(mod, "exefs", "code.ips")));
            File.WriteAllBytes(code, patched);
            byte[] extended = File.ReadAllBytes(Path.Combine(folder, "exheader.bin"));
            if (extended.Length < 0x10) throw new InvalidDataException("Truncated game extended header.");
            extended[0x0d] &= 0xfe; File.WriteAllBytes(Path.Combine(folder, "exheader.bin"), extended);
            AliasExeFs(privateExefs, "banner.bin", "banner.bnr", cancel); AliasExeFs(privateExefs, "icon.bin", "icon.icn", cancel);
            run(new string[] { "-c", "-t", "exefs", "-f", Path.Combine(folder, "new-exefs.bin"), "--header", Path.Combine(folder, "exefs-header.bin"), "--exefs-dir", privateExefs });
            progress("Rebuilding the game filesystem. This can take several minutes...", 77);
            run(new string[] { "-c", "-t", "romfs", "-f", Path.Combine(folder, "new-romfs.bin"), "--romfs-dir", privateRomfs });
            progress("Rebuilding the translated game partition...", 85);
            args = new List<string> { "-c", "-t", "cxi", "-f", Path.Combine(folder, "translated.cxi"), "--header", Path.Combine(folder, "ncch.bin"), "--exh", Path.Combine(folder, "exheader.bin"), "--exefs", Path.Combine(folder, "new-exefs.bin"), "--romfs", Path.Combine(folder, "new-romfs.bin"), "--not-encrypt" };
            foreach (string name in new string[] { "logo", "plain" })
            { string path = Path.Combine(folder, name + ".bin"); if (File.Exists(path) && new FileInfo(path).Length > 0) { args.Add("--" + name); args.Add(path); } }
            run(args.ToArray()); string rebuiltGame = Path.Combine(folder, "translated.cxi"); VerifyNcch(rebuiltGame, true, cancel);
            VerifyEmbeddedFiles(rebuiltGame, folder, cancel);
            progress("Writing the translated .3ds file...", 91); parts[0] = rebuiltGame;
            args = new List<string> { "-c", "-t", "cci", "-f", partial, "--header", Path.Combine(folder, "ncsd.bin"), "--not-pad" };
            foreach (var part in parts) { args.Add("--partition" + part.Key); args.Add(part.Value); }
            run(args.ToArray()); progress("Verifying the rebuilt cartridge and preserved partitions...", 96);
            var rebuiltParts = ReadPartitions(partial);
            if (rebuiltParts.Count != originalParts.Count) throw new InvalidDataException("Cartridge partition set changed.");
            foreach (var pair in originalParts)
            {
                cancel.ThrowIfCancellationRequested(); Part output;
                if (!rebuiltParts.TryGetValue(pair.Key, out output)) throw new InvalidDataException("Cartridge partition set changed.");
                string expected = parts[pair.Key];
                byte[] actualHash = HashRange(partial, output.Offset, output.Size, cancel);
                if (output.Size != new FileInfo(expected).Length || !Equal(actualHash, HashRange(expected, 0, output.Size, cancel))) throw new InvalidDataException("Rebuilt partition verification failed.");
                if (pair.Key != 0 && !Equal(actualHash, HashRange(rom, pair.Value.Offset, pair.Value.Size, cancel))) throw new InvalidDataException("An unrelated cartridge partition changed.");
            }
            // Re-extract both newly built filesystems and compare every path and file byte hash.
            string verifyRomfs = Path.Combine(folder, "verify-romfs"); string verifyExefs = Path.Combine(folder, "verify-exefs");
            run(new string[] { "-x", "-t", "romfs", "-f", Path.Combine(folder, "new-romfs.bin"), "--romfs-dir", verifyRomfs });
            run(new string[] { "-x", "-t", "exefs", "-f", Path.Combine(folder, "new-exefs.bin"), "--exefs-dir", verifyExefs });
            VerifyTree(privateRomfs, verifyRomfs, cancel); VerifyTree(privateExefs, verifyExefs, cancel);
            if (FileHash(rom, cancel) != inputRomHash) throw new IOException("Original cartridge changed during reconstruction.");
            cancel.ThrowIfCancellationRequested();
            // File.Move refuses an existing destination. Partial output is never advertised as usable.
            File.Move(partial, final); progress("Verified cartridge ready for hardware testing.", 100); return final;
        }
    }
}
