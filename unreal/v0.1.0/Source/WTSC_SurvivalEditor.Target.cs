using UnrealBuildTool;
public class WTSC_SurvivalEditorTarget : TargetRules
{
    public WTSC_SurvivalEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("WTSCSurvival");
    }
}
