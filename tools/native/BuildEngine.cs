using System;
using System.IO;
using System.IO.Compression;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Reflection;
using System.Web.Script.Serialization;
using System.Threading;

public sealed class BuildOptions {
    public string Rom, Extracted, Output, Release, WorkRoot, CtrTool, RebuildTool;
    public bool DownloadTools, RomOutput;
}
public sealed class ReleaseRow {
    public string path, source, kind, payload, source_sha256, target_sha256, payload_sha256;
    public long target_size;
}
public sealed class ReleaseManifest {
    public string format, title_id, version;
    public ReleaseRow[] files;
}
public sealed class ReleaseData : IDisposable {
    public const string ManifestHash = "ddcdc0cbc9b28b2b0e5cf93fcf373d9ea97ba84814c92b069e3da8c604c007a9";
    string folder;
    Stream stream;
    ZipArchive archive;
    public ReleaseManifest Manifest;
    public ReleaseData(string external) {
        folder = external;
        if (folder == null) {
            stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("DQXI.release.zip");
            if (stream == null) throw new InvalidDataException("Missing embedded patch package");
            archive = new ZipArchive(stream, ZipArchiveMode.Read);
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var e in archive.Entries) {
                BuildSupport.ValidateName(e.FullName);
                if (!seen.Add(e.FullName) || e.Length > NativeCodecs.MaxSize) throw new InvalidDataException("Invalid bundled package entry");
            }
        }
        var raw = Read("manifest.json");
        if (BuildSupport.Hash(raw) != ManifestHash) throw new InvalidDataException("Patch manifest checksum mismatch");
        Manifest = new JavaScriptSerializer().Deserialize<ReleaseManifest>(System.Text.Encoding.UTF8.GetString(raw));
        if (Manifest == null || Manifest.format != "dqxi-translation-deltas-v1" || Manifest.title_id != "0004000000199200" || Manifest.version != "0.6.0" || Manifest.files == null || Manifest.files.Length != 787)
            throw new InvalidDataException("Unsupported patch package");
    }
    public byte[] Read(string name) {
        BuildSupport.ValidateName(name);
        if (folder != null) return BuildSupport.ReadLimited(BuildSupport.Safe(folder, name));
        var e = archive.GetEntry(name);
        if (e == null || e.Length > NativeCodecs.MaxSize) throw new InvalidDataException("Missing/oversized bundled payload");
        using (var s = e.Open()) using (var m = new MemoryStream()) {
            BuildSupport.CopyLimited(s, m, NativeCodecs.MaxSize, CancellationToken.None);
            if (m.Length != e.Length) throw new InvalidDataException("Truncated payload");
            return m.ToArray();
        }
    }
    public void Dispose() { if (archive != null) archive.Dispose(); if (stream != null) stream.Dispose(); }
}
public static class BuildEngine {
    public static void ValidatePayloads(string release, CancellationToken cancel) {
        using (var data = new ReleaseData(release)) foreach (var row in data.Manifest.files) {
            cancel.ThrowIfCancellationRequested();
            if (BuildSupport.Hash(data.Read(row.payload)) != row.payload_sha256) throw new InvalidDataException("Payload checksum mismatch: " + row.payload);
        }
    }
    public static string Build(BuildOptions options, Action<string,int> notify, CancellationToken cancel) {
        if(options == null) throw new ArgumentNullException("options");
        // Keep a read-only lock through extraction and reconstruction, not just rebuilding.
        if(!String.IsNullOrEmpty(options.Rom)) {
            string input=Path.GetFullPath(options.Rom); BuildSupport.NoReparse(input);
            using(var originalLock=new FileStream(input,FileMode.Open,FileAccess.Read,FileShare.Read))
                return BuildLocked(options,notify,cancel);
        }
        return BuildLocked(options,notify,cancel);
    }
    static string BuildLocked(BuildOptions options, Action<string,int> notify, CancellationToken cancel) {
        if (notify == null) notify = delegate {};
        cancel.ThrowIfCancellationRequested();
        if (String.IsNullOrEmpty(options.Output)) throw new ArgumentException("Choose a separate output folder");
        string output = Path.GetFullPath(options.Output);
        BuildSupport.NoReparse(output);
        if (Directory.Exists(output) || File.Exists(output)) throw new IOException("Output already exists; choose a new directory");
        string work = Path.GetFullPath(options.WorkRoot ?? Path.Combine(Path.GetDirectoryName(output), ".dqxi-private"));
        BuildSupport.NoReparse(work);
        if (options.RomOutput && String.IsNullOrEmpty(options.Rom)) throw new ArgumentException("A cartridge ROM is required for .3ds output");
        if (!String.IsNullOrEmpty(options.Rom) && !String.IsNullOrEmpty(options.Extracted)) throw new ArgumentException("Choose exactly one input");
        string extracted;
        notify("Checking the frozen 0.6.0 patch package...",0);
        using (var data = new ReleaseData(options.Release)) {
            if (!String.IsNullOrEmpty(options.Rom)) {
                string rom = Path.GetFullPath(options.Rom);
                BuildSupport.NoReparse(rom);
                string ext = Path.GetExtension(rom).ToLowerInvariant();
                if (!File.Exists(rom) || (ext != ".3ds" && ext != ".cci" && ext != ".cxi" && ext != ".app")) throw new ArgumentException("Select a decrypted .3ds, .cci, .cxi or .app file");
                if (options.RomOutput) RomBuilder.ValidateCartridge(rom);
                Directory.CreateDirectory(work);
                string tool = options.DownloadTools ? BuildSupport.FetchTool(BuildSupport.CtrUrl, BuildSupport.CtrSha, "ctrtool.exe", Path.Combine(work,"ctrtool-"+Guid.NewGuid().ToString("N")),cancel) : options.CtrTool;
                if (String.IsNullOrEmpty(tool) || !File.Exists(tool)) throw new IOException("A verified extractor download or local CTRTool is required");
                extracted = Path.Combine(work,"e-"+Guid.NewGuid().ToString("N").Substring(0,12));
                BuildSupport.CreateExclusiveDirectory(extracted);
                notify("Extracting your game into a separate private folder...",8);
                BuildSupport.RunTool(tool,new string[]{"-p","-n","0","--romfsdir="+Path.Combine(extracted,"romfs"),"--exefsdir="+Path.Combine(extracted,"exefs"),rom},extracted,Path.Combine(extracted,"extractor.log"),cancel);
            } else {
                if (String.IsNullOrEmpty(options.Extracted)) throw new ArgumentException("An input is required");
                extracted = Path.GetFullPath(options.Extracted);
                BuildSupport.NoReparse(extracted);
                if (!Directory.Exists(extracted)) throw new IOException("Extracted input folder does not exist");
            }
            if (BuildSupport.IsWithin(extracted, output) || BuildSupport.IsWithin(output, extracted)) throw new IOException("Input and output folders must be separate");
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for (int i=0;i<data.Manifest.files.Length;i++) {
                cancel.ThrowIfCancellationRequested();
                var row = data.Manifest.files[i];
                string dest = BuildSupport.Safe(output,row.path);
                if (!seen.Add(dest)) throw new InvalidDataException("Duplicate output path");
                if (row.target_size < 0 || row.target_size > NativeCodecs.MaxSize) throw new InvalidDataException("Invalid target size");
                var source = BuildSupport.ReadLimited(BuildSupport.Safe(extracted,row.source));
                if (row.kind == "delta") source = NativeCodecs.Normalize(source);
                else if (row.kind != "ips" || row.path != "exefs/code.ips" || row.source != "exefs/code.bin") throw new InvalidDataException("Unsupported patch type");
                if (BuildSupport.Hash(source) != row.source_sha256) throw new InvalidDataException("Game version/input mismatch: "+row.source);
                if (BuildSupport.Hash(data.Read(row.payload)) != row.payload_sha256) throw new InvalidDataException("Damaged payload: "+row.payload);
                if ((i+1)%10==0 || i+1==data.Manifest.files.Length) notify("Checking game version: "+(i+1)+"/787",15+30*(i+1)/787);
            }
            cancel.ThrowIfCancellationRequested();
            BuildSupport.CreateExclusiveDirectory(output);
            for (int i=0;i<data.Manifest.files.Length;i++) {
                cancel.ThrowIfCancellationRequested();
                var row = data.Manifest.files[i];
                byte[] patch = data.Read(row.payload);
                if (BuildSupport.Hash(patch) != row.payload_sha256) throw new InvalidDataException("Payload changed after preflight");
                byte[] result;
                if (row.kind == "delta") {
                    var source = NativeCodecs.Normalize(BuildSupport.ReadLimited(BuildSupport.Safe(extracted,row.source)));
                    if (BuildSupport.Hash(source) != row.source_sha256) throw new InvalidDataException("Source changed after preflight");
                    result = NativeCodecs.ApplyDelta(source,patch);
                } else {
                    if (BuildSupport.Hash(BuildSupport.ReadLimited(BuildSupport.Safe(extracted,row.source))) != row.source_sha256) throw new InvalidDataException("Executable source changed after preflight");
                    NativeCodecs.ApplyIps(BuildSupport.ReadLimited(BuildSupport.Safe(extracted,row.source)),patch);
                    result = patch;
                }
                if (result.LongLength != row.target_size || BuildSupport.Hash(result) != row.target_sha256) throw new InvalidDataException("Output verification failed: "+row.path);
                string dest = BuildSupport.Safe(output,row.path);
                Directory.CreateDirectory(Path.GetDirectoryName(dest));
                BuildSupport.WriteNew(dest,result);
                if (BuildSupport.HashFile(dest) != row.target_sha256 || new FileInfo(dest).Length != row.target_size) throw new IOException("Output readback failed");
                if ((i+1)%10==0 || i+1==787) notify("Building and verifying: "+(i+1)+"/787",45+(options.RomOutput?20:55)*(i+1)/787);
            }
        }
        string completed = options.RomOutput ? RomBuilder.Build(Path.GetFullPath(options.Rom),extracted,output,notify,cancel,options.RebuildTool) : output;
        notify("Complete. Separate verified output created; original ROM and saves unchanged.",100);
        return completed;
    }
}
