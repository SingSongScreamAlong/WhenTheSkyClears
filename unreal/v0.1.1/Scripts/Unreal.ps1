param(
    [ValidateSet('Stage','BuildEditor','BuildGame','AuthorContent','Play','Replay','Package')][string]$Action='Stage',
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [switch]$ResourcesReleased
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$projectFile=Join-Path $projectRoot 'WTSC_Survival.uproject'
if(-not(Test-Path -LiteralPath $projectFile)){throw 'WTSC project identity missing'}
$evidenceRoot=Join-Path $projectRoot 'Evidence'
New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
if($Action -eq 'Stage'){
    & python (Join-Path $PSScriptRoot 'stage_sources.py'); if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
    & python (Join-Path $PSScriptRoot 'bake_static_gltf.py'); exit $LASTEXITCODE
}
if($Action -in @('AuthorContent','Play','Replay','Package') -and -not $ResourcesReleased){throw 'Wait for root to coordinate editor/GPU availability; pass -ResourcesReleased only after release.'}
$buildTool=Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$editorCmd=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
switch($Action){
    'BuildEditor' { & $buildTool WTSC_SurvivalEditor Win64 Development $projectFile -WaitMutex -MaxParallelActions=2 -NoHotReloadFromIDE; exit $LASTEXITCODE }
    'BuildGame' { & $buildTool WTSC_Survival Win64 Development $projectFile -WaitMutex -MaxParallelActions=2 -NoHotReloadFromIDE; exit $LASTEXITCODE }
    'AuthorContent' { & $editorCmd $projectFile -run=pythonscript "-script=$PSScriptRoot\author_content.py" -unattended -NullRHI -NoAudio -NoSplash -NoSourceControl "-abslog=$evidenceRoot\AuthorContent.log"; exit $LASTEXITCODE }
    'Play' { & $editor $projectFile /Game/Maps/ShelterDawn -game -windowed -ResX=1600 -ResY=900 -NoSplash -NoAudio "-abslog=$evidenceRoot\PlayablePreview.log"; exit $LASTEXITCODE }
    'Replay' { $runArgs=@($projectFile,'/Game/Maps/ShelterDawn','-game','-windowed','-ResX=1600','-ResY=900','-NoSplash','-NoAudio','-unattended','-WTSCReplay','-WTSCRecord','-WTSCExitAfterReplay',"-abslog=$evidenceRoot\GameplayReplay.log"); $run=Start-Process -FilePath $editor -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait; exit $run.ExitCode }
    'Package' { & (Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat') BuildCookRun "-project=$projectFile" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive "-archivedirectory=$projectRoot\Saved\Packaged" -utf8output -unattended; exit $LASTEXITCODE }
}
