using System;
using System.IO;
using System.Collections.Generic;
using System.Threading;
using System.Windows.Forms;
using System.Web.Script.Serialization;

public static class Program {
    [STAThread] public static int Main(string[] args) {
        try {
            // Application-local path handling only; no Windows/registry policy changes.
            AppContext.SetSwitch("Switch.System.IO.UseLegacyPathHandling",false);
            AppContext.SetSwitch("Switch.System.IO.BlockLongPaths",false);
            Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false);
            if(args.Length==0) { Application.Run(new BuilderForm()); return 0; }
            if(args.Length==1 && args[0]=="--codec-tests") { if(CodecTests.Run()!=0) return 1; SupportTests.Run(); return 0; }
            var options=new Dictionary<string,string>(StringComparer.Ordinal);
            bool self=false;
            for(int i=0;i<args.Length;i++) {
                string key=args[i];
                if(key=="--self-test") { self=true; continue; }
                if(key=="--download-tools") { options.Add(key,"true"); continue; }
                if(key!="--rom" && key!="--extracted" && key!="--output" && key!="--report" && key!="--release" && key!="--ctrtool" && key!="--rebuild-tool" && key!="--output-format" && key!="--work-root") throw new ArgumentException("Unknown option: "+key);
                if(++i==args.Length) throw new ArgumentException("Missing option value: "+key);
                options.Add(key,args[i]);
            }
            Func<string,string> get=delegate(string key) { string v; return options.TryGetValue(key,out v)?v:null; };
            bool gui=false;
            if(self) {
                if(String.IsNullOrEmpty(get("--report"))) throw new ArgumentException("Self-test requires a fresh --report path");
                using(var form=new BuilderForm()) { form.CreateControl(); var handle=form.Handle; Application.DoEvents(); gui=handle!=IntPtr.Zero; }
                if(!gui) throw new Exception("GUI construction failed");
                if(CodecTests.Run()!=0) throw new Exception("Synthetic codec checks failed");
                SupportTests.Run();
                BuildEngine.ValidatePayloads(get("--release"),CancellationToken.None);
            }
            string result=null;
            if(get("--rom")!=null || get("--extracted")!=null) {
                string mode=get("--output-format")??"mod";
                if(mode!="rom" && mode!="mod") throw new ArgumentException("Unknown output format");
                result=BuildEngine.Build(new BuildOptions {Rom=get("--rom"),Extracted=get("--extracted"),Output=get("--output"),Release=get("--release"),WorkRoot=get("--work-root"),CtrTool=get("--ctrtool"),RebuildTool=get("--rebuild-tool"),DownloadTools=options.ContainsKey("--download-tools"),RomOutput=mode=="rom"},delegate(string message,int p) { Console.WriteLine(p+"% "+message); },CancellationToken.None);
            } else if(!self) throw new ArgumentException("Choose --rom or --extracted");
            if(get("--report")!=null) {
                var report=new { version="0.5.2",engine="Windows .NET Framework; no Python",gui_created=gui,payloads=733,completed_output=result,utc=DateTime.UtcNow.ToString("o"),scope="Bounded builder checks only; not gameplay/whole-game certification" };
                BuildSupport.WriteNew(Path.GetFullPath(get("--report")),System.Text.Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(report)));
            }
            return 0;
        } catch(Exception e) { Console.Error.WriteLine(e.ToString()); if(args.Length==0) MessageBox.Show(e.Message,"Builder stopped safely",MessageBoxButtons.OK,MessageBoxIcon.Error); return 1; }
    }
}
