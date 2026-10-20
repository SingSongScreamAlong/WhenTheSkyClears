param([switch]$NoCapture)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$packageRoot=Join-Path $projectRoot 'Saved\Packaged\Windows'
$game=Join-Path $packageRoot 'WTSC_Survival\Binaries\Win64\WTSC_Survival.exe'
if(-not(Test-Path -LiteralPath $game -PathType Leaf)){throw 'Packaged WTSC executable missing'}
$testEvidence=Join-Path $projectRoot $(if($NoCapture){'Evidence\Regression'}else{'Evidence'})
New-Item -ItemType Directory -Path $testEvidence -Force | Out-Null
$log=Join-Path $testEvidence 'PackagedGameplay.log'
$argsWTSC=@('-windowed','-ResX=1600','-ResY=900','-NoSplash','-NoAudio','-unattended','-WTSCReplay','-WTSCExitAfterReplay',"-abslog=$log")
if($NoCapture){$argsWTSC+="-WTSCReceipt=$(Join-Path $testEvidence 'GameplayReplay.json')"}else{$argsWTSC+='-WTSCRecord'}
$run=Start-Process -FilePath $game -ArgumentList $argsWTSC -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -Wait
if($run.ExitCode -ne 0){throw "Packaged WTSC replay exited $($run.ExitCode); inspect PackagedGameplay.log"}
$receipt=if($NoCapture){Join-Path $testEvidence 'GameplayReplay.json'}else{Join-Path $packageRoot 'WTSC_Survival\Evidence\GameplayReplay.json'}
if(-not(Test-Path -LiteralPath $receipt)){throw 'Packaged game returned without its own acceptance receipt'}
$result=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
if(-not $result.passed -or $result.events.Count -ne 11){throw 'Packaged replay did not pass all eleven acceptance events'}
Copy-Item -LiteralPath $receipt -Destination (Join-Path $testEvidence 'PackagedGameplayReplay.json')
Write-Output "PACKAGED ACCEPTANCE PASS: $($result.game_seconds) seconds, $($result.events.Count) events, $($result.recorded_frames) frames"
