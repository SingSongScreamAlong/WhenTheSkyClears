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
#include "Engine/GameViewportClient.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "HAL/PlatformTime.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, WTSCSurvival, "WTSCSurvival");

static const FName GeneratedTag(TEXT("WTSCGenerated"));
static const TCHAR* SaveSlot = TEXT("WTSC_ShelterStudy_v011");

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
    Shape(TEXT("RoofShadow"),TEXT("Cube"),FVector(-370,80,620),FVector(1240,470,24),TEXT("Wood"));
    Shape(TEXT("UpperFloorWest"),TEXT("Cube"),FVector(-370,80,325),FVector(1240,440,18),TEXT("Wood"));
    Shape(TEXT("UpperFloorEast"),TEXT("Cube"),FVector(815,80,325),FVector(330,440,18),TEXT("Wood"));
    Shape(TEXT("RoofEast"),TEXT("Cube"),FVector(815,80,620),FVector(370,470,24),TEXT("Wood"));
    Shape(TEXT("CutawayFloorEdge"),TEXT("Cube"),FVector(-370,-150,322),FVector(1240,22,12),TEXT("DarkWood"));
    Shape(TEXT("CutawayRoofEdge"),TEXT("Cube"),FVector(-370,-150,620),FVector(1240,24,18),TEXT("DarkWood"));
    Shape(TEXT("EastFloorTrim"),TEXT("Cube"),FVector(815,-150,322),FVector(330,22,12),TEXT("DarkWood"));
    Shape(TEXT("EastRoofTrim"),TEXT("Cube"),FVector(815,-150,620),FVector(370,24,18),TEXT("DarkWood"));
    // The collapsed stair and broken landing explicitly close the upper floor.
    for(int32 I=0;I<6;++I)
        Shape(TEXT("BrokenStairTread"),TEXT("Cube"),FVector(400+I*24,155,18+I*24),FVector(55,140,10),TEXT("OldWood"),false,FRotator(I==5?14:0,0,0));
    Shape(TEXT("BrokenStairStringer"),TEXT("Cube"),FVector(460,155,72),FVector(205,16,16),TEXT("Wood"),false,FRotator(43,0,0));
    for(float X:{265.f,635.f})
        Shape(TEXT("SplinteredLanding"),TEXT("Cube"),FVector(X,110,305),FVector(85,390,12),TEXT("OldWood"),false,FRotator(X<300?-18:12,0,0));
    Shape(TEXT("StairBarrierLeft"),TEXT("Cube"),FVector(385,90,58),FVector(13,16,110),TEXT("Wood"));
    Shape(TEXT("StairBarrierRight"),TEXT("Cube"),FVector(590,90,58),FVector(13,16,110),TEXT("Wood"));
    Shape(TEXT("StairBarricade"),TEXT("Cube"),FVector(485,79,66),FVector(245,13,16),TEXT("Ochre"),false,FRotator(8,0,0));
    for(int32 I=0;I<15;++I)
        Shape(TEXT("CollapseDebris"),TEXT("Cube"),FVector(285+I*24,125+(I%3)*35,10+(I%4)*8),FVector(36+(I%3)*25,32,18),I%3?TEXT("Brick"):TEXT("OldWood"),false,FRotator(I%4*12,I*33,0));
    // The shallow masonry face keeps the cutaway ground legible below the play lane.
    for(int32 I=0;I<20;++I)
        Shape(TEXT("ExposedFoundationStone"),TEXT("Cube"),FVector(-950+I*103,-446,-22-(I%3)*3),FVector(98,15,38),I%2?TEXT("Stone"):TEXT("OldWood"));
    for(float X:{-980.f,-330.f,980.f})
    {
        Shape(TEXT("Pier"),TEXT("Cube"),FVector(X,205,300),FVector(35,170,610),TEXT("Brick"));
        Shape(TEXT("Beam"),TEXT("Cube"),FVector(X,70,609),FVector(30,410,25),TEXT("DarkWood"));
    }
    int32 WindowIndex=0;
    for(float X:{-660.f,20.f,690.f})
    {
        ++WindowIndex;
        Shape(TEXT("UpperWindowVoid"),TEXT("Cube"),FVector(X,272,475),FVector(190,18,165),TEXT("Dark"));
        Shape(TEXT("WindowFrameTop"),TEXT("Cube"),FVector(X,250,565),FVector(215,24,12),TEXT("Wood"));
        Shape(TEXT("WindowFrameBottom"),TEXT("Cube"),FVector(X,250,388),FVector(215,40,14),TEXT("Wood"));
        for(float DX:{-101.f,101.f,0.f}) Shape(TEXT("WindowMullion"),TEXT("Cube"),FVector(X+DX,250,478),FVector(10,20,175),TEXT("Wood"));
        for(int32 B=0;B<WindowIndex;++B) Shape(TEXT("BoardedGlass"),TEXT("Cube"),FVector(X,230,425+B*45),FVector(220,13,19),TEXT("OldWood"),false,FRotator(B%2?11:-8,0,0));
        WarmLight(FVector(X,55,255),1800,620);
        Shape(TEXT("LampShade"),TEXT("Cylinder"),FVector(X,60,270),FVector(24,24,16),TEXT("Metal"));
        Shape(TEXT("LampGlow"),TEXT("Sphere"),FVector(X,60,254),FVector(12),TEXT("Lamp"));
    }
    // Local repair, exposed brick and cracks interrupt broad plaster rather than repeating a wall pattern.
    for(int32 I=0;I<18;++I)
    {
        float X=-905+(I%6)*46;float Z=24+(I/6)*22;
        Shape(TEXT("ExposedBrickPatch"),TEXT("Cube"),FVector(X,269,Z),FVector(42,13,17),TEXT("Brick"));
    }
    for(int32 I=0;I<5;++I)
        Shape(TEXT("PlasterCrack"),TEXT("Cube"),FVector(-70+I*14,265,520-I*24),FVector(3,5,35),TEXT("OldWood"),false,FRotator(I%2?27:-23,0,0));
    Shape(TEXT("WaterStain"),TEXT("Cube"),FVector(780,273,290),FVector(145,6,110),TEXT("Stain"));
    Shape(TEXT("PatchedPlaster"),TEXT("Cube"),FVector(-560,272,235),FVector(150,5,56),TEXT("Plaster"));
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
    for(int32 I=0;I<5;++I) Shape(TEXT("LooseFloorboard"),TEXT("Cube"),FVector(700+I*38,140,341+I%2*4),FVector(150,24,8),TEXT("OldWood"),false,FRotator(0,I*17,0));
    Shape(TEXT("UpperBedFrame"),TEXT("Cube"),FVector(-690,190,350),FVector(250,95,17),TEXT("OldWood"));
    Shape(TEXT("AbandonedMattress"),TEXT("Cube"),FVector(-690,175,367),FVector(235,88,22),TEXT("Cloth"));
    for(float X:{-795.f,-585.f}) Shape(TEXT("UpperBedLeg"),TEXT("Cube"),FVector(X,190,337),FVector(10,78,23),TEXT("Wood"));
    Shape(TEXT("TornCurtain"),TEXT("Cube"),FVector(-755,225,477),FVector(24,5,132),TEXT("Cloth"),false,FRotator(-7,0,0));
    Shape(TEXT("UpperChairBack"),TEXT("Cube"),FVector(-130,190,390),FVector(13,55,70),TEXT("OldWood"),false,FRotator(19,0,0));
    Shape(TEXT("UpperChairSeat"),TEXT("Cube"),FVector(-110,175,352),FVector(60,55,10),TEXT("Wood"));
    Shape(TEXT("StorageClothMarker"),TEXT("Cube"),FVector(650,115,74),FVector(74,8,7),TEXT("Ochre"));
    auto* FrontFill=NewObject<UPointLightComponent>(this);AddInstanceComponent(FrontFill);FrontFill->ComponentTags.Add(GeneratedTag);FrontFill->SetupAttachment(StageRoot);
    FrontFill->SetRelativeLocation(FVector(0,-700,-60));FrontFill->SetMobility(EComponentMobility::Movable);FrontFill->SetIntensity(23000);
    FrontFill->SetLightColor(FLinearColor(.53f,.55f,.48f));FrontFill->SetAttenuationRadius(2000);FrontFill->SetSourceRadius(200);FrontFill->SetCastShadows(false);FrontFill->RegisterComponent();
    // A narrow, nearby street leads to a single damaged shop.
    Shape(TEXT("ShopBackWall"),TEXT("Cube"),FVector(CacheX,290,222),FVector(900,40,445),TEXT("ShopPlaster"));
    Shape(TEXT("ShopRoof"),TEXT("Cube"),FVector(CacheX,100,455),FVector(950,430,35),TEXT("Stone"));
    Shape(TEXT("ShopFrontRoofEdge"),TEXT("Cube"),FVector(CacheX,-135,455),FVector(960,22,18),TEXT("DarkWood"));
    for(float DX:{-430.f,430.f}) Shape(TEXT("ShopPillar"),TEXT("Cube"),FVector(CacheX+DX,150,225),FVector(50,260,460),TEXT("Brick"));
    Shape(TEXT("ShopCounter"),TEXT("Cube"),FVector(CacheX+110,180,78),FVector(390,100,145),TEXT("OldWood"));
    Shape(TEXT("ShopCounterTop"),TEXT("Cube"),FVector(CacheX+110,170,154),FVector(415,125,12),TEXT("DarkWood"));
    Shape(TEXT("CacheCrate"),TEXT("Cube"),FVector(CacheX,35,34),FVector(100,72,65),TEXT("Wood"));
    Shape(TEXT("CacheLid"),TEXT("Cube"),FVector(CacheX-12,45,72),FVector(110,75,12),TEXT("OldWood"),false,FRotator(0,0,-9));
    Shape(TEXT("CrateSearchMark"),TEXT("Cube"),FVector(CacheX,-3,39),FVector(46,5,10),TEXT("Ochre"));
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


// 2D cutout rig. All visible bends are in X/Z (Pitch about Y), not through the card depth.
AWTSCChild::AWTSCChild()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostPhysics;
    GetCapsuleComponent()->InitCapsuleSize(20,64);
    GetCharacterMovement()->MaxWalkSpeed=112;GetCharacterMovement()->MaxAcceleration=720;
    GetCharacterMovement()->BrakingDecelerationWalking=1100;
    GetCharacterMovement()->bConstrainToPlane=true;GetCharacterMovement()->SetPlaneConstraintNormal(FVector(0,1,0));
    GetCharacterMovement()->bOrientRotationToMovement=false;bUseControllerRotationYaw=false;
    Puppet=CreateDefaultSubobject<USceneComponent>(TEXT("PaintedPuppet"));Puppet->SetupAttachment(RootComponent);
}
USceneComponent* AWTSCChild::Pivot(const TCHAR* Name,USceneComponent* Parent,FVector P)
{
    auto* C=NewObject<USceneComponent>(this,Name);AddInstanceComponent(C);C->SetupAttachment(Parent);
    C->SetRelativeLocation(P);C->RegisterComponent();return C;
}
void AWTSCChild::Card(const FString& Name,USceneComponent* Parent,FVector P,FVector2D Size,const FString& Material)
{
    auto* C=NewObject<UStaticMeshComponent>(this,*Name);AddInstanceComponent(C);C->SetupAttachment(Parent);
    C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane.Plane")));
    C->SetRelativeLocation(P);C->SetRelativeRotation(FRotator(0,0,90));C->SetRelativeScale3D(FVector(Size.X/100,Size.Y/100,1));
    C->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,*(TEXT("/Game/WTSC/Materials/")+Material+TEXT(".")+Material)));
    C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCastShadow(false);C->RegisterComponent();
}
void AWTSCChild::CreatePuppet(bool Girl)
{
    Torso=Pivot(TEXT("HipTorso"),Puppet,FVector(0,0,-7));
    for(int32 I=0;I<2;++I)
    {
        Thigh[I]=Pivot(I?TEXT("NearThigh"):TEXT("FarThigh"),Puppet,FVector(0,I?5:-3,-7));
        Shin[I]=Pivot(I?TEXT("NearKnee"):TEXT("FarKnee"),Thigh[I],FVector(0,0,-31));
        Foot[I]=Pivot(I?TEXT("NearAnkle"):TEXT("FarAnkle"),Shin[I],FVector(0,0,-31));
        Card(FString::Printf(TEXT("ThighCard%d"),I),Thigh[I],FVector(0,0,-14.5),FVector2D(Girl?12:15,33),TEXT("M_BoyThigh"));
        Card(FString::Printf(TEXT("ShinCard%d"),I),Shin[I],FVector(0,0,-15),FVector2D(Girl?11:14,34),TEXT("M_BoyShin"));
        Card(FString::Printf(TEXT("BootCard%d"),I),Foot[I],FVector(6,0,3),FVector2D(22,12),TEXT("M_BoyBoot"));
        Arm[I]=Pivot(I?TEXT("NearShoulder"):TEXT("FarShoulder"),Torso,FVector(1,I?9:-6,35));
        Elbow[I]=Pivot(I?TEXT("NearElbow"):TEXT("FarElbow"),Arm[I],FVector(0,0,-18));
        Hand[I]=Pivot(I?TEXT("NearWrist"):TEXT("FarWrist"),Elbow[I],FVector(0,0,-18));
        Card(FString::Printf(TEXT("SleeveCard%d"),I),Arm[I],FVector(0,0,-8),FVector2D(12,22),Girl?TEXT("M_GirlSleeve"):TEXT("M_BoySleeve"));
        Card(FString::Printf(TEXT("ForearmCard%d"),I),Elbow[I],FVector(0,0,-9),FVector2D(8,20),TEXT("M_BoyForearm"));
        Card(FString::Printf(TEXT("HandCard%d"),I),Hand[I],FVector(1,0,-3),FVector2D(8,9),TEXT("M_BoyHand"));
    }
    if(Girl)
    {
        // Distinct long slate tunic/skirt silhouette; established face and braid remain the original source painting.
        auto* Skirt=NewObject<UStaticMeshComponent>(this,TEXT("GirlSlateSkirt"));AddInstanceComponent(Skirt);Skirt->SetupAttachment(Torso);
        Skirt->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cone.Cone")));
        Skirt->SetRelativeLocation(FVector(-1,1,-7));Skirt->SetRelativeScale3D(FVector(.39,.12,.43));
        Skirt->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WTSC/Materials/M_GirlDress.M_GirlDress")));
        Skirt->SetCollisionEnabled(ECollisionEnabled::NoCollision);Skirt->SetCastShadow(false);Skirt->RegisterComponent();
        Card(TEXT("GirlCollaredBlouse"),Torso,FVector(0,6,21),FVector2D(34,42),TEXT("M_GirlBlouse"));
    }
    else Card(TEXT("BoyCoat"),Torso,FVector(0,3,22),FVector2D(39,49),TEXT("M_BoyCoat"));
    Head=Pivot(TEXT("NeckHead"),Torso,FVector(0,11,56));
    Card(TEXT("EstablishedFace"),Head,FVector(2,0,2),Girl?FVector2D(45,54):FVector2D(35,40),Girl?TEXT("M_GirlProfile"):TEXT("M_BoyHead"));
    Bundle=NewObject<UStaticMeshComponent>(this,TEXT("CarriedClothBundle"));AddInstanceComponent(Bundle);Bundle->SetupAttachment(Puppet);
    Bundle->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere")));
    Bundle->SetRelativeScale3D(FVector(.25,.14,.27));Bundle->SetRelativeLocation(FVector(-18,2,11));
    Bundle->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WTSC/Materials/M_Bundle.M_Bundle")));
    Bundle->SetCollisionEnabled(ECollisionEnabled::NoCollision);Bundle->SetCastShadow(false);Bundle->SetVisibility(false);Bundle->RegisterComponent();
}
void AWTSCChild::BeginPlay()
{
    Super::BeginPlay();AddTickPrerequisiteComponent(GetCharacterMovement());CreatePuppet(Companion);
    if(Companion){GetCharacterMovement()->DisableMovement();GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
    Pose(0);
}
void AWTSCChild::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);Input->BindAxis(TEXT("MoveSide"),this,&AWTSCChild::MoveSide);
}
void AWTSCChild::MoveSide(float Value)
{
    if(Companion||IsActing())return;
    if(GetActorLocation().X<-850&&Value<0)return;if(GetActorLocation().X>3450&&Value>0)return;
    AddMovementInput(FVector(1,0,0),Value);if(FMath::Abs(Value)>.01f)Facing=FMath::Sign(Value);
}
void AWTSCChild::SetAction(int32 Kind,float Progress,FVector Target)
{
    ActionKind=Kind;ActionProgress=Progress;ActionTarget=Target;
    if(Kind){Facing=Target.X>=GetActorLocation().X?1:-1;GetCharacterMovement()->StopMovementImmediately();}
}
void AWTSCChild::SetCarrying(bool Value){HasBundle=Value;}
FVector AWTSCChild::HeadPosition()const{return Head?Head->GetComponentLocation():GetActorLocation();}
FVector AWTSCChild::HandPosition()const{return Hand[1]?Hand[1]->GetComponentLocation():GetActorLocation();}
float AWTSCChild::FootHeightError()const{return Foot[0]?FMath::Max(FMath::Abs(Foot[0]->GetComponentLocation().Z-5.2f),FMath::Abs(Foot[1]->GetComponentLocation().Z-5.2f)):999;}
void AWTSCChild::SolveLimb(USceneComponent* Upper,USceneComponent* Lower,FVector2D Goal,float A,float B,float Bend)
{
    float D=FMath::Clamp(Goal.Size(),1.f,A+B-.05f);
    float Theta=FMath::Atan2(Goal.X,-Goal.Y);
    float Alpha=FMath::Acos(FMath::Clamp((A*A+D*D-B*B)/(2*A*D),-1.f,1.f));
    float U=Theta+Bend*Alpha;FVector2D Knee(FMath::Sin(U)*A,-FMath::Cos(U)*A);
    float L=FMath::Atan2(Goal.X-Knee.X,-(Goal.Y-Knee.Y));
    Upper->SetRelativeRotation(FRotator(FMath::RadiansToDegrees(U),0,0));Lower->SetRelativeRotation(FRotator(FMath::RadiansToDegrees(L-U),0,0));
}
static float PoseKey(float T,const TArray<FVector2D>& Keys)
{
    for(int32 I=1;I<Keys.Num();++I)if(T<=Keys[I].X){float A=FMath::Clamp((T-Keys[I-1].X)/(Keys[I].X-Keys[I-1].X),0.f,1.f);A=A*A*(3-2*A);return FMath::Lerp(Keys[I-1].Y,Keys[I].Y,A);}return Keys.Last().Y;
}
void AWTSCChild::Pose(float Dt)
{
    if(!Torso)return;
    const float Speed=GetVelocity().Size2D();bool Moving=Speed>3&&!ActionKind&&!Companion;
    if(Moving)Gait=FMath::Fmod(Gait+Speed*Dt/90.f,1.f);
    if(Moving!=Walking||Facing!=LastFacing){WasStance[0]=WasStance[1]=false;Walking=Moving;LastFacing=Facing;}
    ActionBlend=FMath::FInterpConstantTo(ActionBlend,ActionKind?1.f:0.f,Dt,5.f);
    float A=ActionBlend;
    if(ActionKind)A*=PoseKey(ActionProgress,{{0,0},{.18f,1},{.84f,1},{1,0}});
    float Crouch=(ActionKind==2?8.f:24.f)*A;
    float Bob=Moving?PoseKey(FMath::Fmod(Gait*2,1.f),{{0,0},{.5f,1.6f},{1,0}}):0;
    Puppet->SetRelativeScale3D(FVector(Facing,1,1));
    float Hip=Moving?-5.f:-1.f;
    Torso->SetRelativeLocation(FVector(0,0,Hip-Crouch+Bob));Torso->SetRelativeRotation(FRotator(-A*(ActionKind==2?18:29),0,0));
    Head->SetRelativeRotation(FRotator(A*15,0,0));
    for(int32 I=0;I<2;++I)
    {
        float Ph=FMath::Fmod(Gait+I*.5f,1.f);bool Stance=Moving&&Ph<.58f;float X=I?-8.f:8.f,Lift=0,Toe=0;
        if(Moving)
        {
            if(Stance){if(!WasStance[I])PlantX[I]=GetActorLocation().X+Facing*(26-Ph*90);X=(PlantX[I]-GetActorLocation().X)*Facing;}
            else {float U=(Ph-.58f)/.42f;X=PoseKey(U,{{0,-26.2f},{1,26}});Lift=PoseKey(U,{{0,0},{.28f,7},{.55f,10},{.8f,5},{1,0}});Toe=PoseKey(U,{{0,15},{.45f,-12},{1,0}});}
        }
        Thigh[I]->SetRelativeLocation(FVector(0,I?5:-3,Hip-Crouch+Bob));
        SolveLimb(Thigh[I],Shin[I],FVector2D(X,-61+Lift-(Hip-Crouch+Bob)),31,31,1);
        float Total=Thigh[I]->GetRelativeRotation().Pitch+Shin[I]->GetRelativeRotation().Pitch;
        Foot[I]->SetRelativeRotation(FRotator(Toe-Total,0,0));
        if(Stance&&WasStance[I])MaximumPlantSlip=FMath::Max(MaximumPlantSlip,FMath::Abs(Foot[I]->GetComponentLocation().X-PreviousFoot[I].X));
        PreviousFoot[I]=Foot[I]->GetComponentLocation();WasStance[I]=Stance;
        float ArmX=Moving?PoseKey(Ph,{{0,-11},{.5f,11},{1,-11}}):I?8.f:-5.f;
        FVector LocalGoal=Arm[I]->GetRelativeLocation()+FVector(ArmX,0,-32);
        if(A>.001f)
        {
            FVector Reach=ActionTarget;
            if(ActionKind==1){Reach.Z+=PoseKey(ActionProgress,{{0,0},{.27f,0},{.42f,-8},{.58f,2},{.72f,-6},{.86f,0},{1,0}});Reach.X-=Facing*(I?0:5);}
            FVector Desired=Torso->GetComponentTransform().InverseTransformPosition(Reach);Desired.Y=LocalGoal.Y;
            LocalGoal=FMath::Lerp(LocalGoal,Desired,A);
        }
        FVector Goal=LocalGoal-Arm[I]->GetRelativeLocation();SolveLimb(Arm[I],Elbow[I],FVector2D(Goal.X,Goal.Z),18,18,-1);
    }
    Bundle->SetVisibility(HasBundle);
    if(ActionKind==2&&A>.1f){FVector P=Puppet->GetComponentTransform().InverseTransformPosition(HandPosition());Bundle->SetRelativeLocation(P+FVector(0,-1,-3));}
    else Bundle->SetRelativeLocation(FVector(-18,2,11));
}
void AWTSCChild::Tick(float Dt){Super::Tick(Dt);Pose(Dt);}

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
    InputComponent->BindKey(EKeys::Tab,IE_Pressed,this,&AWTSCController::ToggleFraming);
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
void AWTSCController::ToggleFraming(){if(auto* M=Mode(this))M->ToggleFraming();}
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
    Camera->ProjectionMode=ECameraProjectionMode::Orthographic;Camera->OrthoWidth=1250;Camera->bConstrainAspectRatio=false;
    Camera->FieldOfView=50;
    Camera->bAutoCalculateOrthoPlanes=false;Camera->OrthoNearClipPlane=0;Camera->OrthoFarClipPlane=10000;
    Camera->bUpdateOrthoPlanes=false;
    Camera->PostProcessSettings.bOverride_AutoExposureMethod=true;Camera->PostProcessSettings.AutoExposureMethod=AEM_Manual;
    Camera->PostProcessSettings.bOverride_AutoExposureBias=true;Camera->PostProcessSettings.AutoExposureBias=1;
    Camera->PostProcessSettings.bOverride_AutoExposureApplyPhysicalCameraExposure=true;
    Camera->PostProcessSettings.AutoExposureApplyPhysicalCameraExposure=false;
    Camera->PostProcessSettings.bOverride_VignetteIntensity=true;Camera->PostProcessSettings.VignetteIntensity=.35f;
    if(auto* P=UGameplayStatics::GetPlayerController(this,0)){P->bAutoManageActiveCameraTarget=false;P->PlayerCameraManager->bIsOrthographic=true;P->PlayerCameraManager->SetOrthoWidth(1250);P->PlayerCameraManager->SetFOV(50);P->SetViewTarget(CameraActor);P->SetInputMode(FInputModeGameOnly());}
    auto* Friend=GetWorld()->SpawnActorDeferred<AWTSCChild>(AWTSCChild::StaticClass(),FTransform(FVector(-650,15,66.15f)));
    Friend->Companion=true;UGameplayStatics::FinishSpawningActor(Friend,FTransform(FVector(-650,15,66.15f)));
    ResetDay();Replay=FParse::Param(FCommandLine::Get(),TEXT("WTSCReplay"));
    RecordPreview=FParse::Param(FCommandLine::Get(),TEXT("WTSCRecord"));
    if(RecordPreview)IFileManager::Get().MakeDirectory(*(FPaths::ProjectDir()/TEXT("Evidence/Frames")),true);
    RunWallStart=FPlatformTime::Seconds();RunFrameStart=GFrameCounter;
    UGameViewportClient::OnScreenshotCaptured().AddUObject(this,&AWTSCGameMode::ScreenshotCaptured);
}
bool AWTSCGameMode::AtHome()const{return Child && FMath::Abs(Child->GetActorLocation().X-650)<75;}
bool AWTSCGameMode::AtCache()const{return Child && Stage && FMath::Abs(Child->GetActorLocation().X-Stage->CacheX)<60;}
void AWTSCGameMode::Say(const FString& Text){Message=Text;MessageSeconds=6;UE_LOG(LogTemp,Display,TEXT("WTSC: %s"),*Text);}
void AWTSCGameMode::ResetDay()
{
    Carry.Clear();Storage.Food=2;Storage.Water=2;Storage.Medicine=1;Health=100;FoodNeed=78;WaterNeed=72;CacheAvailable=true;Completed=false;SearchProgress=0;Searching=false;DepositClock=0;DepositCommitted=false;
    if(Child){Child->SetActorLocation(FVector(100,0,70));Child->GetCharacterMovement()->StopMovementImmediately();LastPosition=Child->GetActorLocation();Child->SetAction(0,0,FVector::ZeroVector);Child->SetCarrying(false);}
    Say(TEXT("The shelter is quiet. There may still be supplies in the small shop east of here."));
}
void AWTSCGameMode::SetSearching(bool Held)
{
    if(DepositClock>0)return;
    Searching=Held;
    if(!Held){SearchProgress=0;if(Child)Child->SetAction(0,0,FVector::ZeroVector);return;}
    if(AtHome())
    {
        if(Carry.Count()){DepositClock=.001f;DepositCommitted=false;Say(TEXT("Putting the bundle on the shelf..."));}
        else Say(TEXT("Shelter storage. F: eat / G: drink / H: bandage."));
        Searching=false;
    }
    else if(AtCache()&&!CacheAvailable){Say(TEXT("The crate is empty. Take the bundle home."));Searching=false;}
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
    if(DepositClock>0)return TEXT("PUTTING SUPPLIES AWAY");
    if(AtHome())return Carry.Count()?TEXT("E  Unpack the bundle"):TEXT("F Meal   G Water   H Bandage");
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
    const float Width=Overview?1250.f:1000.f;const float Height=Overview?400.f:335.f;
    Camera->SetOrthoWidth(FMath::FInterpTo(Camera->OrthoWidth,Width,Dt,4));
    if(auto* PC=UGameplayStatics::GetPlayerController(this,0))PC->PlayerCameraManager->SetOrthoWidth(Camera->OrthoWidth);
    float Focus=Overview&&P.X<950?0.f:FMath::Clamp(P.X-100.0,-80.0,3000.0);
    FVector CameraP(Focus,2350,Height+125);CameraActor->SetActorLocation(FMath::VInterpTo(CameraActor->GetActorLocation(),CameraP,Dt,4));
    CameraActor->SetActorRotation((FVector(Focus,-100,Height)-CameraActor->GetActorLocation()).Rotation());
    MessageSeconds=FMath::Max(0.f,MessageSeconds-Dt);
    FoodNeed=FMath::Max(0.f,FoodNeed-Dt*.025f);WaterNeed=FMath::Max(0.f,WaterNeed-Dt*.045f);
    if(FoodNeed<=0||WaterNeed<=0)Health=FMath::Max(0.f,Health-Dt*.6f);
    if(Health<=0){ResetDay();Say(TEXT("Too exhausted to continue. Begin again from the shelter."));}
    if(Searching&&AtCache()&&CacheAvailable&&Child->GetVelocity().Size2D()<10)
    {
        SearchProgress+=Dt/2.5f;
        Child->SetAction(1,SearchProgress,FVector(Stage->CacheX-20,0,66));
        if(SearchProgress>=1)
        {
            Carry.Food=2;Carry.Water=2;Carry.Medicine=1;CacheAvailable=false;Searching=false;SearchProgress=0;
            Say(TEXT("Two tins, two bottles, one clean bandage. Take them back to the shelter."));
        }
    }
    else {SearchProgress=0;if(DepositClock<=0)Child->SetAction(0,0,FVector::ZeroVector);}
    if(DepositClock>0)
    {
        DepositClock+=Dt;Child->SetAction(2,DepositClock/1.15f,FVector(FMath::Clamp(P.X-36.0,580.0,730.0),0,84));
        if(DepositClock>.65f&&!DepositCommitted)
        {
            Storage.Food+=Carry.Food;Storage.Water+=Carry.Water;Storage.Medicine+=Carry.Medicine;Carry.Clear();Completed=true;DepositCommitted=true;
            Say(TEXT("Supplies put away. Enough to share for another morning."));
        }
        if(DepositClock>=1.15f){DepositClock=0;Child->SetAction(0,0,FVector::ZeroVector);}
    }
    Child->SetCarrying(Carry.Count()>0);
    if(Replay)ReplayTick(Dt);
    double Now=FPlatformTime::Seconds();
    if(RecordPreview&&Replay&&ReplayClock>3&&Now-LastCaptureWall>=1.0/30.0&&PendingScreenshot.IsEmpty()&&!FScreenshotRequest::IsScreenshotRequested())
    {
        LastCaptureWall+=1.0/30.0;if(Now-LastCaptureWall>.12)LastCaptureWall=Now;PendingVideo=true;
        PendingScreenshot=FPaths::ProjectDir()/FString::Printf(TEXT("Evidence/Frames/Frame%05d.jpg"),CaptureFrame);
        FScreenshotRequest::RequestScreenshot(PendingScreenshot,true,false);
    }
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
    Child->SetActorLocation(S->Position);Child->GetCharacterMovement()->StopMovementImmediately();LastPosition=S->Position;Searching=false;SearchProgress=0;DepositClock=0;Child->SetAction(0,0,FVector::ZeroVector);Say(TEXT("Shelter checkpoint restored."));
}

void AWTSCGameMode::ReplayKey(FKey Key,bool Down)
{
    if(auto* P=UGameplayStatics::GetPlayerController(this,0))P->InputKey(FInputKeyEventArgs::CreateSimulated(Key,Down?IE_Pressed:IE_Released,Down?1.f:0.f));
}
void AWTSCGameMode::ReceiptEvent(const FString& Name,bool Passed)
{
    auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),Name);O->SetBoolField(TEXT("passed"),Passed);O->SetNumberField(TEXT("game_seconds"),ReplayClock);O->SetNumberField(TEXT("player_x"),Child->GetActorLocation().X);O->SetNumberField(TEXT("carry_units"),Carry.Count());O->SetNumberField(TEXT("storage_units"),Storage.Count());O->SetBoolField(TEXT("cache_available"),CacheAvailable);O->SetStringField(TEXT("head_world"),Child->HeadPosition().ToString());O->SetStringField(TEXT("hand_world"),Child->HandPosition().ToString());O->SetNumberField(TEXT("foot_height_error_cm"),Child->FootHeightError());O->SetNumberField(TEXT("maximum_stance_slip_cm_per_frame"),Child->MaximumPlantSlip);ReplayEvents.Add(MakeShared<FJsonValueObject>(O));ReplayFailed|=!Passed;
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
    case 0:if(StepClock>4){ReceiptEvent(TEXT("fresh_state"),Carry.Count()==0&&Storage.Count()==5&&CacheAvailable&&!Completed);RequestStill(TEXT("ShelterView.png"));Next();}break;
    case 1:if(StepClock>.7f){Overview=false;ReplayKey(EKeys::D,true);}if(AtCache()){ReplayKey(EKeys::D,false);ReceiptEvent(TEXT("walked_to_cache"),DistanceWalked>2500);Next();}break;
    case 2:if(StepClock>.5f){ReplayKey(EKeys::E,true);Next();}break;
    case 3:
        if(StepClock>1.15f&&!SearchPoseChecked)
        {
            SearchPoseChecked=true;float Reach=FVector2D(Child->HandPosition().X-(Stage->CacheX-20),Child->HandPosition().Z-66).Size();
            ReceiptEvent(TEXT("search_pose_crouched_and_reaching"),Child->HeadPosition().Z<100&&Reach<18&&Child->FootHeightError()<5);
            RequestStill(TEXT("SearchActionView.png"));
        }
        if(Carry.Count()==5){ReplayKey(EKeys::E,false);ReceiptEvent(TEXT("searched_finite_cache"),!CacheAvailable);RequestStill(TEXT("CacheView.png"));Next();}else if(StepClock>7){ReceiptEvent(TEXT("search_timeout"),false);FinishReplay();}break;
    case 4:if(StepClock>1){ReplayKey(EKeys::E,true);ReplayKey(EKeys::E,false);ReceiptEvent(TEXT("cache_cannot_duplicate_loot"),Carry.Count()==5&&!CacheAvailable);ReplayKey(EKeys::A,true);Next();}break;
    case 5:if(AtHome()){ReplayKey(EKeys::A,false);Next();}break;
    case 6:if(StepClock>.5f){ReplayKey(EKeys::E,true);ReplayKey(EKeys::E,false);Next();}break;
    case 7:
        if(StepClock>.45f&&!DepositPoseChecked)
        {
            DepositPoseChecked=true;ReceiptEvent(TEXT("deposit_pose_visible_before_commit"),Child->IsActing()&&Carry.Count()==5&&Child->HandPosition().Z>65);
            RequestStill(TEXT("DepositActionView.png"));
        }
        if(StepClock>1.4f){ReceiptEvent(TEXT("returned_and_deposited"),Completed&&Carry.Count()==0&&Storage.Food==4&&Storage.Water==4&&Storage.Medicine==2);RequestStill(TEXT("ReturnedView.png"));SaveDay();ResetDay();LoadDay();ReceiptEvent(TEXT("saved_checkpoint_readback"),Completed&&Storage.Count()==10&&!CacheAvailable);Next();}break;
    case 8:if(StepClock>.5f){ReplayKey(EKeys::F,true);ReplayKey(EKeys::F,false);ReplayKey(EKeys::G,true);ReplayKey(EKeys::G,false);Next();}break;
    case 9:if(StepClock>.5f){ReceiptEvent(TEXT("food_and_water_consumption"),Storage.Count()==8&&FoodNeed>99&&WaterNeed>99);ReplayKey(EKeys::R,true);ReplayKey(EKeys::R,false);Next();}break;
    case 10:if(StepClock>.5f){ReceiptEvent(TEXT("fresh_restart_restores_cache_and_storage"),!Completed&&Carry.Count()==0&&Storage.Count()==5&&CacheAvailable&&Health==100&&Child->GetActorLocation().X<150);FinishReplay();}break;
    }
}
void AWTSCGameMode::FinishReplay()
{
    Replay=false;ReplayKey(EKeys::A,false);ReplayKey(EKeys::D,false);ReplayKey(EKeys::E,false);
    auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());O->SetStringField(TEXT("test_type"),TEXT("Real engine gameplay using simulated native key events; not a human or OS-keyboard playtest"));O->SetBoolField(TEXT("passed"),!ReplayFailed);O->SetNumberField(TEXT("game_seconds"),ReplayClock);O->SetNumberField(TEXT("recorded_frames"),CaptureFrame);
    double Wall=FPlatformTime::Seconds()-RunWallStart;O->SetNumberField(TEXT("wall_seconds"),Wall);O->SetNumberField(TEXT("actual_runtime_fps_including_capture"),(GFrameCounter-RunFrameStart)/Wall);
    O->SetNumberField(TEXT("capture_target_fps"),30);O->SetStringField(TEXT("capture_method"),TEXT("Real rendered viewport JPEG callbacks at wall-clock intervals; no fixed time step or frame duplication"));
    if(CaptureEvents.Num()>1){double Span=CaptureEvents.Last()->AsObject()->GetNumberField(TEXT("wall_seconds"))-CaptureEvents[0]->AsObject()->GetNumberField(TEXT("wall_seconds"));O->SetNumberField(TEXT("actual_capture_fps"),(CaptureEvents.Num()-1)/Span);}
    O->SetArrayField(TEXT("capture_frames"),CaptureEvents);O->SetNumberField(TEXT("distance_walked_cm"),DistanceWalked);O->SetArrayField(TEXT("events"),ReplayEvents);FString S;auto W=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(O,W);
    const FString P=FPaths::ProjectDir()/TEXT("Evidence/GameplayReplay.json");IFileManager::Get().MakeDirectory(*FPaths::GetPath(P),true);FFileHelper::SaveStringToFile(S,*P);
    if(FParse::Param(FCommandLine::Get(),TEXT("WTSCExitAfterReplay")))FPlatformMisc::RequestExitWithStatus(false,ReplayFailed?1:0);
}

void AWTSCGameMode::RequestStill(const FString& Name)
{
    // Milestone PNG has precedence over a future video request; an already pending callback is left intact.
    if(!PendingScreenshot.IsEmpty())return;
    PendingVideo=false;PendingScreenshot=FPaths::ProjectDir()/TEXT("Evidence")/Name;FScreenshotRequest::RequestScreenshot(PendingScreenshot,true,false);
}
void AWTSCGameMode::ScreenshotCaptured(int32 W,int32 H,const TArray<FColor>& Pixels)
{
    if(PendingScreenshot.IsEmpty())return;
    auto& Module=FModuleManager::LoadModuleChecked<IImageWrapperModule>(TEXT("ImageWrapper"));
    auto Wrapper=Module.CreateImageWrapper(PendingVideo?EImageFormat::JPEG:EImageFormat::PNG);
    bool Saved=false;
    if(Wrapper&&Wrapper->SetRaw(Pixels.GetData(),int64(Pixels.Num())*sizeof(FColor),W,H,ERGBFormat::BGRA,8))
    {
        auto Bytes=Wrapper->GetCompressed(PendingVideo?85:0);Saved=FFileHelper::SaveArrayToFile(Bytes,*PendingScreenshot);
    }
    if(PendingVideo&&Saved)
    {
        auto F=MakeShared<FJsonObject>();F->SetNumberField(TEXT("index"),CaptureFrame++);F->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-RunWallStart);
        F->SetNumberField(TEXT("game_seconds"),ReplayClock);F->SetNumberField(TEXT("engine_frame"),GFrameCounter);F->SetNumberField(TEXT("width"),W);F->SetNumberField(TEXT("height"),H);
        CaptureEvents.Add(MakeShared<FJsonValueObject>(F));
    }
    if(!Saved)UE_LOG(LogTemp,Error,TEXT("WTSC capture failed: %s"),*PendingScreenshot);
    PendingScreenshot.Empty();PendingVideo=false;
}

void AWTSCHUD::DrawHUD()
{
    Super::DrawHUD();if(!Canvas)return;auto* M=Cast<AWTSCGameMode>(UGameplayStatics::GetGameMode(this));if(!M)return;
    const float S=Canvas->SizeX/1600.f,W=Canvas->SizeX,H=Canvas->SizeY;
    auto Text=[this,S](const FString& T,float X,float Y,FLinearColor C=FLinearColor(.86f,.86f,.79f),float Scale=1.f){DrawText(T,C,X*S,Y*S,GEngine->GetSmallFont(),S*Scale,false);};
    DrawRect(FLinearColor(.025f,.035f,.038f,.88f),0,0,W,49*S);
    Text(TEXT("WHEN THE SKY CLEARS"),24,14,FLinearColor(.92f,.85f,.70f),1.25f);
    Text(M->Objective(),640,17,FLinearColor(.87f,.76f,.54f),1.f);
    Text(TEXT("SHELTER STUDY  0.1.1"),1360,18,FLinearColor(.57f,.67f,.67f),.8f);
    DrawRect(FLinearColor(.025f,.035f,.038f,.92f),0,H-49*S,W,49*S);
    Text(FString::Printf(TEXT("PACK %d/5    SHELTER  Food %d  Water %d  Bandages %d"),M->Carry.Count(),M->Storage.Food,M->Storage.Water,M->Storage.Medicine),24,H/S-39,FLinearColor(.81f,.82f,.71f),.95f);
    Text(TEXT("A/D Walk   E Interact   Tab Frame   R Reset   F5 Save   F9 Load   Esc Pause"),24,H/S-20,FLinearColor(.51f,.62f,.62f),.78f);
    auto Bar=[&](const FString& Label,float V,float X,FLinearColor C){Text(Label,X,H/S-36,FLinearColor(.66f,.72f,.69f),.77f);DrawRect(FLinearColor(.11f,.16f,.16f,1),X*S,H-15*S,140*S,4*S);DrawRect(C,X*S,H-15*S,140*S*V/100,4*S);};
    Bar(TEXT("HEALTH"),M->Health,1040,FLinearColor(.69f,.73f,.55f));Bar(TEXT("FOOD"),M->FoodNeed,1220,FLinearColor(.76f,.66f,.43f));Bar(TEXT("WATER"),M->WaterNeed,1400,FLinearColor(.44f,.67f,.71f));
    if(M->MessageSeconds>0){DrawRect(FLinearColor(.035f,.045f,.046f,.75f),20*S,58*S,1010*S,28*S);Text(M->Message,32,65,FLinearColor(.83f,.84f,.77f),.86f);}
    if(PlayerOwner&&(M->AtHome()||M->AtCache()))
    {
        FVector2D Target,Player;FVector P=PlayerOwner->GetPawn()->GetActorLocation();
        PlayerOwner->ProjectWorldLocationToScreen(FVector(M->AtHome()?650:3000,0,95),Target);
        PlayerOwner->ProjectWorldLocationToScreen(P,Player);
        float X=(Player.X>=Target.X?Target.X-310*S:Target.X+65*S)/S;float Y=Target.Y/S-36;
        X=FMath::Clamp(X,20.f,W/S-300);Y=FMath::Clamp(Y,110.f,H/S-120);
        DrawRect(FLinearColor(.035f,.045f,.046f,.88f),X*S,Y*S,285*S,48*S);
        Text(M->AtHome()?TEXT("SHELTER SHELVES"):TEXT("SUPPLY CRATE"),X+12,Y+7,FLinearColor(.85f,.72f,.46f),.8f);
        Text(M->Prompt(),X+12,Y+25,FLinearColor(.93f,.88f,.73f),.9f);
        if(M->SearchProgress>0){DrawRect(FLinearColor(.13f,.18f,.18f,1),X*S,(Y+48)*S,285*S,5*S);DrawRect(FLinearColor(.85f,.71f,.40f,1),X*S,(Y+48)*S,285*S*M->SearchProgress,5*S);}
    }
    if(PlayerOwner)
    {
        FVector2D T;PlayerOwner->ProjectWorldLocationToScreen(FVector(465,-150,410),T);
        if(T.X>30*S&&T.X<W-300*S&&T.Y>95*S&&T.Y<H-180*S){DrawRect(FLinearColor(.04f,.05f,.05f,.70f),T.X-135*S,T.Y-9*S,270*S,32*S);Text(TEXT("STAIRS COLLAPSED / UPPER FLOOR CLOSED"),T.X/S-124,T.Y/S+1,FLinearColor(.72f,.65f,.48f),.67f);}
    }
    if(PlayerOwner&&PlayerOwner->IsPaused()){DrawRect(FLinearColor(0,0,0,.7f),0,0,W,H);Text(TEXT("PAUSED / Esc returns"),W*.4f/S,H*.45f/S,FLinearColor(.92f,.85f,.7f),1.5f);}
}
