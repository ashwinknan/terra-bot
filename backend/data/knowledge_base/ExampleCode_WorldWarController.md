# World War - FPS Controller Documentation
## Type
Example

## Overview
Static landscape shooter controller with advanced targeting and weapon systems.

## Core Systems

### Pan & Aim
- **Pan System**:
  - Full-screen pan area
  - Excludes button zones
  - Adjustable sensitivity

- **Focus Aim**:
  - Dedicated aim button
  - Zoom slider functionality
  - Adjustable zoom thresholds

### Weapon Systems

#### Shooting Mechanics
- **Dual Mode**:
  - Manual shoot
  - Auto-shoot option
  - Dual bullet system
- **Magazine System**:
  - Reload indicators
  - Ammo count display
  - Reload button

#### Missile System
- **Types**:
  - Standard missiles
  - Guided missiles
- **Features**:
  - Cooldown system
  - AOE damage
  - Target tracking

### Combat Feedback

#### Target System
- Viewport target indicators
- Out-of-view directional markers
- World space arrows

#### Damage System
- Directional damage indicators
- Health bar (color-coded)
- Visual effects (vignette)
- Camera shake mechanics


---

# Code Implementation

## Bullet.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class Bullet : StudioBehaviour
{

    Vector3 m_ScreenCenter;
    float m_BulletSpeed;
    Rigidbody m_Rb;


    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_ScreenCenter = new Vector3(Screen.width / 2, Screen.height / 2, 0);

        m_Rb = GetComponent(typeof(Rigidbody)) as Rigidbody;
    }

    // Gets called every frame
    private void Update()
    {
       
    }

    private void FixedUpdate()
    {
        m_Rb.velocity = gameObject.transform.forward * m_BulletSpeed;
    }

    public void SetVariables(float BulletSpeed)
    {
        m_BulletSpeed = BulletSpeed;
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }
}


```

## Camera_Movement.cs

```csharp
using CMF;
using RTG;
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.Rendering.UI;
using UnityEngine.UI;

public class Camera_Movement : StudioBehaviour
{
    public float PAN_Sensitivity;
    public float Initial_Zoom_Length;
    Transform m_CameraTransform;
    Camera m_Camera;
    Vector3 m_SniperOffset = new Vector3(0, -0.3f, 0.3f);
    GameObject m_Sniper;
    Transform m_BulletRaycast;
    bool m_AutoShoot;
    Vector3 screenCenter;
    bool m_IsFocused;
    GameObject UI;
    GameObject gameUI;
    GameObject focusSelect;
    GameObject Magnifier;

    //Damage indicator
    GameObject m_DamageIndicagtorUIGO;
    GameObject m_DamageIndicatorUI;
    Image m_DamageIndicatorImg;


    GameObject Enemey;
    Vector3 DamageLocation;

    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        MovePlayerAwayFromScreen();
        StudioController.GetMyController().ChangePanSpeed(PAN_Sensitivity);
        m_IsFocused = false;
        Camera.main.fieldOfView = Initial_Zoom_Length;
        m_AutoShoot = false;
        m_CameraTransform = Camera.main.transform;
        m_Camera = Camera.main;
        m_Sniper = GetGameObjectVariable("Gun");
        //m_BulletRaycast = gameObject.transform.GetChild(1).transform.GetChild(0).transform;
        gameObject.AddComponent<LineRenderer>();
        gameObject.GetComponent<LineRenderer>().startWidth = 0f;
        gameObject.GetComponent<LineRenderer>().endWidth = 0f;
        screenCenter = new Vector3(Screen.width / 2, Screen.height / 2, 0);

        UI = GetGameObjectVariable("UI");
        var Ui = GetTemplate(UI, typeof(EditUITemplate)) as EditUITemplate;
        gameUI = Ui.GetInstantiatedUI;
        focusSelect = StudioExtensions.FindDeepChild(gameUI.transform, "Gun_target").gameObject;
        Button? btn = focusSelect.GetComponent(typeof(Button)) as Button;
        btn.onClick.AddListener(ToggleFocus);

        Magnifier = StudioExtensions.FindDeepChild(gameUI.transform, "Target_Range").gameObject;
        Magnifier.SetActive(false);

        m_DamageIndicagtorUIGO = GetGameObjectVariable("Damage Indicator");
        var DamageUi = GetTemplate(m_DamageIndicagtorUIGO, typeof(EditUITemplate)) as EditUITemplate;
        m_DamageIndicatorUI = DamageUi.GetInstantiatedUI;
        m_DamageIndicatorImg = StudioExtensions.FindDeepChild(m_DamageIndicatorUI.transform, "WorldWar_DamageIndicator").gameObject.GetComponent(typeof(Image)) as Image;

        //Enemey = GetGameObjectVariable("Enemy");

        //m_DamageIndicatorImg.transform.LookAt(Camera.main.WorldToViewportPoint(Enemey.transform.position));
    }

    // Gets called every frame
    private void Update()
    {
        //Debug.Log("HIEE : "+ gameObject.transform.GetChild(1).gameObject.transform.rotation);
        //DamageLocation = Enemey.transform.position;
        //DamageLocation.y = Camera.main.transform.position.y;

        //Vector3 Direction = (DamageLocation - Camera.main.transform.position).normalized;

        //float angle = (Vector3.SignedAngle(Direction, Camera.main.transform.forward, Vector3.up));
        
        //Transform t = m_DamageIndicatorImg.GetComponent(typeof(RectTransform)) as RectTransform;
        
        //t.localEulerAngles = new Vector3(0,0, angle);

        //if (Input.GetMouseButton(1))
        //{
        //    Debug.Log("PRRINTTT");
        //    ZoomIn();
        //}

        //if (Input.GetMouseButton(0))
        //{
        //    ZoomOut();
        //}

        //if(Input.touchCount > 0)
        //{
        //    int touchId = Input.GetTouch(0).fingerId;

        //    if(EventSystem.current.IsPointerOverGameObject(touchId))
        //    {
        //        if(EventSystem.current.currentSelectedGameObject != null)
        //        {
        //            if(EventSystem.current.currentSelectedGameObject.name =="Shoot_button_left" || EventSystem.current.currentSelectedGameObject.name == "Shoot_button_right")
        //            {
        //                Debug.Log("Touching " + EventSystem.current.currentSelectedGameObject);
        //            }

        //            if(EventSystem.current.currentSelectedGameObject.name == "Gun_target")
        //            {
        //                //if (m_IsFocused)
        //                //{
        //                //    m_IsFocused = false;
        //                //    Camera.main.fieldOfView = Initial_Zoom_Length;
        //                //}
        //                //else
        //                //{
        //                //    m_IsFocused = true;
        //                //    Camera.main.fieldOfView = 60;
        //                //}
        //            }
        //        }
        //    }
        //}
        float scrollWheelDelta = Input.GetAxis("Mouse ScrollWheel");

        if (scrollWheelDelta != 0)
        {
            // Scroll wheel was moved
            //Debug.Log("Scroll wheel delta: " + scrollWheelDelta);

            // Do something based on the scroll wheel direction
            if (scrollWheelDelta > 0)
            {
                //Debug.Log("Scrolled up");
                ZoomIn();
            }
            else
            {
                //Debug.Log("Scrolled down");
                ZoomOut() ;
            }
        }

        if (m_AutoShoot)
        {
            //DetectRaycastHit();
        }
        else if (!m_AutoShoot)
        {
            if (Input.GetMouseButton(0))
            {
                //Shoot();
            }
        }

        //gameObject.transform.GetChild(1).gameObject.transform.rotation = Camera.main.gameObject.transform.rotation;
        SetSniperToCamera();
        //DetectRaycastHit();
    }

    void ToggleFocus()
    {
        if (m_IsFocused)
        {
            m_IsFocused = false;
            Camera.main.fieldOfView = Initial_Zoom_Length;
            Magnifier.SetActive(false);
        }
        else
        {
            m_IsFocused = true;
            Camera.main.fieldOfView = 40;
            Magnifier .SetActive(true);
        }
    }

    void SetSniperToCamera()
    {
        m_Sniper.transform.position = m_CameraTransform.position + m_SniperOffset.z * m_CameraTransform.forward + m_SniperOffset.y * m_CameraTransform.up + m_SniperOffset.x * m_CameraTransform.right;

        Quaternion newRotation = Quaternion.Euler(m_CameraTransform.eulerAngles.x, m_CameraTransform.eulerAngles.y, m_CameraTransform.eulerAngles.z);

        //m_Sniper.transform.rotation = newRotation;
        m_Sniper.transform.rotation = Quaternion.Slerp(m_Sniper.transform.rotation, newRotation, 50f * Time.deltaTime);

        //m_Sniper.transform.eulerAngles = new Vector3(270f, m_CameraTransform.eulerAngles.y, -m_CameraTransform.eulerAngles.z);
    }

    void DetectRaycastHit()
    {
        // Perform the raycast
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(screenCenter);

        LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        
        if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
        {
            // Raycast hit something
            //Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);

            // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
            if (hitInfo.collider.gameObject.name.Equals("Toon Diamond Bus 01"))
            {
                //Debug.Log("Hit a go!");
                // Do something when a go is hit
                lineRenderer.startWidth = 0.01f;
                lineRenderer.endWidth = 5f;
                lineRenderer.SetPosition(0, m_BulletRaycast.position);
                lineRenderer.SetPosition(1, m_BulletRaycast.position + m_BulletRaycast.forward * 1000f);
            }
            else
            {
                lineRenderer.startWidth = 0f;
                lineRenderer.endWidth = 0f;
            }
        }
        else
        {
            lineRenderer.startWidth = 0f;
            lineRenderer.endWidth = 0f;
            // Raycast did not hit anything
            //Debug.Log("Raycast did not hit anything.");
        }

        // Visualize the raycast

        //LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BullatRaycast.position);
        //lineRenderer.SetPosition(1, m_BullatRaycast.position + m_BullatRaycast.forward*1000f);
    }


    private void Shoot()
    {
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(screenCenter);

        LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BulletRaycast.position);
        //lineRenderer.SetPosition(1, m_BulletRaycast.position + m_BulletRaycast.forward * 1000f);

        if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
        {
            // Raycast hit something
            //Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);

            // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
            if (hitInfo.collider.gameObject.name.Equals("Toon Diamond Bus 01"))
            {
                //Debug.Log("Hit a go!");
                // Do something when a go is hit
            }
        }
        else
        {
            //lineRenderer.startWidth = 0f;
            //lineRenderer.endWidth = 0f;
            // Raycast did not hit anything
            //Debug.Log("Raycast did not hit anything.");
        }
    }

    private void MovePlayerAwayFromScreen()
    {
        Debug.Log("Controller : " + StudioController.GetMyController());
        StudioController.GetMyController().AllowPlayerMovement(false);
        StudioController.GetMyController().ToggleVisibilityOfJoystick(false);
        StudioController.GetMyController().SetPlayerPosition(new Vector3(1000f, 1000f, 1000f), false, false);
    }

    void ZoomIn()
    {
        if (Camera.main.fieldOfView > 40)
        {
            Camera.main.fieldOfView -= 1;
            //Debug.Log("FOV : "+Camera.main.fieldOfView);
        }
        else
        {
        }
    }

    void ZoomOut()
    {
        if(Camera.main.fieldOfView < 79)
        {
            Camera.main.fieldOfView += 3;
        }
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }

    public void OnPointerDown(PointerEventData eventData)
    {
        
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        
    }
}


```

## Cube.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.UI;

public class Cube : StudioBehaviour
{

    LineRenderer lineRenderer;
    GameObject Gun;
    Vector3 DamageLocation;
    GameObject m_DamageIndicagtorUIGO;
    GameObject m_DamageIndicatorUI;
    Image m_DamageIndicatorImg;
    GameObject m_HealthBar;
    Image healthBar;

    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_HealthBar = GetGameObjectVariable("HealthBar");
        healthBar = m_HealthBar.GetComponent(typeof(Image)) as Image;
        m_DamageIndicagtorUIGO = GetGameObjectVariable("Damage Indicator");
        var DamageUi = GetTemplate(m_DamageIndicagtorUIGO, typeof(EditUITemplate)) as EditUITemplate;
        m_DamageIndicatorUI = DamageUi.GetInstantiatedUI;
        m_DamageIndicatorImg = StudioExtensions.FindDeepChild(m_DamageIndicatorUI.transform, "WorldWar_DamageIndicator").gameObject.GetComponent(typeof(Image)) as Image;

        gameObject.AddComponent<LineRenderer>();
        gameObject.GetComponent<LineRenderer>().startWidth = 0f;
        gameObject.GetComponent<LineRenderer>().endWidth = 0f;

        lineRenderer = gameObject.GetComponent<LineRenderer>();
        Gun = GetGameObjectVariable("Gun");
        StartCoroutine(AutoShoot());
    }

    // Gets called every frame
    private void Update()
    {
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //Vector3 direction = Gun.transform.position - transform.position;
        
        //lineRenderer.SetPosition(0, transform.position);
        //lineRenderer.SetPosition(1,  transform.forward +direction * 1000);
    }

    IEnumerator AutoShoot()
    {
        if (gameObject.name == "Fantasy Yellow Cube 01")
        {
            m_DamageIndicatorImg.gameObject.SetActive(true);

            lineRenderer.startWidth = 0.01f;
            lineRenderer.endWidth = 5f;
            Vector3 direction = Gun.transform.position - transform.position;
            lineRenderer.SetPosition(0, transform.position);
            lineRenderer.SetPosition(1, transform.forward + direction * 1000);
            DamageLocation = gameObject.transform.position;
            DamageLocation.y = Camera.main.transform.position.y;

            Vector3 Direction = (DamageLocation - Camera.main.transform.position).normalized;

            float angle = (Vector3.SignedAngle(Direction, Camera.main.transform.forward, Vector3.up));

            Transform t = m_DamageIndicatorImg.GetComponent(typeof(RectTransform)) as RectTransform;
            healthBar.fillAmount = healthBar.fillAmount - 0.01f;

            t.localEulerAngles = new Vector3(0, 0, angle);
            //Shooting_Manager.DecreseHealth();
            yield return new WaitForSeconds(1.33331f);
            if (t.eulerAngles.z == angle)
            {
                m_DamageIndicatorImg.gameObject.SetActive(false);
            }

            lineRenderer.startWidth = 0f;
            lineRenderer.endWidth= 0f;
            yield return new WaitForSeconds(1.33331f);

        }
        else
        {
            m_DamageIndicatorImg.gameObject.SetActive(true);

            lineRenderer.startWidth = 0.01f;
            lineRenderer.endWidth = 5f;
            Vector3 direction = Gun.transform.position - transform.position;
            lineRenderer.SetPosition(0, transform.position);
            lineRenderer.SetPosition(1, transform.forward + direction * 1000);

            DamageLocation = gameObject.transform.position;
            DamageLocation.y = Camera.main.transform.position.y;

            Vector3 Direction = (DamageLocation - Camera.main.transform.position).normalized;

            float angle = (Vector3.SignedAngle(Direction, Camera.main.transform.forward, Vector3.up));

            Transform t = m_DamageIndicatorImg.GetComponent(typeof(RectTransform)) as RectTransform;

            t.localEulerAngles = new Vector3(0, 0, angle);
            healthBar.fillAmount = healthBar.fillAmount - 0.01f;

            yield return new WaitForSeconds(1.5f);

            if(t.eulerAngles.z == angle)
            {
                m_DamageIndicatorImg.gameObject.SetActive(false);
            }

            lineRenderer.startWidth = 0f;
            lineRenderer.endWidth = 0f;
            yield return new WaitForSeconds(2f);
        }

        StartCoroutine(AutoShoot());

    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }
}


```

## Enemy_Behavior.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.SocialPlatforms;
using static UnityEngine.GraphicsBuffer;

public class Enemy_Behavior : StudioBehaviour
{

    GameObject m_Indicator;
    Vector3 screenPoint;
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_Indicator = GetGameObjectVariable("Indicator");

    }

    // Gets called every frame
    private void Update()
    {
        //if (IsGameObjectVisible(gameObject))
        //{
        //    m_Indicator.SetActive(true);
        //}
        //else
        //{
        //    Debug.Log("FFALLSESEEEE "+gameObject.name);
        //    m_Indicator.SetActive(false);
        //}
        bool isVisible = IsGameObjectInViewport(gameObject);
        if (isVisible)
        {
            // GameObject is visible
            //Debug.Log("GameObject is visible " + gameObject.name);
            m_Indicator.SetActive(true);
        }
        else
        {
            // GameObject is not visible
            m_Indicator.SetActive(false);
        }
    }

    bool IsGameObjectInViewport(GameObject target)
    {
        Vector3 viewportPosition = Camera.main.WorldToViewportPoint(target.transform.position);

        if (viewportPosition.x >= 0 && viewportPosition.x <= 1 &&
            viewportPosition.y >= 0 && viewportPosition.y <= 1 &&
            viewportPosition.z > 0)
        {
            return true;

        }
        else
        {
            return false;
        }
    }

    bool IsGameObjectVisible(GameObject Target)
    {
    //    if (viewportPosition.x >= viewportRect.min.x && viewportPosition.x <= viewportRect.max.x &&
    //viewportPosition.y >= viewportRect.min.y && viewportPosition.y <= viewportRect.max.y &&
    //viewportPosition.z > 0)
    //    {
    //        // GameObject is visible
            return true;
        //    }
        //    else
        //    {
        //        // GameObject is not visible
        //        return false;
        //    }
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }
}


```

## Missile.cs

```csharp
using DG.Tweening;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Net.Mail;
using System.Runtime.Versioning;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.Rendering.Universal;
using UnityEngine.UI;

public class Missile : StudioBehaviour
{

    Vector3 m_ScreenCenter;
    bool m_IsGuidedMissile;
    GameObject m_Target;
    Rigidbody m_Rb;
    float m_MissileSpeed;
    Transform m_LaunchPos;

    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_ScreenCenter = Camera.main.ScreenToWorldPoint(new Vector3(Screen.width / 2, Screen.height / 2, 0));

        m_Rb = GetComponent(typeof(Rigidbody)) as Rigidbody;
    }



    // Gets called every frame
    private void Update()
    {
       
    }

    void LateUpdate()
    {

        Debug.Log("HIE");
    }

    private void FixedUpdate()
    {
        if(!m_Target)
        {
            return;
        }
        if (m_IsGuidedMissile)
        {

            Vector3 direction = m_Target.transform.position - transform.position;
            direction.Normalize();

            Vector3 amountToRotate = Vector3.Cross(direction, transform.forward) * Vector3.Angle(transform.forward, direction);

            m_Rb.angularVelocity = -amountToRotate.normalized * 1f;

            m_Rb.velocity = transform.forward * m_MissileSpeed;

        }
        else
        {
            Vector3 direction = m_ScreenCenter - transform.position;
            direction.Normalize();

            // Apply velocity
            m_Rb.velocity = direction * m_MissileSpeed;
            
        }


    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }

    public void GetEnemy(GameObject target , bool IsGuided, float MissileSpeed,Transform LaunchPoint)
    {
        m_MissileSpeed = MissileSpeed;
        m_Target = target;
        m_LaunchPos = LaunchPoint;
        m_IsGuidedMissile = IsGuided;

        // Get the screen-space position of the crosshair
        m_ScreenCenter = new Vector2(Screen.width / 2, Screen.height / 2);
        // Convert screen-space position to world-space position using a raycast
        Ray ray = Camera.main.ScreenPointToRay(m_ScreenCenter);
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit))
        {
            m_ScreenCenter = hit.point;
        }
        else
        {
            // Calculate target position based on ray direction and desired distance
            float desiredDistance = 50f; // Adjust as needed
            m_ScreenCenter = ray.origin + ray.direction * desiredDistance;
        }
        StartCoroutine(Destroyedd());

        //m_ScreenCenter = Camera.main.transform.forward;
    }

    IEnumerator Destroyedd()
    {
        yield return new WaitForSeconds(5f);
        Destroy(gameObject);
    }
}


```

## Missile_Manager.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;

public class Missile_Manager : StudioBehaviour
{

    public float Damage;
    public float MissileSpeed;
    public float CooldownTime;
    public float AOE_Range;

    Vector3 m_ScreenCenter;
    bool m_IsReloading;


    GameObject[] m_Enemies;
    GameObject m_ClosestEnemy;

    //TEST

    Transform target;
    float speed = 25f;
    float rotateSpeed = 1f;
    bool Launched;

    private Rigidbody rb;
    GameObject g;
    GameObject h;
    GameObject Indicator;
    Vector3 v;
    Transform t;
    int m_MissileCount;

    GameObject m_CrosshairUI;
    GameObject m_CrossHairUIGO;
    GameObject m_CrossHairGO;

    GameObject m_UI;
    GameObject m_GameUI;
    GameObject m_LaunchGO;
    TextMeshProUGUI m_MissileCountText;
    GameObject SpawnerGO;
    Button m_LaunchMissleBtn;
    Image m_LaunchBg;
    Button m_GuidedOffBtn;
    Button m_GuidedOnBtn;
    bool m_IsGuidedMissile;
    Button m_ToggleGuidedMissileBtn;
    Image m_GuidedMissileBg;

    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_IsGuidedMissile = false;
        m_MissileCount = 10;
        m_Enemies = new GameObject[100];
        m_Enemies[0] = GetGameObjectVariable("Enemy_01");
        m_Enemies[1] = GetGameObjectVariable("Enemy_02");
        m_Enemies[2] = GetGameObjectVariable("Enemy_03");
        m_Enemies[3] = GetGameObjectVariable("Enemy_04");
        m_Enemies[4] = GetGameObjectVariable("Enemy_05");
        m_Enemies[5] = GetGameObjectVariable("Enemy_06");
        m_Enemies[6] = GetGameObjectVariable("Enemy_07");
        m_Enemies[7] = GetGameObjectVariable("Enemy_08");

        Indicator = GetGameObjectVariable("Indicator");
        SpawnerGO = GetGameObjectVariable("Spawn");
        t = SpawnerGO.transform;
        gameObject.AddComponent<LineRenderer>();
        gameObject.GetComponent<LineRenderer>().startWidth = 0f;
        gameObject.GetComponent<LineRenderer>().endWidth = 0f;
        m_ScreenCenter = new Vector3(Screen.width / 2, Screen.height / 2, 0);
        g = GetGameObjectVariable("Bullet");
        rb = g.GetComponent<Rigidbody>();
        v = new Vector3(g.transform.position.x, g.transform.position.y, g.transform.position.z + 10f);/*
        Missile? m = h.GetComponent(typeof(Missile)) as Missile;
        m.g = m_Enemies[1];*/
        Launched = false;
        m_IsReloading = false;
        m_UI = GetGameObjectVariable("UI");
        m_CrosshairUI = GetGameObjectVariable("Crosshair");
        var Ui = GetTemplate(m_UI, typeof(EditUITemplate)) as EditUITemplate;
        m_GameUI = Ui.GetInstantiatedUI;
        m_LaunchGO = StudioExtensions.FindDeepChild(m_GameUI.transform, "Launcher_button").gameObject;
        m_LaunchMissleBtn = m_LaunchGO.GetComponent(typeof(Button)) as Button;
        m_LaunchMissleBtn.onClick.AddListener(ShootMissile);
        m_LaunchBg = m_LaunchGO.transform.GetChild(0).GetComponent<Image>();

        m_GuidedOffBtn = StudioExtensions.FindDeepChild(m_GameUI.transform, "Rocket_off_bar_selected").gameObject.GetComponent<Button>();
        m_GuidedOffBtn.onClick.AddListener(() => SetGuidedMissile(false));

        m_GuidedOnBtn = StudioExtensions.FindDeepChild(m_GameUI.transform, "Rocket_on_bar_selected").gameObject.GetComponent<Button>();
        m_GuidedOnBtn.onClick.AddListener(() => SetGuidedMissile(true));

        m_ToggleGuidedMissileBtn = StudioExtensions.FindDeepChild(m_GameUI.transform, "Rocket_box").gameObject.GetComponent<Button>();
        m_ToggleGuidedMissileBtn.onClick.AddListener(ToggleGuidedMissile);

        m_GuidedMissileBg = StudioExtensions.FindDeepChild(m_GameUI.transform, "Rocket_box_bg").gameObject.GetComponent<Image>();
        m_GuidedMissileBg.color = Color.red;

        m_MissileCountText = StudioExtensions.FindDeepChild(m_GameUI.transform, "Rocket_count_text").gameObject.GetComponent<TextMeshProUGUI>();
        m_MissileCountText.text = m_MissileCount.ToString();

        var CrosssHairUI = GetTemplate(m_CrosshairUI, typeof(EditUITemplate)) as EditUITemplate;
        m_CrossHairUIGO = CrosssHairUI.GetInstantiatedUI;
        m_CrossHairGO = StudioExtensions.FindDeepChild(m_CrossHairUIGO.transform, "WorldWar_Crosshair").gameObject;
    }

    // Gets called every frame
    private void Update()
    {
        
        if (Input.GetKey(KeyCode.V))
        {
            //if (!m_IsReloading)
            //{
            //    m_IsReloading = true;
            //    StartCoroutine(Delay());
            //}

        }
        //CalculateAngle();

    }

    private void FixedUpdate()
    {
        CalculateAngle();
    }
    IEnumerator Delay()
    {
        LaunchMissle();
        h = Instantiate(g, t.position, t.rotation);
        yield return new WaitForSeconds(0.1f);

        if (Launched && m_IsGuidedMissile)
        {
            m_MissileCount--;
            m_MissileCountText.text = m_MissileCount.ToString();

            Missile? m = h.GetComponent(typeof(Missile)) as Missile;
            Vector3 direction = m_ClosestEnemy.transform.position - t.transform.position;
            direction.Normalize();
            m.GetEnemy(m_ClosestEnemy,m_IsGuidedMissile,MissileSpeed, t);
            m_LaunchMissleBtn.interactable = false;
            Color newColor = new Color(255, 0, 0, 1);
            m_LaunchBg.color = newColor;
        }
        else
        {
            m_MissileCount--;
            m_MissileCountText.text = m_MissileCount.ToString();

            Missile? m = h.GetComponent(typeof(Missile)) as Missile;
            Vector3 direction = m_ClosestEnemy.transform.position - t.transform.position;
            direction.Normalize();
            Debug.Log("JAAII");
            m.GetEnemy(m_CrossHairGO, false, MissileSpeed,t);
            m_LaunchMissleBtn.interactable = false;
            Color newColor = new Color(255, 0, 0, 1);
            m_LaunchBg.color = newColor;
        }
    }
    void CalculateAngle()
    {
        if (Launched)
        {/*
            //Vector3 New = new Vector3(m_ClosestEnemy.transform.position.x, m_ClosestEnemy.transform.position.y +1f, m_ClosestEnemy.transform.position.z);
            Vector3 direction = m_Enemies[1].transform.position - rb.position;
            direction.Normalize();

            Vector3 amountToRotate = Vector3.Cross(direction, h.transform.forward) * Vector3.Angle(h.transform.forward, direction);
            //rb.velocity = new Vector3(10f,0,0);
            rb.angularVelocity = -amountToRotate.normalized * rotateSpeed;

            //Debug.Log("HIEE  " + rb.velocity);
            rb.velocity = h.transform.forward * speed;*/
        }
        
    }

    void ShootMissile()
    {
        if (!m_IsReloading && m_MissileCount>0)
        {
            Debug.Log("SHOOTt");
            m_IsReloading = true;
            StartCoroutine(Delay());
        }
    }

    void LaunchMissle()
    {
        
        float minDist = 100000f;
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(m_ScreenCenter);

        LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BulletRaycast.position);
        //lineRenderer.SetPosition(1, m_BulletRaycast.position + m_BulletRaycast.forward * 1000f);
        //if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
        {
            //Debug.DrawLine(transform.position, hitInfo.point, Color.green);
            // Raycast hit something
            //Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);
            //lineRenderer.startWidth = 0.1f;
            //lineRenderer.endWidth = 5f;
            //lineRenderer.SetPosition(0, Camera.main.transform.position);
            //lineRenderer.SetPosition(1, Camera.main.transform.position + Camera.main.transform.forward * 1000f);
            Vector2 raycastRef = (Camera.main.transform.position);
            // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
            for (int i = 0; i < 8; i++)
            {
                //Vector3 n = ENEMIES[i].transform.worldToLocalMatrix.GetPosition();

                Vector2 enemy = Camera.main.WorldToScreenPoint(m_Enemies[i].transform.position);

                float dist = Vector2.Distance(enemy, m_ScreenCenter);
                if (IsGameObjectVisible(m_Enemies[i]))
                {

                    Debug.Log("VISIBLE");
                    if(dist < minDist)
                    {
                        Debug.Log("TARGET IS : " + m_Enemies[i] + " DIST : " + dist);
                        minDist = dist;
                        m_ClosestEnemy = m_Enemies[i];
                    }
                    //if (dist > 1000)
                    //{
                    //    Debug.Log("OUTT OF RANGEEE : "+dist);
                    //    return;
                    //}
                }
            }
            if (minDist > AOE_Range /*|| !IsGameObjectVisible(m_ClosestEnemy)*/)
            {
                Launched = false;
                Debug.Log("OUTT OF RANGEEE : "+m_ClosestEnemy +" " + minDist);
                Reload();
                return;
            }
        }
        Launched = true;
        Reload();
    }

    bool IsGameObjectVisible(GameObject Target)
    {
        //Vector3 screenPosition = Camera.main.WorldToScreenPoint(Target.transform.position);

        //// Adjust screen position based on camera rotation
        //if (Mathf.Abs(Camera.main.transform.rotation.eulerAngles.z) >= 90f || Mathf.Abs(Camera.main.transform.rotation.eulerAngles.x) >= 90f)
        //{
        //    screenPosition.x = Mathf.Clamp(screenPosition.x, 0f, Screen.width);
        //    screenPosition.y = Mathf.Clamp(screenPosition.y, 0f, Screen.height);
        //}

        //// Adjust screen position based on camera scale
        //if (Camera.main.orthographic)
        //{
        //    float scaleFactor = Camera.main.orthographicSize / Screen.height;
        //    screenPosition *= scaleFactor;
        //}

        //// Check if the adjusted screen position is within the screen bounds and the z coordinate is positive
        //if (screenPosition.x >= 0 && screenPosition.x <= Screen.width && screenPosition.y >= 0 && screenPosition.y <= Screen.height && screenPosition.z > 0)
        //{
        //    //Debug.Log("GameObject is visible: " + Target.name);
        //    return true;
        //}
        //else
        //{
        //    //Debug.Log("GameObject is not visible: " + Target.name);
        //    return false;
        //}
        Vector3 viewportPosition = Camera.main.WorldToViewportPoint(Target.transform.position);

        if (viewportPosition.x >= 0 && viewportPosition.x <= 1 &&
            viewportPosition.y >= 0 && viewportPosition.y <= 1 &&
            viewportPosition.z > 0)
        {
            return true;

        }
        else
        {
            return false;
        }
    }

    public void Reload()
    {
        if (!m_IsReloading)
        {
            //m_ReloadText.text = "Reloading";
        }
            m_IsReloading = true;
            // Start reloading animation or timer
            StartCoroutine(ReloadCoroutine());
    }

    private IEnumerator ReloadCoroutine()
    {
       
        yield return new WaitForSeconds(CooldownTime);
        //m_CurrentAmmo = ClipSize;
        m_IsReloading = false;
        Launched = false;
        m_LaunchMissleBtn.interactable = true;
        Color newColor = new Color(255, 255, 255, 255);
        m_LaunchBg.color = newColor;
        //m_ReloadText.text = "Reload";
        //m_BulletCountText.text = m_CurrentAmmo.ToString();
    }

    void SetGuidedMissile(bool IsGuided)
    {
        m_IsGuidedMissile = IsGuided;
        Debug.Log("GUIDED : " + m_IsGuidedMissile);
        SetGuidedMissileColor();
    }

    void ToggleGuidedMissile()
    {
        m_IsGuidedMissile = !m_IsGuidedMissile;
        SetGuidedMissileColor() ;
    }

    void SetGuidedMissileColor()
    {
        if (m_IsGuidedMissile)
        {
            m_GuidedMissileBg.color = Color.green;
        }
        else
        {
            Launched = false;
            m_GuidedMissileBg.color = Color.red;
        }
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }
}


```

## Shooting_Manager.cs

```csharp
using DG.Tweening;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Net.Mail;
using System.Runtime.Versioning;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.EnhancedTouch;
using UnityEngine.Rendering.Universal;
using UnityEngine.UI;


public class Shooting_Manager : StudioBehaviour
{
    float m_Pan_Sensitivity;
    bool m_AutoShoot;
    Vector3 m_ScreenCenter;
    Transform m_BulletRaycast;

    public float Damage;
    public float FireRate;
    public float BulletSpeed;
    public int ClipSize;
    public float ReloadTime;

    private int m_CurrentAmmo;
    private bool m_IsReloading;
    private float m_NextFireTime;
    private float m_Health;

    GameObject m_Bullet;
    GameObject m_Spawner;
    GameObject m_UI;
    GameObject m_GameUI;
    GameObject m_ReloadGO;
    TextMeshProUGUI m_BulletCountText;
    TextMeshProUGUI m_ReloadText;
    GameObject m_AutoFire;
    TextMeshProUGUI m_AutoFireText;
    GameObject m_HealthBar;
    Image healthBar;
    GameObject m_LeftFireBtn;
    bool m_IsShooting;

    //TEMP
    GameObject bullet;
    float TEMPHEALTH;
    GameObject[] ENEMIES;
    GameObject CLOSEST;
    LineRenderer lineRenderer;

    //Magazine UI
    GameObject m_MagazineUI;
    GameObject m_MagazineUIGO;
    Image m_MagazineGO;
    float m_PerAmmoFillAmount;

    Transform m_cam;

    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        m_Health = 100f;
        TEMPHEALTH = 100f;
        ENEMIES = new GameObject[100];
        m_IsShooting = false;
        m_AutoShoot = false;
        m_ScreenCenter = new Vector3(Screen.width / 2, Screen.height / 2, 0);
        //m_BulletRaycast = gameObject.transform.GetChild(0).transform;
        //gameObject.AddComponent<LineRenderer>();
        //gameObject.GetComponent<LineRenderer>().startWidth = 0f;
        //gameObject.GetComponent<LineRenderer>().endWidth = 0f;
        m_NextFireTime = Time.time;

        m_Bullet = GetGameObjectVariable("Bullet");
        m_Spawner = GetGameObjectVariable("SpawnPoint");
        //ENEMIES[0] = GetGameObjectVariable("Bus");
        //ENEMIES[1] = GetGameObjectVariable("Stick");
        //Debug.Log("ENEMY  " + ENEMIES[1]);

        m_UI = GetGameObjectVariable("UI");
        var Ui = GetTemplate(m_UI, typeof(EditUITemplate)) as EditUITemplate;
        m_GameUI = Ui.GetInstantiatedUI;
        m_ReloadGO = StudioExtensions.FindDeepChild(m_GameUI.transform, "Reload_box").gameObject;
        Button? ReloadButon = m_ReloadGO.GetComponent(typeof(Button)) as Button;
        ReloadButon.onClick.AddListener(Reload);
        Debug.Log("UII " + m_UI);
        //m_HealthBar = StudioExtensions.FindDeepChild(m_GameUI.transform, "Health_bar_green").gameObject;

        m_AutoFire = StudioExtensions.FindDeepChild(m_GameUI.transform, "Auto_fire_switch_bg").gameObject;
        Button AutoFireButton = m_AutoFire.gameObject.transform.GetChild(0).GetComponent(typeof(Button)) as Button;
        AutoFireButton.onClick.AddListener(ToggleAutoFire);
        Debug.Log("BUTTON " + AutoFireButton);

        m_AutoFireText = m_AutoFire.transform.GetChild(1).gameObject.GetComponent<TextMeshProUGUI>();
        m_AutoFire.GetComponent<Image>().color = Color.red;

        m_LeftFireBtn = StudioExtensions.FindDeepChild(m_GameUI.transform, "Shoot_button_left").gameObject;

        m_BulletCountText = m_ReloadGO.transform.GetChild(0).transform.GetChild(2).gameObject.GetComponent<TextMeshProUGUI>();
        m_CurrentAmmo = int.Parse(m_BulletCountText.text);
        m_ReloadText = m_ReloadGO.transform.GetChild(0).transform.GetChild(1).gameObject.GetComponent<TextMeshProUGUI>();
        GameObject CAM = GetGameObjectVariable("Camera");
        m_Pan_Sensitivity = (CAM.transform.GetComponent(typeof(Camera_Movement)) as Camera_Movement).PAN_Sensitivity;

        m_HealthBar = GetGameObjectVariable("HealthBar");
        healthBar = m_HealthBar.GetComponent(typeof(Image)) as Image;
        //healthBar.fillCenter = true;
        healthBar.fillAmount = 1f;
        //m_HealthBar.SetActive(false);
        lineRenderer = gameObject.GetComponent<LineRenderer>();

        m_MagazineUI = GetGameObjectVariable("Magazine");
        var MagUI = GetTemplate(m_MagazineUI, typeof(EditUITemplate)) as EditUITemplate;
        m_MagazineUIGO = MagUI.GetInstantiatedUI;
        m_MagazineGO = StudioExtensions.FindDeepChild(m_MagazineUIGO.transform, "MagazineIndicator_Fill_____").gameObject.GetComponent(typeof(Image)) as Image;

        //m_MagazineGO.fillAmount = 0.7f;

        m_PerAmmoFillAmount = 0.43f / ClipSize;

    }


    // Gets called every frame
    private void Update()
    {
        //healthBar.fillAmount = 0.4f;

        if (Input.touchCount > 0)
        {
            UnityEngine.Touch touch = Input.GetTouch(0);
            int touchId = Input.GetTouch(0).fingerId;


            if (touch.phase == TouchPhase.Began && EventSystem.current.IsPointerOverGameObject(touchId) && (EventSystem.current.currentSelectedGameObject.name == "Shoot_button_right" || EventSystem.current.currentSelectedGameObject.name == "Shoot_button_left"))
            {
                if((EventSystem.current.currentSelectedGameObject.name == "Shoot_button_right" || EventSystem.current.currentSelectedGameObject.name == "Shoot_button_left"))
                {
                    m_IsShooting = true;
                }
                Debug.Log("HELLOWW");
                if (!m_IsReloading)
                {
                    if (Time.time >= m_NextFireTime)
                    {
                        Shoot();
                        m_NextFireTime = Time.time + 1f / FireRate;
                    }
                }
            }
            else if ((touch.phase == TouchPhase.Moved || touch.phase ==  TouchPhase.Stationary) && m_IsShooting)
            {
                if (!m_IsReloading)
                {
                    if (Time.time >= m_NextFireTime)
                    {
                        Shoot();
                        m_NextFireTime = Time.time + 1f / FireRate;
                    }
                }
            }
            else if (touch.phase == TouchPhase.Ended || touch.phase == TouchPhase.Canceled)
            {
                m_IsShooting = false;
            }
        }

        if (Input.touchCount > 0)
        {
            int touchId = Input.GetTouch(0).fingerId;
            if(Input.GetTouch(0).phase == TouchPhase.Stationary)
            {
                StudioController.GetMyController().DisablePan();
                Camera.main.transform.rotation = m_cam.rotation;
                Camera.main.transform.position = m_cam.position;
            }
            else
            {
                StudioController.GetMyController().EnablePan();
                m_cam = Camera.main.transform;
            }
            if (EventSystem.current.IsPointerOverGameObject(touchId))
            {

                StudioController.GetMyController().ChangePanSpeed(0);

                //if (EventSystem.current.currentSelectedGameObject != null && !m_AutoShoot)
                //{
                //    if (EventSystem.current.currentSelectedGameObject.name == "Shoot_button_right" || EventSystem.current.currentSelectedGameObject.name == "Shoot_button_left" && !m_AutoShoot)
                //    {
                //        //Debug.Log("Touching " + EventSystem.current.currentSelectedGameObject);
                //        if (!m_IsReloading)
                //        {
                //            if (Time.time >= m_NextFireTime)
                //            {
                //                Shoot();
                //                m_NextFireTime = Time.time + 1f / FireRate;
                //            }
                //        }
                //    }
                //    else if(!m_AutoShoot)
                //    {
                       
                //        lineRenderer.startWidth = 0f;
                //        lineRenderer.endWidth = 0f;
                //    }

                //    if (EventSystem.current.currentSelectedGameObject.name == "Reload_box" && !m_IsReloading && m_CurrentAmmo < ClipSize)
                //    {
                //        //Reload();
                //        //if (m_IsFocused)
                //        //{
                //        //    m_IsFocused = false;
                //        //    Camera.main.fieldOfView = Initial_Zoom_Length;
                //        //}
                //        //else
                //        //{
                //        //    m_IsFocused = true;
                //        //    Camera.main.fieldOfView = 60;
                //        //}
                //    }
                //}
            }
            else
            {
                StudioController.GetMyController().ChangePanSpeed(m_Pan_Sensitivity);
                if (!m_AutoShoot)
                {

                    //lineRenderer.startWidth = 0f;
                    //lineRenderer.endWidth = 0f;
                }
            }
        }

        if (m_AutoShoot)
        {
            DetectRaycastHit();
        }
        else if (!m_AutoShoot)
        {
            //gameObject.GetComponent<LineRenderer>().startWidth = 0f;
            //gameObject.GetComponent<LineRenderer>().endWidth = 0;
        }
    }

    void ToggleAutoFire()
    {
        Debug.Log("byeeee");
        if (m_AutoFireText.text == "OFF")
        {
            Debug.Log("ONN");
            m_AutoFireText.text = "ON";
            m_AutoFire.GetComponent<Image>().color = Color.green;
            m_AutoShoot = true;
            m_LeftFireBtn.gameObject.SetActive(false);
        }
        else
        {
            m_AutoFireText.text = "OFF";
            m_AutoFire.GetComponent<Image>().color = Color.red;
            m_AutoShoot = false;
            m_LeftFireBtn.gameObject.SetActive(true);
        }
    }

    void DetectRaycastHit()
    {
        // Perform the raycast
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(m_ScreenCenter);

        //LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        if (!m_IsReloading && m_CurrentAmmo > 0)
        {
            if (Time.time >= m_NextFireTime)
            {
                
                if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
                {
                    // Raycast hit something
                    Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);

                    // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
                    if (hitInfo.collider.gameObject.transform.root.name.Equals("Toon Diamond Bus 01") || hitInfo.collider.gameObject.transform.root.name.Equals("City Truck Engine 01") 
                        || hitInfo.collider.gameObject.transform.root.name.Equals("Scifi Racing Car 01") || hitInfo.collider.gameObject.transform.root.name.Equals("City Goods Truck 01")
                        || hitInfo.collider.gameObject.transform.root.name.Equals("Swat Military Tank 01") || hitInfo.collider.gameObject.transform.root.name.Equals("Farm Utility Pickup 01")
                        || hitInfo.collider.gameObject.transform.root.name.Equals("Farm Utility Pickup 02") || hitInfo.collider.gameObject.transform.root.name.Equals("Fantasy Goods Vehicle 01"))  
                    {
                        //GameObject bullet = Instantiate(m_Bullet, m_Spawner.transform.position, m_Spawner.transform.rotation);
                        StartCoroutine(InstantiateBullet());

                        m_CurrentAmmo--;
                        DecreaseMagazineFillAmount();
                        m_BulletCountText.text = m_CurrentAmmo.ToString();
                        //lineRenderer.startWidth = 0.01f;
                        //lineRenderer.endWidth = 5f;
                        //lineRenderer.SetPosition(0, Camera.main.transform.position);
                        //lineRenderer.SetPosition(1, Camera.main.transform.position + Camera.main.transform.forward * 10000f);
                        //Debug.Log("Hit a go!");
                        // Do something when a go is hit
                    }
                    else
                    {
                        //lineRenderer.startWidth = 0f;
                        //lineRenderer.endWidth = 0f;
                    }
                    
                    ////Debug.Log(m_BulletCountText.text + " BULLET");
                    //if (!m_IsReloading && m_CurrentAmmo <= 0)
                    //{
                    //    Reload();
                    //    lineRenderer.startWidth = 0f;
                    //    lineRenderer.endWidth = 0f;
                    //}
                }
                else
                {
                    //lineRenderer.startWidth = 0f;
                    //lineRenderer.endWidth = 0f;
                    // Raycast did not hit anything
                    //Debug.Log("Raycast did not hit anything.");
                }
                
                //Debug.Log(m_BulletCountText.text + " BULLET");
                if (!m_IsReloading && m_CurrentAmmo <= 0)
                {
                    Reload();
                    //lineRenderer.startWidth = 0f;
                    //lineRenderer.endWidth = 0f;
                }
                m_NextFireTime = Time.time + 1f / FireRate;
            }
        }

        // Visualize the raycast

        //LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BullatRaycast.position);
        //lineRenderer.SetPosition(1, m_BullatRaycast.position + m_BullatRaycast.forward*1000f);
    }

    private void Shoot()
    {
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(m_ScreenCenter);

        LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BulletRaycast.position);
        //lineRenderer.SetPosition(1, m_BulletRaycast.position + m_BulletRaycast.forward * 1000f);

        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, Camera.main.transform.position);
        //lineRenderer.SetPosition(1, Camera.main.transform.position + Camera.main.transform.forward * 10000f);
        //GameObject bullet = Instantiate(m_Bullet, m_Spawner.transform.position, m_Spawner.transform.rotation);
        StartCoroutine(InstantiateBullet());
        if (!m_IsReloading && m_CurrentAmmo > 0)
        {
            // Create a bullet object and fire it

            if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
            {
                //lineRenderer.startWidth = 0.01f;
                //lineRenderer.endWidth = 5f;
                //lineRenderer.SetPosition(0, Camera.main.transform.position);
                //lineRenderer.SetPosition(1, Camera.main.transform.position + Camera.main.transform.forward * 10000f);
                // Raycast hit something
                //Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);

                // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
                if (hitInfo.collider.gameObject.name.Equals("Toon Diamond Bus 01"))
                {
                    //Debug.Log("Hit a go!");
                    // Do something when a go is hit
                    TEMPHEALTH -= Damage;
                    Debug.Log("HEALTH : " + TEMPHEALTH);

                }
            }
            else
            {
                //lineRenderer.startWidth = 0f;
                //lineRenderer.endWidth = 0f;
            }

            m_CurrentAmmo--;
            DecreaseMagazineFillAmount();
            m_BulletCountText.text = m_CurrentAmmo.ToString();

            //Debug.Log(m_BulletCountText.text + " BULLET");
            if (!m_IsReloading && m_CurrentAmmo <= 0)
            {
                Reload();
            }
        }
        //if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
        //{
        //    // Raycast hit something
        //    Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);

        //    // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
        //    if (hitInfo.collider.gameObject.name.Equals("Toon Diamond Bus 01"))
        //    {
        //        //Debug.Log("Hit a go!");
        //        // Do something when a go is hit
        //    }
        //}
        //else
        //{
        //    //lineRenderer.startWidth = 0f;
        //    //lineRenderer.endWidth = 0f;
        //    // Raycast did not hit anything
        //    //Debug.Log("Raycast did not hit anything.");
        //}
    }

    IEnumerator InstantiateBullet()
    {
        {

            bullet = Instantiate(m_Bullet, m_Spawner.transform.position, m_Spawner.transform.rotation);
        }
        yield return null;

        {

            Bullet? BULLET = bullet.GetComponent(typeof(Bullet)) as Bullet;
            BULLET.SetVariables(BulletSpeed);
        }
    }
    public void Reload()
    {
        if (!m_IsReloading)
        {
            healthBar.fillAmount = 12f;

            m_ReloadText.text = "Reloading";
            m_IsReloading = true;
            // Start reloading animation or timer
            StartCoroutine(ReloadCoroutine());
        }
    }

    private IEnumerator ReloadCoroutine()
    {
        yield return new WaitForSeconds(ReloadTime);
        m_CurrentAmmo = ClipSize;
        m_IsReloading = false;
        m_ReloadText.text = "Reload";
        m_MagazineGO.fillAmount = 0.7f;
        m_BulletCountText.text = m_CurrentAmmo.ToString();
    }

    void LaunchMissle()
    {
        float minDist = Mathf.Infinity;
        RaycastHit hitInfo;
        Ray ray = Camera.main.ScreenPointToRay(m_ScreenCenter);

        LineRenderer lineRenderer = gameObject.GetComponent<LineRenderer>();
        //lineRenderer.startWidth = 0.01f;
        //lineRenderer.endWidth = 5f;
        //lineRenderer.SetPosition(0, m_BulletRaycast.position);
        //lineRenderer.SetPosition(1, m_BulletRaycast.position + m_BulletRaycast.forward * 1000f);
        //if (Physics.Raycast(ray.origin, ray.direction, out hitInfo))
        {
            //Debug.DrawLine(transform.position, hitInfo.point, Color.green);
            // Raycast hit something
            //Debug.Log("Hit object: " + hitInfo.collider.gameObject.name);
            lineRenderer.startWidth = 0.1f;
            lineRenderer.endWidth = 5f;
            lineRenderer.SetPosition(0, Camera.main.transform.position);
            lineRenderer.SetPosition(1, Camera.main.transform.position + Camera.main.transform.forward * 1000f);
            Vector2 raycastRef = (Camera.main.transform.position);
            Debug.Log("TARGET IS FROM : " + raycastRef);
            // Check if the hit object is a go (you can replace "go" with the actual tag or layer)
            for (int i = 0; i < 2; i++)
            {
                //Vector3 n = ENEMIES[i].transform.worldToLocalMatrix.GetPosition();
                
                Vector2 enemy = Camera.main.WorldToScreenPoint(ENEMIES[i].transform.position);

                float dist = Vector2.Distance(enemy,m_ScreenCenter);
                Debug.Log("TARGET IS : "+enemy + " DIST : "+dist);  
                if(dist < minDist)
                {
                    //if (dist > 1000)
                    //{
                    //    Debug.Log("OUTT OF RANGEEE : "+dist);
                    //    return;
                    //}
                    minDist = dist;
                    CLOSEST = ENEMIES[i];
                }
            }
            if (minDist > 700 || !IsGameObjectVisible(CLOSEST))
            {
                Debug.Log("OUTT OF RANGEEE : " + minDist);
                return;
            }
            Debug.Log("TARGET IS SET TO : " + CLOSEST);
        }
    }

    bool IsGameObjectVisible(GameObject Target)
    {
        Vector3 screenPosition = Camera.main.WorldToScreenPoint(Target.transform.position);

        // Adjust screen position based on camera rotation
        if (Mathf.Abs(Camera.main.transform.rotation.eulerAngles.z) >= 90f || Mathf.Abs(Camera.main.transform.rotation.eulerAngles.x) >= 90f)
        {
            screenPosition.x = Mathf.Clamp(screenPosition.x, 0f, Screen.width);
            screenPosition.y = Mathf.Clamp(screenPosition.y, 0f, Screen.height);
        }

        // Adjust screen position based on camera scale
        if (Camera.main.orthographic)
        {
            float scaleFactor = Camera.main.orthographicSize / Screen.height;
            screenPosition *= scaleFactor;
        }

        // Check if the adjusted screen position is within the screen bounds and the z coordinate is positive
        if (screenPosition.x >= 0 && screenPosition.x <= Screen.width && screenPosition.y >= 0 && screenPosition.y <= Screen.height && screenPosition.z > 0)
        {
            //Debug.Log("GameObject is visible: " + Target.name);
            return true;
        }
        else
        {
            //Debug.Log("GameObject is not visible: " + Target.name);
            return false;
        }
    }   

    
    void DecreaseMagazineFillAmount()
    {
        if (m_CurrentAmmo==0)
        {
            m_MagazineGO.fillAmount = 0f;
        }
        else
        {
            m_MagazineGO.fillAmount -= m_PerAmmoFillAmount;
        }
    }

    public void DecreseHealth()
    {
        m_Health -= 1;
        healthBar.fillAmount = healthBar.fillAmount - 0.01f;
    }

    // Gets called whenever a broadcast is triggered by Behaviours or Other T# scripts
    public override void OnBroadcasted(string x)
    {
        
    }
}


```
