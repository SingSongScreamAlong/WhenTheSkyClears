using UnrealBuildTool;
public class WTSCSurvival : ModuleRules
{
    public WTSCSurvival(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "Json", "JsonUtilities", "ImageWrapper" });
    }
}
