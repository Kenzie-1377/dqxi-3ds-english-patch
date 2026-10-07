$ErrorActionPreference='Stop'
$repoDir=$PSScriptRoot
$nativeDir=Join-Path $repoDir 'tools/native'
$releaseDir=Join-Path $repoDir 'release'
if((Get-FileHash -LiteralPath (Join-Path $releaseDir 'manifest.json')).Hash.ToLowerInvariant()-ne'f1265829a7c2e19e43723b1775b953aa92775f95adcaec3b7bb582ccd384adfa'){throw 'Frozen 0.5.3 manifest pin mismatch'}
if(@(Get-ChildItem -LiteralPath $releaseDir -File).Count-ne734){throw 'Unexpected patch package files'}
$compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
if(!(Test-Path -LiteralPath $compiler)){throw 'Windows .NET Framework 4.8 x64 compiler required'}
$buildDir=Join-Path $repoDir ('build/native-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $buildDir -ErrorAction Stop|Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$bundle=Join-Path $buildDir 'release.zip'
[IO.Compression.ZipFile]::CreateFromDirectory($releaseDir,$bundle,[IO.Compression.CompressionLevel]::NoCompression,$false)
$dist=Join-Path $repoDir 'dist'
New-Item -ItemType Directory -Path $dist -Force|Out-Null
$output=Join-Path $dist 'DQXI-English-Translation-Builder.exe'
if(Test-Path -LiteralPath $output){throw 'Existing executable retained; move it aside before compiling another build'}
$arguments=@('/nologo','/target:winexe','/platform:x64','/optimize+','/checked-','/langversion:5',"/out:$output",'/reference:System.dll','/reference:System.Core.dll','/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll','/reference:System.Web.Extensions.dll','/reference:System.IO.Compression.dll','/reference:System.IO.Compression.FileSystem.dll',"/resource:$bundle,DQXI.release.zip",("/win32manifest:"+(Join-Path $nativeDir 'app.manifest')))
foreach($source in @('Program.cs','AssemblyInfo.cs','GUI.cs','BuildEngine.cs','BuildSupport.cs','Codecs.cs','CodecTests.cs','SupportTests.cs','RomBuilder.cs')){$arguments+=(Join-Path $nativeDir $source)}
& $compiler @arguments
if($LASTEXITCODE-ne0){throw 'Native builder compilation failed'}
$testReport=Join-Path $buildDir 'self-test.json'
$process=Start-Process -FilePath $output -ArgumentList @('--self-test','--report',('"'+$testReport+'"')) -WindowStyle Hidden -PassThru -Wait
if($process.ExitCode-ne0){throw 'Compiled builder self-test failed; do not distribute this executable'}
Write-Output "Native builder compiled and synthetic/GUI/payload self-test passed: $output"
Write-Output 'Source builds are not the separately verified release asset; matching-original builds and independent readbacks remain necessary.'
