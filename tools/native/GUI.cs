using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

// Windows-native UI only. The engine owns extraction, verification and cleanup.
// No input ROM, save, existing mod or emulator setting is written by this form.
public sealed class BuilderForm : Form
{
    private readonly TextBox rom = new TextBox();
    private readonly TextBox output = new TextBox();
    private readonly TextBox ctrtool = new TextBox();
    private readonly RadioButton romOutput = new RadioButton();
    private readonly RadioButton modOutput = new RadioButton();
    private readonly CheckBox download = new CheckBox();
    private readonly Label status = new Label();
    private readonly ProgressBar progress = new ProgressBar();
    private readonly Button start = new Button();
    private readonly Button cancel = new Button();
    private readonly Button open = new Button();
    private readonly List<Control> inputControls = new List<Control>();
    private CancellationTokenSource cancellation;
    private bool busy;
    private bool closeWhenFinished;
    private string built;
    private int generation;

    public BuilderForm()
    {
        Text = "DQXI 3DS — English Translation Builder 0.5.3 (experimental)";
        Font = new Font("Segoe UI", 9F);
        AutoScaleMode = AutoScaleMode.Dpi;
        ClientSize = new Size(830, 710);
        MinimumSize = new Size(760, 660);
        StartPosition = FormStartPosition.CenterScreen;

        Panel scroll = new Panel { Dock = DockStyle.Fill, AutoScroll = true, Padding = new Padding(24) };
        TableLayoutPanel layout = new TableLayoutPanel
        {
            Dock = DockStyle.Top, AutoSize = true, ColumnCount = 1,
            RowCount = 0, GrowStyle = TableLayoutPanelGrowStyle.AddRows
        };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
        scroll.Controls.Add(layout);
        Controls.Add(scroll);

        AddRow(layout, new Label
        {
            Text = "Build your English translation", AutoSize = true,
            Font = new Font("Segoe UI", 20F, FontStyle.Bold), Margin = new Padding(0, 0, 0, 6)
        });
        AddText(layout, "DRAGON QUEST XI • Japanese Nintendo 3DS edition", 12);
        AddText(layout, "Experimental, incomplete translation. Heliodor fix passed a limited emulator test; NOT hardware tested.\r\nYour original ROM and saves are never modified. No automatic installation.", 16);

        AddPath(layout, "1. Your decrypted Japanese game (.3ds, .cci, .cxi, .app)", rom, PickRom);
        output.Text = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "DQXI Translation Builds");
        AddPath(layout, "2. Output parent folder (each build creates a unique new subfolder)", output, PickOutput);

        FlowLayoutPanel modes = new FlowLayoutPanel { AutoSize = true, Dock = DockStyle.Fill, Margin = new Padding(0, 10, 0, 6) };
        romOutput.Text = "Translated .3ds file";
        romOutput.AutoSize = true;
        romOutput.Checked = true;
        modOutput.Text = "Mod folders (romfs + exefs)";
        modOutput.AutoSize = true;
        modes.Controls.Add(romOutput);
        modes.Controls.Add(modOutput);
        inputControls.Add(romOutput);
        inputControls.Add(modOutput);
        AddRow(layout, modes);

        download.Text = "Download verified tools from GitHub (ROM output also needs 3dstool)";
        download.AutoSize = true;
        download.Checked = true;
        download.Margin = new Padding(0, 4, 0, 8);
        inputControls.Add(download);
        AddRow(layout, download);
        AddPath(layout, "Optional: local ctrtool.exe instead of downloading the extractor", ctrtool, PickCtrTool);
        AddText(layout, "A local extractor does not supply the ROM rebuilder; .3ds output may still download verified 3dstool.", 8);

        status.Text = "Ready. Select your game to begin.";
        status.AutoSize = true;
        status.MaximumSize = new Size(710, 0);
        status.Margin = new Padding(0, 12, 0, 8);
        AddRow(layout, status);
        progress.Dock = DockStyle.Fill;
        progress.Height = 22;
        progress.Maximum = 100;
        AddRow(layout, progress);

        FlowLayoutPanel buttons = new FlowLayoutPanel { AutoSize = true, Dock = DockStyle.Fill, Margin = new Padding(0, 16, 0, 12) };
        start.Text = "Build translation";
        cancel.Text = "Cancel";
        open.Text = "Open output folder";
        Button help = new Button { Text = "Installation help", AutoSize = true };
        start.AutoSize = cancel.AutoSize = open.AutoSize = true;
        cancel.Enabled = open.Enabled = false;
        start.Click += StartBuild;
        cancel.Click += delegate { RequestCancel(); };
        open.Click += delegate { OpenOutput(); };
        help.Click += delegate { ShowHelp(); };
        inputControls.Add(start);
        buttons.Controls.AddRange(new Control[] { start, cancel, open, help });
        AddRow(layout, buttons);
        AddText(layout, "Supply your own decrypted game. ROM output requires a .3ds/.cci cartridge image.\r\nAllow at least 20 GB free for rebuilding. CIA files are not supported.\r\nDo not distribute generated ROMs, mod folders or .dqxi-private game-derived data.", 0);
        FormClosing += ClosingRequested;
    }

    private static void AddRow(TableLayoutPanel layout, Control control)
    {
        int row = layout.RowCount++;
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        layout.Controls.Add(control, 0, row);
    }

    private static void AddText(TableLayoutPanel layout, string text, int bottom)
    {
        AddRow(layout, new Label
        {
            Text = text, AutoSize = true, MaximumSize = new Size(710, 0),
            Margin = new Padding(0, 0, 0, bottom)
        });
    }

    private void AddPath(TableLayoutPanel layout, string caption, TextBox field, EventHandler browse)
    {
        AddText(layout, caption, 5);
        TableLayoutPanel row = new TableLayoutPanel { ColumnCount = 2, RowCount = 1, Dock = DockStyle.Fill, AutoSize = true, Margin = new Padding(0, 0, 0, 12) };
        row.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
        row.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
        field.Dock = DockStyle.Fill;
        field.Margin = new Padding(0, 3, 8, 3);
        Button button = new Button { Text = "Browse…", AutoSize = true };
        button.Click += browse;
        row.Controls.Add(field, 0, 0);
        row.Controls.Add(button, 1, 0);
        inputControls.Add(field);
        inputControls.Add(button);
        AddRow(layout, row);
    }

    private void PickRom(object sender, EventArgs args)
    {
        using (OpenFileDialog dialog = new OpenFileDialog())
        {
            dialog.Title = "Select your decrypted Japanese game";
            dialog.Filter = "Decrypted 3DS game (*.3ds;*.cci;*.cxi;*.app)|*.3ds;*.cci;*.cxi;*.app";
            dialog.CheckFileExists = true;
            if (dialog.ShowDialog(this) == DialogResult.OK) rom.Text = dialog.FileName;
        }
    }

    private void PickOutput(object sender, EventArgs args)
    {
        using (FolderBrowserDialog dialog = new FolderBrowserDialog())
        {
            dialog.Description = "Choose the parent folder for new translation builds";
            if (Directory.Exists(output.Text)) dialog.SelectedPath = output.Text;
            if (dialog.ShowDialog(this) == DialogResult.OK) output.Text = dialog.SelectedPath;
        }
    }

    private void PickCtrTool(object sender, EventArgs args)
    {
        using (OpenFileDialog dialog = new OpenFileDialog())
        {
            dialog.Title = "Select local ctrtool.exe";
            dialog.Filter = "Executable (*.exe)|*.exe";
            dialog.CheckFileExists = true;
            if (dialog.ShowDialog(this) == DialogResult.OK)
            {
                ctrtool.Text = dialog.FileName;
                download.Checked = false;
            }
        }
    }

    private async void StartBuild(object sender, EventArgs args)
    {
        if (busy) return;
        BuildOptions options;
        try
        {
            string input = Path.GetFullPath(rom.Text.Trim());
            string extension = Path.GetExtension(input).ToLowerInvariant();
            if (!File.Exists(input) || (extension != ".3ds" && extension != ".cci" && extension != ".cxi" && extension != ".app"))
                throw new ArgumentException("Choose your decrypted Japanese .3ds, .cci, .cxi or .app game file.");
            if (String.IsNullOrWhiteSpace(output.Text)) throw new ArgumentException("Choose an output parent folder.");
            string parent = Path.GetFullPath(output.Text.Trim());
            if (File.Exists(parent)) throw new ArgumentException("The output parent must be a folder, not a file.");
            string localTool = String.IsNullOrWhiteSpace(ctrtool.Text) ? null : Path.GetFullPath(ctrtool.Text.Trim());
            if (!download.Checked && (localTool == null || !File.Exists(localTool) || !String.Equals(Path.GetExtension(localTool), ".exe", StringComparison.OrdinalIgnoreCase)))
                throw new ArgumentException("Select a local ctrtool.exe, or enable the verified download.");
            if (romOutput.Checked && extension != ".3ds" && extension != ".cci")
                throw new ArgumentException("Translated .3ds output requires a .3ds/.cci cartridge image. Choose mod folders for .cxi/.app input.");
            if (romOutput.Checked && MessageBox.Show(this,
                "Create a new translated .3ds file? The builder may download verified 3dstool. Allow at least 20 GB free.\r\n\r\nYour original ROM stays unchanged. Heliodor fix passed a limited emulator test; NOT hardware tested. This does not confirm whole-game stability.",
                "Build a translated .3ds?", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;

            // Unique destination avoids reuse/overwrite; the engine must also fail closed.
            string destination = Path.Combine(parent, "English-mod-" + DateTime.Now.ToString("yyyyMMdd-HHmmss-fff") + "-" + Guid.NewGuid().ToString("N").Substring(0, 8));
            options = new BuildOptions
            {
                Rom = input, Extracted = null, Output = destination, Release = null,
                WorkRoot = Path.Combine(parent, ".dqxi-private"),
                CtrTool = download.Checked ? null : localTool, RebuildTool = null,
                DownloadTools = download.Checked, RomOutput = romOutput.Checked
            };
        }
        catch (Exception error)
        {
            MessageBox.Show(this, error.Message, "Check build options", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        built = null;
        busy = true;
        closeWhenFinished = false;
        int thisGeneration = ++generation;
        cancellation = new CancellationTokenSource();
        CancellationToken token = cancellation.Token;
        SetBusy(true);
        progress.Value = 0;
        status.Text = "Starting verified build…";
        try
        {
            string result = await Task.Run(delegate
            {
                return BuildEngine.Build(options, delegate(string text, int value)
                {
                    PostProgress(thisGeneration, text, value);
                }, token);
            });
            if (String.IsNullOrWhiteSpace(result) || (!File.Exists(result) && !Directory.Exists(result)))
                throw new IOException("The engine did not return an existing verified output.");
            built = result;
            progress.Value = 100;
            status.Text = "Build verification completed. Heliodor fix passed a limited emulator test; NOT hardware tested. See Installation help.";
        }
        catch (OperationCanceledException)
        {
            status.Text = "Cancelled. Do not install partial output. Your original ROM and saves are unchanged.";
        }
        catch (Exception error)
        {
            status.Text = "Build failed. Do not install partial output. Your original ROM and saves are unchanged.";
            MessageBox.Show(this, error.Message + "\r\n\r\nDo not install partial output.", "Unable to build translation", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        finally
        {
            busy = false;
            ++generation; // Ignore progress already queued from the completed worker.
            cancellation.Dispose();
            cancellation = null;
            SetBusy(false);
            if (closeWhenFinished) Close();
        }
    }

    private void PostProgress(int buildGeneration, string text, int value)
    {
        if (IsDisposed || Disposing || !IsHandleCreated) return;
        try
        {
            BeginInvoke((Action)delegate
            {
                if (IsDisposed || !busy || generation != buildGeneration) return;
                progress.Value = Math.Max(0, Math.Min(100, value));
                if (cancellation != null && !cancellation.IsCancellationRequested)
                    status.Text = text ?? "Building…";
            });
        }
        catch (InvalidOperationException) { /* Form lifetime ended; never touch controls off-thread. */ }
    }

    private void SetBusy(bool value)
    {
        foreach (Control control in inputControls) control.Enabled = !value;
        cancel.Enabled = value;
        open.Enabled = !value && built != null;
        UseWaitCursor = value;
    }

    private void RequestCancel()
    {
        if (!busy || cancellation == null || cancellation.IsCancellationRequested) return;
        cancellation.Cancel();
        cancel.Enabled = false;
        status.Text = "Cancelling safely; waiting for the current operation…";
    }

    private void ClosingRequested(object sender, FormClosingEventArgs args)
    {
        if (!busy) return;
        args.Cancel = true;
        if (closeWhenFinished) return;
        if (MessageBox.Show(this, "Cancel the build and close after the current operation stops safely?\r\nDo not install any partial output.",
            "Build in progress", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
        {
            closeWhenFinished = true;
            RequestCancel();
        }
    }

    private void OpenOutput()
    {
        if (busy || built == null) return;
        try
        {
            string folder = File.Exists(built) ? Path.GetDirectoryName(built) : built;
            if (!Directory.Exists(folder)) throw new DirectoryNotFoundException("The output folder is no longer available.");
            Process.Start(new ProcessStartInfo(folder) { UseShellExecute = true });
        }
        catch (Exception error)
        {
            MessageBox.Show(this, error.Message, "Unable to open output", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
    }

    private void ShowHelp()
    {
        MessageBox.Show(this,
            "This is an experimental, incomplete translation. Successful file verification is not in-game validation. Heliodor fix passed a limited emulator test; NOT hardware tested. A successful bridge test does not prove all scenes or hardware are safe.\r\n\r\n" +
            "For .3ds output: use the new ROM in a compatible emulator or your appropriate custom-firmware workflow. No mod folders need to be installed for its embedded patch. Older LayeredFS mods or external IPS patches can override embedded data; do not mix test sets.\r\n\r\n" +
            "For mod folders:\r\n1. Close the game and back up existing mods and saves.\r\n2. Open the game's Mods Location in your emulator.\r\n3. Copy the generated romfs and exefs folders into:\r\nload/mods/0004000000199200/\r\n4. Restart the emulator and load a normal save.\r\n\r\n" +
            "The builder never installs mods, changes emulator settings or edits saves. Do not share generated ROMs, mod folders or .dqxi-private: they contain game-derived data. Share only the public builder and patches.",
            "Installation help — experimental", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
}
