# Space Marshal - Game Documentation
## Type
Example

## Overview
Space Marshal is a tactical top-down stealth-action game set in outer space, featuring specialist Burton's fight against criminal elements. The game emphasizes tactical combat and stealth over traditional run-and-gun gameplay.

## Core Gameplay Loop
```
Start Mission → Plan Approach → Combat/Stealth → Collect Rewards → Complete Mission
```

## Primary Systems

### Combat Mechanics
- **Control Scheme**:
  - Tilted top-down perspective
  - Tap to reload
  - Tap to crouch (sneak mode)
  - Tap weapon icons to switch
  - Directional drag for shooting
  - Drag controls for grenade throws

### Stealth System
- Sneak mode mechanics
- Multiple approach options:
  - Aggressive combat
  - Stealth takedowns
  - Mixed tactical approach

### Mission Structure
- **Time per Level**: 5-7 minutes
- **Chapter Organization**:
  - 10 total levels
  - 2 chapters/locations
  - Progressive difficulty scaling

## Gameplay Elements

### Core Mechanics
- Health management
- Ammo conservation
- Tactical positioning
- Enemy engagement choices

### Collection Systems
- Health pickups
- Ammo reserves
- Mission-specific collectibles
- Enemy drops (varies by approach)

## Meta Progression

### Mission Flow
1. Start mission
2. Choose approach
3. Execute plan
4. Complete objectives
5. Collect rewards

### Reward Systems
- Coin collection
- XP accumulation
- New gear unlocks
- Mission completion bonuses

## Technical Details
- Top-down camera system
- Touch-based controls
- Stealth mechanics integration
- Combat balancing

---

# Code Implementation

## AnalyticsAndLeaderboard.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

/// <summary>
/// This Script manages the upload of variables for the analytics and leaderboard
/// </summary>
public class AnalyticsAndLeaderboard : StudioBehaviour
{
    public static int NoD;

    private static int coinEnter;
    private static int coinExit;

    private static int initialScore;
    private static string gunType;
    private static string levelInfo, buyInfo, currencyInfo;

    // Updates the value of the KillCount to sync with the leaderboard
    public static void SetKillCount()
    {
        int kills = PlayerController.GetEnemyKills();
        StudioLeaderboard.Set("KillCount", kills);
        Debug.Log("KillCount " + kills);
    }

    // Stores the value of coins when the player enters the shop
    public static void SetCoinEnter()
    {
        coinEnter = PlayerBase.GetScore();
        StudioPrefs.SetInt("CoinEnter", coinEnter);
    }

    // The currencyInfo is updated for Analytics
    public static void SetCoinExit()
    { 
        coinExit = PlayerBase.GetScore();
        coinEnter = StudioPrefs.GetInt("CoinEnter");

        currencyInfo = coinEnter + "," + coinExit;

        StudioPrefs.SetString("CurrencyInfo", currencyInfo);
        StudioAnalytics.SetGameAnalyticsPrefs(levelInfo, buyInfo, currencyInfo, "", "", "");

        Debug.Log("CurrencyInfo " + currencyInfo);
    }

    // Updates levelInfo based on the way the player exited the level (Victory, Defeat, Back Button)
    public static void SetExitType(string exitType)
    {
        levelInfo = StudioPrefs.GetString("LevelInfo");
        levelInfo += exitType + "||";

        StudioPrefs.SetString("LevelInfo", levelInfo);
        StudioAnalytics.SetGameAnalyticsPrefs(levelInfo, buyInfo, currencyInfo, "", "", "");
        Debug.Log("LevelInfo " + levelInfo);

        SetCoinExit();
    }

    // Updates BuyInfo based on the purchased weapon
    public static void SetBuyInfo()
    {
        buyInfo = StudioPrefs.GetString("BuyInfo");
        buyInfo += initialScore + "," + gunType + "||";

        StudioPrefs.SetString("BuyInfo", buyInfo);
        StudioAnalytics.SetGameAnalyticsPrefs(levelInfo, buyInfo, currencyInfo, "", "", "");
        Debug.Log("BuyInfo " + buyInfo);
    }

    // Used to set BuyInfo is player does not buy gun
    public static void SetInitialScore()
    {
        initialScore = PlayerBase.GetScore();
        gunType = "NA";
    }

    // Used to set BuyInfo is player buys gun
    public static void SetGunType(string gt)
    {
        gunType = gt;
    }
}


```

## CheckEnemyCollision.cs

```csharp
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

/// <summary>
/// Used for the hostage
/// </summary>
public class CheckEnemyCollision : StudioBehaviour
{
    string enemyName;

    private void Start()
    {
        enemyName = GetStringVariable("EnemyName");
    }

    // Checks if the Enemy has touched the hostage and if so then trigger Mission Fail
    private void OnTriggerEnter(Collider other)
    {
        string name = other.transform.root.name.Split()[0];
        if (name == enemyName)
        {
            Broadcast("PlayerDead");
        }
    }
}


```

## Collectible.cs

```csharp
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

/// <summary>
/// Used in all the collectibles
/// </summary>
public class Collectible : StudioBehaviour
{
    private int id;
    private GameObject? player;

    private const string var_ID = "ID";
    
    private void Start()
    {
        player = StudioController.GetMyController().GetPlayerData().GetModelTransform().root.gameObject;
        id = GetIntVariable(var_ID);
    }
    
    // Check if the player touched the collectible
    public void OnTriggerEnter(Collider other)
    {
        if (other.transform.root.gameObject == player)
        {
            ApplyAbilityEffect();
        }
    }

    // Trigger effect based on the type of collectible
    void ApplyAbilityEffect()
    {
        switch (id)
        {
            case 0:
                Broadcast("IncreaseHP");
                break;

            case 1:
                Broadcast("AddAmmo");
                break;

            case 2:
                Broadcast("Armor");
                break;

            case 3:
                Broadcast("AddMoreAmmo");
                break;
        }
        DestroyTemplate? destroy = GetTemplate(typeof(DestroyTemplate)) as DestroyTemplate;
        destroy?.Execute();
    }
}


```

## DestroyableObject.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

/// <summary>
/// Used in all the destroyable objects
/// </summary>
public class DestroyableObject : StudioBehaviour
{
    float health;
    float shrinkSpeed = 3;

    private void Start()
    {
        health = GetFloatVariable("Health");
    }

    // Check if the bullet hit the object and destroy the object if health reaches 0
    void OnCollisionEnter(Collision other)
    {
        if(other.collider.gameObject.name == "Bullet")
        {
            TerraBullet bullet = other.collider.gameObject.GetComponent(typeof(TerraBullet)) as TerraBullet;

            health -= TerraBullet.GetDamage();

            if(health <= 0)
            {
                StartCoroutine(DestroyObject());
            }
        }
    }

    // Shrink the object and destroy it
    IEnumerator DestroyObject()
    {
        float constTime = 0.6f;
        float time = constTime;
        Vector3 defScale = transform.localScale;
        while (time > 0)
        {
            transform.localScale -= (Time.deltaTime / constTime) * defScale;
            time -= Time.deltaTime;

            yield return null;
        }

        DestroyTemplate destroy = GetTemplate(typeof(DestroyTemplate)) as DestroyTemplate;
        destroy.Execute();
    }
}


```

## Hostage.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

/// <summary>
/// manages the behaviour of hostage
/// </summary>
public class Hostage : StudioBehaviour
{
    private float radius;
    private float minRadius;
    private Transform playerTransform;
    private float speed;
    private int hostageState;
    private PlayAnimationTemplate anim;
    private bool hasSeenplayer = false;
    private TerraAutoAim playerAutoAim;
    private bool playerKnown;
    private Vector3 escapePos;
    private Vector3 targetPosition;
    private bool isFindingEnemy;
    private int newPosTime;
    private ParticleEffectTemplate panicParticle;
    private float playerDist;

    private const int IDLE = 1;
    private const int FOLLOW = 2;

    private string ANIM_IDLE = "idle_02_tp";
    private string ANIM_RUN = "run_front_tp";

    private void Start()
    {
        anim = GetTemplate(typeof(PlayAnimationTemplate)) as PlayAnimationTemplate;
        radius = GetFloatVariable("Radius");
        minRadius = GetFloatVariable("MinRadius");
        speed = GetFloatVariable("Speed");
        newPosTime = GetIntVariable("NewPosTime");
        GameObject obj1 = GetGameObjectVariable("PanicParticle");
        panicParticle = GetTemplate(obj1, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;

        playerTransform = StudioController.GetMyController().GetPlayerData().GetModelTransform();
        GameObject obj = GetGameObjectVariable("PlayerModel");
        playerAutoAim = obj.GetComponent(typeof(TerraAutoAim)) as TerraAutoAim;
        ChangeState(IDLE);

        targetPosition = transform.position;
        escapePos = transform.position;
    }

    private void Update()
    {
        if (playerTransform == null) // Checks if the player exists
        {
            return;
        }
        MoveToPosition();
        if (playerAutoAim.IsEnemyThere()) // If enemy encounter, stop following and run away
        {
            StopAllCoroutines();
            panicParticle.Execute();
            isFindingEnemy = false;
            targetPosition = escapePos;
            return;
        }
        playerDist = Vector3.Distance(playerTransform.position, transform.position);
        if (playerDist <= radius) // Checks if the player is in the range
        {
            Vector3 dir = (playerTransform.position - transform.position).normalized;
            RaycastHit hit;
            if (Physics.Raycast(transform.position + transform.up * 0.5f, dir, out hit, radius)) // Checks if there is nothing between the hostage and player
            {
                if (hit.collider.transform.root.name != playerTransform.root.name)
                {
                    ChangeState(IDLE);
                    hasSeenplayer = false;
                    targetPosition = transform.position;
                }
                else
                {
                    targetPosition = playerTransform.position;
                    hasSeenplayer = true;
                    playerKnown = true;
                }
            }
            if (!isFindingEnemy)
            {
                StartCoroutine(FindEnemy());
            }
        }
        else
        {
            ChangeState(IDLE);
            hasSeenplayer = false;
        }
    }

    // Manages the state of the hostage
    void ChangeState(int state)
    {
        if (hostageState == state)
        {
            return;
        }
        hostageState = state;
        switch (hostageState)
        {
            case IDLE:
                anim.PlayAnimationOverride(ANIM_IDLE, true);
                break;

            case FOLLOW:
                anim.PlayAnimationOverride(ANIM_RUN, true);
                break;
        }
    }

    // Gets if the hostage can see the player
    public bool PlayerSeen()
    {
        return hasSeenplayer;
    }

    // Gets if the hostage can saw the player for the first time
    public bool PlayerKnown()
    {
        return playerKnown;
    }

    // Moves the hostage to the target position
    void MoveToPosition()
    {
        if (Vector3.Distance(transform.position, targetPosition) > minRadius)
        {
            transform.LookAt(targetPosition);
            transform.position += speed * Time.deltaTime * transform.forward;
            ChangeState(FOLLOW);
        }
        else
        {
            ChangeState(IDLE);
        }

    }

    // Updates the escape position in every newPosTime
    IEnumerator FindEnemy()
    {
        isFindingEnemy = true;

        yield return new WaitForSeconds(newPosTime);
        escapePos = transform.position;
        StartCoroutine(FindEnemy());
    }
    public float PlayerDistance()
    {
        return playerDist;
    }
}


```

## LevelManager.cs

```csharp
using Terra.Studio.Exposed;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// It manages the mission success/fail UI
/// </summary>

/*
 * 0 - Mission Success
 * 1 - Mission Fail
 */
public class LevelManager : StudioBehaviour
{
    int stateID;
    EditUITemplate UI;
    bool wasActiveWin;
    bool wasActiveLose;
    bool dontCallWin;
    bool dontCallLose;
    bool isTimerOn;
    float timer;
    
    private void Start()
    {
        stateID = GetIntVariable("StateID");
        UI = GetTemplate(typeof(EditUITemplate)) as EditUITemplate;
        isTimerOn = true;
    }
    private void Update()
    {
        // if stateid is 0 then mission success else mission failed
        switch (stateID)
        {
            case 0:
                if (wasActiveWin && !dontCallWin)
                {
                    wasActiveWin = false;
                    dontCallWin = true;
                    MissionSuccess();
                    isTimerOn = false;
                }
                break;
            case 1:
                if (wasActiveLose && !dontCallLose)
                {
                    wasActiveLose = false;
                    dontCallLose = true;
                    MissionFailed();
                    isTimerOn = false;
                }
                break;
        }
        if(isTimerOn)
        {
            timer += Time.deltaTime;
        }
    }

    public override void OnBroadcasted(string x)
    {
        if(x == "PlayerWin") // Trigger Mission Success
        {
            wasActiveWin = true;
        }
        else if(x == "PlayerDead") // Trigger Mission failed
        {
            wasActiveLose = true;
        }
    }

    // Start next level when player presses the continue button
    void LevelFinished()
    {
        Broadcast("NextLevel");
    }

    // Restart level when player presses the restart button
    void LevelRestart()
    {
        Broadcast("RestartLevel");
    }

    // Go to base level when player presses the home button
    void GoHome()
    {
        HomescreenMenu.SetHasGameStarted(1);
        Broadcast("Home");
    }
    // Initialize UI for mission success
    void MissionSuccess()
    {
        var instantiatedUI = UI.GetInstantiatedUI;
        var buttonObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "msContinue");
        var buttonComponent = buttonObj.GetComponent(typeof(Button)) as Button;
        buttonComponent.onClick.AddListener(LevelFinished);

        var enemyTextObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "msDeath_count");
        TMP_Text text = enemyTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        text.text = PlayerController.GetLevelEnemyKills().ToString();

        var timerTextObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "mstime_count");
        TMP_Text text2 = timerTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        timer = Mathf.Round(timer);
        text2.text = (timer / 60).ToString("0") + ":" + (timer % 60).ToString("00") + " min";

        var rewardObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "msreward_count");
        TMP_Text text3 = rewardObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        text3.text = (PlayerController.GetLevelEnemyKills() * 15).ToString();

        var homeButtonObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "MSHomeButton");
        var homeButtonComp = homeButtonObj.GetComponent(typeof(Button)) as Button;
        homeButtonComp.onClick.AddListener(GoHome);

        if(HomescreenMenu.GetMissionsUnlocked() == 1)
        {
            StartCoroutine(AnimateObjective(homeButtonObj.gameObject, true, 1, 0.3f));
            buttonComponent.interactable = false;
        }
        StudioHaptics.PlayHapticSuccess();
    }

    // Initialize UI for mission failed
    void MissionFailed()
    {
        var instantiatedUI = UI.GetInstantiatedUI;
        var buttonObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "Restart");
        var buttonComponent = buttonObj.GetComponent(typeof(Button)) as Button;
        buttonComponent.onClick.AddListener(LevelRestart);

        var enemyTextObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "Death_count"); 
        TMP_Text text = enemyTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        text.text = PlayerController.GetLevelEnemyKills().ToString();

        var timerTextObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "time_count");
        TMP_Text text2 = timerTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        timer = Mathf.Round(timer);
        text2.text = (timer / 60).ToString("0") + ":" + (timer % 60).ToString("00") + " min";

        var rewardObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "reward_count");
        TMP_Text text3 = rewardObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        text3.text = (PlayerController.GetLevelEnemyKills() * 15).ToString();

        var homeButtonObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "HomeButton");
        var homeButtonComp = homeButtonObj.GetComponent(typeof(Button)) as Button;
        homeButtonComp.onClick.AddListener(GoHome);

        StudioHaptics.PlayHapticFailure();
    }

    // Used in tutorial to popup UI
    IEnumerator AnimateObjective(GameObject obj, bool isforever = false, float magnify = 1.5f, float speed = 1)
    {
        float defaultval = obj.transform.localScale.x;
        float def = defaultval;
        float count = 5;
        if (isforever)
        {
            count = 100000;
        }

        for (int i = 0; i < count; i++)
        {
            while (magnify > def)
            {
                obj.transform.localScale = new Vector3(def, def, 1);

                yield return null;

                def += speed * Time.deltaTime;
            }

            while (def > defaultval)
            {
                obj.transform.localScale = new Vector3(def, def, 1);

                yield return null;

                def -= speed * Time.deltaTime;
            }

            def = defaultval;
            obj.transform.localScale = new Vector3(def, def, 1);
        }
    }
}

```

## LevelSelection.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Used in the Level Selection Panel
/// </summary>

/*
 * 2 - Normal_selected
 * 3 - completed_selected
 * 4 - completed_UNSELECT
 * 5 - lock_unselected
 * 6 - lock_selected
 * 7 - normal_unselectd
 */
public class LevelSelection : StudioBehaviour
{
    GameObject levelSelectionUI;
    GameObject homescreenUI;
    GameObject leaderboardButtonObj;
    GameObject addon;
    Transform missionsParent;
    int currentUnlockedMission;
    static int currentSelectedMission;
    Button rightBtn;
    Button leftBtn;
    Button backBtn;
    Button playBtn;
    ScrollRect scrollView;
    RectTransform content;
    HomescreenMenu homescreenScript;

    SoundFxTemplate button1;
    SoundFxTemplate button2;
    SoundFxTemplate buttonObjective;
    
    private void Start()
    {
        StartCoroutine(Initialization());
    }

    // Initializes the variables
    IEnumerator Initialization()
    {
        currentUnlockedMission = HomescreenMenu.GetMissionsUnlocked();

        var lsObj = GetGameObjectVariable("LevelSelectionPanel");
        var editUI = GetTemplate(lsObj, typeof(EditUITemplate)) as EditUITemplate;
        levelSelectionUI = editUI.GetInstantiatedUI;

        GameObject homescreenObj = GetGameObjectVariable("HomescreenUI");
        EditUITemplate obj = GetTemplate(homescreenObj, typeof(EditUITemplate)) as EditUITemplate;
        homescreenUI = obj.GetInstantiatedUI;

        GameObject obj2;
        Transform music = GetGameObjectVariable("Music").transform;
        obj2 = music.GetChild(4).gameObject;
        button1 = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj2 = music.GetChild(5).gameObject;
        button2 = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj2 = music.GetChild(6).gameObject;
        buttonObjective = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;

        missionsParent = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "Content");
        var btn = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "rightarrow");
        rightBtn = btn.GetComponent(typeof(Button)) as Button;
        rightBtn.onClick.AddListener(() => SetMissionsState(-1, false));

        btn = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "leftarrow");
        leftBtn = btn.GetComponent(typeof(Button)) as Button;
        leftBtn.onClick.AddListener(() => SetMissionsState(-1, true));

        if (GetCurrentSelectedMission() >= 9)
        {
            leftBtn.interactable = false;
        }
        else if (GetCurrentSelectedMission() <= 0)
        {
            rightBtn.interactable = false;
        }

        btn = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "Backbutton");
        backBtn = btn.GetComponent(typeof(Button)) as Button;
        backBtn.onClick.AddListener(() => SetInactive());

        btn = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "Scroll_View");
        scrollView = btn.GetComponent(typeof(ScrollRect)) as ScrollRect;
        content = scrollView.content;

        btn = StudioExtensions.FindDeepChild(levelSelectionUI.transform, "LSplaybutton");
        playBtn = btn.GetComponent(typeof(Button)) as Button;
        playBtn.onClick.AddListener(() => PlayMission());

        SetMissionsState(currentUnlockedMission, false);
        homescreenScript = GetComponent(typeof(HomescreenMenu)) as HomescreenMenu;

        var lbObj = GetGameObjectVariable("LeaderboardButton");
        var lbeditUI = GetTemplate(lbObj, typeof(EditUITemplate)) as EditUITemplate;
        leaderboardButtonObj = lbeditUI.GetInstantiatedUI;

        var addonObj = GetGameObjectVariable("HomescreenAddon");
        var adeditUI = GetTemplate(addonObj, typeof(EditUITemplate)) as EditUITemplate;
        addon = adeditUI.GetInstantiatedUI;

        yield return null;

        levelSelectionUI.SetActive(false);
    }

    // Sets selected mission based on the right/button pressed
    void SetMissionsState(int mission, bool isRight)
    {
        if (mission < 0) // initializes missions is the player enters
        {
            if (isRight)
            {
                content.GetChild(GetCurrentSelectedMission()).transform.localScale = Vector3.one;

                SetCurrentSelectedMission(GetCurrentSelectedMission() + 1);
                button2.Execute();
                StudioHaptics.PlayHapticSelection();
            }
            else
            {
                content.GetChild(GetCurrentSelectedMission()).transform.localScale = Vector3.one;

                SetCurrentSelectedMission(GetCurrentSelectedMission() - 1);
                button1.Execute();
                StudioHaptics.PlayHapticSelection();
            }

            leftBtn.interactable = true;
            rightBtn.interactable = true;

            if (GetCurrentSelectedMission() >= 9)
            {
                content.GetChild(GetCurrentSelectedMission()).transform.localScale = Vector3.one;
                SetCurrentSelectedMission(9);
                leftBtn.interactable = false;
            }
            else if (GetCurrentSelectedMission() <= 0)
            {
                content.GetChild(GetCurrentSelectedMission()).transform.localScale = Vector3.one;

                SetCurrentSelectedMission(0);
                rightBtn.interactable = false;
            }
        }
        else
        {
            SetCurrentSelectedMission(mission);
        }

        GameObject selectedLevel = content.GetChild(GetCurrentSelectedMission()).gameObject;

        content.anchoredPosition =
                (Vector2)scrollView.transform.InverseTransformPoint(content.position)
                - (Vector2)scrollView.transform.InverseTransformPoint(selectedLevel.transform.position); // Scrolls to next/previous mission

        selectedLevel.transform.localScale = Vector2.one * 1.4f; // Scales the selected mission

        for (int i = 0; i < missionsParent.childCount; i++)
        {
            ResetMissionStates(i);

            if (i < currentUnlockedMission)
            {
                missionsParent.GetChild(i).GetChild(4).gameObject.SetActive(true);
            }
            else if (i == currentUnlockedMission)
            {
                missionsParent.GetChild(i).GetChild(7).gameObject.SetActive(true);
            }
            else
            {
                missionsParent.GetChild(i).GetChild(5).gameObject.SetActive(true);
            }
        }
        int mis = GetCurrentSelectedMission();
        if (mis < currentUnlockedMission)
        {
            ResetMissionStates(mis);
            missionsParent.GetChild(mis).GetChild(3).gameObject.SetActive(true);

            playBtn.gameObject.SetActive(true);
        }
        else if (mis == currentUnlockedMission)
        {
            ResetMissionStates(mis);
            missionsParent.GetChild(mis).GetChild(2).gameObject.SetActive(true);

            playBtn.gameObject.SetActive(true);
        }
        else
        {
            ResetMissionStates(mis);
            missionsParent.GetChild(mis).GetChild(6).gameObject.SetActive(true);

            playBtn.gameObject.SetActive(false);
        }
    }

    // Turns off all mission UI
    void ResetMissionStates(int id)
    {
        for (int i = 2; i <= 7; i++)
        {
            missionsParent.GetChild(id).GetChild(i).gameObject.SetActive(false);
        }
    }
    
    // Switches from Level Selection Panel to Homescreen Menu
    void SetInactive()
    {
        addon.SetActive(true);
        StudioExtensions.ToggleHomeButton(true);
        leaderboardButtonObj.SetActive(true);
        StudioHaptics.PlayHapticSelection();
        buttonObjective.Execute();
        homescreenUI.SetActive(true);
        levelSelectionUI.SetActive(false);
    }

    // Plays the selected mission
    void PlayMission()
    {
        AnalyticsAndLeaderboard.SetCoinEnter();
        Broadcast("Level" + (GetCurrentSelectedMission() + 1));
        StudioHaptics.PlayHapticSelection();
        buttonObjective.Execute();
    }
    public static int GetCurrentSelectedMission()
    {
        currentSelectedMission = StudioPrefs.GetInt("SelectedMission", 0);
        return currentSelectedMission;
    }
    public static void SetCurrentSelectedMission(int mission)
    {
        currentSelectedMission = mission;

        StudioPrefs.SetInt("SelectedMission", currentSelectedMission);
    }
}


```

## PlayerBase.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using UnityEngine;

/// <summary>
/// Keeps track of the equipped gun and score (Diamonds)
/// </summary>
public class PlayerBase : StudioBehaviour
{
    /*
     * 0 - Handgun
     * 1 - Shotgun
     * 2 - Sniper
     */
    private static int equippedGun = 2;
    private static int weaponIdx = 0;

    // Gets the equipped gun type pistol/shotgun/sniper
    public static int GetEquippedGun()
    {
        equippedGun = StudioPrefs.GetInt("EquippedGun");
        return equippedGun;
    }

    // Sets the equipped gun type pistol/shotgun/sniper
    public static void SetEquippedGun(int idx)
    {
        if(idx >= 0 && idx <= 2)
        {
            equippedGun = idx;
            StudioPrefs.SetInt("EquippedGun", equippedGun);
        }
    }

    // Gets the gun variant of the equipped gun type
    public static int GetWeaponIdx()
    {
        return StudioPrefs.GetInt("WeaponIdx");
    }

    // Sets the gun variant of the equipped gun type
    public static void SetWeaponIdx(int idx)
    {
        if (idx >= 0 && idx <= 5)
        {
            weaponIdx = idx;
            StudioPrefs.SetInt("WeaponIdx", weaponIdx);
        }
    }

    // Gets the score (Diamonds)
    public static int GetScore()
    {
        int score = StudioPrefs.GetInt("Score");
        StudioUser.UpdateCurrentInGameCurrency("Diamonds", score);
        Debug.Log("UpdateInGameCurrency " + score);
        return score;
    }

    // Sets the score (Diamonds)
    public static void SetScore(int score)
    {
        StudioPrefs.SetInt("Score", score);
        StudioUser.UpdateCurrentInGameCurrency("Diamonds", score);
        Debug.Log("UpdateInGameCurrency " + score);
    }
}


```

## PlayerController.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class PlayerController : StudioBehaviour
{
    private static int levelEnemyKills = 0;
    private static int enemyKills = 0;
    public static bool isGameStarted;

    private GameObject enemyUI;
    private int levelID;
    private float barrierTime;
    private float barrierCounter;
    private bool increaseHealth = false;
    private int maxShieldDamage = 2;
    private int shieldDamageCount;
    private int maxEnemies;
    private int levelNumber;
    private Transform playerTransform;
    private GameObject damageParticle;
    private GameObject shieldObject;
    private GameObject directionalArrow;
    private GameObject retrievalItem;
    private GameObject endPoint;
    private GameObject postRescueEnemies;
    private GameObject directionalArrow2;
    private GameObject directionalArrow3;
    private Transform currentObjective;
    private GameObject hostageObject;
    private GameObject[] objectsToDestroy = new GameObject[3];
    private GameObject objectsToDestroyParent;
    private GameObject enemiesToKill;
    private GameObject healthCollectUI;
    private GameObject ammoCollectUI;
    private GameObject armorCollectUI;
    private GameObject healthCollectInstantiatedUI;
    private GameObject ammoCollectInstantiatedUI;
    private GameObject armorCollectInstantiatedUI;
    private GameObject objectiveUI;
    private GameObject objectiveInstantiatedUI;
    private GameObject newObjectiveUI;
    private Image healthUI;
    private GameObject healthObj;
    private Transform objectiveArrowParent;
    private Hostage hostageScript;
    private TMP_Text timerText;
    private TMP_Text enemyCountText;
    private Vector3 arrowOffset = new Vector3(0, 2.1f, -0.5f);
    private ParticleEffectTemplate shieldEffect;
    private ParticleEffectTemplate damageEffect;
    private bool isShowingdamage = false;
    public static bool isShowingShield;
    private bool isItemCollected;
    private bool isEnter;
    private bool hasSpawnedEnemies;
    private float health;
    private float maxHealth = 100;
    private float timer = 300;
    private float countDown;
    private bool isObjectiveMoving;
    private bool hasWon;
    private bool hasLost;
    private bool isEnemyBroadcasted;
    private string objective1;
    private string objective2;
    private int heartsCollected;
    private TMP_Text objectiveText;

    private const string var_EnemyUI = "EnemyUI";
    private const string var_BarrierTime = "BarrierTime";
    private const string var_PostRescueEnemies = "PostRescueEnemies";
    private const string var_DamageParticle = "DamageParticle";
    private const string var_ShieldObject = "ShieldObject";
    private const string var_DirectionalArrow = "DirectionalArrow";
    private const string var_DirectionalArrow2 = "DirectionalArrow2";
    private const string var_DirectionalArrow3 = "DirectionalArrow3";
    private const string var_EndPoint = "EndPoint";
    private const string var_LevelID = "LevelID";
    private const string var_RetrievalItem = "RetrievalItem";
    private const string var_HostageObject = "HostageObject";
    private const string var_ObjectsToDestroy = "ObjectsToDestroy";
    private const string var_EnemiesToKill = "EnemiesToKill";
    private const string var_MissionFailedUI = "MissionFailedUI";
    private const string var_MissionSuccessUI = "MissionSuccessUI";

    private void Start()
    {
        StudioExtensions.ToggleHomeButton(false);

        StartCoroutine(Initialization());
        barrierCounter = barrierTime;

        if (levelID == 1)
        {
            currentObjective = endPoint.transform;
        }

        TerraEnemy.SetStop(true);
        TerraSpiderEnemy.SetStop(true);
    }
    private void Update()
    {
        if (levelNumber == 1)
        {
            if (GetLevelEnemyKills() == 1 && !isEnemyBroadcasted)
            {
                Broadcast("Milestone0");
                isEnemyBroadcasted = true;
            }
        }
        LookArrowAtObjective();
        if (levelID == 0)
        {
            Level1Objective();
            
        }
        else if (levelID == 2)
        {
            Level3Objective();
        }
        else if (levelID == 3)
        {
            Level4Objective();
        }
        else if (levelID == 4)
        {
            Camera.main.nearClipPlane = 7;
            if (isGameStarted)
            {
                countDown -= Time.deltaTime;
                if (countDown <= 0)
                {
                    if (!hasWon)
                    {
                        Broadcast("PlayerDead");
                        hasLost = true;
                    }
                }
                else
                {
                    int min = (int)(countDown / 60);
                    int sec = (int)(countDown % 60);
                    timerText.text = min.ToString() + ":" + sec.ToString("00") + " sec";
                }
            }
            Level5Objective();
        }
        if (isShowingdamage)
        {
            ShowDamageParticle();
        }
        if (isShowingShield)
        {
            ShowShieldParticle();
        }
    }
    public static int GetEnemyKills()
    {
        enemyKills = StudioPrefs.GetInt("EnemyKills");
        return enemyKills;
    }
    public static void SetEnemyKills(int kills)
    {
        enemyKills = kills;
        StudioPrefs.SetInt("EnemyKills", enemyKills);
    }
    public static int GetLevelEnemyKills()
    {
        return levelEnemyKills;
    }
    public static void SetLevelEnemyKills(int kills)
    {
        levelEnemyKills = kills;
    }
    private void ShowShieldParticle()
    {
        shieldObject.transform.position = playerTransform.position + Vector3.up * 1.3f;
        shieldObject.SetActive(true);
    }
    private void IncreaseHealth()
    {
        health += 20;
        if (health > maxHealth)
        {
            health = maxHealth;
        }
        healthUI.fillAmount = health / maxHealth;
    }
    private void DecreaseHealth()
    {
        health -= 13;
        healthUI.fillAmount = health / maxHealth;

        if (health <= 0)
        {
            if (!hasWon)
            {
                Broadcast("PlayerDead");
                hasLost = true;
            }
        }
    }

    public override void OnBroadcasted(string x)
    {
        if (x == "Armor")
        {
            isShowingShield = true;
        }
        else if (x == "DamageShield")
        {
            if (isShowingShield)
            {
                shieldDamageCount--;
                if (shieldDamageCount <= 0)
                {
                    shieldObject.SetActive(false);
                    isShowingShield = false;
                }
            }
        }
        else if (x == "PlayerHit")
        {
            isShowingdamage = true;
        }
        else if (x == "ShowHealth")
        {
            StartCoroutine(StartHealth());
            heartsCollected++;
            if(heartsCollected == 1)
            {
                Broadcast("Milestone1");
            }
            
        }
        else if (x == "ShowAmmo")
        {
            StartCoroutine(StartAmmo());
        }
        else if (x == "ShowArmor")
        {
            StartCoroutine(StartArmor());
        }
        else if (x == "ItemCollected")
        {
            isItemCollected = true;
            StudioHaptics.PlayHapticSuccess();
        }
        else if (x == "PlayeReach")
        {
            isEnter = true;
            if (levelID == 1)
            {
                if (!hasLost)
                {
                    Broadcast("PlayerWin");
                    hasWon = true;
                }
            }
        }
        else if (x == "PlayerExit")
        {
            isEnter = false;
        }
        else if (x == "TimeOver")
        {
            Broadcast("Game Lose");
        }
        else if (x == "IncreaseHP")
        {
            IncreaseHealth();
        }
        else if (x == "DealDamage")
        {
            DecreaseHealth();
        }
        else if (x == "PlayerWin")
        {
            if (isGameStarted)
            {
                AnalyticsAndLeaderboard.SetExitType("Victory");
            }

            isGameStarted = false;

            int missionsUnlocked = HomescreenMenu.GetMissionsUnlocked();
            if (missionsUnlocked < levelNumber)
            {
                HomescreenMenu.SetMissionsUnlocked(levelNumber);
            }
        }
        else if (x == "PlayerDead")
        {
            AnalyticsAndLeaderboard.SetExitType("Defeat");
            isGameStarted = false;
        }
    }
    void GoHome()
    {
        AnalyticsAndLeaderboard.SetExitType("Back button");
        HomescreenMenu.SetHasGameStarted(1);
        Broadcast("Home");
    }
    IEnumerator Initialization()
    {
        health = maxHealth;

        SetLevelEnemyKills(0);
        enemyUI = GetGameObjectVariable(var_EnemyUI);
        barrierTime = GetFloatVariable(var_BarrierTime);
        damageParticle = GetGameObjectVariable(var_DamageParticle);
        shieldObject = GetGameObjectVariable(var_ShieldObject);
        levelID = GetIntVariable(var_LevelID);
        levelNumber = GetIntVariable("LevelNum");
        healthCollectUI = GetGameObjectVariable("HealthCollectUI");
        ammoCollectUI = GetGameObjectVariable("AmmoCollectUI");
        armorCollectUI = GetGameObjectVariable("ArmorCollectUI");
        var obj = GetTemplate(healthCollectUI, typeof(EditUITemplate)) as EditUITemplate;
        healthCollectInstantiatedUI = obj.GetInstantiatedUI;
        obj = GetTemplate(ammoCollectUI, typeof(EditUITemplate)) as EditUITemplate;
        ammoCollectInstantiatedUI = obj.GetInstantiatedUI;
        obj = GetTemplate(armorCollectUI, typeof(EditUITemplate)) as EditUITemplate;
        armorCollectInstantiatedUI = obj.GetInstantiatedUI;
        objectiveUI = GetGameObjectVariable("ObjectiveUI");
        obj = GetTemplate(objectiveUI, typeof(EditUITemplate)) as EditUITemplate;
        objectiveInstantiatedUI = obj.GetInstantiatedUI;

        GameObject healthObjtemp = GetGameObjectVariable("HealthUI");
        var healthEditUI = GetTemplate(healthObjtemp, typeof(EditUITemplate)) as EditUITemplate;
        healthObj = healthEditUI.GetInstantiatedUI;
        GameObject healthimg = StudioExtensions.FindDeepChild(healthObj.transform, "Fillup").gameObject;
        healthUI = healthimg.GetComponent(typeof(Image)) as Image;
        healthUI.fillAmount = health / maxHealth;
        healthObj.SetActive(false);

        GameObject btnObj = StudioExtensions.FindDeepChild(objectiveInstantiatedUI.transform, "Continue_button").gameObject;
        Button btn = btnObj.GetComponent(typeof(Button)) as Button;
        btn.onClick.AddListener(StartGame);

        isGameStarted = false;
        healthCollectInstantiatedUI.SetActive(false);
        ammoCollectInstantiatedUI.SetActive(false);
        armorCollectInstantiatedUI.SetActive(false);

        btnObj = GetGameObjectVariable("BackCanvas");
        EditUITemplate editUI = GetTemplate(btnObj, typeof(EditUITemplate)) as EditUITemplate;
        btnObj = editUI.GetInstantiatedUI;
        GameObject backObj = StudioExtensions.FindDeepChild(btnObj.transform, "SpaceMarshals_Back_button").gameObject;
        Button backBtn = btnObj.GetComponent(typeof(Button)) as Button;
        backBtn.onClick.AddListener(GoHome);

        if (levelID != 4)
        {
            directionalArrow = GetGameObjectVariable(var_DirectionalArrow);
        }
        if (levelID != 3 && levelID != 4)
        {
            endPoint = GetGameObjectVariable(var_EndPoint);
        }
        if (levelID == 0)
        {
            retrievalItem = GetGameObjectVariable(var_RetrievalItem);
            objective1 = "Retrieve the artifact";
            objective2 = "Reach the checkpoint";

        }
        else if (levelID == 2)
        {
            hostageObject = GetGameObjectVariable(var_HostageObject);
            postRescueEnemies = GetGameObjectVariable(var_PostRescueEnemies);
            hostageScript = hostageObject.GetComponent(typeof(Hostage)) as Hostage;
            currentObjective = hostageObject.transform;

            objective1 = "Rescue the hostage";
            objective2 = "Escape the village";
        }
        else if (levelID == 3)
        {
            directionalArrow2 = GetGameObjectVariable(var_DirectionalArrow2);
            directionalArrow3 = GetGameObjectVariable(var_DirectionalArrow3);
            objectsToDestroyParent = GetGameObjectVariable(var_ObjectsToDestroy);

            objectsToDestroy[0] = objectsToDestroyParent.transform.GetChild(0).gameObject;
            objectsToDestroy[1] = objectsToDestroyParent.transform.GetChild(1).gameObject;
            objectsToDestroy[2] = objectsToDestroyParent.transform.GetChild(2).gameObject;

            objective1 = "Destroy the 3 chambers";
        }
        else if (levelID == 4)
        {
            enemiesToKill = GetGameObjectVariable(var_EnemiesToKill);
            directionalArrow = GetGameObjectVariable(var_DirectionalArrow);
            objectiveArrowParent = GetGameObjectVariable("ObjectiveArrowParent").transform;
            maxEnemies = enemiesToKill.transform.childCount;
            objective1 = "Kill all enemies";

            GameObject killCanvas = GetGameObjectVariable("EnemyCountCanvas");
            var countEditCanvas = GetTemplate(killCanvas, typeof(EditUITemplate)) as EditUITemplate;
            GameObject countObj = countEditCanvas.GetInstantiatedUI;
            GameObject countTextObj = StudioExtensions.FindDeepChild(countObj.transform, "killcount").gameObject;
            enemyCountText = countTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

            GameObject timeCanvas = GetGameObjectVariable("TimeCanvas");
            var editCanvas = GetTemplate(timeCanvas, typeof(EditUITemplate)) as EditUITemplate;
            GameObject timeObj = editCanvas.GetInstantiatedUI;
            GameObject timerObj = StudioExtensions.FindDeepChild(timeObj.transform, "Timetxt").gameObject;
            timerText = timerObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
            countDown = timer;
            timerText.text = (countDown / 60).ToString("0") + ":" + (countDown % 60).ToString("00") + " sec";
            GameObject arrow;
            for (int i = 0; i < enemiesToKill.transform.childCount; i++)
            {
                arrow = Instantiate(directionalArrow, objectiveArrowParent);
                arrow.transform.localPosition = Vector3.zero;
            }
        }
        shieldEffect = GetTemplate(shieldObject, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;
        damageEffect = GetTemplate(damageParticle, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;

        playerTransform = StudioController.GetMyController().GetPlayerData().GetPlayerTransform();

        if (levelID == 1)
        {
            StudioController.GetMyController().GetPlayerData().SetMaxMovementSpeed(0);
            objective1 = "Escape the Village";
        }
        else
        {
            StudioController.GetMyController().AllowPlayerMovement(false);
        }
        shieldDamageCount = maxShieldDamage;

        var msObj = GetGameObjectVariable("NewObjectiveUI");
        var msEditUI = GetTemplate(msObj, typeof(EditUITemplate)) as EditUITemplate;
        newObjectiveUI = msEditUI.GetInstantiatedUI;
        GameObject textObj = StudioExtensions.FindDeepChild(newObjectiveUI.transform, "Mission_txt").gameObject;
        objectiveText = textObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

        objectiveText.text = objective1;

        yield return null;
        shieldObject.SetActive(false);
        newObjectiveUI.SetActive(false);
        if (levelNumber == 1)
        {
            directionalArrow.SetActive(false);
        }
    }
    void Level1Objective()
    {
        if (!isItemCollected)
        {
            currentObjective = retrievalItem.transform;
            objectiveText.text = objective1;
        }
        else
        {
            currentObjective = endPoint.transform;
            objectiveText.text = objective2;
        }
        if (isEnter && isItemCollected)
        {
            if (!hasLost)
            {
                Broadcast("PlayerWin");
                hasWon = true;
            }
        }
        else if (isEnter)
        {
            StartCoroutine(AnimateObjective());
        }
        
    }
    void Level3Objective()
    {
        if (hostageScript.PlayerSeen())
        {
            currentObjective = endPoint.transform;
            objectiveText.text = objective2;

            if (isEnter && hostageScript.PlayerDistance() < 1.5f)
            {
                if (!hasLost)
                {
                    Broadcast("PlayerWin");
                    hasWon = true;
                }

            }
            else if (isEnter)
            {
                StartCoroutine(AnimateObjective());
            }
        }
        else if (isEnter)
        {
            StartCoroutine(AnimateObjective());
        }
        else
        {
            currentObjective = hostageObject.transform;
            objectiveText.text = objective1;
        }

        if (!hasSpawnedEnemies)
        {
            if (hostageScript.PlayerKnown())
            {
                Transform enemy = postRescueEnemies.transform.GetChild(0);
                Transform spawnParent = postRescueEnemies.transform.GetChild(1);
                for (int i = 0; i < spawnParent.childCount; i++)
                {
                    enemy.GetChild(i).position = spawnParent.GetChild(i).position;
                }
                hasSpawnedEnemies = true;
                Broadcast("DestroyArrow");
            }
        }
    }
    void Level4Objective()
    {
        if (objectsToDestroyParent.transform.childCount == 0)
        {
            if (!hasLost)
            {
                Broadcast("PlayerWin");
                hasWon = true;
            }

        }
    }
    void Level5Objective()
    {
        enemyCountText.text = (maxEnemies - enemiesToKill.transform.childCount) + " / " + maxEnemies;
        if (enemiesToKill.transform.childCount == 0)
        {
            if (!hasLost)
            {
                Broadcast("PlayerWin");
                hasWon = true;
            }

        }
    }
    IEnumerator SpawnEnemy(GameObject enemy, Transform spawnParent, int i)
    {
        Instantiate(enemy, spawnParent.GetChild(i).transform.position, Quaternion.identity);

        yield return null;
    }
    void ShowDamageParticle()
    {
        damageParticle.transform.position = playerTransform.position;
        damageEffect.Execute();
        isShowingdamage = false;
    }
    void LookArrowAtObjective()
    {
        if (levelID == 4)
        {
            objectiveArrowParent.position = playerTransform.position + Vector3.up;
            for (int i = 0; i < objectiveArrowParent.childCount; i++)
            {
                if (i >= enemiesToKill.transform.childCount)
                {
                    Destroy(objectiveArrowParent.GetChild(i).gameObject);
                }
                else
                {
                    objectiveArrowParent.GetChild(i).LookAt(enemiesToKill.transform.GetChild(i));
                }
            }
            return;
        }
        if (levelID != 3)
        {
            directionalArrow.transform.position = playerTransform.position + arrowOffset;
            directionalArrow.transform.LookAt(currentObjective);
            Vector3 rot = directionalArrow.transform.rotation.eulerAngles;
            rot.x = 0;
            directionalArrow.transform.rotation = Quaternion.Euler(rot);
        }
        else
        {
            if (objectsToDestroy[0] != null)
            {
                directionalArrow.transform.position = playerTransform.position + arrowOffset;
                directionalArrow.transform.LookAt(objectsToDestroy[0].transform);
                Vector3 rot = directionalArrow.transform.rotation.eulerAngles;
                rot.x = 0;
                directionalArrow.transform.rotation = Quaternion.Euler(rot);
            }
            else
            {
                Destroy(directionalArrow);
            }

            if (objectsToDestroy[1] != null)
            {
                directionalArrow2.transform.position = playerTransform.position + arrowOffset;
                directionalArrow2.transform.LookAt(objectsToDestroy[1].transform);
                Vector3 rot = directionalArrow2.transform.rotation.eulerAngles;
                rot.x = 0;
                directionalArrow2.transform.rotation = Quaternion.Euler(rot);
            }
            else
            {
                Destroy(directionalArrow2);
            }

            if (objectsToDestroy[2] != null)
            {
                directionalArrow3.transform.position = playerTransform.position + arrowOffset;
                directionalArrow3.transform.LookAt(objectsToDestroy[2].transform);
                Vector3 rot = directionalArrow3.transform.rotation.eulerAngles;
                rot.x = 0;
                directionalArrow3.transform.rotation = Quaternion.Euler(rot);
            }
            else
            {
                Destroy(directionalArrow3);
            }
        }
    }
    void StartGame()
    {
        TerraEnemy.SetStop(false);
        TerraSpiderEnemy.SetStop(false);
        if (levelID == 1)
        {
            StudioController.GetMyController().GetPlayerData().SetMaxMovementSpeed(5);
        }
        else
        {
            StudioController.GetMyController().AllowPlayerMovement(true);
        }
        isGameStarted = true;
        objectiveInstantiatedUI.SetActive(false);
        healthObj.SetActive(true);
        newObjectiveUI.SetActive(true);
        Broadcast("GameStarted");
    }
    IEnumerator StartHealth()
    {
        healthCollectInstantiatedUI.SetActive(true);

        yield return new WaitForSeconds(2);

        healthCollectInstantiatedUI.SetActive(false);
    }
    IEnumerator StartAmmo()
    {
        ammoCollectInstantiatedUI.SetActive(true);

        yield return new WaitForSeconds(2);

        ammoCollectInstantiatedUI.SetActive(false);
    }
    IEnumerator StartArmor()
    {
        armorCollectInstantiatedUI.SetActive(true);

        yield return new WaitForSeconds(2);

        armorCollectInstantiatedUI.SetActive(false);
    }
    IEnumerator AnimateObjective()
    {
        if (isObjectiveMoving)
        {
            yield break;
        }
        float magnify = 1.5f;
        float def = 1;
        float count = 3;

        isObjectiveMoving = true;
        for (int i = 0; i < count; i++)
        {
            while (magnify > def)
            {
                newObjectiveUI.transform.localScale = new Vector3(def, def, 1);

                yield return null;

                def += Time.deltaTime;
            }

            while (def > 1)
            {
                newObjectiveUI.transform.localScale = new Vector3(def, def, 1);

                yield return null;

                def -= Time.deltaTime;
            }

            def = 1;
            newObjectiveUI.transform.localScale = new Vector3(def, def, 1);
        }

        isObjectiveMoving = false;
    }
}

```

## Shop.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;

public class Shop : StudioBehaviour
{
    GameObject homescreenUI;
    GameObject shopUI;
    GameObject actualShopUI;
    GameObject playerStats;
    GameObject shotgunSelect;
    GameObject sniperSelect;
    GameObject handgunSelect;
    GameObject shotgunList;
    GameObject sniperList;
    GameObject handgunList;
    GameObject gunImageList;
    GameObject coinPopup;
    GameObject currentWeaponText;
    GameObject leaderboardButtonObj;
    GameObject addon;

    SoundFxTemplate gunTap;
    SoundFxTemplate gunBuy;
    SoundFxTemplate gunEquip;
    SoundFxTemplate buttonObjective;

    GameObject fireRate;
    GameObject reloadTime;
    GameObject clipSize;

    GameObject[] gunSelectionPanel;
    GameObject[] selectedButton;
    GameObject[] selectedGunOptions;

    HomescreenMenu homescreenScript;
    TMP_Text gemCount;
    TMP_Text gunName;
    TMP_Text gunBuyPrice;
    int selectedPanel;
    PlayerBase player;
    Tutorial Tutorial;
    int gunIdx;
    int gunType;
    bool[][] hasPurchased = new bool[][]{
        new bool[]{true, false, false, false, false},
        new bool[]{false, false, false, false, false},
        new bool[]{false, false, false, false, false}
    };
    string[] gunNames = new string[] 
    {
        "Enforcer",
        "Viper",
        "Marauder",
        "Ravager",
        "Overlord",
        "Hawkeye",
        "Longshot",
        "Reaper",
        "Phantom",
        "Predator",
        "Blaster",
        "Thunderstrike",
        "Berserker",
        "Wraith",
        "Doomsday"
    };
    string[] gunPurchasableNames = new string[]
    {
        "PistolEnforcer",
        "PistolViper",
        "PistolMarauder",
        "PistolRavager",
        "PistolOverlord",
        "ShotgunHawkeye",
        "ShotgunLongshot",
        "ShotgunReaper",
        "ShotgunPhantom",
        "ShotgunPredator",
        "SniperBlaster",
        "SniperThunderstrike",
        "SniperBerserker",
        "SniperWraith",
        "SniperDoomsday",
    };
    /*
     * Gun Slot order
     * 0 - Normal Btn
     * 1 - Equip Btn
     * 2 - Icon
     * 3 - Buy Btn
     */
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        StartCoroutine(Initialization());

        //PlayerBase.SetScore(1000);
        //actualShopUI.SetActive(false);
    }

    // Gets called every frame
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.K))
        {
            actualShopUI.SetActive(!actualShopUI.activeSelf);
        }

    }

    void GetPurchasedGuns()
    {
        string s = StudioPrefs.GetString("PurchasedGuns");
        char[] c = s.ToCharArray();
        int zero = Convert.ToInt32('0');
        for (int i = 0; i < c.Length; i++)
        {
            int c2 = Convert.ToInt32(c.GetValue(i));
            if (c2 == zero)
            {
                hasPurchased[i / 5][i % 5] = false;
            }
            else
            {
                hasPurchased[i / 5][i % 5] = true;
            }

        }
    }
    public bool[][] GetPurchasedGunsArray()
    {
        return hasPurchased;
    }
    void SetPurchasedGuns()
    {
        string s = "";

        for (int i = 0; i < hasPurchased.Length; i++)
        {
            for (int j = 0; j < hasPurchased[i].Length; j++)
            {
                if (hasPurchased[i][j])
                {
                    s += "1";
                }
                else
                {
                    s += "0";
                }
            }
        }

        StudioPrefs.SetString("PurchasedGuns", s);
    }
    IEnumerator Initialization()
    {
        //id = GetIntVariable("ID");
        //gunType = GetIntVariable("GunType");
        shopUI = GetGameObjectVariable("ShopUI");
        playerStats = GetGameObjectVariable("PlayerStats");
        player = playerStats.GetComponent(typeof(PlayerBase)) as PlayerBase;
        var UI = GetTemplate(shopUI, typeof(EditUITemplate)) as EditUITemplate;
        actualShopUI = UI.GetInstantiatedUI;

        GameObject obj2;
        Transform music = GetGameObjectVariable("Music").transform;
        obj2 = music.GetChild(1).gameObject;
        gunBuy = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj2 = music.GetChild(2).gameObject;
        gunEquip = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj2 = music.GetChild(3).gameObject;
        gunTap = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj2 = music.GetChild(6).gameObject;
        buttonObjective = GetTemplate(obj2, typeof(SoundFxTemplate)) as SoundFxTemplate;

        GameObject homescreenObj = GetGameObjectVariable("HomescreenUI");
        EditUITemplate objTemp = GetTemplate(homescreenObj, typeof(EditUITemplate)) as EditUITemplate;
        homescreenUI = objTemp.GetInstantiatedUI;
        homescreenScript = GetComponent(typeof(HomescreenMenu)) as HomescreenMenu;

        selectedButton = new GameObject[3];

        shotgunSelect = StudioExtensions.FindDeepChild(actualShopUI.transform, "SHOTGUN").gameObject;
        Button btn = shotgunSelect.GetComponent(typeof(Button)) as Button;
        Image img = shotgunSelect.GetComponent(typeof(Image)) as Image;
        img.preserveAspect = false;
        btn.onClick.AddListener(() => { SelectGunPanel(1); });
        selectedButton[1] = StudioExtensions.FindDeepChild(shotgunSelect.transform, "SELECTEDSTAT1").gameObject;

        sniperSelect = StudioExtensions.FindDeepChild(actualShopUI.transform, "SNIPER").gameObject;
        btn = sniperSelect.GetComponent(typeof(Button)) as Button;
        img = sniperSelect.GetComponent(typeof(Image)) as Image;
        img.preserveAspect = false;
        btn.onClick.AddListener(() => { SelectGunPanel(2); });
        selectedButton[2] = StudioExtensions.FindDeepChild(sniperSelect.transform, "SELECTEDSTAT2").gameObject;
        handgunSelect = StudioExtensions.FindDeepChild(actualShopUI.transform, "PISTOL").gameObject;
        btn = handgunSelect.GetComponent(typeof(Button)) as Button;
        img = handgunSelect.GetComponent(typeof(Image)) as Image;
        img.preserveAspect = false;
        btn.onClick.AddListener(() => { SelectGunPanel(0); });
        selectedButton[0] = StudioExtensions.FindDeepChild(handgunSelect.transform, "SELECTEDSTAT3").gameObject;
        for (int i = 0; i < selectedButton.Length; i++)
        {
            selectedButton[i].SetActive(false);
        }

        GameObject allGunDisplay = StudioExtensions.FindDeepChild(actualShopUI.transform, "ALL_GUN_DISPLAY").gameObject;
        shotgunList = allGunDisplay.transform.GetChild(0).gameObject;
        sniperList = allGunDisplay.transform.GetChild(1).gameObject;
        handgunList = allGunDisplay.transform.GetChild(2).gameObject;

        gunImageList = StudioExtensions.FindDeepChild(actualShopUI.transform, "all_gun").gameObject;

        fireRate = StudioExtensions.FindDeepChild(actualShopUI.transform, "FILL1").gameObject;
        reloadTime = StudioExtensions.FindDeepChild(actualShopUI.transform, "FILL2").gameObject;
        clipSize = StudioExtensions.FindDeepChild(actualShopUI.transform, "FILL3").gameObject;

        GameObject gemObj = StudioExtensions.FindDeepChild(actualShopUI.transform, "gemmmcount").gameObject;
        gemCount = gemObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

        GameObject backObj = StudioExtensions.FindDeepChild(actualShopUI.transform, "Back_button").gameObject;
        Button backBtn = backObj.GetComponent(typeof(Button)) as Button;
        GameObject gunNameObj = StudioExtensions.FindDeepChild(actualShopUI.transform, "Gun_name").gameObject;
        gunName = gunNameObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        GameObject gunPriceObj = StudioExtensions.FindDeepChild(actualShopUI.transform, "gemcount").gameObject;
        gunBuyPrice = gunPriceObj.GetComponent(typeof(TMP_Text)) as TMP_Text;
        currentWeaponText = StudioExtensions.FindDeepChild(actualShopUI.transform, "CWtxt").gameObject;

        GameObject coinpopup = GetGameObjectVariable("CoinPopUp");
        EditUITemplate coinEdit = GetTemplate(coinpopup, typeof(EditUITemplate)) as EditUITemplate;
        coinPopup = coinEdit.GetInstantiatedUI;

        var addonObj = GetGameObjectVariable("HomescreenAddon");
        var adeditUI = GetTemplate(addonObj, typeof(EditUITemplate)) as EditUITemplate;
        addon = adeditUI.GetInstantiatedUI;

        Tutorial = GetComponent(typeof(Tutorial)) as Tutorial;

        yield return null;
        gemCount.text = PlayerBase.GetScore().ToString();

        GameObject obj = StudioExtensions.FindDeepChild(actualShopUI.transform, "states").gameObject;
        selectedGunOptions = new GameObject[] {
            obj.transform.GetChild(0).gameObject,
            obj.transform.GetChild(1).gameObject,
            obj.transform.GetChild(2).gameObject,
        };

        var lbObj = GetGameObjectVariable("LeaderboardButton");
        var lbeditUI = GetTemplate(lbObj, typeof(EditUITemplate)) as EditUITemplate;
        leaderboardButtonObj = lbeditUI.GetInstantiatedUI;

        gunSelectionPanel = new GameObject[] { handgunList, shotgunList, sniperList };

        backBtn.onClick.AddListener(SwitchShop);

        GetPurchasedGuns();
        int type = PlayerBase.GetEquippedGun();
        int idx = PlayerBase.GetWeaponIdx();
        for (int i = 0; i < gunSelectionPanel.Length; i++)
        {
            for (int j = 0; j < gunSelectionPanel[i].transform.childCount; j++)
            {
                if (i == type && idx == j)
                {
                    EquipButton(i, j);
                }
                else
                {
                    if (hasPurchased[i][j])
                    {
                        NormalButton(i, j);
                    }
                    else
                    {
                        BuyButton(i, j);
                    }
                }
            }
        }
        SetGunImage(-1);
        ButtonInitialization();

        SelectGunPanel(0);
        DoSomething(PlayerBase.GetEquippedGun(), PlayerBase.GetWeaponIdx(), 1);

        yield return null;

        actualShopUI.SetActive(false);
        coinPopup.SetActive(false);
    }
    void SetGunImage(int idx)
    {
        int type = idx / 5;
        int weapon = idx % 5;
        for (int i = 0; i < gunImageList.transform.childCount; i++)
        {
            gunImageList.transform.GetChild(i).gameObject.SetActive(false);
        }
        switch (type)
        {
            case 0:
                gunImageList.transform.GetChild(5 + weapon).gameObject.SetActive(true);
                break;
            case 1:
                gunImageList.transform.GetChild(weapon).gameObject.SetActive(true);
                break;
            case 2:
                gunImageList.transform.GetChild(10 + weapon).gameObject.SetActive(true);
                break;
        }
    }
    void SelectGunPanel(int idx)
    {
        for (int i = 0; i < gunSelectionPanel.Length; i++)
        {
            if (i == idx)
            {
                gunSelectionPanel[i].SetActive(true);
                selectedButton[i].SetActive(true);

                bool val = hasPurchased[idx][0];
                if (PlayerBase.GetEquippedGun() == idx && PlayerBase.GetWeaponIdx() == 0)
                {
                    DoSomething(idx, 0, 1);
                }
                else if (val)
                {
                    DoSomething(idx, 0, 0);
                }
                else if (val == false)
                {
                    DoSomething(idx, 0, 3);
                }
            }
            else
            {
                gunSelectionPanel[i].SetActive(false);
                selectedButton[i].SetActive(false);
            }
        }

        StudioHaptics.PlayHapticSelection();
    }
    void DoSomething(int type, int idx, int var)
    {
        gunType = type;
        gunIdx = idx;

        int equippedType = PlayerBase.GetEquippedGun();
        int equippedidx = PlayerBase.GetWeaponIdx();

        if (gunType == equippedType && gunIdx == equippedidx)
        {
            currentWeaponText.SetActive(true);
        }
        else
        {
            currentWeaponText.SetActive(false);
        }

        SetGunImage(type * 5 + idx);
        SetWeaponStats(type, idx);
        SelectedGunOptions(var);
        gunBuyPrice.text = Weapon.price[gunType][gunIdx].ToString();

        gunTap.Execute();
        StudioHaptics.PlayHapticSelection();
        gunName.text = gunNames[type * 5 + idx];
        Tutorial.DoIt(type, idx);
    }
    void SelectedGunOptions(int state)
    {
        Button btn = selectedGunOptions[0].GetComponent(typeof(Button)) as Button;
        btn.onClick.RemoveAllListeners();
        btn = selectedGunOptions[2].GetComponent(typeof(Button)) as Button;
        btn.onClick.RemoveAllListeners();
        switch (state)
        {
            case 0:
                selectedGunOptions[0].SetActive(true);
                selectedGunOptions[1].SetActive(false);
                selectedGunOptions[2].SetActive(false);
                break;

            case 1:
                selectedGunOptions[0].SetActive(false);
                selectedGunOptions[1].SetActive(true);
                selectedGunOptions[2].SetActive(false);
                break;

            case 3:
                selectedGunOptions[0].SetActive(false);
                selectedGunOptions[1].SetActive(false);
                selectedGunOptions[2].SetActive(true);
                break;
        }

        btn = selectedGunOptions[0].GetComponent(typeof(Button)) as Button;
        btn.onClick.AddListener(() => EquipGun(false));
        btn = selectedGunOptions[2].GetComponent(typeof(Button)) as Button;
        btn.onClick.AddListener(BuyGun);

        TMP_Text txt = selectedGunOptions[2].transform.GetChild(1).GetComponent(typeof(TMP_Text)) as TMP_Text;

        txt.text = Weapon.price[gunType][gunIdx].ToString();
    }
    public GameObject GetBuyButton()
    {
        return selectedGunOptions[2];
    }
    void EquipGun(bool isBuy)
    {
        NormalButton(PlayerBase.GetEquippedGun(), PlayerBase.GetWeaponIdx());
        EquipButton(gunType, gunIdx);
        PlayerBase.SetEquippedGun(gunType);
        PlayerBase.SetWeaponIdx(gunIdx);

        if (!isBuy)
        {
            currentWeaponText.SetActive(true);
            gunEquip.Execute();
            StudioHaptics.PlayHapticSelection();
        }

        SelectedGunOptions(1);
    }
    void BuyGun()
    {
        int score = PlayerBase.GetScore();
        if (score >= Weapon.price[gunType][gunIdx])
        {
            string gunTypeStr = "";
            switch(gunType)
            {
                case 0:
                    gunTypeStr = "Pistol";
                    break;
                case 1:
                    gunTypeStr = "Shotgun";
                    break;
                case 2:
                    gunTypeStr = "Sniper";
                    break;
            }
            AnalyticsAndLeaderboard.SetGunType(gunTypeStr);

            SelectedGunOptions(0);
            StudioHaptics.PlayHapticSelection();
            PlayerBase.SetScore(score - Weapon.price[gunType][gunIdx]);
            gemCount.text = PlayerBase.GetScore().ToString();
            hasPurchased[gunType][gunIdx] = true;
            NormalButton(gunType, gunIdx);
            StudioUser.OnItemPurchased(gunPurchasableNames[gunType * 5 + gunIdx]);
            Debug.Log("OnItemPurchased " + gunPurchasableNames[gunType * 5 + gunIdx]);

            gunBuy.Execute();
            SetPurchasedGuns();
            EquipGun(true);
        }
        else
        {
            StartCoroutine(ShowNoCoinPopUp());
        }
    }
    IEnumerator ShowNoCoinPopUp()
    {
        coinPopup.SetActive(true);

        yield return new WaitForSeconds(3);

        coinPopup.SetActive(false);
    }
    void EquipButton(int i, int j)
    {
        gunSelectionPanel[i].transform.GetChild(j).GetChild(0).gameObject.SetActive(false);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(1).gameObject.SetActive(true);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(3).gameObject.SetActive(false);
    }
    void NormalButton(int i, int j)
    {
        gunSelectionPanel[i].transform.GetChild(j).GetChild(0).gameObject.SetActive(true);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(1).gameObject.SetActive(false);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(3).gameObject.SetActive(false);
    }
    void BuyButton(int i, int j)
    {
        gunSelectionPanel[i].transform.GetChild(j).GetChild(0).gameObject.SetActive(false);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(1).gameObject.SetActive(false);
        gunSelectionPanel[i].transform.GetChild(j).GetChild(3).gameObject.SetActive(true);
    }
    public GameObject GetGunSlot(int i, int j)
    {
        return gunSelectionPanel[i].transform.GetChild(j).gameObject;
    }
    void SetWeaponStats(int type, int idx)
    {
        float firerate = 0, damage = 0, clipsize = 0;
        switch (type)
        {
            case 0:
                firerate = Weapon.handgunStats[idx][0];
                damage = Weapon.handgunStats[idx][2];
                clipsize = Weapon.handgunStats[idx][1];
                break;

            case 1:
                firerate = Weapon.shotgunStats[idx][0];
                damage = Weapon.shotgunStats[idx][2];
                clipsize = Weapon.shotgunStats[idx][1];
                break;

            case 2:
                firerate = Weapon.sniperStats[idx][0];
                damage = Weapon.sniperStats[idx][2];
                clipsize = Weapon.sniperStats[idx][1];
                break;
        }
        int maxCount, dmg, maxClipSize;
        if (type == 0)
        {
            maxCount = 10;
            dmg = 10;
            maxClipSize = 30;
        }
        else if (type == 1)
        {
            maxCount = 5;
            dmg = 15;
            maxClipSize = 15;
        }
        else
        {
            maxCount = 5;
            dmg = 20;
            maxClipSize = 20;
        }
        Image img = fireRate.GetComponent(typeof(Image)) as Image;
        img.fillAmount =  damage / dmg;

        img = reloadTime.GetComponent(typeof(Image)) as Image;
        img.fillAmount = firerate / maxCount;

        img = clipSize.GetComponent(typeof(Image)) as Image;
        img.fillAmount = clipsize / maxClipSize;
    }
    void ButtonInitialization()
    {
        Button btn2;
        btn2 = gunSelectionPanel[0].transform.GetChild(0).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 0, 0); });
        btn2 = gunSelectionPanel[0].transform.GetChild(0).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 0, 1); });
        btn2 = gunSelectionPanel[0].transform.GetChild(0).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 0, 3); });

        btn2 = gunSelectionPanel[0].transform.GetChild(1).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 1, 0); });
        btn2 = gunSelectionPanel[0].transform.GetChild(1).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 1, 1); });
        btn2 = gunSelectionPanel[0].transform.GetChild(1).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 1, 3); });

        btn2 = gunSelectionPanel[0].transform.GetChild(2).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 2, 0); });
        btn2 = gunSelectionPanel[0].transform.GetChild(2).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 2, 1); });
        btn2 = gunSelectionPanel[0].transform.GetChild(2).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 2, 3); });

        btn2 = gunSelectionPanel[0].transform.GetChild(3).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 3, 0); });
        btn2 = gunSelectionPanel[0].transform.GetChild(3).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 3, 1); });
        btn2 = gunSelectionPanel[0].transform.GetChild(3).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 3, 3); });

        btn2 = gunSelectionPanel[0].transform.GetChild(4).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 4, 0); });
        btn2 = gunSelectionPanel[0].transform.GetChild(4).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 4, 1); });
        btn2 = gunSelectionPanel[0].transform.GetChild(4).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(0, 4, 3); });



        btn2 = gunSelectionPanel[1].transform.GetChild(0).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 0, 0); });
        btn2 = gunSelectionPanel[1].transform.GetChild(0).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 0, 1); });
        btn2 = gunSelectionPanel[1].transform.GetChild(0).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 0, 3); });

        btn2 = gunSelectionPanel[1].transform.GetChild(1).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 1, 0); });
        btn2 = gunSelectionPanel[1].transform.GetChild(1).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 1, 1); });
        btn2 = gunSelectionPanel[1].transform.GetChild(1).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 1, 3); });

        btn2 = gunSelectionPanel[1].transform.GetChild(2).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 2, 0); });
        btn2 = gunSelectionPanel[1].transform.GetChild(2).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 2, 1); });
        btn2 = gunSelectionPanel[1].transform.GetChild(2).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 2, 3); });

        btn2 = gunSelectionPanel[1].transform.GetChild(3).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 3, 0); });
        btn2 = gunSelectionPanel[1].transform.GetChild(3).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 3, 1); });
        btn2 = gunSelectionPanel[1].transform.GetChild(3).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 3, 3); });

        btn2 = gunSelectionPanel[1].transform.GetChild(4).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 4, 0); });
        btn2 = gunSelectionPanel[1].transform.GetChild(4).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 4, 1); });
        btn2 = gunSelectionPanel[1].transform.GetChild(4).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(1, 4, 3); });



        btn2 = gunSelectionPanel[2].transform.GetChild(0).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 0, 0); });
        btn2 = gunSelectionPanel[2].transform.GetChild(0).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 0, 1); });
        btn2 = gunSelectionPanel[2].transform.GetChild(0).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 0, 3); });

        btn2 = gunSelectionPanel[2].transform.GetChild(1).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 1, 0); });
        btn2 = gunSelectionPanel[2].transform.GetChild(1).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 1, 1); });
        btn2 = gunSelectionPanel[2].transform.GetChild(1).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 1, 3); });

        btn2 = gunSelectionPanel[2].transform.GetChild(2).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 2, 0); });
        btn2 = gunSelectionPanel[2].transform.GetChild(2).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 2, 1); });
        btn2 = gunSelectionPanel[2].transform.GetChild(2).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 2, 3); });

        btn2 = gunSelectionPanel[2].transform.GetChild(3).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 3, 0); });
        btn2 = gunSelectionPanel[2].transform.GetChild(3).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 3, 1); });
        btn2 = gunSelectionPanel[2].transform.GetChild(3).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 3, 3); });

        btn2 = gunSelectionPanel[2].transform.GetChild(4).GetChild(0).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 4, 0); });
        btn2 = gunSelectionPanel[2].transform.GetChild(4).GetChild(1).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 4, 1); });
        btn2 = gunSelectionPanel[2].transform.GetChild(4).GetChild(3).GetComponent(typeof(Button)) as Button;
        btn2.onClick.AddListener(() => { DoSomething(2, 4, 3); });

        for (int i = 0; i < gunSelectionPanel.Length; i++)
        {
            for (int j = 0; j < gunSelectionPanel[i].transform.childCount; j++)
            {
                Transform obj = gunSelectionPanel[i].transform.GetChild(j).GetChild(3).GetChild(2);
                TMP_Text txt = obj.GetComponent(typeof(TMP_Text)) as TMP_Text;

                txt.text = Weapon.price[i][j].ToString();
            }
        }
    }

    void SwitchShop()
    {
        addon.SetActive(true);
        StudioExtensions.ToggleHomeButton(true);
        leaderboardButtonObj.SetActive(true);
        AnalyticsAndLeaderboard.SetBuyInfo();
        homescreenScript.UpdateCoins();
        StudioHaptics.PlayHapticSelection();
        buttonObjective.Execute();
        homescreenScript.SetGunImage();

        homescreenUI.SetActive(true);
        actualShopUI.SetActive(false);
    }
}


```

## TC_Shop.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class TC_Shop : StudioBehaviour
{
    GameObject tcShop;
    GameObject homescreenUI;
    GameObject leaderboardButtonObj;
    Button Buy1;
    Button Buy2;
    Button Buy3;
    Button Buy4;
    TMP_Text terraCoinText;
    TMP_Text DiamondText;
    TMP_Text bottomText;
    GameObject addon;
    HomescreenMenu homescreen;
    string[] buyStrings = new string[]
    {
        "300Diamonds",
        "150Diamonds",
        "900Diamonds",
        "500Diamonds",
    };
    int[] buyDiamondPrice = new int[] {300, 150, 900, 500};
    int[] spendCoinPrice = new int[] {80, 45, 650, 100};
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        Initialization();
    }

    // Gets called every frame
    private void Update()
    {
       
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }

    void Initialization()
    {
        var tcshopObj = GetGameObjectVariable("TCShop");
        var editUI = GetTemplate(tcshopObj, typeof(EditUITemplate)) as EditUITemplate;
        tcShop = editUI.GetInstantiatedUI;

        homescreen = GetComponent(typeof(HomescreenMenu)) as HomescreenMenu;

        GameObject homescreenObj = GetGameObjectVariable("HomescreenUI");
        EditUITemplate obj = GetTemplate(homescreenObj, typeof(EditUITemplate)) as EditUITemplate;
        homescreenUI = obj.GetInstantiatedUI;

        var homeObj = StudioExtensions.FindDeepChild(tcShop.transform, "Home_button").gameObject;
        Button homeButton = homeObj.GetComponent(typeof(Button)) as Button;
        homeButton.onClick.AddListener(GoHome);

        var button = StudioExtensions.FindDeepChild(tcShop.transform, "Item1_buy_button").gameObject;
        Button buyButton = button.GetComponent(typeof(Button)) as Button;
        buyButton.onClick.AddListener(() => BuyCoins(0));

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Item2_buy_button").gameObject;
        buyButton = button.GetComponent(typeof(Button)) as Button;
        buyButton.onClick.AddListener(() => BuyCoins(1));

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Item3_buy_button").gameObject;
        buyButton = button.GetComponent(typeof(Button)) as Button;
        buyButton.onClick.AddListener(() => BuyCoins(2));

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Item4_buy_button").gameObject;
        buyButton = button.GetComponent(typeof(Button)) as Button;
        buyButton.onClick.AddListener(() => BuyCoins(3));

        var lbObj = GetGameObjectVariable("LeaderboardButton");
        var lbeditUI = GetTemplate(lbObj, typeof(EditUITemplate)) as EditUITemplate;
        leaderboardButtonObj = lbeditUI.GetInstantiatedUI;

        var addonObj = GetGameObjectVariable("HomescreenAddon");
        var adeditUI = GetTemplate(addonObj, typeof(EditUITemplate)) as EditUITemplate;
        addon = adeditUI.GetInstantiatedUI;

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Terra_coin_count_text").gameObject;
        terraCoinText = button.GetComponent(typeof(TMP_Text)) as TMP_Text;

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Diamond_count_text").gameObject;
        DiamondText = button.GetComponent(typeof(TMP_Text)) as TMP_Text;

        button = StudioExtensions.FindDeepChild(tcShop.transform, "Bottom_text").gameObject;
        bottomText = button.GetComponent(typeof(TMP_Text)) as TMP_Text;

        terraCoinText.text = StudioUser.GetUserTerraCoins().ToString();
        DiamondText.text = PlayerBase.GetScore().ToString();
        tcShop.SetActive(false);
    }

    void GoHome()
    {
        StudioHaptics.PlayHapticSelection();
        StudioExtensions.ToggleHomeButton(true);

        leaderboardButtonObj.SetActive(true);
        homescreen.UpdateTerraCoinText();
        homescreen.UpdateCoins();
        tcShop.SetActive(false);
        homescreenUI.SetActive(true);
        addon.SetActive(true);
    }

    void BuyCoins(int idx)
    {
        int terraCoins = StudioUser.GetUserTerraCoins();
        if (terraCoins < spendCoinPrice[idx])
        {
            Debug.Log("Not Enough Coins");
            bottomText.text = "Not Enough Coins to buy Diamonds";
            bottomText.color = Color.red;
            return;
        }

        Broadcast("GunBuy");

        StudioUser.OnItemPurchased(buyStrings[idx]);
        Debug.Log("OnItemPurchased " + buyStrings[idx]);

        StudioUser.SpendUserTerraCoins(spendCoinPrice[idx]);
        Debug.Log("SpendUserCoins " + spendCoinPrice[idx]);

        PlayerBase.SetScore(PlayerBase.GetScore() + buyDiamondPrice[idx]);

        terraCoinText.text = StudioUser.GetUserTerraCoins().ToString();
        DiamondText.text = PlayerBase.GetScore().ToString();

        bottomText.text = "Diamonds Purchased";
        bottomText.color = Color.white;
    }
}


```

## TerraAutoAim.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class TerraAutoAim : StudioBehaviour
{
    private float targetSwitchDelay = 1f;
    private float radius;
    private float turnRate = 5f;
    private float lineOfSightAngle = 30f;
    private float indicatorHeight;
    private GameObject enemyIndicator;
    private Material meshMaterial;
    private Transform modelTr;
    private bool wasTrackingInLastFrame;
    private Transform currentLockedEnemy;
    private float cachedRadius;
    private Mesh cachedMesh;
    private Coroutine coroutine;
    private StudioController controller;

    public Transform CurrentLockedEnemy => currentLockedEnemy;

    private void Start()
    {
        targetSwitchDelay = GetFloatVariable("TargetSwitchDelay");
        radius = GetFloatVariable("Radius");
        turnRate = GetFloatVariable("TurnRate");
        lineOfSightAngle = GetFloatVariable("LineOfSightAngle");
        indicatorHeight = GetFloatVariable("IndicatorHeight");
        enemyIndicator = GetGameObjectVariable("EnemyIndicator");
        //meshMaterial = (GetGameObjectVariable("MeshReference").GetComponent(typeof(MeshRenderer)) as MeshRenderer).material;
        modelTr = transform;
    }

    public void Init(StudioController controller)
    {
        this.controller = controller;
    }

    public bool TryTrackEnemy(Transform newEnemy)
    {
        if (!newEnemy || !modelTr)
        {
            return false;
        }
        var distance = Vector3.Distance(newEnemy.position, modelTr.position);
        if (coroutine != null || distance > radius)
        {
            return false;
        }
        if (currentLockedEnemy && distance > GetTrackedEnemyDistanceDelta())
        {
            return false;
        }
        Untrack(currentLockedEnemy);
        currentLockedEnemy = newEnemy;
        TogglePlayerMovementRotation(false);
        coroutine = StartCoroutine(TrackCoroutine());
        return true;
    }

    public bool IsEnemyInLineOfSight()
    {
        if (!currentLockedEnemy)
        {
            return false;
        }
        var targetDir = currentLockedEnemy.transform.position - modelTr.position;
        targetDir.y = 0f;
        var angle = Vector3.Angle(modelTr.forward, targetDir);
        return angle < lineOfSightAngle;
    }

    public void Untrack(Transform enemy)
    {
        if (!currentLockedEnemy)
        {
            return;
        }
        if (currentLockedEnemy == enemy)
        {
            ResetStoredValues();
        }
    }

    private IEnumerator TrackCoroutine()
    {
        yield return new WaitForSeconds(targetSwitchDelay);
        coroutine = null;
    }

    private void HaltTrackCoroutine()
    {
        if (coroutine == null)
        {
            return;
        }
        StopCoroutine(coroutine);
        coroutine = null;
    }

    private void TogglePlayerMovementRotation(bool status)
    {
        controller.TogglePlayerRotation(status);
    }

    private void ResetStoredValues()
    {
        currentLockedEnemy = null;
        HaltTrackCoroutine();
        TogglePlayerMovementRotation(true);
    }

    private void Update()
    {
        //DrawMesh();
        if (!currentLockedEnemy)
        {
            enemyIndicator.transform.position = Vector3.down;
            if (wasTrackingInLastFrame)
            {
                ResetStoredValues();
            }
            wasTrackingInLastFrame = false;
            return;
        }
        else
        {
            enemyIndicator.transform.position = currentLockedEnemy.position + Vector3.up * indicatorHeight;
        }

        LockOnToEnemy();
        CheckCurrentDelta();
        wasTrackingInLastFrame = true;
    }
    public bool IsEnemyThere()
    {
        if (currentLockedEnemy)
        {
            return true;
        }

        return false;
    }
    private void CheckCurrentDelta()
    {
        var distance = GetTrackedEnemyDistanceDelta();
        if (distance > radius || distance < 0f)
        {
            ResetStoredValues();
        }
    }

    private float GetTrackedEnemyDistanceDelta()
    {
        if (!currentLockedEnemy)
        {
            return float.PositiveInfinity;
        }
        return Vector3.Distance(currentLockedEnemy.position, modelTr.position);
    }

    private void LockOnToEnemy()
    {
        var targetDir = currentLockedEnemy.transform.position - modelTr.position;
        targetDir.y = 0f;
        var step = Time.deltaTime * turnRate;
        var newDir = Vector3.RotateTowards(modelTr.forward, targetDir, step, 0.0f);
        modelTr.rotation = Quaternion.LookRotation(newDir);
    }

    private void DrawMesh()
    {
        if (cachedRadius != radius) GenerateMesh();
        var position = transform.position;
        position.y += 0.1f;
        Graphics.DrawMesh(cachedMesh, position, Quaternion.Euler(new Vector3(-180f, 0f, 0f)), meshMaterial, 0);
    }

    private void GenerateMesh()
    {
        if (!cachedMesh) Destroy(cachedMesh);
        var mesh = CreateDisc(radius, 32);
        cachedMesh = mesh;
        cachedRadius = radius;
    }

    private Mesh CreateDisc(float radius, int segments)
    {
        var mesh = new Mesh();
        var vertices = new Vector3[segments + 1];
        var triangles = new int[segments * 3];
        vertices[0] = Vector3.zero;
        var angleStep = 360f / segments;
        for (int i = 1; i <= segments; i++)
        {
            var angle = angleStep * i * Mathf.Deg2Rad;
            vertices[i] = new Vector3(Mathf.Cos(angle) * radius, 0, Mathf.Sin(angle) * radius);
            if (i < segments)
            {
                triangles[(i - 1) * 3] = 0;
                triangles[(i - 1) * 3 + 1] = i;
                triangles[(i - 1) * 3 + 2] = i + 1;
            }
        }
        triangles[(segments - 1) * 3] = 0;
        triangles[(segments - 1) * 3 + 1] = segments;
        triangles[(segments - 1) * 3 + 2] = 1;
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.RecalculateNormals();
        mesh.name = $"Disc {radius} {segments}";
        return mesh;
    }
}
```

## TerraBootstrap.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class TerraBootstrap : StudioBehaviour
{
    private TerraWeaponController weaponController;
    private TerraAutoAim autoAim;

    private void Start()
    {
        StartCoroutine(WaitAndSetup());
    }

    private IEnumerator WaitAndSetup()
    {
        yield return null;
        var controller = GetGameObjectVariable("Controller");
        weaponController = controller.GetComponent(typeof(TerraWeaponController)) as TerraWeaponController;

        autoAim = controller.GetComponent(typeof(TerraAutoAim)) as TerraAutoAim;
        StartCoroutine(WaitForController());
    }

    private IEnumerator WaitForController()
    {
        StudioController controller = null;
        while (controller == null)
        {
            yield return null;
            controller = StudioController.GetMyController();
        }
        weaponController.Init(controller);
        autoAim.Init(controller);
    }
}
```

## TerraBullet.cs

```csharp
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class TerraBullet : StudioBehaviour
{
    public float speed = 15f;
    public float destroyAfter = 10f;
    private static float damageToDeal = 1f;
    private Rigidbody rb;
    private float minSize;
    private float maxSize;
    private float smoothTime;

    private Vector3 cachedForward;

    private const string var_Speed = "Speed";
    private const string var_DestroyAfter = "DestroyAfter";
    private const string var_DamageToDeal = "DamageToDeal";
    private const string var_MinSize = "MinSize";
    private const string var_MaxSize = "MaxSize";
    private const string var_SmoothTime = "SmoothTime";

    private void Start()
    {
        Initialization();
    }

    private void Update()
    {
        DestroyCounter();
    }

    private void FixedUpdate()
    {
        if (speed != 0)
        {
            rb.velocity = cachedForward * speed;

            transform.localScale = Vector3.Lerp(transform.localScale, Vector3.one * maxSize, smoothTime);
        }
    }

    private void OnCollisionEnter(Collision other)
    {
        var controller = StudioController.CheckIfController(other.gameObject);
        if (controller != null) return;
        Destroy(gameObject);
    }

    void Initialization()
    {
        speed = GetFloatVariable(var_Speed);
        destroyAfter = GetFloatVariable(var_DestroyAfter);
        damageToDeal = GetFloatVariable(var_DamageToDeal);
        minSize = GetFloatVariable(var_MinSize);
        maxSize = GetFloatVariable(var_MaxSize);
        smoothTime = GetFloatVariable(var_SmoothTime);
        rb = GetComponent(typeof(Rigidbody)) as Rigidbody;
        cachedForward = transform.up;

        transform.localScale = Vector3.one * minSize;
    }

    void DestroyCounter()
    {
        if (destroyAfter <= 0f)
        {
            Destroy(gameObject);
        }
        else
        {
            destroyAfter -= Time.deltaTime;
        }
    }
    public static float GetDamage()
    {
        return damageToDeal;
    }
    public static void SetDamage(float dmg)
    {
        damageToDeal = dmg;
    }
}
```

## TerraEnemy.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.UI;

/*
 * 1 - Idle
 * 2 - Follow
 * 3 - Attack
 * 4 - Hit
 * 5 - Dead
 */
public class TerraEnemy : StudioBehaviour
{
    private static bool stop;

    private bool IsInCooldown;
    private float cooldownTime;
    private float radius;
    private float totalHealth;
    private float followingHealth;
    private float maxHealth;
    private GameObject playerModel;
    private GameObject[] collectibles = new GameObject[3];
    private TerraAutoAim autoAim;
    private StudioController controller;
    private float speed;
    private float maxSpeed;
    private int enemyState;
    private bool isHurt;
    private float hitRecoverTime;
    private PlayAnimationTemplate anim;
    private ParticleEffectTemplate hitParticleEffect;
    private GameObject healthbar;
    private Image healthbarFiller;

    private SoundFxTemplate attackFx;
    private SoundFxTemplate dieFx;
    private SoundFxTemplate[] hitFx = new SoundFxTemplate[8];
    private SoundFxTemplate footstepFx;

    private const int IDLE = 1;
    private const int FOLLOW = 2;
    private const int ATTACK = 3;
    private const int HIT = 4;
    private const int DEAD = 5;

    private const int AttackIdx = 2;
    private const int DieIdx = 3;
    private const int HitIdx = 4;

    private const string ANIM_IDLE = "Take 001";
    private const string ANIM_RUN = "Run";
    private const string ANIM_ATTACK = "Attack";
    private const string ANIM_GETHIT = "Hit";
    private const string ANIM_DEATH = "Dead";

    private const string var_Radius = "Radius";
    private const string var_TotalHealth = "TotalHealth";
    private const string var_PlayerModel = "PlayerModel";
    private const string var_Speed = "Speed";
    private const string var_BackDist = "BackDist";
    private const string var_HitRecoverTime = "HitRecoverTime";
    private const string var_HitParticleObject = "HitParticleObject";
    private const string var_HealthCollect = "HealthCollect";
    private const string var_AmmoCollect = "AmmoCollect";
    private const string var_ArmorCollect = "ArmorCollect";
    private const string var_CooldownTime = "AttackCooldown";

    private void Start()
    {
        Initialization();

        anim.OnAnimationCompleted += AnimationTransition;

        Init(StudioController.GetMyController(), playerModel.GetComponent(typeof(TerraAutoAim)) as TerraAutoAim);

        ChangeState(IDLE);
    }
    private void Update()
    {
        if (controller == null)
        {
            return;
        }
        if (healthbar != null)
        {
            healthbar.transform.position = Camera.main.WorldToScreenPoint(transform.position);
        }
        if (stop)
        {
            return;
        }
        if(followingHealth > totalHealth)
        {
            followingHealth -= Time.deltaTime * 10;
            healthbarFiller.fillAmount = followingHealth / maxHealth;
        }
        else
        {
            followingHealth = totalHealth;
        }
        if (enemyState == DEAD)
        {
            return;
        }
        if (isHurt)
        {
            return;
        }
        if (enemyState != ATTACK)
        {
            CheckPlayerAndFollow();
        }

        DieAndDropCollectible();
    }
    public override void OnBroadcasted(string x)
    {
        if (x == "PlayerWin")
        {
            stop = true;
        }
        else if (x == "PlayerDead")
        {
            stop = true;
        }
    }
    private void OnCollisionEnter(Collision other)
    {
        if (stop)
        {
            return;
        }
        if (other == null || other.gameObject == null)
        {
            return;
        }
        if (enemyState == DEAD)
        {
            return;
        }

        var script = other.gameObject.GetComponent(typeof(TerraBullet));
        if (script == null)
        {
            return;
        }
        var bullet = script as TerraBullet;
        if (bullet == null)
        {
            return;
        }

        TakeDamage(bullet);
    }
    IEnumerator AttackCooldown()
    {
        IsInCooldown = true;

        yield return new WaitForSeconds(cooldownTime);

        IsInCooldown = false;
    }
    void Initialization()
    {
        int gunType = PlayerBase.GetEquippedGun();
        switch (gunType)
        {
            case 0:
                radius = 9;
                break;
            case 1:
                radius = 6;
                break;
            case 2:
                radius = 12;
                break;
        }
        maxHealth = GetFloatVariable(var_TotalHealth);
        playerModel = GetGameObjectVariable(var_PlayerModel);
        maxSpeed = GetFloatVariable(var_Speed);
        hitRecoverTime = GetFloatVariable(var_HitRecoverTime);
        cooldownTime = GetFloatVariable(var_CooldownTime);

        GameObject hitParticleObject = transform.GetChild(1).gameObject;
        hitParticleEffect = GetTemplate(hitParticleObject, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;

        GameObject obj;
        obj = transform.GetChild(AttackIdx).gameObject;
        attackFx = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj = transform.GetChild(DieIdx).gameObject;
        dieFx = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj = transform.GetChild(4).gameObject;
        footstepFx = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        footstepFx.Volume = 0;
        footstepFx.Execute();

        int counter = 0;
        for (int i = 5; i < transform.childCount; i++, counter++)
        {
            obj = transform.GetChild(i).gameObject;
            hitFx[counter] = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        }

        anim = GetTemplate(typeof(PlayAnimationTemplate)) as PlayAnimationTemplate;

        collectibles[0] = GetGameObjectVariable(var_HealthCollect);
        collectibles[1] = GetGameObjectVariable(var_AmmoCollect);
        collectibles[2] = GetGameObjectVariable(var_ArmorCollect);

        var UI = GetTemplate(GetGameObjectVariable("HealthUI"), typeof(EditUITemplate)) as EditUITemplate;
        healthbar = UI.GetInstantiatedUI;
        healthbarFiller = StudioExtensions.FindDeepChild(UI.GetInstantiatedUI.transform, "Health_fill").GetComponent(typeof(Image)) as Image;

        totalHealth = maxHealth;
        followingHealth = totalHealth;
        speed = maxSpeed;
    }
    public void Init(StudioController controller, TerraAutoAim autoAim)
    {
        this.controller = controller;
        this.autoAim = autoAim;
    }
    private void CheckPlayerAndFollow()
    {
        var delta = Vector3.Distance(controller.GetPlayerPosition(), transform.position);
        if (delta <= radius)
        {
            Vector3 dir = (controller.GetPlayerPosition() - transform.position).normalized;
            if (dir.y > 0.4f || dir.y < -0.4f)
            {
                ChangeState(IDLE);
                return;
            }
            RaycastHit hit;
            if (Physics.Raycast(transform.position + transform.up, dir, out hit, radius))
            {
                if (hit.collider.transform.root.name != autoAim.transform.root.name)
                {
                    ChangeState(IDLE);
                    return;
                }
            }
            autoAim.TryTrackEnemy(transform);
            transform.LookAt(controller.GetPlayerPosition());
            float dist = Vector3.Distance(transform.position, controller.GetPlayerPosition());

            if (dist >= 1)
            {
                ChangeState(FOLLOW);
                transform.position += speed * Time.deltaTime * transform.forward;
            }
            else
            {
                if (!IsInCooldown)
                {
                    AttackPlayer();
                    StartCoroutine(AttackCooldown());
                }
            }
        }
        else
        {
            ChangeState(IDLE);
        }
    }
    void ChangeState(int state)
    {
        if (enemyState == state)
        {
            return;
        }
        switch (state)
        {
            case IDLE:
                footstepFx.Volume = 0f;
                footstepFx.Execute();
                if (isHurt)
                {
                    return;
                }
                anim.PlayAnimationOverride(ANIM_IDLE, true);
                break;

            case FOLLOW:
                footstepFx.Volume = 0.2f;
                footstepFx.Execute();
                if (isHurt)
                {
                    return;
                }
                anim.PlayAnimationOverride(ANIM_RUN, true);
                break;

            case ATTACK:
                footstepFx.Volume = 0f;
                footstepFx.Execute();
                attackFx.Execute();
                anim.PlayAnimationOverride(ANIM_ATTACK, false);
                break;

            case HIT:
                if (anim.CurrentAnimation == ANIM_GETHIT)
                {
                    break;
                }
                footstepFx.Volume = 0f;
                footstepFx.Execute();
                StartCoroutine(HitRecoverTimer());
                int fx = Random.Range(0, hitFx.Length);
                hitFx[fx].Execute();
                hitParticleEffect.Execute();
                anim.PlayAnimationOverride(ANIM_GETHIT, false);
                break;

            case DEAD:
                footstepFx.Volume = 0f;
                footstepFx.Execute();
                dieFx.Execute();

                anim.PlayAnimationOverride(ANIM_DEATH, false);

                break;
        }

        enemyState = state;
    }
    IEnumerator HitRecoverTimer()
    {
        isHurt = true;

        yield return new WaitForSeconds(hitRecoverTime);

        isHurt = false;
    }
    void AttackPlayer()
    {
        //if (other.transform.root == playerModel.transform.root)
        //{
        ChangeState(ATTACK);
        //IsInRange = true;
        if (!PlayerController.isShowingShield)
        {
            Broadcast("DealDamage");
        }
        else
        {
            Broadcast("DamageShield");
        }
        //}
    }
    void TakeDamage(TerraBullet bullet)
    {
        totalHealth -= TerraBullet.GetDamage();

        if (totalHealth <= 0)
        {
            healthbar.SetActive(false);
            return;
        }
        if (!isHurt)
        {
            ChangeState(HIT);
        }
    }
    void AnimationTransition(string str)
    {
        if (str == ANIM_DEATH)
        {
            PlayerController.SetEnemyKills(PlayerController.GetEnemyKills() + 1);
            PlayerController.SetLevelEnemyKills(PlayerController.GetLevelEnemyKills() + 1);
            AnalyticsAndLeaderboard.SetKillCount();
            PlayerBase.SetScore(PlayerBase.GetScore() + 15);

            GrowTemplate destroy = GetTemplate(typeof(GrowTemplate)) as GrowTemplate;
            destroy.Speed = 2;
            destroy.Execute();
            autoAim.TryTrackEnemy(null);
            StudioAnalytics.SetPrimarySessionScore(PlayerController.GetLevelEnemyKills());
            StartCoroutine(DestroyEnemy());
        }
        else if (str == ANIM_ATTACK)
        {
            ChangeState(IDLE);
        }
    }
    IEnumerator DestroyEnemy()
    {
        DestroyTemplate destroy = GetTemplate(typeof(DestroyTemplate)) as DestroyTemplate;

        yield return new WaitForSeconds(0.7f);

        destroy.Execute();
    }
    void DieAndDropCollectible()
    {
        if (totalHealth <= 0)
        {
            if (Random.Range(0, 2) == 0)
            {
                Instantiate(collectibles[Random.Range(0, collectibles.Length)], transform.position, Quaternion.identity);
            }
            ChangeState(DEAD);
        }
    }

    public static void SetStop(bool val)
    {
        stop = val;
    }
}
```

## TerraMagazine.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using UnityEngine;

public class TerraMagazine : StudioBehaviour
{
    private GameObject bulletPrefab;
    private Transform bulletSpawnLoc;
    private float bulletSpread;
    private float damage;
    private int totalBulletCount;
    private int currentBulletCount;
    private SoundFxTemplate shootSound;
    private ParticleEffectTemplate shootParticle;

    private const string var_BulletSpread = "BulletSpread";
    private const string var_BulletPrefab = "BulletPrefab";
    private const string var_BulletSpawnLoc = "BulletSpawnLoc";
    private const string var_TotalBulletCount = "TotalBulletCount";

    private void Start()
    {
        Initialization();
        ReloadMag();
    }
    void Initialization()
    {
        bulletPrefab = GetGameObjectVariable(var_BulletPrefab);
        bulletSpawnLoc = GetGameObjectVariable(var_BulletSpawnLoc).transform;
        totalBulletCount = GetIntVariable(var_TotalBulletCount);

        GameObject shoot = bulletSpawnLoc.GetChild(0).gameObject;
        shootSound = GetTemplate(shoot, typeof(SoundFxTemplate)) as SoundFxTemplate;
        shoot = bulletSpawnLoc.GetChild(1).gameObject;
        shootParticle = GetTemplate(shoot, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;

        if (GetIntVariable("ID") == 1)
        {
            bulletSpread = GetFloatVariable(var_BulletSpread);
        }
    }
    public bool CanShoot()
    {
        return currentBulletCount > 0;
    }
    public void SetTotalBulletCount(int bulletCount)
    {
        totalBulletCount = bulletCount;
    }
    public void SetBulletSpread(float bulletSpread)
    {
        this.bulletSpread = bulletSpread;
    }
    public void Shoot(Vector3 dir)
    {
        int weaponIdx = PlayerBase.GetEquippedGun();
        if (weaponIdx == 1)
        {
            StartCoroutine(FireShotgun(dir));
        }
        else
        {
            StartCoroutine(Fire(dir));
        }
        currentBulletCount--;
        shootSound.Execute();
        shootParticle.Execute();
        StudioHaptics.PlayHapticLightImpact();
    }
    IEnumerator Fire(Vector3 dir)
    {
        var bullet = Instantiate(bulletPrefab);
        bullet.transform.position = bulletSpawnLoc.position;
        bullet.gameObject.layer = LayerMask.NameToLayer("Bullet");
        bullet.gameObject.name = "Bullet";
        bullet.transform.up = dir;
        bullet.SetActive(true);

        yield return null;
        
    }
    IEnumerator FireShotgun(Vector3 dir)
    {
        for (int i = -1; i <= 1; i++)
        {
            var bullet = Instantiate(bulletPrefab);

            bullet.transform.position = bulletSpawnLoc.position + transform.right * i * bulletSpread;
            bullet.gameObject.layer = LayerMask.NameToLayer("Bullet");
            bullet.gameObject.name = "Bullet";
            bullet.transform.up = dir;
            bullet.SetActive(true);
            yield return null;
        }
    }
    public void ReloadMag()
    {
        currentBulletCount = totalBulletCount;
    }

    public int GetCurrentBulletCount()
    {
        return currentBulletCount;
    }
    public int GetTotalBullets()
    {
        return totalBulletCount;
    }
}
```

## TerraProjectileWeapon.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

public class TerraProjectileWeapon : StudioBehaviour
{
    public int totalMagazines;
    public int firingRate;
    private int upgradeVersion;
    private int id;
    public float reloadTime = 1;
    private Coroutine reloadCoroutine;
    private int currentActiveMagazines;
    private TerraMagazine currentMagazine;
    private float lastBulletShotTime;
    private GameObject playerStats;
    private GameObject reloadingObject;
    private GameObject gunModelParent;
    private ShowUITemplate ammoUI;
    private Image reloadingImage;
    private bool isReloading;
    private GameObject[] allWeapons;

    private const string var_TotalMagazines = "TotalMagazines";
    private const string var_FiringRate = "FiringRate";
    private const string var_ReloadTime = "ReloadTime";
    private const string var_PlayerStats = "PlayerStats";
    private const string var_ReloadingUI = "ReloadingUI";
    private const string var_UpgradeVersion = "UpgradeVersion";
    private const string var_UpgradeOne = "UpgradeOne";
    private const string var_UpgradeTwo = "UpgradeTwo";
    private const string var_GunModelParent = "GunModelParent";
    private const string var_UpgradeThree = "UpgradeThree";
    private const string var_UpgradeFour = "UpgradeFour";
    private void Start()
    {
        id = GetIntVariable("ID");
        if (PlayerBase.GetEquippedGun() != id)
        {
            return;
        }
        Initialization();
        //StartCoroutine(ShowAmmoUI());
    }

    private void Initialization()
    {
        totalMagazines = GetIntVariable(var_TotalMagazines);
        firingRate = GetIntVariable(var_FiringRate);
        reloadTime = 1;
        playerStats = GetGameObjectVariable(var_PlayerStats);
        var reloadObj = GetGameObjectVariable("ReloadCanvas");
        var editUI = GetTemplate(reloadObj, typeof(EditUITemplate)) as EditUITemplate;
        reloadingObject = editUI.GetInstantiatedUI;
        reloadingImage = reloadingObject.GetComponent(typeof(Image)) as Image;
        reloadingImage.fillAmount = 1;

        gunModelParent = GetGameObjectVariable(var_GunModelParent);
        allWeapons = new GameObject[5];

        for(int i = 0; i < gunModelParent.transform.childCount; i++)
        {
            allWeapons[i] = gunModelParent.transform.GetChild(i).gameObject;
        }

        SetVersionModel();

        StartCoroutine(WaitAndGetMagazine());
        ammoUI = GetTemplate(playerStats, typeof(ShowUITemplate)) as ShowUITemplate;
        reloadingObject.SetActive(false);
    }

    public int[] GetAmmoCount()
    {
        if(currentMagazine)
        {
            return new int[] { currentMagazine.GetCurrentBulletCount(), currentActiveMagazines, currentMagazine.GetTotalBullets() };
        }

        return null;
    }
    private IEnumerator WaitAndGetMagazine()
    {
        yield return null;
        currentMagazine = GetComponent(typeof(TerraMagazine)) as TerraMagazine;
        SetGunStats(id, upgradeVersion);
    }

    public void Equip()
    {
        currentActiveMagazines = totalMagazines - 1;
        lastBulletShotTime = float.NegativeInfinity;
        Transform model = transform.GetChild(1);
        if (model.childCount != 0)
        {
            Transform prevGun = model.GetChild(0);
            prevGun.SetParent(null);
            prevGun.position = Vector3.down * 100;
        }
        SetVersionModel();
    }

    public void Shoot(Vector3 dir)
    {
        if (currentMagazine == null) return;
        if (currentActiveMagazines < 0) return;
        OnAttemptedToShoot(dir);
    }
    void SetVersionModel()
    {
        upgradeVersion = PlayerBase.GetWeaponIdx();

        allWeapons[upgradeVersion].transform.SetParent(transform.GetChild(1), false);
        allWeapons[upgradeVersion].transform.localPosition = Vector3.zero;
        allWeapons[upgradeVersion].transform.localRotation = Quaternion.identity;
    }
    private void OnAttemptedToShoot(Vector3 dir)
    {
        if (!CanShoot()) return;
        if (reloadCoroutine != null) return;
        if (currentMagazine.CanShoot())
        {
            currentMagazine.Shoot(dir);
            lastBulletShotTime = Time.time;
        }
        //Check => so that we can do an early reload
        if (!currentMagazine.CanShoot())
        {
            if (currentActiveMagazines == 0)
            {
                return;
            }
            reloadCoroutine ??= StartCoroutine(DoReload());
        }
    }
    public void AddMagazines(int mag)
    {
        currentActiveMagazines += mag;
    }
    private bool CanShoot()
    {
        var delta = Time.time - lastBulletShotTime;
        return delta >= 1f / firingRate;
    }

    private IEnumerator DoReload()
    {
        reloadingObject.SetActive(true);
        isReloading = true;
        float increment = 1f;
        float val = reloadTime;
        while (val > 0)
        {
            reloadingImage.fillAmount = 1 - (val / reloadTime);
            yield return null;
            val -= Time.deltaTime;
        }
        
        reloadCoroutine = null;
        ReloadWeapon();

        yield return null;

        isReloading = false;
        reloadingObject.SetActive(false);
    }
    void SetGunStats(int id, int version)
    {
        float[] stats = new float[4];
        switch (id)
        {
            case 0:
                stats = Weapon.handgunStats[version];
                break;
            case 1:
                stats = Weapon.shotgunStats[version];
                break;
            case 2:
                stats = Weapon.sniperStats[version];
                break;
        }
        firingRate = (int) stats[0];
        currentMagazine.SetTotalBulletCount((int) stats[1]);
        TerraBullet.SetDamage(stats[2]);
        //reloadTime = stats[2];
        if(id == 1)
        {
            currentMagazine.SetBulletSpread(stats[3]);
        }
    }
    public void ReloadWeapon()
    {
        currentActiveMagazines--;
        currentMagazine.ReloadMag();
    }
    public bool IsReloading()
    {
        return isReloading;
    }

    public float GetFireRate()
    {
        return firingRate;
    }
}
```

## TerraSpiderEnemy.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.UI;

public class TerraSpiderEnemy : StudioBehaviour
{
    private static bool stop;

    private float radius;
    private float totalHealth;
    private float followingHealth;
    private GameObject playerModel;
    private GameObject[] collectibles = new GameObject[3];
    private TerraAutoAim autoAim;
    private StudioController controller;
    private float maxHealth;
    private float speed;
    private float backDist;
    private bool hasTouched = false;
    private int enemyState;
    private bool isHurt;
    private float hitRecoverTime;
    private PlayAnimationTemplate anim;
    private ParticleEffectTemplate hitParticleEffect;
    private GameObject healthbar;
    private Image healthbarFiller;

    private SoundFxTemplate attackFx;
    private SoundFxTemplate dieFx;
    private SoundFxTemplate[] hitFx = new SoundFxTemplate[8];

    private const int IDLE = 1;
    private const int FOLLOW = 2;
    private const int ATTACK = 3;
    private const int HIT = 4;
    private const int DEAD = 5;

    private const int AttackIdx = 2;
    private const int DieIdx = 3;
    private const int HitIdx = 4;

    private string ANIM_IDLE = "idle";
    private string ANIM_WALK = "walk";
    private string ANIM_ATTACK = "attack1";
    private string ANIM_GETHIT = "hit1";
    private string ANIM_DEATH = "death1";

    private const string var_Radius = "Radius";
    private const string var_TotalHealth = "TotalHealth";
    private const string var_PlayerModel = "PlayerModel";
    private const string var_Speed = "Speed";
    private const string var_BackDist = "BackDist";
    private const string var_HitRecoverTime = "HitRecoverTime";
    private const string var_HitParticleObject = "HitParticleObject";
    private const string var_HealthCollect = "HealthCollect";
    private const string var_AmmoCollect = "AmmoCollect";
    private const string var_ArmorCollect = "ArmorCollect";

    private void Start()
    {
        Initialization();

        anim.OnAnimationCompleted += AnimationTransition;

        Init(StudioController.GetMyController(), playerModel.GetComponent(typeof(TerraAutoAim)) as TerraAutoAim);

        ChangeState(IDLE);
    }
    private void Update()
    {
        if (controller == null)
        {
            return;
        }
        if (healthbar != null)
        {
            healthbar.transform.position = Camera.main.WorldToScreenPoint(transform.position);
        }
        if (stop)
        {
            return;
        }
        if (followingHealth > totalHealth)
        {
            followingHealth -= Time.deltaTime * 10;
            healthbarFiller.fillAmount = followingHealth / maxHealth;
        }
        else
        {
            followingHealth = totalHealth;
        }
        if (enemyState == DEAD)
        {
            return;
        }
        if (anim.CurrentAnimation == ANIM_GETHIT)
        {
            return;
        }

        CheckPlayerAndFollow();
        DieAndDropCollectible();
    }
    public override void OnBroadcasted(string x)
    {
        if (x == "PlayerWin")
        {
            stop = true;
        }
        else if (x == "PlayerDead")
        {
            stop = true;
        }
    }
    private void OnCollisionEnter(Collision other)
    {
        if (stop)
        {
            return;
        }
        if (other == null || other.gameObject == null)
        {
            return;
        }
        if (enemyState == DEAD)
        {
            return;
        }
        AttackPlayer(other);

        var script = other.gameObject.GetComponent(typeof(TerraBullet));
        if (script == null)
        {
            return;
        }
        var bullet = script as TerraBullet;
        if (bullet == null)
        {
            return;
        }
        TakeDamage(bullet);
    }
    private void CheckPlayerAndFollow()
    {
        var delta = Vector3.Distance(controller.GetPlayerPosition(), transform.position);
        if (delta <= radius)
        {
            Vector3 dir = (controller.GetPlayerPosition() - transform.position).normalized;
            if (dir.y > 0.4f || dir.y < -0.4f)
            {
                ChangeState(IDLE);
                return;
            }
            RaycastHit hit;
            if (Physics.Raycast(transform.position, dir, out hit, radius))
            {
                if (hit.collider.transform.root.name != autoAim.transform.root.name)
                {
                    ChangeState(IDLE);
                    return;
                }
            }
            autoAim.TryTrackEnemy(transform);
            transform.LookAt(controller.GetPlayerPosition());
            float dist = Vector3.Distance(transform.position, controller.GetPlayerPosition());
            if (dist >= backDist)
            {
                hasTouched = false;
                ChangeState(FOLLOW);
            }
            else
            {
                ChangeState(ATTACK);
            }

            if (!hasTouched)
            {
                transform.position += speed * Time.deltaTime * transform.forward;
            }
            else
            {
                transform.position -= (speed / 4) * Time.deltaTime * transform.forward;
                ChangeState(ATTACK);
            }
        }
        else
        {
            ChangeState(IDLE);
        }
    }
    private void TakeDamage(TerraBullet bullet)
    {
        totalHealth -= TerraBullet.GetDamage();
        if (totalHealth <= 0)
        {
            healthbar.SetActive(false);
            return;
        }
        if (!isHurt)
        {
            ChangeState(HIT);
        }
    }
    void DieAndDropCollectible()
    {
        if (totalHealth <= 0)
        {
            if (Random.Range(0, 2) == 0)
            {
                Instantiate(collectibles[Random.Range(0, collectibles.Length)], transform.position, Quaternion.identity);
            }
            ChangeState(DEAD);
        }
    }
    private void AttackPlayer(Collision other)
    {
        if (other.transform.root == playerModel.transform.root)
        {
            hasTouched = true;
            if (!PlayerController.isShowingShield)
            {
                Broadcast("DealDamage");
            }
            else
            {
                Broadcast("DamageShield");
            }
        }
    }
    private void Initialization()
    {
        int gunType = PlayerBase.GetEquippedGun();
        switch (gunType)
        {
            case 0:
                radius = 9;
                break;
            case 1:
                radius = 6;
                break;
            case 2:
                radius = 12;
                break;
        }
        maxHealth = GetFloatVariable(var_TotalHealth);
        playerModel = GetGameObjectVariable(var_PlayerModel);
        speed = GetFloatVariable(var_Speed);
        backDist = GetFloatVariable(var_BackDist);
        hitRecoverTime = GetFloatVariable(var_HitRecoverTime);

        GameObject hitParticleObject = transform.GetChild(1).gameObject;
        hitParticleEffect = GetTemplate(hitParticleObject, typeof(ParticleEffectTemplate)) as ParticleEffectTemplate;

        GameObject obj;
        obj = transform.GetChild(AttackIdx).gameObject;
        attackFx = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj = transform.GetChild(DieIdx).gameObject;
        dieFx = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        obj = transform.GetChild(4).gameObject;
        int counter = 0;
        for (int i = 4; i < transform.childCount; i++, counter++)
        {
            obj = transform.GetChild(i).gameObject;
            hitFx[counter] = GetTemplate(obj, typeof(SoundFxTemplate)) as SoundFxTemplate;
        }

        anim = GetTemplate(typeof(PlayAnimationTemplate)) as PlayAnimationTemplate;

        collectibles[0] = GetGameObjectVariable(var_HealthCollect);
        collectibles[1] = GetGameObjectVariable(var_AmmoCollect);
        collectibles[2] = GetGameObjectVariable(var_ArmorCollect);

        var UI = GetTemplate(GetGameObjectVariable("HealthUI"), typeof(EditUITemplate)) as EditUITemplate;
        healthbar = UI.GetInstantiatedUI;
        healthbarFiller = StudioExtensions.FindDeepChild(UI.GetInstantiatedUI.transform, "Health_fill").GetComponent(typeof(Image)) as Image;

        totalHealth = maxHealth;
        followingHealth = totalHealth;
    }
    public void Init(StudioController controller, TerraAutoAim autoAim)
    {
        this.controller = controller;
        this.autoAim = autoAim;
    }
    void ChangeState(int state)
    {
        if (enemyState == state)
        {
            return;
        }

        switch (state)
        {
            case IDLE:
                anim.PlayAnimationOverride(ANIM_IDLE, true);
                break;

            case FOLLOW:
                anim.PlayAnimationOverride(ANIM_WALK, true);
                break;

            case ATTACK:
                attackFx.Execute();
                anim.PlayAnimationOverride(ANIM_ATTACK, true);
                break;

            case HIT:
                if (anim.CurrentAnimation == ANIM_GETHIT)
                {
                    break;
                }
                int fx = Random.Range(0, hitFx.Length);
                hitFx[fx].Execute();
                hitParticleEffect.Execute();
                anim.PlayAnimationOverride(ANIM_GETHIT, false);
                break;

            case DEAD:
                dieFx.Execute();
                anim.PlayAnimationOverride(ANIM_DEATH, false);

                break;
        }

        enemyState = state;
    }
    IEnumerator HitRecoverTimer()
    {
        isHurt = true;

        yield return new WaitForSeconds(hitRecoverTime);

        isHurt = false;
    }
    void AnimationTransition(string str)
    {
        if (str == ANIM_GETHIT)
        {
            StartCoroutine(HitRecoverTimer());
        }
        else if (str == ANIM_DEATH)
        {
            PlayerController.SetEnemyKills(PlayerController.GetEnemyKills() + 1);
            PlayerController.SetLevelEnemyKills(PlayerController.GetLevelEnemyKills() + 1);
            AnalyticsAndLeaderboard.SetKillCount();
            PlayerBase.SetScore(PlayerBase.GetScore() + 15);

            GrowTemplate destroy = GetTemplate(typeof(GrowTemplate)) as GrowTemplate;
            destroy.Speed = 2;
            destroy.Execute();
            autoAim.TryTrackEnemy(null);
            StudioAnalytics.SetPrimarySessionScore(PlayerController.GetLevelEnemyKills());
            StartCoroutine(DestroyEnemy());
        }
    }
    IEnumerator DestroyEnemy()
    {
        DestroyTemplate destroy = GetTemplate(typeof(DestroyTemplate)) as DestroyTemplate;

        yield return new WaitForSeconds(0.7f);

        destroy.Execute();
    }
    public static void SetStop(bool val)
    {
        stop = val;
    }
}

```

## TerraWeaponController.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
//"one_handgun_one_hand_idle"   
public class TerraWeaponController : StudioBehaviour
{
    /*
     * Dazed_Heavy
Dazed_Launcher
Dazed_Pistol
Dazed_Rifle
Death1_Heavy
Death1_Launcher
Death1_Pistol
Death1_Rifle
Death2_Heavy
Death2_Launcher
Death2_Pistol
Death2_Rifle
Death3_Heavy
Death3_Launcher
Death3_Pistol
Death3_Rifle
Fire_Heavy
Fire_Launcher
Fire_Pistol
Fire_Rifle
Idle_Heavy
Idle_Launcher
Idle_Pistol
Idle_Rifle
Jump_Heavy
Jump_Launcher
Jump_Pistol
Jump_Rifle
Knockback_Heavy
Knockback_Launcher
Knockback_Pistol
Knockback_Rifle
Melee1_Heavy
Melee1_Launcher
Melee1_Pistol
Melee1_Rifle
Pain_Heavy
Pain_Launcher
Pain_Pistol
Pain_Rifle
Reload_Heavy
Reload_Launcher
Reload_Pistol
Reload_Rifle
Run_Backward_Heavy
Run_Backward_Launcher
Run_Backward_Pistol
Run_Backward_Rifle
Run_Heavy
Run_Launcher
Run_Left_Heavy
Run_Left_Launcher
Run_Left_Pistol
Run_Left_Rifle
Run_Pistol
Run_Rifle
Run_Right_Heavy
Run_Right_Launcher
Run_Right_Pistol
Run_Right_Rifle
Walk_Heavy
Walk_Launcher
Walk_Pistol
Walk_Rifle
     */
    //==Assign from Inspector==
    private float delayBetweenChecks = 1f;
    private Transform dir;

    //==Animation==
    private const string POSE_LAYER_NAME = "PoseLayer";
    private const string IDLE_PISTOL = "one_handgun_one_hand_idle";
    private const string FIRE_PISTOL = "Fire_Pistol";
    private const string FIRE_RIFLE = "Fire_Rifle";
    private const string IDLE_PISTOL2 = "Idle_Pistol";
    private const string IDLE_RIFLE = "Idle_Rifle";
    private const string RELOAD_PISTOL = "Reload_Pistol";
    private const string RELOAD_RIFLE = "Reload_Rifle";
    private const string RUN_BACKWARD_PISTOL = "Run_Backward_Pistol";
    private const string RUN_LEFT_PISTOL = "Run_Left_Pistol";
    private const string RUN_PISTOL = "Run_Pistol";
    private const string RUN_RIGHT_PISTOL = "Run_Right_Pistol";
    private const string RUN_BACKWARD_RIFLE = "Run_Backward_Rifle";
    private const string RUN_LEFT_RIFLE = "Run_Left_Rifle";
    private const string RUN_RIFLE = "Run_Rifle";
    private const string RUN_RIGHT_RIFLE = "Run_Right_Rifle";
    private const string WALK_PISTOL = "Walk_Pistol";
    private const string WALK_RIFLE = "Walk_Rifle";

    private TerraAutoAim autoAim;
    private TerraProjectileWeapon Weapon;
    private GameObject shootUI;
    private GameObject defaultWeaponObj;
    private GameObject shotgunWeaponObj;
    private GameObject sniperWeaponObj;
    private GameObject[] equipableWeapons = new GameObject[3];
    private StudioController controller;
    private GameObject Gun;
    private GameObject ammo;
    private TMP_Text ammoText;
    private Transform ammoParent;
    private Transform ammoTypeParent;
    private int ammoID;
    private Transform weaponLoc;
    private int[] gunIdxArr = new int[] { 0, 1, 2, 9, 10, 3, 4, 5, 11, 12, 6, 7, 8, 13, 14 };
    Animator animator;
    private int magCollectible;
    private int magCrateCollectible;
    private bool hasFinishedReloading;
    private int isBase;
    private bool isReloading;
    private PlayerAnimationControlTemplate animation;
    private Vector2 playerDir;
    private Vector2 joystickDir;
    private string currentState;
    private bool isSwitching;
    private string nextState;

    private SoundFxTemplate footstepFx;

    private const string var_DelayBetweenChecks = "DelayBetweenChecks";
    private const string var_Weapon = "Weapon";
    private const string var_ShotgunWeapon = "Shotgun";
    private const string var_SniperWeapon = "Sniper";
    private const string var_Dir = "Dir";
    private const string var_MagCollectible = "MagCollectible";
    private const string var_MagCrateCollectible = "MagCrateCollectible";
    private const string var_ShootUI = "ShootUI";

    public const string IDLE = "Idle";
    public const string RUN = "Run";
    public const string FIRE = "Fire";
    public const string RELOAD = "Reload";

    private void Start()
    {
        Initialization();
    }

    private void Initialization()
    {
        delayBetweenChecks = GetFloatVariable(var_DelayBetweenChecks);
        defaultWeaponObj = GetGameObjectVariable(var_Weapon);
        shotgunWeaponObj = GetGameObjectVariable(var_ShotgunWeapon);
        sniperWeaponObj = GetGameObjectVariable(var_SniperWeapon);
        dir = GetGameObjectVariable(var_Dir).transform;
        magCollectible = GetIntVariable(var_MagCollectible);
        magCrateCollectible = GetIntVariable(var_MagCrateCollectible);
        shootUI = GetGameObjectVariable(var_ShootUI);
        isBase = GetIntVariable("IsBase");

        Transform obj = transform.GetChild(transform.childCount - 1);

        footstepFx = GetTemplate(obj.gameObject, typeof(SoundFxTemplate)) as SoundFxTemplate;
        footstepFx.Volume = 0;
        footstepFx.Execute();

        ammo = GetGameObjectVariable("GunUI");
        var ammoTemplate = GetTemplate(ammo, typeof(EditUITemplate)) as EditUITemplate;
        var instantiatedUISniperAmmo = ammoTemplate.GetInstantiatedUI;
        ammoParent = StudioExtensions.FindDeepChild(instantiatedUISniperAmmo.transform, "allBullet");
        ammoTypeParent = StudioExtensions.FindDeepChild(instantiatedUISniperAmmo.transform, "ALL_Gun");
        ammoText = StudioExtensions.FindDeepChild(instantiatedUISniperAmmo.transform, "Bullet_count").GetComponent(typeof(TMP_Text)) as TMP_Text;


        ammoID = 5 * PlayerBase.GetEquippedGun() + PlayerBase.GetWeaponIdx();

        int totalGuns = ammoTypeParent.childCount;
        for (int i = 0; i < totalGuns; i++)
        {
            ammoTypeParent.GetChild(i).gameObject.SetActive(false);
        }

        ammoTypeParent.GetChild(gunIdxArr[ammoID]).gameObject.SetActive(true);

        var UI = GetTemplate(shootUI, typeof(EditUITemplate)) as EditUITemplate;
        var instantiatedUI = UI.GetInstantiatedUI;
        var buttonObj = StudioExtensions.FindDeepChild(instantiatedUI.transform, "SpaceMarshal_Controller_weapon");
        var buttonComponent = buttonObj.GetComponent(typeof(Button)) as Button;
        buttonComponent.onClick.AddListener(Shoot);

        equipableWeapons[0] = defaultWeaponObj;
        equipableWeapons[1] = shotgunWeaponObj;
        equipableWeapons[2] = sniperWeaponObj;

        if (isBase != 1)
        {
            StartCoroutine(ChangeAmmoUI());
        }
        StartCoroutine(SetupAnimation());
    }
    IEnumerator SetupAnimation()
    {
        animation = GetTemplate(typeof(PlayerAnimationControlTemplate)) as PlayerAnimationControlTemplate;

        yield return null;

        ChangeAnimState(IDLE);
    }
    public void Init(StudioController controller)
    {
        this.controller = controller;
        StartCoroutine(Setup());
    }
    public override void OnBroadcasted(string x)
    {
        if (x == "AddAmmo")
        {
            Weapon.AddMagazines(magCollectible);
        }
        else if (x == "AddMoreAmmo")
        {
            Weapon.AddMagazines(magCrateCollectible);
        }
    }
    private IEnumerator Setup()
    {
        //animator = null;
        while (weaponLoc == null)
        {
            weaponLoc = controller.GetLocatorEnumBased(StudioController.PlayerLocEnum.ShootIKLoc);
            yield return new WaitForSeconds(delayBetweenChecks);
        }
        yield return StartCoroutine(SetupWeapon(weaponLoc));
        //yield return StartCoroutine(SetupAnimator(animator));
        autoAim = gameObject.GetComponent(typeof(TerraAutoAim)) as TerraAutoAim;
    }
    public void SetupWeaponSwitch()
    {
        StartCoroutine(SetupWeapon(weaponLoc));
    }
    private IEnumerator SetupWeapon(Transform weaponLoc)
    {
        int weaponIdx = PlayerBase.GetEquippedGun();
        //GameObject weaponObj = Instantiate(equipableWeapons[weaponIdx], weaponLoc);
        GameObject weaponObj = equipableWeapons[weaponIdx];
        weaponObj.transform.SetParent(weaponLoc, false);
        switch (weaponIdx)
        {
            case 0:
                weaponObj.transform.localPosition = Vector3.zero;
                weaponObj.transform.localRotation = Quaternion.identity;
                weaponObj.transform.localScale = Vector3.one * 0.0095f;
                break;

            case 1:
                weaponObj.transform.localPosition = Vector3.zero;
                weaponObj.transform.localRotation = Quaternion.identity;
                weaponObj.transform.localScale = Vector3.one * 0.0095f;
                break;

            case 2:
                weaponObj.transform.localPosition = Vector3.zero;
                weaponObj.transform.localRotation = Quaternion.identity;
                weaponObj.transform.localScale = Vector3.one * 0.0095f;
                break;
        }

        yield return null; //Mandatory wait to fetch the component, only available in the next frame
        Weapon = weaponObj.GetComponent(typeof(TerraProjectileWeapon)) as TerraProjectileWeapon;
        if (Weapon != null)
        {
            Weapon.Equip();
            //ChangeAmmoUI();
        }
    }

    private IEnumerator SetupAnimator(Animator animator)
    {
        while (animator == null)
        {
            animator = gameObject.GetComponentInChildren(typeof(Animator)) as Animator;
            yield return new WaitForSeconds(delayBetweenChecks);
        }
        if (animator != null)
        {
            var layerIndex = animator.GetLayerIndex(POSE_LAYER_NAME);
            animator.Play(IDLE_PISTOL2, layerIndex);
            animator.SetLayerWeight(layerIndex, 1f);
        }
    }
    private void Update()
    {
        //AttemptAutoShoot();
        if (Weapon == null)
        {
            return;
        }
        if (Weapon.IsReloading() && !isReloading)
        {
            StartCoroutine(SetReloadFalse());
            ChangeAnimState(RELOAD);
        }
        else if (Input.GetMouseButton(1))
        {
            Shoot();
        }
        else if (controller.IsMoving() && !isReloading)
        {
            ChangeAnimState(RUN);
        }
        else if (!isReloading)
        {
            ChangeAnimState(IDLE);
        }
    }
    IEnumerator SetReloadFalse()
    {
        yield return new WaitForSeconds(Weapon.reloadTime);

        isReloading = false;
    }
    private void AttemptAutoShoot()
    {
        if (!autoAim || !autoAim.CurrentLockedEnemy) return;
        if (!autoAim.IsEnemyInLineOfSight()) return;
        Shoot();
    }
    public void Shoot()
    {
        if (!PlayerController.isGameStarted)
        {
            return;
        }
        StartCoroutine(ShootTime());
    }
    IEnumerator ShootTime()
    {
        ChangeAnimState(FIRE);
        yield return new WaitForSeconds(0.05f);
        Weapon.Shoot(dir.forward);
    }
    public GameObject GetCurrentWeapon()
    {
        return Weapon.gameObject;
    }
    IEnumerator ChangeAmmoUI()
    {
        if (Weapon != null)
        {
            int[] ammoDetail = Weapon.GetAmmoCount();
            if (ammoDetail != null)
            {
                int ammoCount = ammoDetail[0];

                ammoText.text = (ammoDetail[1] * ammoDetail[2] + ammoCount).ToString();
                for (int i = 0; i < ammoParent.childCount; i++)
                {
                    if (i >= ammoCount)
                    {
                        ammoParent.GetChild(i).gameObject.SetActive(false);
                    }
                    else
                    {
                        ammoParent.GetChild(i).gameObject.SetActive(true);
                    }
                }
            }
        }

        yield return new WaitForSeconds(0.2f);

        StartCoroutine(ChangeAmmoUI());
    }

    void PlayIdle()
    {
        if (isReloading)
        {
            return;
        }
        if (PlayerBase.GetEquippedGun() == 0)
        {
            animation.AnimationName = IDLE_PISTOL2;
        }
        else
        {
            animation.AnimationName = IDLE_RIFLE;
        }
        animation.Execute();
    }
    void PlayRun()
    {
        if (isReloading)
        {
            return;
        }

        if (PlayerBase.GetEquippedGun() == 0)
        {
            animation.AnimationName = RUN_PISTOL;
        }
        else
        {
            animation.AnimationName = RUN_RIFLE;
        }

        animation.Execute();
    }
    void PlayFire()
    {
        if (isReloading)
        {
            return;
        }

        if (PlayerBase.GetEquippedGun() == 0)
        {
            animation.AnimationName = FIRE_PISTOL;
        }
        else
        {
            animation.AnimationName = FIRE_RIFLE;
        }
        animation.Execute();
        float time = 1 / Weapon.GetFireRate();
        StartCoroutine(SwitchAnimation(time));
    }
    void PlayReload()
    {
        if (PlayerBase.GetEquippedGun() == 0)
        {
            animation.AnimationName = RELOAD_PISTOL;
        }
        else
        {
            animation.AnimationName = RELOAD_RIFLE;
        }
        animation.Execute();
        StartCoroutine(SwitchAnimation(1));
    }
    void PlayForward()
    {
        if (PlayerBase.GetEquippedGun() == 0)
        {
            animation.AnimationName = RUN_PISTOL;
        }
        else
        {
            animation.AnimationName = RUN_RIFLE;
        }
        //Debug.Log(animation.AnimationName);
        animation.Execute();
    }

    IEnumerator SwitchAnimation(float time)
    {
        isSwitching = true;

        yield return new WaitForSeconds(time);

        isSwitching = false;
        if (nextState != "")
        {
            ChangeAnimState(nextState);
        }
    }

    void ChangeAnimState(string state)
    {
        if (currentState == state)
        {
            return;
        }

        switch (state)
        {
            case IDLE:
                if ((currentState == FIRE || currentState == RELOAD) && isSwitching)
                {
                    nextState = IDLE;
                }
                else
                {
                    footstepFx.Volume = 0f;
                    footstepFx.Execute();

                    nextState = "";
                    currentState = IDLE;
                    PlayIdle();
                }
                break;
            case RUN:
                if ((currentState == FIRE || currentState == RELOAD) && isSwitching)
                {
                    nextState = RUN;
                }
                else
                {
                    footstepFx.Volume = 0.5f;
                    footstepFx.Execute();

                    nextState = "";
                    currentState = RUN;
                    PlayRun();
                }
                break;
            case FIRE:
                if (currentState == RELOAD && isSwitching)
                {
                    nextState = FIRE;
                    return;
                }
                else
                {
                    footstepFx.Volume = 0f;
                    footstepFx.Execute();

                    nextState = "";
                    currentState = FIRE;
                    PlayFire();
                }
                break;
            case RELOAD:
                if (currentState == FIRE && isSwitching)
                {
                    nextState = RELOAD;
                    isReloading = true;
                }
                else
                {
                    footstepFx.Volume = 0f;
                    footstepFx.Execute();

                    nextState = "";
                    currentState = RELOAD;
                    PlayReload();
                }
                break;
        }
    }
}

```

## Tutorial.cs

```csharp
using System.Collections;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class Tutorial : StudioBehaviour
{
    GameObject tutorialCursor;
    GameObject tutorialText;
    GameObject shootButton;
    GameObject newObjectiveUI;
    GameObject homescreenUI;
    GameObject buyButton;
    GameObject destroyableObject;
    GameObject addon;
    TMP_Text tutText;
    Button playBtn;
    Button nextMissionBtn;
    Button shootBtn;
    Shop shop;
    Vector3 moveUpPos = new Vector3(300, 50, 0);
    string[] tutTexts = new string[] {
        "Use D-Pad to move",
        "Shoot the enemy",
        "Collect the Heart ahead",
        "Shoot this to clear path",
        "Stay close to hostage",
        "Follow the objective arrow",
        "Tap on the Loadout button below to purchase or equip guns"
    };
    Vector3[] tutTextPos = new Vector3[] {
        new Vector3(-600, -500, 0),
        new Vector3(500, -500, 0),
        new Vector3(0, -800, 0),
        new Vector3(0, 0, 0),
        new Vector3(0, 0, 0),
        new Vector3(0, 0, 0),
        new Vector3(0, 0, 0),
    };
    float moveUpLength = 1.5f;
    float moveUpSpeed = 300;
    int tutorialSteps = 0;
    int suggestedGun;
    bool isFirePoint;
    bool isObjectiveMoving;
    bool isShopClicked;
    bool isTutorialStarted;
    bool shouldPulsateBuyButton;
    bool isTutorialDone;
    int id;
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        Initialization();
    }

    // Gets called every frame
    private void Update()
    {
        if (id == 0 & isTutorialStarted)
        {
            float hor = StudioController.GetMyController().GetHorizontalJoystick();
            float ver = StudioController.GetMyController().GetVerticalJoystick();

            if (hor + ver > 0.2f)
            {
                if (tutorialSteps == 0)
                {
                    StopAllCoroutines();
                    if (!isFirePoint)
                    {
                        isFirePoint = true;
                        StartTutorial(1);
                    }
                }
            }
        }
        else if (id == 2)
        {
            if (destroyableObject)
            {
                tutorialText.transform.position = Camera.main.WorldToScreenPoint(destroyableObject.transform.position + Vector3.right * 2);
            }
            else
            {
                tutorialText.SetActive(false);
            }
        }
        else if(id == 1)
        {
            if(shouldPulsateBuyButton && !isTutorialDone)
            {
                PulsateBuyButton();
            }
        }
    }
    public override void OnBroadcasted(string x)
    {
        if (x == "GameStarted")
        {
            if (id == 0)
            {
                isTutorialStarted = true;
                StartTutorial(0);
            }
        }
        else if (x == "ShowHealth")
        {
            tutorialText.SetActive(false);
        }
    }
    void Initialization()
    {
        id = GetIntVariable("TutID");

        if (id == 0)
        {
            GameObject cursorObj = GetGameObjectVariable("TutCursor");
            EditUITemplate editUI = GetTemplate(cursorObj, typeof(EditUITemplate)) as EditUITemplate;
            tutorialCursor = editUI.GetInstantiatedUI;

            GameObject textObj = GetGameObjectVariable("TutText");
            EditUITemplate editTextUI = GetTemplate(textObj, typeof(EditUITemplate)) as EditUITemplate;
            tutorialText = editTextUI.GetInstantiatedUI;
            var tutTextObj = StudioExtensions.FindDeepChild(tutorialText.transform, "Info_Text");
            tutText = tutTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

            textObj = GetGameObjectVariable("ShootButton");
            editTextUI = GetTemplate(textObj, typeof(EditUITemplate)) as EditUITemplate;
            shootButton = editTextUI.GetInstantiatedUI;
            shootBtn = shootButton.GetComponent(typeof(Button)) as Button;
            shootBtn.onClick.AddListener(StopFireTut);
            shootBtn.interactable = false;

            var msObj = GetGameObjectVariable("NewObjectiveUI");
            var msEditUI = GetTemplate(msObj, typeof(EditUITemplate)) as EditUITemplate;
            newObjectiveUI = msEditUI.GetInstantiatedUI;

            tutorialText.SetActive(false);
            tutorialCursor.SetActive(false);
        }
        else if (id == 1)
        {
            isTutorialDone = StudioPrefs.GetInt("TutorialDone") == 0 ? false : true ;

            int mis = StudioPrefs.GetInt("TutorialDone");
            int missionsUnlocked = StudioPrefs.GetInt("MissionsUnlocked");

            GameObject textObj = GetGameObjectVariable("TutText");
            EditUITemplate editTextUI = GetTemplate(textObj, typeof(EditUITemplate)) as EditUITemplate;
            tutorialText = editTextUI.GetInstantiatedUI;
            var tutTextObj = StudioExtensions.FindDeepChild(tutorialText.transform, "Info_Text");
            tutText = tutTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

            if (mis == 0 && missionsUnlocked > 0)
            {
                GameObject homescreenObj = GetGameObjectVariable("HomescreenUI");
                EditUITemplate obj = GetTemplate(homescreenObj, typeof(EditUITemplate)) as EditUITemplate;
                homescreenUI = obj.GetInstantiatedUI;

                Transform loadout = StudioExtensions.FindDeepChild(homescreenUI.transform, "Loadoutbuttn");
                Button loadoutBtn = loadout.GetComponent(typeof(Button)) as Button;
                loadoutBtn.onClick.AddListener(StopShop);

                Transform moremis = StudioExtensions.FindDeepChild(homescreenUI.transform, "moremission");
                nextMissionBtn = moremis.GetComponent(typeof(Button)) as Button;
                nextMissionBtn.interactable = false;

                Transform play = StudioExtensions.FindDeepChild(homescreenUI.transform, "playbutton");
                playBtn = play.GetComponent(typeof(Button)) as Button;
                playBtn.interactable = false;

                shop = GetComponent(typeof(Shop)) as Shop;

                StartCoroutine(AnimateObjective(loadout.gameObject, true));

                var addonObj = GetGameObjectVariable("HomescreenAddon");
                var adeditUI = GetTemplate(addonObj, typeof(EditUITemplate)) as EditUITemplate;
                addon = adeditUI.GetInstantiatedUI;
                GameObject shopButton = StudioExtensions.FindDeepChild(addon.transform, "Shop_Button").gameObject;
                Button tcshopButton = shopButton.GetComponent(typeof(Button)) as Button;
                tcshopButton.interactable = false;
            }
            else
            {
                tutorialText.SetActive(false);
            }
        }
        else if (id == 2)
        {
            GameObject textObj = GetGameObjectVariable("TutText");
            EditUITemplate editTextUI = GetTemplate(textObj, typeof(EditUITemplate)) as EditUITemplate;
            tutorialText = editTextUI.GetInstantiatedUI;
            var tutTextObj = StudioExtensions.FindDeepChild(tutorialText.transform, "Info_Text");
            tutText = tutTextObj.GetComponent(typeof(TMP_Text)) as TMP_Text;

            destroyableObject = GetGameObjectVariable("DestroyableObj");
            tutText.text = tutTexts[3];
        }

    }
    void StartTutorial(int step)
    {
        tutorialSteps = step;
        switch (tutorialSteps)
        {
            case 0:
                MoveTutorial();
                break;
            case 1:
                FirePointTutorial();
                break;
            case 2:
                ObjectiveTutorial();
                break;
            case 3:
                CollectCollectible();
                break;
        }
    }
    void StopFireTut()
    {
        if (isFirePoint)
        {
            StartTutorial(2);
            tutorialCursor.SetActive(false);
            isFirePoint = false;
        }
    }
    void MoveTutorial()
    {
        tutorialText.SetActive(true);
        tutorialCursor.SetActive(true);

        tutText.text = tutTexts[0];
        tutorialText.transform.localPosition = tutTextPos[0];

        StartCoroutine(MoveCursorUp());
    }
    void FirePointTutorial()
    {
        tutorialCursor.SetActive(true);
        shootBtn.interactable = true;

        tutText.text = tutTexts[1];
        tutorialText.transform.localPosition = tutTextPos[1];

        StartCoroutine(ArrowPoint(shootButton.transform, new Vector3(-200, -200, 0)));
    }
    void ObjectiveTutorial()
    {
        tutorialText.SetActive(false);

        StartCoroutine(AnimateObjective(newObjectiveUI));
        StartCoroutine(StartCollectible());
    }
    void StopShop()
    {
        StopAllCoroutines();
        nextMissionBtn.interactable = true;
        playBtn.interactable = true;
        tutorialText.SetActive(false);
        if (!isShopClicked)
        {
            PulseGun();
            isShopClicked = true;
        }
    }
    void CollectCollectible()
    {
        tutorialText.SetActive(true);
        tutText.text = tutTexts[2];
        tutorialText.transform.localPosition = tutTextPos[2];
    }
    IEnumerator StartCollectible()
    {
        yield return new WaitForSeconds(5);

        StartTutorial(3);
    }
    void PulseGun()
    {
        int type = PlayerBase.GetEquippedGun();
        int idx = PlayerBase.GetWeaponIdx();
        bool[][] purchasedGuns = shop.GetPurchasedGunsArray();
        for (int i = 0; i < 5; i++)
        {
            bool pg = purchasedGuns[0][i];
            if (!pg && Weapon.price[0][i] <= PlayerBase.GetScore())
            {
                suggestedGun = i;
                GameObject obj = shop.GetGunSlot(0, i);
                StartCoroutine(AnimateObjective(obj.transform.GetChild(3).gameObject, true, 1.1f, 0.3f));

                buyButton = shop.GetBuyButton();
                Button buybtn = buyButton.GetComponent(typeof(Button)) as Button;
                buybtn.onClick.AddListener(StopPulsateBuyButton);

                Button btn = obj.transform.GetChild(3).GetComponent(typeof(Button)) as Button;
                btn.onClick.AddListener(PulseBuyButton);
                break;
            }
        }
    }
    void PulseBuyButton()
    {
        StopAllCoroutines();
        //StartCoroutine(AnimateObjective(shop.GetBuyButton(), true, 1.1f, 0.3f));
        shouldPulsateBuyButton = true;
    }
    void PulsateBuyButton()
    {
        if(buyButton)
        {
            buyButton.transform.localScale = Vector3.one + Mathf.Abs(Mathf.Sin(2 * Time.time)) * Vector3.one * 0.3f;
        }
    }
    void StopPulsateBuyButton()
    {
        shouldPulsateBuyButton = false;
        if(buyButton)
        {
            buyButton.transform.localScale = Vector3.one;
            StudioPrefs.SetInt("TutorialDone", 1); 
            isTutorialDone = true;
        }
    }
    public void DoIt(int guntp, int gunIx)
    {
        if(guntp == 0 && gunIx == suggestedGun && shouldPulsateBuyButton)
        {
            PulseBuyButton();
        }
        else
        {
            StopPulsateBuyButton();
        }
    }
    IEnumerator MoveCursorUp()
    {
        tutorialCursor.transform.position = moveUpPos;
        Vector3 initialPos = moveUpPos;
        float val = 0;
        while (true)
        {
            while (moveUpLength > val)
            {
                yield return null;

                tutorialCursor.transform.position += moveUpSpeed * Time.deltaTime * Vector3.up;
                val += Time.deltaTime;
            }
            val = 0;
            tutorialCursor.transform.position = initialPos;
        }
    }
    IEnumerator ArrowPoint(Transform obj, Vector3 offset)
    {
        tutorialCursor.transform.position = obj.position + offset;
        Vector3 initialPos = obj.position + offset;
        float val = 0;
        Vector3 dir = obj.position - tutorialCursor.transform.position;
        while (true)
        {
            while (0.8f > val)
            {
                yield return null;

                tutorialCursor.transform.position += Time.deltaTime * dir;
                val += Time.deltaTime;
            }

            val = 0;
            tutorialCursor.transform.position = initialPos;
        }
    }
    IEnumerator AnimateObjective(GameObject obj, bool isforever = false, float magnify = 1.5f, float speed = 1)
    {
        float def = 1;
        float count = 5;
        if (isforever)
        {
            count = 100000;
        }

        for (int i = 0; i < count; i++)
        {
            while (magnify > def)
            {
                obj.transform.localScale = new Vector3(def, def, 1);
                yield return null;

                def += speed * Time.deltaTime;
            }

            while (def > 1)
            {
                obj.transform.localScale = new Vector3(def, def, 1);
                yield return null;

                def -= speed * Time.deltaTime;
            }

            def = 1;
            obj.transform.localScale = new Vector3(def, def, 1);
        }
    }
}

```

## WeaponModifier.cs

```csharp
using Terra.Studio.Exposed;

/*
 * 0 - firingRate
 * 1 - totalBulletCount
 * 2 - reloadTime
 * 3 - bulletSpread
 */
public class WeaponModifier : StudioBehaviour
{
    private int firingRate;
    private int totalBulletCount;
    private float reloadTime;
    private float bulletSpread;
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        firingRate = GetIntVariable("FiringRate");
        totalBulletCount = GetIntVariable("TotalBulletCount");
        reloadTime = GetIntVariable("ReloadTime");
        bulletSpread = GetIntVariable("BulletSpread");
    }

    // Gets called every frame
    private void Update()
    {

    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {

    }

    public void SetCurrentWeaponStats()
    {

    }
}

public class Weapon
{
    /*
        Hand gun Range 9
        Shotgun Range 6
        Sniper Range 12
     */
    public static float[][] handgunStats = new float[][] {
        new float[] { 1, 4, 1f, 0 },
        new float[] { 1.5f, 6, 3f, 0 },
        new float[] { 6, 10, 4f, 0 },
        new float[] { 9, 12, 3f, 0 },
        new float[] { 12, 30, 5f, 0 },
    };
    public static float[][] shotgunStats = new float[][] {
        new float[] { 1, 6, 2, 0.1f},
        new float[] { 1, 6, 3f, 0.2f },
        new float[] { 1, 8, 4f, 0.25f },
        new float[] { 3, 2, 4f, 0.25f },
        new float[] { 3, 12, 6f, 0.25f },
    };
    public static float[][] sniperStats = new float[][] {
        new float[] { 1, 4, 5, 0},
        new float[] { 1, 6, 6, 0 },
        new float[] { 3, 12, 3, 0 },
        new float[] { 5, 18, 2, 0 },
        new float[] { 1, 6, 15, 0 },
    };

    public static int[][] price = new int[][] {
        new int[] { 60, 80, 120, 280, 350},
        new int[] { 80, 100, 140, 300, 370},
        new int[] { 100, 120, 160, 320, 390},
    };
}


```
