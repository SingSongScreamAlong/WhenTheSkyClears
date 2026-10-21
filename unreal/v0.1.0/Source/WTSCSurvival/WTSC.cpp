#include "WTSC.h"
#include "Modules/ModuleManager.h"
#include "Camera/CameraComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "InputCoreTypes.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "UnrealClient.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, WTSCSurvival, "WTSCSurvival");

static const FName GeneratedTag(TEXT("WTSCGenerated"));
static const TCHAR* SaveSlot = TEXT("WTSC_ShelterStudy_v1");

AWTSCStage::AWTSCStage()
{
    StageRoot=CreateDefaultSubobject<USceneComponent>(TEXT("StageRoot"));
    StageRoot->SetMobility(EComponentMobility::Static);
    RootComponent=StageRoot;
}

void AWTSCStage::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    RebuildStage();
}

UStaticMeshComponent* AWTSCStage::Shape(const FString& Name, const FString& MeshName, FVector P, FVector Size, FName Material, bool Collision, FRotator Rotation)
{
    auto* Mesh=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Engine/BasicShapes/")+MeshName+TEXT(".")+MeshName));
    auto* C=NewObject<UStaticMeshComponent>(this,*MakeUniqueObjectName(this,UStaticMeshComponent::StaticClass(),*Name).ToString());
    AddInstanceComponent(C);
    C->ComponentTags.Add(GeneratedTag);
    C->SetupAttachment(StageRoot);
    C->SetStaticMesh(Mesh);
    C->SetRelativeLocation(P);
    C->SetRelativeRotation(Rotation);
    FVector Extent=Mesh?Mesh->GetBounds().BoxExtent*2:FVector(100);
    C->SetRelativeScale3D(FVector(Size.X/FMath::Max(Extent.X,1.0),Size.Y/FMath::Max(Extent.Y,1.0),Size.Z/FMath::Max(Extent.Z,1.0)));
    C->SetCollisionEnabled(Collision?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);
    C->SetCollisionResponseToAllChannels(ECR_Block);
    C->SetMobility(EComponentMobility::Static);
    if (auto* M=Materials.Find(Material)) C->SetMaterial(0,*M);
    C->RegisterComponent();
    return C;
}

void AWTSCStage::Prop(FName Key, FVector Ground, float Width, FRotator Rotation)
{
    auto* Found=PropMeshes.Find(Key);
    if(!Found || !*Found) return; // Missing imports are recorded, never represented as completed imports.
    UStaticMesh* Mesh=*Found;
    auto* C=NewObject<UStaticMeshComponent>(this,*MakeUniqueObjectName(this,UStaticMeshComponent::StaticClass(),Key).ToString());
    AddInstanceComponent(C); C->ComponentTags.Add(GeneratedTag); C->SetupAttachment(StageRoot);
    C->SetStaticMesh(Mesh); C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    const auto B=Mesh->GetBounds();
    float Scale=Width/FMath::Max(B.BoxExtent.X*2,1.0);
    C->SetRelativeScale3D(FVector(Scale)); C->SetRelativeRotation(Rotation);
    Ground.Z-=(B.Origin.Z-B.BoxExtent.Z)*Scale;
    C->SetRelativeLocation(Ground); C->RegisterComponent();
}

void AWTSCStage::WarmLight(FVector P, float Intensity, float Radius)
{
    auto* L=NewObject<UPointLightComponent>(this);
    AddInstanceComponent(L); L->ComponentTags.Add(GeneratedTag); L->SetupAttachment(StageRoot);
    L->SetRelativeLocation(P); L->SetMobility(EComponentMobility::Movable);
    L->SetIntensity(Intensity); L->SetLightColor(FLinearColor(1.f,.66f,.32f));
    L->SetAttenuationRadius(Radius); L->SetSourceRadius(14.f); L->RegisterComponent();
}

void AWTSCStage::RebuildStage()
{
    TArray<UActorComponent*> Components; GetComponents(Components);
    for(auto* C:Components) if(C && C->ComponentHasTag(GeneratedTag)) C->DestroyComponent();
    if(!GetWorld()) return;
    StageRoot->SetMobility(EComponentMobility::Static);
    SetActorScale3D(FVector(1,-1,1));
    // Background source paintings are matte planes, not claimed as generated 3D terrain.
    Shape(TEXT("ColdDawn"),TEXT("Cube"),FVector(1400,1800,650),FVector(10000,30,2600),TEXT("Sky"));
    Shape(TEXT("PaintedVillage"),TEXT("Plane"),FVector(1400,1200,550),FVector(7600,2500,1),TEXT("Backdrop"),false,FRotator(0,0,90));
    Shape(TEXT("WalkableFoundation"),TEXT("Cube"),FVector(1300,60,-500),FVector(6500,1000,1000),TEXT("Stone"),true);
    Shape(TEXT("StreetSurface"),TEXT("Cube"),FVector(1500,-60,-2),FVector(6200,500,10),TEXT("Road"));
    Shape(TEXT("ShelterFoundation"),TEXT("Cube"),FVector(0,80,-10),FVector(2050,440,30),TEXT("Stone"));
    Shape(TEXT("ShelterPlaster"),TEXT("Cube"),FVector(0,300,300),FVector(ShelterHalfWidth*2,35,600),TEXT("Plaster"));
    Shape(TEXT("SleepingRoomPaint"),TEXT("Cube"),FVector(-640,278,150),FVector(610,8,285),TEXT("FadedBlue"));
    Shape(TEXT("KitchenPaint"),TEXT("Cube"),FVector(20,278,150),FVector(660,8,285),TEXT("WarmPlaster"));
    Shape(TEXT("RoofShadow"),TEXT("Cube"),FVector(0,80,620),FVector(2030,470,45),TEXT("Wood"));
    Shape(TEXT("UpperFloor"),TEXT("Cube"),FVector(0,80,325),FVector(1980,440,30),TEXT("Wood"));
    Shape(TEXT("CutawayFloorEdge"),TEXT("Cube"),FVector(0,-150,322),FVector(2030,30,42),TEXT("DarkWood"));
    Shape(TEXT("CutawayRoofEdge"),TEXT("Cube"),FVector(0,-150,620),FVector(2060,35,55),TEXT("DarkWood"));
    for(float X:{-980.f,-330.f,360.f,980.f})
    {
        Shape(TEXT("Pier"),TEXT("Cube"),FVector(X,205,300),FVector(35,170,610),TEXT("Brick"));
        Shape(TEXT("Beam"),TEXT("Cube"),FVector(X,70,609),FVector(30,410,25),TEXT("DarkWood"));
    }
    for(float X:{-660.f,20.f,690.f})
    {
        Shape(TEXT("UpperWindowVoid"),TEXT("Cube"),FVector(X,272,475),FVector(190,18,165),TEXT("Dark"));
        Shape(TEXT("WindowFrameTop"),TEXT("Cube"),FVector(X,250,565),FVector(215,24,12),TEXT("Wood"));
        Shape(TEXT("WindowFrameBottom"),TEXT("Cube"),FVector(X,250,388),FVector(215,40,14),TEXT("Wood"));
        for(float DX:{-101.f,101.f,0.f}) Shape(TEXT("WindowMullion"),TEXT("Cube"),FVector(X+DX,250,478),FVector(10,20,175),TEXT("Wood"));
        for(int32 B=0;B<3;++B) Shape(TEXT("BoardedGlass"),TEXT("Cube"),FVector(X,230,425+B*45),FVector(220,13,19),TEXT("OldWood"),false,FRotator(0,0,B%2?7:-5));
        WarmLight(FVector(X,55,255),1800,620);
        Shape(TEXT("LampShade"),TEXT("Cylinder"),FVector(X,60,270),FVector(24,24,16),TEXT("Metal"));
        Shape(TEXT("LampGlow"),TEXT("Sphere"),FVector(X,60,254),FVector(12),TEXT("Lamp"));
    }
    // Reusable publisher props are placed only after the editor import records real native assets.
    Prop(TEXT("vintage_day_bed"),FVector(-650,145,8),220,FRotator(0,0,0));
    Prop(TEXT("barrel_stove"),FVector(-185,180,8),72);
    Prop(TEXT("wooden_table_02"),FVector(170,130,8),115);
    Prop(TEXT("bench_vice_01"),FVector(145,125,89),22);
    Prop(TEXT("medical_box"),FVector(560,155,74),34);
    Prop(TEXT("russian_food_cans_01"),FVector(650,150,74),25);
    Prop(TEXT("plastic_bottle_gallon"),FVector(720,170,74),20);
    Shape(TEXT("StorageBench"),TEXT("Cube"),FVector(650,170,65),FVector(270,100,18),TEXT("Wood"));
    for(float X:{530.f,770.f}) Shape(TEXT("BenchLeg"),TEXT("Cube"),FVector(X,170,32),FVector(14,80,65),TEXT("Wood"));
    for(int32 S=0;S<3;++S) Shape(TEXT("StorageShelf"),TEXT("Cube"),FVector(680,245,130+S*62),FVector(280,45,10),TEXT("OldWood"));
    for(float X:{540.f,820.f}) Shape(TEXT("ShelfUpright"),TEXT("Cube"),FVector(X,249,170),FVector(12,35,240),TEXT("DarkWood"));
    Shape(TEXT("StovePipe"),TEXT("Cylinder"),FVector(-190,235,203),FVector(18,18,210),TEXT("Metal"));
    Shape(TEXT("StoveHearth"),TEXT("Cube"),FVector(-180,150,8),FVector(150,160,15),TEXT("Stone"));
    WarmLight(FVector(-185,70,65),850,250);
    for(float X:{-650.f,0.f,650.f})
    {
        auto* L=NewObject<UPointLightComponent>(this);AddInstanceComponent(L);L->ComponentTags.Add(GeneratedTag);L->SetupAttachment(StageRoot);
        L->SetRelativeLocation(FVector(X,-40,470));L->SetMobility(EComponentMobility::Movable);L->SetIntensity(6500);
        L->SetLightColor(FLinearColor(.36f,.56f,.66f));L->SetAttenuationRadius(620);L->SetSourceRadius(80);L->RegisterComponent();
    }
    // Upper-room belongings establish an interrupted civilian life without expanding the map.
    Shape(TEXT("RolledBlanket"),TEXT("Cylinder"),FVector(-720,120,363),FVector(45,45,120),TEXT("Cloth"),false,FRotator(0,0,90));
    Shape(TEXT("Suitcase"),TEXT("Cube"),FVector(60,170,366),FVector(100,55,52),TEXT("OldWood"));
    Shape(TEXT("Schoolbook"),TEXT("Cube"),FVector(70,160,397),FVector(38,25,7),TEXT("FadedBlue"),false,FRotator(0,12,0));
    for(int32 I=0;I<8;++I) Shape(TEXT("LooseFloorboard"),TEXT("Cube"),FVector(480+I*45,140,350+I%2*4),FVector(150,24,8),TEXT("OldWood"),false,FRotator(0,I*17,0));
    // A narrow, nearby street leads to a single damaged shop.
    Shape(TEXT("ShopBackWall"),TEXT("Cube"),FVector(CacheX,290,222),FVector(900,40,445),TEXT("ShopPlaster"));
    Shape(TEXT("ShopRoof"),TEXT("Cube"),FVector(CacheX,100,455),FVector(950,430,35),TEXT("Stone"));
    Shape(TEXT("ShopFrontRoofEdge"),TEXT("Cube"),FVector(CacheX,-135,455),FVector(960,30,45),TEXT("DarkWood"));
    for(float DX:{-430.f,430.f}) Shape(TEXT("ShopPillar"),TEXT("Cube"),FVector(CacheX+DX,150,225),FVector(50,260,460),TEXT("Brick"));
    Shape(TEXT("ShopCounter"),TEXT("Cube"),FVector(CacheX+110,180,78),FVector(390,100,145),TEXT("OldWood"));
    Shape(TEXT("ShopCounterTop"),TEXT("Cube"),FVector(CacheX+110,170,154),FVector(415,125,12),TEXT("DarkWood"));
    Shape(TEXT("CacheCrate"),TEXT("Cube"),FVector(CacheX,35,34),FVector(100,72,65),TEXT("Wood"));
    Shape(TEXT("CacheLid"),TEXT("Cube"),FVector(CacheX-12,45,72),FVector(110,75,12),TEXT("OldWood"),false,FRotator(0,0,-9));
    Prop(TEXT("medical_box"),FVector(CacheX+30,170,162),40);
    Prop(TEXT("plastic_bottle_gallon"),FVector(CacheX+210,170,160),22);
    Shape(TEXT("ShopSign"),TEXT("Cube"),FVector(CacheX,257,370),FVector(300,12,70),TEXT("FadedBlue"));
    Shape(TEXT("MedicalCrossVertical"),TEXT("Cube"),FVector(CacheX,245,370),FVector(14,8,44),TEXT("WarmPlaster"));
    Shape(TEXT("MedicalCrossHorizontal"),TEXT("Cube"),FVector(CacheX,244,370),FVector(44,8,14),TEXT("WarmPlaster"));
    WarmLight(FVector(CacheX-280,140,230),650,500);
    auto* ShopFill=NewObject<UPointLightComponent>(this);AddInstanceComponent(ShopFill);ShopFill->ComponentTags.Add(GeneratedTag);ShopFill->SetupAttachment(StageRoot);
    ShopFill->SetRelativeLocation(FVector(CacheX+100,-120,235));ShopFill->SetMobility(EComponentMobility::Movable);ShopFill->SetIntensity(4200);
    ShopFill->SetLightColor(FLinearColor(.66f,.73f,.68f));ShopFill->SetAttenuationRadius(760);ShopFill->SetSourceRadius(90);ShopFill->SetCastShadows(false);ShopFill->RegisterComponent();
    FRandomStream Rand(10219);
    for(int32 I=0;I<90;++I)
    {
        float X=Rand.FRandRange(1050,2450);
        Shape(TEXT("StreetRubble"),TEXT("Cube"),FVector(X,Rand.FRandRange(75,350),Rand.FRandRange(1,22)),FVector(Rand.FRandRange(15,85),Rand.FRandRange(15,65),Rand.FRandRange(8,30)),I%3?TEXT("Brick"):TEXT("Stone"),false,FRotator(Rand.FRandRange(-12,12),Rand.FRandRange(0,180),Rand.FRandRange(-12,12)));
    }
    for(int32 I=0;I<12;++I) Shape(TEXT("RoadScar"),TEXT("Cube"),FVector(1050+I*155,-100,-.5f),FVector(80,6,1),TEXT("Dark"),false,FRotator(0,I*21,0));
    auto* Moon=NewObject<UDirectionalLightComponent>(this);AddInstanceComponent(Moon);Moon->ComponentTags.Add(GeneratedTag);Moon->SetupAttachment(StageRoot);
    Moon->SetRelativeRotation(FRotator(-38,-38,0));Moon->SetIntensity(1.2f);Moon->SetLightColor(FLinearColor(.53f,.68f,.79f));Moon->SetMobility(EComponentMobility::Movable);Moon->RegisterComponent();
    auto* Sky=NewObject<USkyLightComponent>(this);AddInstanceComponent(Sky);Sky->ComponentTags.Add(GeneratedTag);Sky->SetupAttachment(StageRoot);Sky->SetIntensity(.65f);Sky->SetMobility(EComponentMobility::Movable);Sky->RegisterComponent();
}

AWTSCChild::AWTSCChild()
{
    PrimaryActorTick.bCanEverTick=true;
    GetCapsuleComponent()->InitCapsuleSize(20,64);
    GetCharacterMovement()->MaxWalkSpeed=175;
    GetCharacterMovement()->MaxAcceleration=1200;
    GetCharacterMovement()->BrakingDecelerationWalking=1400;
    GetCharacterMovement()->bConstrainToPlane=true;
    GetCharacterMovement()->SetPlaneConstraintNormal(FVector(0,1,0));
    GetCharacterMovement()->bOrientRotationToMovement=false;
    bUseControllerRotationYaw=false;
    Puppet=CreateDefaultSubobject<USceneComponent>(TEXT("PaintedPuppet"));Puppet->SetupAttachment(RootComponent);
}

void AWTSCChild::Card(const FString& Name,USceneComponent* Parent,FVector Position,FVector2D Size,const FString& Material)
{
    auto* C=NewObject<UStaticMeshComponent>(this,*Name);AddInstanceComponent(C);C->SetupAttachment(Parent);
    C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane.Plane")));
    C->SetRelativeLocation(Position);C->SetRelativeRotation(FRotator(0,0,90));C->SetRelativeScale3D(FVector(Size.X/100,Size.Y/100,1));
    C->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,*(TEXT("/Game/WTSC/Materials/")+Material+TEXT(".")+Material)));
    C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCastShadow(false);C->RegisterComponent();
}

void AWTSCChild::CreatePuppet(bool Girl)
{
    auto Pivot=[this](const TCHAR* Name,FVector P){auto* S=NewObject<USceneComponent>(this,Name);AddInstanceComponent(S);S->SetupAttachment(Puppet);S->SetRelativeLocation(P);S->RegisterComponent();return S;};
    LeftLeg=Pivot(TEXT("LeftLeg"),FVector(-8,1,-8));RightLeg=Pivot(TEXT("RightLeg"),FVector(8,-1,-8));
    LeftArm=Pivot(TEXT("LeftArm"),FVector(-12,2,26));RightArm=Pivot(TEXT("RightArm"),FVector(12,-2,26));
    Card(TEXT("FarLeg"),LeftLeg,FVector(0,0,-27),FVector2D(17,56),TEXT("M_BoyLeg"));
    Card(TEXT("NearLeg"),RightLeg,FVector(0,0,-27),FVector2D(17,56),TEXT("M_BoyLeg"));
    Card(TEXT("FarBoot"),LeftLeg,FVector(5,-.5f,-49),FVector2D(25,16),TEXT("M_BoyBoot"));
    Card(TEXT("NearBoot"),RightLeg,FVector(5,-.5f,-49),FVector2D(25,16),TEXT("M_BoyBoot"));
    Card(TEXT("FarArm"),LeftArm,FVector(0,0,-20),FVector2D(13,43),TEXT("M_BoyArm"));
    Card(TEXT("Body"),Puppet,FVector(0,-4,15),FVector2D(39,49),TEXT("M_BoyCoat"));
    Card(TEXT("NearArm"),RightArm,FVector(0,-3,-20),FVector2D(13,43),TEXT("M_BoyArm"));
    Card(TEXT("EstablishedFace"),Puppet,FVector(2,-9,51),Girl?FVector2D(48,57):FVector2D(35,40),Girl?TEXT("M_GirlProfile"):TEXT("M_BoyHead"));
}

void AWTSCChild::BeginPlay()
{
    Super::BeginPlay();CreatePuppet(Companion);
    if(Companion){GetCharacterMovement()->DisableMovement();GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
}

void AWTSCChild::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);Input->BindAxis(TEXT("MoveSide"),this,&AWTSCChild::MoveSide);
}
void AWTSCChild::MoveSide(float Value)
{
    if(Companion)return;
    if(GetActorLocation().X<-850 && Value<0)return;
    if(GetActorLocation().X>3450 && Value>0)return;
    AddMovementInput(FVector(1,0,0),Value);
    if(FMath::Abs(Value)>.01f)Facing=FMath::Sign(Value);
}
void AWTSCChild::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(!LeftLeg)return;
    const float Speed=GetVelocity().Size2D();Gait+=DeltaSeconds*(Speed>4?7.5f:1.4f);
    const float Swing=FMath::Sin(Gait)*FMath::Clamp(Speed/175.f,0.f,1.f)*23.f;
    LeftLeg->SetRelativeRotation(FRotator(0,0,Swing));RightLeg->SetRelativeRotation(FRotator(0,0,-Swing));
    LeftArm->SetRelativeRotation(FRotator(0,0,-Swing*.6f));RightArm->SetRelativeRotation(FRotator(0,0,Swing*.6f));
    Puppet->SetRelativeScale3D(FVector(Facing,1,1));
    Puppet->SetRelativeLocation(FVector(0,0,Speed>4?FMath::Abs(FMath::Sin(Gait))*1.3f:FMath::Sin(Gait)*.3f));
}

static AWTSCGameMode* Mode(APlayerController* P){return P?Cast<AWTSCGameMode>(UGameplayStatics::GetGameMode(P)):nullptr;}
void AWTSCController::SetupInputComponent()
{
    Super::SetupInputComponent();bShowMouseCursor=false;
    InputComponent->BindKey(EKeys::E,IE_Pressed,this,&AWTSCController::SearchPressed);
    InputComponent->BindKey(EKeys::E,IE_Released,this,&AWTSCController::SearchReleased);
    InputComponent->BindKey(EKeys::R,IE_Pressed,this,&AWTSCController::RestartDay);
    InputComponent->BindKey(EKeys::F5,IE_Pressed,this,&AWTSCController::SaveCheckpoint);
    InputComponent->BindKey(EKeys::F9,IE_Pressed,this,&AWTSCController::LoadCheckpoint);
    InputComponent->BindKey(EKeys::F,IE_Pressed,this,&AWTSCController::Eat);
    InputComponent->BindKey(EKeys::G,IE_Pressed,this,&AWTSCController::Drink);
    InputComponent->BindKey(EKeys::H,IE_Pressed,this,&AWTSCController::Heal);
    auto& Pause=InputComponent->BindKey(EKeys::Escape,IE_Pressed,this,&AWTSCController::PauseStudy);Pause.bExecuteWhenPaused=true;
}
void AWTSCController::SearchPressed(){if(auto* M=Mode(this))M->SetSearching(true);}
void AWTSCController::SearchReleased(){if(auto* M=Mode(this))M->SetSearching(false);}
void AWTSCController::RestartDay(){if(auto* M=Mode(this))M->ResetDay();}
void AWTSCController::SaveCheckpoint(){if(auto* M=Mode(this))M->SaveDay();}
void AWTSCController::LoadCheckpoint(){if(auto* M=Mode(this))M->LoadDay();}
void AWTSCController::Eat(){if(auto* M=Mode(this))M->UseSupply(0);}
void AWTSCController::Drink(){if(auto* M=Mode(this))M->UseSupply(1);}
void AWTSCController::Heal(){if(auto* M=Mode(this))M->UseSupply(2);}
void AWTSCController::PauseStudy(){SetPause(!IsPaused());}

AWTSCGameMode::AWTSCGameMode()
{
    PrimaryActorTick.bCanEverTick=true;DefaultPawnClass=AWTSCChild::StaticClass();PlayerControllerClass=AWTSCController::StaticClass();HUDClass=AWTSCHUD::StaticClass();
}
void AWTSCGameMode::StartPlay()
{
    Super::StartPlay();
    for(TActorIterator<AWTSCStage> I(GetWorld());I;++I){Stage=*I;break;}
    if(!Stage)Stage=GetWorld()->SpawnActor<AWTSCStage>();
    Child=Cast<AWTSCChild>(UGameplayStatics::GetPlayerCharacter(this,0));
    if(!Child){Child=GetWorld()->SpawnActor<AWTSCChild>();if(auto* P=UGameplayStatics::GetPlayerController(this,0))P->Possess(Child);}
    auto* StageCamera=GetWorld()->SpawnActor<ACameraActor>();CameraActor=StageCamera;Camera=StageCamera->GetCameraComponent();Camera->Activate();
    Camera->ProjectionMode=ECameraProjectionMode::Orthographic;Camera->OrthoWidth=1450;Camera->bConstrainAspectRatio=false;
    Camera->FieldOfView=50;
    Camera->bAutoCalculateOrthoPlanes=false;Camera->OrthoNearClipPlane=0;Camera->OrthoFarClipPlane=10000;
    Camera->bUpdateOrthoPlanes=false;
    Camera->PostProcessSettings.bOverride_AutoExposureMethod=true;Camera->PostProcessSettings.AutoExposureMethod=AEM_Manual;
    Camera->PostProcessSettings.bOverride_AutoExposureBias=true;Camera->PostProcessSettings.AutoExposureBias=1;
    Camera->PostProcessSettings.bOverride_AutoExposureApplyPhysicalCameraExposure=true;
    Camera->PostProcessSettings.AutoExposureApplyPhysicalCameraExposure=false;
    Camera->PostProcessSettings.bOverride_VignetteIntensity=true;Camera->PostProcessSettings.VignetteIntensity=.35f;
    if(auto* P=UGameplayStatics::GetPlayerController(this,0)){P->bAutoManageActiveCameraTarget=false;P->PlayerCameraManager->bIsOrthographic=true;P->PlayerCameraManager->SetOrthoWidth(1450);P->PlayerCameraManager->SetFOV(50);P->SetViewTarget(CameraActor);P->SetInputMode(FInputModeGameOnly());}
    auto* Friend=GetWorld()->SpawnActorDeferred<AWTSCChild>(AWTSCChild::StaticClass(),FTransform(FVector(-650,15,70)));
    Friend->Companion=true;UGameplayStatics::FinishSpawningActor(Friend,FTransform(FVector(-650,15,70)));
    ResetDay();Replay=FParse::Param(FCommandLine::Get(),TEXT("WTSCReplay"));
    RecordPreview=FParse::Param(FCommandLine::Get(),TEXT("WTSCRecord"));
    if(RecordPreview)IFileManager::Get().MakeDirectory(*(FPaths::ProjectDir()/TEXT("Evidence/Frames")),true);
}
bool AWTSCGameMode::AtHome()const{return Child && FMath::Abs(Child->GetActorLocation().X-650)<135;}
bool AWTSCGameMode::AtCache()const{return Child && Stage && FMath::Abs(Child->GetActorLocation().X-Stage->CacheX)<105;}
void AWTSCGameMode::Say(const FString& Text){Message=Text;MessageSeconds=6;UE_LOG(LogTemp,Display,TEXT("WTSC: %s"),*Text);}
void AWTSCGameMode::ResetDay()
{
    Carry.Clear();Storage.Food=2;Storage.Water=2;Storage.Medicine=1;Health=100;FoodNeed=78;WaterNeed=72;CacheAvailable=true;Completed=false;SearchProgress=0;Searching=false;
    if(Child){Child->SetActorLocation(FVector(100,0,70));Child->GetCharacterMovement()->StopMovementImmediately();LastPosition=Child->GetActorLocation();}
    Say(TEXT("The shelter is quiet. There may still be supplies in the small shop east of here."));
}
void AWTSCGameMode::SetSearching(bool Held)
{
    Searching=Held;if(!Held){SearchProgress=0;return;}
    if(AtHome())
    {
        if(Carry.Count())
        {
            Storage.Food+=Carry.Food;Storage.Water+=Carry.Water;Storage.Medicine+=Carry.Medicine;Carry.Clear();Completed=true;
            Say(TEXT("Supplies put away. Enough to share for another quiet morning."));
        }
        else Say(TEXT("Shelter storage. F: eat / G: drink / H: use a bandage. R begins a fresh test day."));
        Searching=false;
    }
    else if(AtCache()&&!CacheAvailable){Say(TEXT("Nothing more here. Take what you found home."));Searching=false;}
}
void AWTSCGameMode::UseSupply(int32 Kind)
{
    if(!AtHome()){Say(TEXT("Use the supplies beside the shelter shelves."));return;}
    if(Kind==0&&Storage.Food>0){--Storage.Food;FoodNeed=FMath::Min(100.f,FoodNeed+30);Say(TEXT("A small meal, shared in the shelter."));}
    else if(Kind==1&&Storage.Water>0){--Storage.Water;WaterNeed=FMath::Min(100.f,WaterNeed+35);Say(TEXT("Clean water. Keep some for later."));}
    else if(Kind==2&&Storage.Medicine>0&&Health<100){--Storage.Medicine;Health=FMath::Min(100.f,Health+35);Say(TEXT("The bandage will help."));}
    else Say(TEXT("That supply is empty, or it is not needed yet."));
}
FString AWTSCGameMode::Prompt()const
{
    if(AtHome())return Carry.Count()?TEXT("E  Put supplies in shelter storage"):TEXT("E  Shelter storage  |  F Eat  G Drink  H Bandage");
    if(AtCache())return CacheAvailable?TEXT("HOLD E  Search the abandoned crate"):TEXT("The crate is empty. Return to the shelter.");
    return TEXT("A / D  Walk   |   E  Interact nearby");
}
FString AWTSCGameMode::Objective()const
{
    if(Completed)return TEXT("SUPPLIES HOME  /  The first search is complete");
    if(Carry.Count())return TEXT("RETURN  /  Put the supplies on the shelter shelves");
    return TEXT("SEARCH  /  Reach the small shop to the east");
}
void AWTSCGameMode::Tick(float Dt)
{
    Super::Tick(Dt);if(!Child||!CameraActor)return;
    FVector P=Child->GetActorLocation();DistanceWalked+=FVector::Dist2D(P,LastPosition);LastPosition=P;
    float Focus=FMath::Clamp(P.X-140.0,-20.0,3000.0);
    FVector CameraP(Focus,2350,440);CameraActor->SetActorLocation(FMath::VInterpTo(CameraActor->GetActorLocation(),CameraP,Dt,3));
    CameraActor->SetActorRotation((FVector(Focus,-100,315)-CameraActor->GetActorLocation()).Rotation());
    MessageSeconds=FMath::Max(0.f,MessageSeconds-Dt);
    FoodNeed=FMath::Max(0.f,FoodNeed-Dt*.025f);WaterNeed=FMath::Max(0.f,WaterNeed-Dt*.045f);
    if(FoodNeed<=0||WaterNeed<=0)Health=FMath::Max(0.f,Health-Dt*.6f);
    if(Health<=0){ResetDay();Say(TEXT("Too exhausted to continue. Begin again from the shelter."));}
    if(Searching&&AtCache()&&CacheAvailable&&Child->GetVelocity().Size2D()<10)
    {
        SearchProgress+=Dt/2.5f;
        if(SearchProgress>=1)
        {
            Carry.Food=2;Carry.Water=2;Carry.Medicine=1;CacheAvailable=false;Searching=false;SearchProgress=0;
            Say(TEXT("Two tins, two bottles, one clean bandage. Take them back to the shelter."));
        }
    }
    else SearchProgress=0;
    if(Replay)ReplayTick(Dt);
    if(RecordPreview&&Replay&&ReplayClock>3){CaptureClock+=Dt;if(CaptureClock>=.2f&&!FScreenshotRequest::IsScreenshotRequested()){CaptureClock=0;FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/FString::Printf(TEXT("Evidence/Frames/Frame%05d.png"),CaptureFrame++),false,false);}}
}
void AWTSCGameMode::SaveDay()
{
    auto* S=Cast<UWTSCCheckpoint>(UGameplayStatics::CreateSaveGameObject(UWTSCCheckpoint::StaticClass()));
    S->Carry=Carry;S->Storage=Storage;S->Health=Health;S->FoodNeed=FoodNeed;S->WaterNeed=WaterNeed;S->Position=Child->GetActorLocation();S->CacheAvailable=CacheAvailable;S->Completed=Completed;
    Say(UGameplayStatics::SaveGameToSlot(S,SaveSlot,0)?TEXT("Shelter checkpoint saved."):TEXT("Checkpoint could not be saved."));
}
void AWTSCGameMode::LoadDay()
{
    auto* S=Cast<UWTSCCheckpoint>(UGameplayStatics::LoadGameFromSlot(SaveSlot,0));
    if(!S||S->Version!=1){Say(TEXT("No compatible shelter checkpoint yet."));return;}
    Carry=S->Carry;Storage=S->Storage;Health=S->Health;FoodNeed=S->FoodNeed;WaterNeed=S->WaterNeed;CacheAvailable=S->CacheAvailable;Completed=S->Completed;
    Child->SetActorLocation(S->Position);Child->GetCharacterMovement()->StopMovementImmediately();LastPosition=S->Position;Searching=false;SearchProgress=0;Say(TEXT("Shelter checkpoint restored."));
}

void AWTSCGameMode::ReplayKey(FKey Key,bool Down)
{
    if(auto* P=UGameplayStatics::GetPlayerController(this,0))P->InputKey(FInputKeyEventArgs::CreateSimulated(Key,Down?IE_Pressed:IE_Released,Down?1.f:0.f));
}
void AWTSCGameMode::ReceiptEvent(const FString& Name,bool Passed)
{
    auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),Name);O->SetBoolField(TEXT("passed"),Passed);O->SetNumberField(TEXT("game_seconds"),ReplayClock);O->SetNumberField(TEXT("player_x"),Child->GetActorLocation().X);O->SetNumberField(TEXT("carry_units"),Carry.Count());O->SetNumberField(TEXT("storage_units"),Storage.Count());O->SetBoolField(TEXT("cache_available"),CacheAvailable);ReplayEvents.Add(MakeShared<FJsonValueObject>(O));ReplayFailed|=!Passed;
    if(auto* P=UGameplayStatics::GetPlayerController(this,0)){const auto& POV=P->PlayerCameraManager->GetCameraCacheView();O->SetStringField(TEXT("view_target"),GetNameSafe(P->GetViewTarget()));O->SetBoolField(TEXT("orthographic"),POV.ProjectionMode==ECameraProjectionMode::Orthographic);O->SetNumberField(TEXT("ortho_width"),POV.OrthoWidth);O->SetStringField(TEXT("camera_location"),POV.Location.ToString());}
    UE_LOG(LogTemp,Display,TEXT("WTSC_REPLAY %s %s"),*Name,Passed?TEXT("PASS"):TEXT("FAIL"));
}
void AWTSCGameMode::ReplayTick(float Dt)
{
    ReplayClock+=Dt;StepClock+=Dt;
    auto Next=[this](){++ReplayStep;StepClock=0;};
    if(ReplayClock>100){ReceiptEvent(TEXT("bounded_timeout"),false);FinishReplay();return;}
    switch(ReplayStep)
    {
    case 0:if(StepClock>4){ReceiptEvent(TEXT("fresh_state"),Carry.Count()==0&&Storage.Count()==5&&CacheAvailable&&!Completed);FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/TEXT("Evidence/ShelterView.png"),false,false);ReplayKey(EKeys::D,true);Next();}break;
    case 1:if(AtCache()){ReplayKey(EKeys::D,false);ReceiptEvent(TEXT("walked_to_cache"),DistanceWalked>2500);Next();}break;
    case 2:if(StepClock>.5f){ReplayKey(EKeys::E,true);Next();}break;
    case 3:if(Carry.Count()==5){ReplayKey(EKeys::E,false);ReceiptEvent(TEXT("searched_finite_cache"),!CacheAvailable);FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/TEXT("Evidence/CacheView.png"),false,false);Next();}else if(StepClock>7){ReceiptEvent(TEXT("search_timeout"),false);FinishReplay();}break;
    case 4:if(StepClock>1){ReplayKey(EKeys::E,true);ReplayKey(EKeys::E,false);ReceiptEvent(TEXT("cache_cannot_duplicate_loot"),Carry.Count()==5&&!CacheAvailable);ReplayKey(EKeys::A,true);Next();}break;
    case 5:if(AtHome()){ReplayKey(EKeys::A,false);Next();}break;
    case 6:if(StepClock>.5f){ReplayKey(EKeys::E,true);ReplayKey(EKeys::E,false);Next();}break;
    case 7:if(StepClock>.4f){ReceiptEvent(TEXT("returned_and_deposited"),Completed&&Carry.Count()==0&&Storage.Food==4&&Storage.Water==4&&Storage.Medicine==2);FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/TEXT("Evidence/ReturnedView.png"),false,false);SaveDay();ResetDay();LoadDay();ReceiptEvent(TEXT("saved_checkpoint_readback"),Completed&&Storage.Count()==10&&!CacheAvailable);Next();}break;
    case 8:if(StepClock>.5f){ReplayKey(EKeys::F,true);ReplayKey(EKeys::F,false);ReplayKey(EKeys::G,true);ReplayKey(EKeys::G,false);Next();}break;
    case 9:if(StepClock>.5f){ReceiptEvent(TEXT("food_and_water_consumption"),Storage.Count()==8&&FoodNeed>99&&WaterNeed>99);ReplayKey(EKeys::R,true);ReplayKey(EKeys::R,false);Next();}break;
    case 10:if(StepClock>.5f){ReceiptEvent(TEXT("fresh_restart_restores_cache_and_storage"),!Completed&&Carry.Count()==0&&Storage.Count()==5&&CacheAvailable&&Health==100&&Child->GetActorLocation().X<150);FinishReplay();}break;
    }
}
void AWTSCGameMode::FinishReplay()
{
    Replay=false;ReplayKey(EKeys::A,false);ReplayKey(EKeys::D,false);ReplayKey(EKeys::E,false);
    auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());O->SetStringField(TEXT("test_type"),TEXT("Real engine gameplay using simulated native key events; not a human or OS-keyboard playtest"));O->SetBoolField(TEXT("passed"),!ReplayFailed);O->SetNumberField(TEXT("game_seconds"),ReplayClock);O->SetNumberField(TEXT("recorded_frames"),CaptureFrame);O->SetNumberField(TEXT("distance_walked_cm"),DistanceWalked);O->SetArrayField(TEXT("events"),ReplayEvents);FString S;auto W=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(O,W);
    const FString P=FPaths::ProjectDir()/TEXT("Evidence/GameplayReplay.json");IFileManager::Get().MakeDirectory(*FPaths::GetPath(P),true);FFileHelper::SaveStringToFile(S,*P);
    if(FParse::Param(FCommandLine::Get(),TEXT("WTSCExitAfterReplay")))FPlatformMisc::RequestExitWithStatus(false,ReplayFailed?1:0);
}

void AWTSCHUD::DrawHUD()
{
    Super::DrawHUD();if(!Canvas)return;auto* M=Cast<AWTSCGameMode>(UGameplayStatics::GetGameMode(this));if(!M)return;
    const float S=Canvas->SizeX/1600.f;const float W=Canvas->SizeX,H=Canvas->SizeY;
    auto Text=[this,S](const FString& T,float X,float Y,FLinearColor C=FLinearColor(.85f,.85f,.79f),float Scale=1.f){DrawText(T,C,X*S,Y*S,GEngine->GetSmallFont(),S*Scale,false);};
    DrawRect(FLinearColor(.025f,.035f,.038f,.87f),0,0,W,78*S);
    Text(TEXT("WHEN THE SKY CLEARS"),36,21,FLinearColor(.91f,.85f,.71f),1.45f);
    Text(TEXT("SHELTER STUDY  /  FIRST MORNING"),36,48,FLinearColor(.53f,.64f,.65f),.85f);
    Text(M->Objective(),630,32,FLinearColor(.86f,.74f,.52f),1.05f);
    DrawRect(FLinearColor(.025f,.035f,.038f,.91f),0,H-132*S,W,132*S);
    Text(M->Prompt(),36,H/S-112,FLinearColor(.93f,.86f,.67f),1.15f);
    Text(FString::Printf(TEXT("PACK  %d / 5    Food %d   Water %d   Bandages %d"),M->Carry.Count(),M->Carry.Food,M->Carry.Water,M->Carry.Medicine),36,H/S-78);
    Text(FString::Printf(TEXT("SHELTER    Food %d   Water %d   Bandages %d"),M->Storage.Food,M->Storage.Water,M->Storage.Medicine),36,H/S-50,FLinearColor(.67f,.73f,.66f));
    auto Bar=[&](const FString& Label,float V,float X,FLinearColor C){Text(Label,X,H/S-105,FLinearColor(.61f,.68f,.67f),.85f);DrawRect(FLinearColor(.1f,.15f,.16f,1),X*S,H-80*S,150*S,5*S);DrawRect(C,X*S,H-80*S,150*S*V/100,5*S);};
    Bar(TEXT("HEALTH"),M->Health,1050,FLinearColor(.68f,.72f,.55f));Bar(TEXT("FOOD"),M->FoodNeed,1240,FLinearColor(.72f,.64f,.42f));Bar(TEXT("WATER"),M->WaterNeed,1430,FLinearColor(.43f,.65f,.69f));
    Text(TEXT("R Reset day   F5 Save   F9 Load   Esc Pause"),1050,H/S-45,FLinearColor(.48f,.58f,.59f),.8f);
    Text(TEXT("Painted child puppets / procedural motion: provisional"),36,90,FLinearColor(.53f,.62f,.64f),.75f);
    if(M->MessageSeconds>0){DrawRect(FLinearColor(.035f,.045f,.046f,.78f),W*.17f,H-194*S,W*.66f,40*S);Text(M->Message,W*.17f/S+18,H/S-182,FLinearColor(.83f,.84f,.77f),.95f);}
    if(M->SearchProgress>0){DrawRect(FLinearColor(.08f,.12f,.13f,1),W*.35f,H*.64f,W*.3f,7*S);DrawRect(FLinearColor(.83f,.69f,.4f,1),W*.35f,H*.64f,W*.3f*M->SearchProgress,7*S);}
    if(PlayerOwner&&PlayerOwner->IsPaused()){DrawRect(FLinearColor(0,0,0,.7f),0,0,W,H);Text(TEXT("PAUSED  /  Esc returns to the shelter study"),W*.3f/S,H*.45f/S,FLinearColor(.92f,.85f,.7f),1.5f);}
}
