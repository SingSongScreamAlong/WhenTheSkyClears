#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/HUD.h"
#include "GameFramework/SaveGame.h"
#include "WTSC.generated.h"

class UStaticMesh;
class UStaticMeshComponent;
class UMaterialInterface;
class USceneComponent;
class UCameraComponent;
class FJsonValue;

USTRUCT(BlueprintType)
struct FWTSCBag
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Food = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Water = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Medicine = 0;
    int32 Count() const { return Food + Water + Medicine; }
    void Clear() { Food = Water = Medicine = 0; }
};

UCLASS()
class UWTSCCheckpoint : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 Version = 1;
    UPROPERTY(SaveGame) FWTSCBag Carry;
    UPROPERTY(SaveGame) FWTSCBag Storage;
    UPROPERTY(SaveGame) float Health = 100;
    UPROPERTY(SaveGame) float FoodNeed = 78;
    UPROPERTY(SaveGame) float WaterNeed = 72;
    UPROPERTY(SaveGame) FVector Position = FVector::ZeroVector;
    UPROPERTY(SaveGame) bool CacheAvailable = true;
    UPROPERTY(SaveGame) bool Completed = false;
};

UCLASS()
class AWTSCStage : public AActor
{
    GENERATED_BODY()
public:
    AWTSCStage();
    virtual void OnConstruction(const FTransform& Transform) override;
    UFUNCTION(CallInEditor, BlueprintCallable) void RebuildStage();
    UPROPERTY(EditAnywhere, Category="WTSC|Assets") TMap<FName, TObjectPtr<UStaticMesh>> PropMeshes;
    UPROPERTY(EditAnywhere, Category="WTSC|Assets") TMap<FName, TObjectPtr<UMaterialInterface>> Materials;
    UPROPERTY(EditAnywhere, Category="WTSC|Layout") float ShelterHalfWidth = 980;
    UPROPERTY(EditAnywhere, Category="WTSC|Layout") float CacheX = 3000;
private:
    UPROPERTY() TObjectPtr<USceneComponent> StageRoot;
    UStaticMeshComponent* Shape(const FString& Name, const FString& Mesh, FVector P, FVector Size, FName Material, bool Collision=false, FRotator Rotation=FRotator::ZeroRotator);
    void Prop(FName Key, FVector Ground, float Width, FRotator Rotation=FRotator::ZeroRotator);
    void WarmLight(FVector P, float Intensity, float Radius);
};

UCLASS()
class AWTSCChild : public ACharacter
{
    GENERATED_BODY()
public:
    AWTSCChild();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    void MoveSide(float Value);
    void CreatePuppet(bool Girl=false);
    UPROPERTY(EditAnywhere, Category="WTSC|Character") bool Companion = false;
private:
    UPROPERTY() TObjectPtr<USceneComponent> Puppet;
    UPROPERTY() TObjectPtr<USceneComponent> LeftLeg;
    UPROPERTY() TObjectPtr<USceneComponent> RightLeg;
    UPROPERTY() TObjectPtr<USceneComponent> LeftArm;
    UPROPERTY() TObjectPtr<USceneComponent> RightArm;
    float Gait = 0;
    float Facing = 1;
    void Card(const FString& Name, USceneComponent* Parent, FVector Position, FVector2D Size, const FString& Material);
};

UCLASS()
class AWTSCController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void SetupInputComponent() override;
    void SearchPressed();
    void SearchReleased();
    void RestartDay();
    void SaveCheckpoint();
    void LoadCheckpoint();
    void Eat();
    void Drink();
    void Heal();
    void PauseStudy();
};

UCLASS()
class AWTSCGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AWTSCGameMode();
    virtual void StartPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    void SetSearching(bool Held);
    void ResetDay();
    void SaveDay();
    void LoadDay();
    void UseSupply(int32 Kind);
    FString Prompt() const;
    FString Objective() const;
    bool AtHome() const;
    bool AtCache() const;
    UPROPERTY(BlueprintReadOnly) FWTSCBag Carry;
    UPROPERTY(BlueprintReadOnly) FWTSCBag Storage;
    UPROPERTY(BlueprintReadOnly) float Health = 100;
    UPROPERTY(BlueprintReadOnly) float FoodNeed = 78;
    UPROPERTY(BlueprintReadOnly) float WaterNeed = 72;
    UPROPERTY(BlueprintReadOnly) float SearchProgress = 0;
    UPROPERTY(BlueprintReadOnly) bool CacheAvailable = true;
    UPROPERTY(BlueprintReadOnly) bool Completed = false;
    UPROPERTY(BlueprintReadOnly) FString Message;
    UPROPERTY(BlueprintReadOnly) float MessageSeconds = 0;
    UPROPERTY(BlueprintReadOnly) float DistanceWalked = 0;
private:
    UPROPERTY() TObjectPtr<AWTSCStage> Stage;
    UPROPERTY() TObjectPtr<AWTSCChild> Child;
    UPROPERTY() TObjectPtr<AActor> CameraActor;
    UPROPERTY() TObjectPtr<UCameraComponent> Camera;
    bool Searching = false;
    bool Replay = false;
    bool ReplayFailed = false;
    int32 ReplayStep = 0;
    float ReplayClock = 0;
    float StepClock = 0;
    bool RecordPreview = false;
    float CaptureClock = 0;
    int32 CaptureFrame = 0;
    FVector LastPosition;
    TArray<TSharedPtr<FJsonValue>> ReplayEvents;
    void Say(const FString& Text);
    void ReplayTick(float DeltaSeconds);
    void ReplayKey(FKey Key, bool Down);
    void ReceiptEvent(const FString& Name, bool Passed);
    void FinishReplay();
};

UCLASS()
class AWTSCHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
