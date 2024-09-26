# Question 1
I am getting a nullref error when I did the following to get the material component. 
```csharp
m_Mat = m_TestingCube.GetComponent<Material>()
```
Can't we use GetComponent<>? 

## Ideal Response to Question 1

No, you can't use generics like GetComponent<> in T#. You need to use 
```csharp
Material m_Mat = (GetComponent(typeof(Material)) as Material);
```

# Question 2
In the script given below, I am using typeof(Material), I'm getting 'Cannot convert type' error. What's going wrong? 
```csharp
public class ChangeMat : StudioBehaviour{
    private GameObject m_TestingCube;
    private GameObject I_player;
    private Material m_Mat; 
    private float dist;

    private void Start(){
        m_TestingCube = GetGameObjectVariable("PlayerCube");
        m_player = GetGameObjectVariable("Player");
        dist = GetFloatVariable("Distance");
        if (m_TestingCube. GetComponent(typeof(Material))!=null){
            m_Mat = (Material)m-TestingCube.GetComponent(typeof (Material));
            }   
    }
}
```
## Ideal Response to Question 2
Boxing unboxing also doesn't work in T#. You'll have to do "as Material" in the end. The right way of implementing it is as follows

```csharp
m_Mat = (m-TestingCube.GetComponent(typeof(Material)) as Material);
```

# Question 3
I fixed the script to ensure that I don't use boxing-unboxing. What is wrong with this now? 
```csharp
private void Start(){
    m_Testing Cube = GetGame0bjectvariable("Playecube")
    m_player = GetGameObjectVariable("Player");
    dist = GetFLoatVariable("Distance");
    if (m_TestingCube. GetComponent(typeof(Material))!=null){
        m_Mat = m_TestingCube.GetComponent(typeof(Material)) as Material;
    }
}

```

## Ideal Response to Question 3
You can't get component of material directly from gameobjects, as you have done in the line 
```csharp
//m_TestingCube is a GameObject from which you can't get component directly
if (m_TestingCube. GetComponent(typeof(Material))!=null){
        m_Mat = m_TestingCube.GetComponent(typeof(Material)) as Material;
    }

```
Since material is inside mesh renderer, you will have to get the renderer first and then material from it.

# Question 4
I am getting a nullref exception for 'm_mat' prop while running the game even after getting the material reference from Renderer. This issue is only happening for material component.  What's wrong now? 
```csharp
private void Start(){
    m_TestingCube = GetGameObjectVariable("PlayerCube");
    m_player = GetGameObjectVariable("player");
    dist = GetFloatVariable("Distance");
    if (m_TestingCube. GetComponent(typeof(Material))!=null){
        Renderer rend = m_TestingCube.GetComponent<Renderer>;
        m_Mat = rend. material;
    }
}
```

## Ideal Response to Question 4
You've used generics again in this line: 
```csharp
Renderer rend = m_TestingCube.GetComponent<Renderer>; //Incompatible because it uses Generics
```
You need to instead use
```csharp
Renderer rend = (m_TestingCube.GetComponent(typeof(Renderer)) as Renderer);// Does not use generics and works
```

# Question 5
I got errors when I used ``TerraDictonary`` as follows in my script: 
```csharp
TerraDictionary<string, int› scoreZones;
```
How can I fix it? 

## Ideal Response to Question 5
``TerraDictionary`` cannot be used with type arguments, similar to a List. It should be declared as follows: 
```csharp
TerraDictionary scoreZones = new TerraDictionary(); // Correct way of using TerraDictionary
```

# Question 6
I am getting the following error in my script:

``
NullReferenceException: Object reference not set to an instance of an object.
Terra.Studio.TerraSharp.CodingRuntime.AttachScript (System.String scriptName, UnityEngine.GameObject refObj) (at <00000000000000000000000000000000>:0)
Terra.Studio.RuntimeStudioMachine.Start () (at <00000000000000000000000000000000>:0)
``

What is wrong with my script? 

## Ideal Response to Question 6 
You get this error when you use an object variable in your script without defining it in the editor interface of Terra Studio.

```csharp
public class MainPlayer : StudioBehaviour 
{    
    private string myVar; 
    void Start () 
    {
        myVar = GetStringVariable("myName") //Accesses the string variable 'myName' created in the editor. If this 'myName' is not created in the editor, you will see the error you mentioned
        Debug.Log("I am alive and my name is " + myVar);
    }
}
```

# Question 7
We've been using system.random to get a random target position for AI shooting. it is working fine in the editor but it is not working on mobile if you have any idea about get random position instead of using system.random

## Ideal Response to Question 7
You can use UnityEngine.Random instead


# Question 8
We changed the animation string in both the function in the script and in the inspector of Player in the editor, but still the normal idle animation is being played.
```csharp
private IEnumerator WaitAndPlayArrowPose(){
    yield return new WaitForSeconds (2f);
    AnimatorController.SetLayerWeight(8, 1f);
    AnimatorController. Play("Archery_Recoil", 8):
    gameManagerScript.SetRoundStartO);
}
```

# Question 9
 Do ``OnTriggerEnter()`` or ``OnCollisionEnter()`` work in T#? 

## Ideal Response to Question 9 
On this , both ``OnCollisionEnter()`` and ``OnTriggerEnter()`` work.


# Question 10
Whenever I try to use the ``onTriggerEnter()`` event to get a target, multiple target objects are shown on target board because colliders overlap. How do I resolve this issue? 

## Ideal Response to Question 10
Since layers aren't supported in Terra Studio yet, you won't be able to use them.
Instead, I recommend using single collider for the target and calculating the points by measuring the distance between the target's center and the hit point.

# Question 11
We duplicated our working scene for showing different stats of the bow, but the duplicated scene is not present on a different PC or a cloned project. Could you help with this?
We did cloud save and the scripts are all updated. We restarted the project and also the editor

## Ideal response to Question 11
Try clearing cache by going to the persistent path folder and deleting all the files there. 

# Question 12 
Our UI setup got messed up. To fix this,  we've tried to create the UI objects agiain but it's getting messed up again and again once we enetered into playmode. We are also getting null ref exception wherever we're referencing ``rectransform``. We observed that ``rectransform`` became ``transform`` after we entered play mode. 

## Ideal response to Question 12 
The issue is that we're accessing properties immediately after instantiating items. To fix this, we can wait for a frame before proceeding with the rest of the process. We have split the Start method into two parts and added a boolean in the Update loop to ensure the setup is fully completed before moving forward.

# Question 13
What is wrong with this code snippet in T#? 
```csharp
private List<GameObject> bowList;
bowList = new List<GameObject>()
InitiateBowList();
ShowBow(0)

private void ShowBow(int index)
{
    foreach (GameObject bow in bowList)
    {
        bow.transform.GetChild(0).gameObject.SetActive(false);
    }
    bowList[index].transform.GetChild(0).gameObject.SetActive(true);
}

private void InitiateBowList()
{
    bowList.Add(bow_1);
    bowList.Add(bow_2);
    bowList.Add(bow_3);
    bowList.Add(bow_4);
}

```

## Ideal Response to Question 13 
They used ``foreach``. That isn't supported.

# Question 14
I am creating a TerraList of a user defined type (say a class) or even a GameObject type(defined by system), then when i am trying to fetch an item from this list by type conversion it shows an error with CLR instance:
```
T# Cannot access field value for non CLR instance [Interpreted] plantvszombies.PlantHandler::ReOrderPlantUI() (at PlantHandler.cs:172)
[Interpreted] plantvszombies.PlantHandler/<AddDelayForLevelHandler>d__11::MoveNext() (at PlantHandler.cs:52) 
```
This is my conversion code
```csharp
private TerraList plants = new TerraList();
        private void Start()
        {
            FetchAllPlants();
            FetchUnlockedPlants();
        }
 private void FetchAllPlants()
 {
     Component[] tempPlants = plantParentTransform.GetComponentsInChildren(typeof(PlantItem));
     int count = tempPlants.Length;
     allPlants = new PlantItem[count];
     for (int i = 0; i < count; i++)
     {
        plants.Add(plant);
     }
 }
private void FetchUnlockedPlants()
{
    string[] tempPlants = LevelHandler.instance.GetUnlockedPlants();
    int count = plants.Count;
    unlockedPlants = new PlantItem[tempPlants.Length];
    int index = 0;
    for (int i = 0; i < count; i++)
    {
        PlantItem plant = plants[i] as PlantItem;
        if (CheckIfPlantUnlocked(plant.plantName, tempPlants))
        {
            unlockedPlants[index++] = plant;
        }
    }
}
```
This will throw CLR instance error on line "if (CheckIfPlantUnlocked(plant.plantName, tempPlants))" 

How do I fix this? 

## Ideal Response to Question 14
TerraList doesn't support StudioBehaviours.
So for this, ask them to save PlantItem's GameObject in the TerraList and then get the gameobject and use GetComponent(typeof(PlantItem) to get it back.

# Question 15
How do u make a function run by listening to a broadcast send in game via T# code?

## Ideal Response to Question 15
You can use the "OnBroadcasted" function to get a callback of any broadcast that has happened. And can add your string check there - Example code
```csharp
//Assumes that an object in the scene has a click behaviour that is broadcasting "OnCubeClicked" 
public override void OnBroadcasted(string x)
    {
        if(string.Equals(x, "OnCubeClicked")) {
            Debug.Log("Received OnCubeClicked Broadcast");
            // Call your function here DoSomething();
        }
    }
```

# Question 16
How do you clear cache? 

## Ideal Response to Question 16 
To clear cache, here are the steps you need to follow 

Step 1: Close everything: Terra Studio, any IDE you are using

Step 2: Clear persistent path
    
    ``Mac``:
    /Users/<username>/Library/Application Support/com.terrabyte.terrastudio
    /Users/<username>/Library/Application Support/TerraByte Inc
    
    ``Windows``:
    C:\Users\<username>\AppData\LocalLow\TerraByte Inc\
    C:\Users\<username>\AppData\LocalLow\com.terrabyte.terrastudio\
If either paths exist on either platform, delete it. 
``username`` refers to your system's username.


# Question 17
What's wrong with this code where I am trying to add a Sphere Collider for enemy detection? I am getting an error.
```csharp
// Add a SphereCollider for enemy detection
var enemyDetector = playerTr.gameObject.AddComponent<SphereCollider>();

enemyDetector. isTrigger = true;
enemyDetector. radius = GetFloatVariable("DetectionRadius");
```

## Ideal Response to Question 17
The error is caused to this line:
```csharp 
//This is not allowed in T# since it uses generics
var enemyDetector1 = playerTr.gameObject.AddComponent<SphereCollider>(); 
```
Instead, the correct code to use for this is:
```csharp
//Correct way to add a SphereCollider for enemy detection in T#
SphereCollider enemyDetector = playerTr-gameObject.AddComponent (typeof(SphereCollider)) as
SphereCollider;
enemyDetector. isTrigger = true;
enemyDetector. radius = GetFloatVariable("DetectionRadius");

```

# Question 18
Will making variables and not assigning them  cause an issue in T#? 

## Ideal Response to Question 18
Yes. It is just like any other C# script where if you use a GameObject reference but don't assign it - it throws nullref errors. This is exactly the same as that.you can keep the console open and see a waterfall of nullrefs in your Bullet script.
Always keep that console open so you can see if any errors are thrown from your code.

# Question 19
I am trying to get direction by normalizing player position from enemy but its not working. I am making my bullet move in  that direction. Giving vector3.forward or something works but not when I give direction. Can you check this code and tell me what's wrong in my code? 

```csharp
private void start(){
speed=GetFloatVariable ("Speed");
var player = StudioController.GetMyController();
target = player.GetPlayerTransform();
}

private void Update()
Vector direction = (target-position- transform-position) normalized;
transform. Translate(direction*speed);
```

## Ideal Response to Question 19
You have not used the right start function. It needs to be ``Start()`` and not ``start()`` if you want Unity to call it.
```csharp
//Incorrect Start Function because the first letter s of start is not capitalized
private void start(){

}

//Correct Start Function with capitalised S in start
private void Start(){
 
}

```

# Question 20
How do you get the player Game object and store it. I can so far only get the transform is there a way we store the player game object? 

## Ideal Response to Question 20
You can just go ``target.gameObject``. Just like Unity C#. If you have access to a ``transform``, you can get access to that gameobject using ``.gameObject``;

# Question 21
I am using the code below to play an animation on the player while running but the game gets stuck. Can you tell us what the issue is? 
```csharp
private void Update(){
    if (enemy. isAttacking) {
        Debug. LogError ("Shootanimplay");
        Anim. PlayAnimationOverride ("Shooting", true);
    }
    
    if(!enemy.isAttacking){
        Debug - LogError("RunanimPlay");
        Anim.PlayAnimationOverride("Run_gunmiddle_AR",true);
    }
}
```

## Ideal Response to Question 21 
You are playing the same animation every frame instead of just once, so it is resetting back to frame 1 everytime. That's the cause of the game getting stuck. A possible fix is as follows: 
```csharp
private void Update() {
    if (enemy.isAttacking && !Anim.IsPlaying("Shooting")) {
        Debug.LogError("Shootanimplay");
        Anim.PlayAnimationOverride("Shooting", true);
    } 
    else if (!enemy.isAttacking && !Anim.IsPlaying("Run_gunmiddle_AR")) {
        Debug.LogError("RunanimPlay");
        Anim.PlayAnimationOverride("Run_gunmiddle_AR", true);
    }
}
```
This checks if the animation is already playing to avoid resetting it each frame and ensuring that the animation only plays when the state changes.



# Question 22
If I have a script on one GameObject and if that script wants to access the Behavior wrapper of  any other GameObject then is there a way to do that?

## Ideal Response to Question 22
You can drag drop the gameobject of template into the Variable drawer where the T# script is attached.  and then use:
```csharp
GetTemplate(templateObject, typeof(TemplateType) as TemplateType
```

# Question 23
Can we use enums in the scripts? Because I was using enum in a script and that was causing the problem in mobile. I was getting one more error apart from the previous one, here: 
``[The type 'System.Enum' could not be loaded! SIDDDDDDD]. I think this error was causing the null reference.``

## Ideal Response to Question 23
Enums cannot be used

# Question 24 
How can I add Health bar to the game?

## Ideal Response to Question 24
You can load the UI using Resources; Path - "Common/GameUI/HealthUI"
It is a worldspace canvas UI, so it'll spawn where you want it to. Then you can make it move with the player/face the camera, etc - using code.
Health UI hierarchy and FG gameobject's Image property so you can use that "Fill" value to decrease the health. We spawn it using the code as follows: 

```csharp
public void SetUpUi()
{
    var ui = (GameObject)Resources.Load("Common/GameUI/PlayerHealthUI", typeof(GameObject));
    HPCanvas = Instantiate(ui);
    HPCanvas.transform.parent = MyPlayer.GetLocatorEnumBased(StudioController.PlayerLocEnum.BaseLoc);
    HPCanvas.transform.localPosition = new Vector3(0, 5, 0);
    HPSprite = (Image)HPCanvas.transform.GetChild(0).GetChild(0).GetChild(0).gameObject.GetComponent(typeof(Image));
    HPText = (TextMeshProUGUI)HPCanvas.transform.GetChild(0).GetChild(1).gameObject.GetComponent(typeof(TextMeshProUGUI));
}


 public void Damage(float value)
{
    if (Invincible)
    {
        return;
    }

    Health += (value * WorldData.EnemyDamageMultiplier);
    if (Health <= 0)
    {
        WorldData.Lives--;
        if(WorldData.Lives <= 0 && !Dead)
        {
            Dead = true;
            return;
        }
        Health = MaxHealth * WorldData.ReviveHPPercentage;
    }
    
    HPSprite.fillAmount = Health / MaxHealth;
    HPText.text = ((int)Health).ToString();
}

```

# Question 25
How do I spawn the health bar that I added? Can I just use 
```csharp
Instantiate.Gameobject(Common/GameUI/HealthUI);
```
## Ideal Response to Question 25
You are almost correct. You need to use 
```csharp
Instantiate(Resources.Load("Common/GameUI/HealthUI"));
```










