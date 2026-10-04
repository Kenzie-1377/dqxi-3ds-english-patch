using System;
using System.IO;
using System.Threading;
public static class SupportTests {
    static int count;
    static void Reject(Action action) { count++; try { action(); } catch(InvalidDataException) { return; } catch(ArgumentException) { return; } throw new Exception("Unsafe path accepted"); }
    static void Assert(bool value) { count++; if(!value) throw new Exception("Support check failed"); }
    public static void Run() {
        count=0;
        foreach(string name in new string[]{"","/absolute","../x","a/../x","a//x","a\\x","C:/x","a:stream","CON","com1.bin","LPT9","x.","x ","a/./x","a/*"}) {
            string captured=name; Reject(delegate {BuildSupport.ValidateName(captured);});
        }
        string root=Path.Combine(Path.GetTempPath(),"dqxi-native-tests-"+Guid.NewGuid().ToString("N"));
        Assert(BuildSupport.IsWithin(root,Path.Combine(root,"child")));
        Assert(!BuildSupport.IsWithin(root,root+"-other"));
        Assert(BuildSupport.Safe(root,"romfs/a.pack")==Path.Combine(root,"romfs","a.pack"));
        Assert(BuildSupport.Quote("")=="\"\"");
        Assert(BuildSupport.Quote("a b")=="\"a b\"");
        Assert(BuildSupport.Quote("a\\")=="\"a\\\\\"");
        var stop=new CancellationTokenSource(); stop.Cancel();
        bool cancelled=false;
        try {BuildEngine.Build(new BuildOptions{Output=root,Extracted=root+"-input"},null,stop.Token);} catch(OperationCanceledException) {cancelled=true;}
        Assert(cancelled && !Directory.Exists(root));
        Console.WriteLine("Support checks PASS: "+count);
    }
}
