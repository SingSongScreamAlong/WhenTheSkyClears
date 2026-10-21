using UnrealBuildTool;
public class WTSC_SurvivalTarget : TargetRules
{
    public WTSC_SurvivalTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("WTSCSurvival");
    }
}
