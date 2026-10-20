param([switch]$Packaged,[switch]$Record,[switch]$Overview,[string]$Label='ArtReview01')
$ErrorActionPreference='Stop'
if($Label -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple evidence folder label'}
$projectRoot=Split-Path $PSScriptRoot -Parent
$evidence=Join-Path $projectRoot "Evidence\$Label"
if(Test-Path -LiteralPath (Join-Path $evidence 'GameplayReplay.json')){throw 'Evidence label already exists; preserve it and choose a fresh label'}
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if($Packaged){
    $game=Join-Path $projectRoot 'Saved\Packaged\Windows\WTSC_Survival\Binaries\Win64\WTSC_Survival.exe'
    $sourceEvidence=Join-Path $projectRoot 'Saved\Packaged\Windows\WTSC_Survival\Evidence'
    $runArgs=@()
}else{
    $game='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
    $sourceEvidence=Join-Path $projectRoot 'Evidence'
    $runArgs=@((Join-Path $projectRoot 'WTSC_Survival.uproject'),'/Game/Maps/ShelterDawn','-game')
}
$runArgs+=@('-windowed','-ResX=1600','-ResY=900','-NoSplash','-NoAudio','-unattended','-WTSCExitAfterReplay',"-WTSCReceipt=$evidence\GameplayReplay.json","-abslog=$evidence\ArtStudy.log")
$runArgs+= $(if($Overview){'-WTSCArtOverview'}else{'-WTSCArtStudy'})
if($Record){$runArgs+='-WTSCRecord'}
$run=Start-Process -FilePath $game -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
if($run.ExitCode -ne 0){throw "Art study returned $($run.ExitCode); inspect $evidence\ArtStudy.log"}
$still=$(if($Overview){'ArtOverview.png'}else{'RoomStudy.png'})
Copy-Item -LiteralPath (Join-Path $sourceEvidence $still) -Destination (Join-Path $evidence $still)
if($Record){Copy-Item -LiteralPath (Join-Path $sourceEvidence 'Frames') -Destination (Join-Path $evidence 'Frames') -Recurse}
$result=Get-Content -LiteralPath (Join-Path $evidence 'GameplayReplay.json') -Raw | ConvertFrom-Json
if(-not $result.art_study){throw 'Returned receipt is not an art-study run'}
Write-Output "ACTUAL ENGINE ART STUDY COMPLETE: $($result.game_seconds) seconds; $($result.recorded_frames) real video frames; $Label. This is not an art-approval result."
