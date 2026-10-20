$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$packageRoot=Join-Path $projectRoot 'Saved\Packaged\Windows'
$game=Join-Path $packageRoot 'WTSC_Survival\Binaries\Win64\WTSC_Survival.exe'
if(-not(Test-Path -LiteralPath $game -PathType Leaf)){throw 'Packaged WTSC executable missing'}
$log=Join-Path $projectRoot 'Evidence\PackagedGameplay.log'
$argsWTSC=@('-windowed','-ResX=1600','-ResY=900','-NoSplash','-NoAudio','-unattended','-WTSCReplay','-WTSCRecord','-WTSCExitAfterReplay',"-abslog=$log")
$run=Start-Process -FilePath $game -ArgumentList $argsWTSC -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -Wait
if($run.ExitCode -ne 0){throw "Packaged WTSC replay exited $($run.ExitCode); inspect PackagedGameplay.log"}
$receipt=Join-Path $packageRoot 'WTSC_Survival\Evidence\GameplayReplay.json'
if(-not(Test-Path -LiteralPath $receipt)){throw 'Packaged game returned without its own acceptance receipt'}
$result=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
if(-not $result.passed -or $result.events.Count -ne 8){throw 'Packaged replay did not pass all eight acceptance events'}
Copy-Item -LiteralPath $receipt -Destination (Join-Path $projectRoot 'Evidence\PackagedGameplayReplay.json')
Write-Output "PACKAGED ACCEPTANCE PASS: $($result.game_seconds) seconds, $($result.events.Count) events, $($result.recorded_frames) frames"
