# Traffic Rider - Controller Documentation
## Type
Example

## Overview
Traffic Rider implements a precision motorcycle control system focusing on realistic steering, acceleration, and braking mechanics through touch and tilt controls.

## Core Systems

### Basic Controls
- **Acceleration**:
  - Right-side screen button
  - Press and hold functionality
  - Variable acceleration rates

- **Braking**:
  - Left-side screen button
  - Press and hold for deceleration
  - Variable brake strength

- **Steering**:
  - Device tilt-based control
  - Gyroscopic responsiveness
  - Adjustable sensitivity

### Advanced Mechanics

#### Wheelie System
- **Activation Effects**:
  - Increased acceleration
  - Higher top speed
  - Reduced stability
  - Limited visibility
- **Cooldown System**:
  - Post-wheelie recovery period
  - Level-specific availability

#### Horn Mechanic
- Positioned above brake
- Influences AI vehicle behavior
- Lane-change inducement

### Technical Parameters
- Velocity control
- Turn rate limitations
- Damage calculation
- Balance mechanics
- Tilt sensitivity
- Deceleration rates

---

# Code Implementation

## BikeController.cs

```csharp
using RTG;
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.UI;

public class BikeController : StudioBehaviour
{
    public CameraController cameraController;
    public Transform bikeMesh;

    public float forwardSpeed = 10f;
    public float boostedSpeed = 50f;
    public float brakeSpeed = 5f;
    public float horizontalMovementSpeed = 0.3f;

    public float rotationSensi = 0;

    public float accelerator = 1f;
    public float deAccelerator = 1f;

    public float maxTiltAmount = 0.3f;

    public float maxHealth = 1;
    public float damageAmount = 1f;
    public float maxSpeedForCollison = 0f;

    public float maxSteerAngle = 0.1f;
    public float limitSideMovement = 5f;

    public float acceleratorOnWheelie = 1f;
    public float wheelieSpeed = 30f;
    public float timeToFillWheelie = 1f;
    public float wheelieFillSpeed;

    private bool isBraking = false;
    private bool isBoosting = false;
    private bool isWheelie = false;

    public bool useGyro = true;

    private float tilt = 0;
    private float speed = 0;
    private float directionX = 0;
    private float tiltAmount;
    private Vector3 direction;
    private float health;
    private bool canCarMove = true;
    private float wheelieCoolDown = 0;

    private float damageMultiplier = 0;

    private float smoothingFactor = 0.1f;
    private float deadZoneThreshold = 0.02f;
    private Vector3 smoothAcceleration;

    public static Action OnBrakeHoldAction;
    public static Action OnBrakeLeaveAction;
    public static Action OnBoostHoldAction;
    public static Action OnBoostLeaveAction;
    public static Action OnClickHornAction;
    public static Action OnClickWheelieHoldAction;
    public static Action OnClickWheelieLeaveAction;

    public static Image wheelieFillImage;
    private float wheelieFillMultiplier;

    private Transform bikeHandleTransform;

    private Coroutine wheelieRoutine;

    private void Start()
    {
        Screen.orientation = ScreenOrientation.LandscapeLeft;

        forwardSpeed = GetFloatVariable("NormalSpeed");
        boostedSpeed = GetFloatVariable("BoostedSpeed");
        brakeSpeed = GetFloatVariable("BreakSpeed");
        accelerator = GetFloatVariable("Accelerator");
        deAccelerator = GetFloatVariable("DeAccelerator");
        maxHealth = GetFloatVariable("Health");
        damageAmount = GetFloatVariable("DamageAmount");
        horizontalMovementSpeed = GetFloatVariable("HorizontalMovementSpeed");
        useGyro = GetIntVariable("UseGyro") == 1 ? true : false;
        maxTiltAmount = GetFloatVariable("MaxTiltAmount");
        maxSpeedForCollison = GetFloatVariable("MaxSpeedForCollison");
        bikeMesh = GetGameObjectVariable("BikeMesh").transform;

        maxSteerAngle = GetFloatVariable("MaxSteerAngle");
        rotationSensi = GetFloatVariable("RotationSensi");

        acceleratorOnWheelie = GetFloatVariable("AccelerationOnWheelie");
        wheelieSpeed = GetFloatVariable("WheelieSpeed");
        timeToFillWheelie = GetFloatVariable("WheelieCooldown");
        wheelieFillSpeed = GetFloatVariable("WheelieFillSpeed");

        cameraController = GetGameObjectVariable("CameraController").GetComponent(typeof(CameraController)) as CameraController;
;
        bikeHandleTransform = GetGameObjectVariable("BikeHandle").transform;

        direction = transform.position;
        limitSideMovement = transform.position.x + limitSideMovement;

        OnBrakeHoldAction = () => Braking(true);
        OnBrakeLeaveAction = () => Braking(false);
        OnBoostHoldAction = () => Boosting(true);
        OnBoostLeaveAction = () => Boosting(false);
        OnClickWheelieHoldAction = WheeliePressed;
        OnClickWheelieLeaveAction = WheelieLeft;
        OnClickHornAction = Horn;

        speed = forwardSpeed;
        tiltAmount = 1 / maxTiltAmount;
        damageMultiplier = boostedSpeed / maxHealth;
        health = maxHealth;
        wheelieFillMultiplier = 1 / timeToFillWheelie;
        Input.gyro.enabled = true;

        cameraController.SetAngleMultiplier(maxTiltAmount);

        bikeHandleTransform.rotation = Quaternion.identity;

        smoothAcceleration = Input.acceleration;
    }

    private void Update()
    {
        if (canCarMove)
        {
            AdjustSpeed();
            HandleSteeringAngle();
            HandleMovement();

            CheckWheelieCoolDown();

            cameraController.UpdateCamera();
            cameraController.AdjustAngle(directionX, rotationSensi, isWheelie);
        }
    }

    private void AdjustSpeed()
    {
        if(isWheelie)
        {
            speed = Mathf.Clamp(speed + (acceleratorOnWheelie * Time.deltaTime), brakeSpeed, wheelieSpeed);
        }
        if (isBoosting)
        {
            speed = Mathf.Clamp(speed + (accelerator * Time.deltaTime), brakeSpeed, boostedSpeed);
        }
        else if (isBraking)
        {
            speed = Mathf.Clamp(speed - (deAccelerator * Time.deltaTime), brakeSpeed, boostedSpeed);
        }
        else
        {
            if (speed < forwardSpeed)
            {
                speed = Mathf.Clamp(speed + (accelerator * Time.deltaTime), brakeSpeed, forwardSpeed);
            }
            else if (speed > forwardSpeed)
            {
                speed = Mathf.Clamp(speed - (deAccelerator * Time.deltaTime), forwardSpeed, boostedSpeed);
            }
        }
    }

    private void HandleMovement()
    {
        //transform.Translate((Vector3.forward + new Vector3(Input.GetAxis("Horizontal"), 0, 0)) * speed * Time.deltaTime);

        direction = direction + ((Vector3.forward + new Vector3((directionX * horizontalMovementSpeed), 0, 0)) * speed * Time.deltaTime);
        if ((direction.x > limitSideMovement || direction.x < -limitSideMovement) && speed > 15)
        {
            canCarMove = false;
            CarAccident();
        }
        else
        {
            direction.x = Mathf.Clamp(direction.x, -limitSideMovement, limitSideMovement);
        }
        transform.position = direction;
    }

    private void HandleSteeringAngle()
    {
        Vector3 rawAcceleration = Input.acceleration;
        if (!useGyro)
        {
            rawAcceleration = new Vector3(Input.GetAxis("Horizontal"), 0, 0);
        }

        smoothAcceleration = Vector3.Lerp(smoothAcceleration, rawAcceleration, smoothingFactor);
        directionX = smoothAcceleration.x;

        if (Mathf.Abs(directionX) < deadZoneThreshold)
        {
            directionX = 0;
        }

        directionX = Mathf.Clamp(directionX, -maxTiltAmount, maxTiltAmount);
        tilt = directionX * tiltAmount;

        //Debug.LogError(smoothAcceleration.x);

        //tilt = Mathf.Clamp(tilt * turnSpeed, -maxSteerAngle, maxSteerAngle);

        tilt = tilt * maxSteerAngle;

        bikeHandleTransform.rotation = Quaternion.Lerp(bikeHandleTransform.rotation, new Quaternion(bikeHandleTransform.rotation.x, tilt , bikeHandleTransform.rotation.z, bikeHandleTransform.rotation.w), rotationSensi * Time.deltaTime);
    }

    private void Braking(bool brake)
    {
        isBraking = brake;
    }

    private void Boosting(bool boost)
    {
        isBoosting = boost;
    }

    private void CheckWheelieCoolDown()
    {
        if(!isWheelie)
        {
            if(wheelieCoolDown < timeToFillWheelie)
            {
                wheelieCoolDown += wheelieFillSpeed * Time.deltaTime;

                wheelieFillImage.fillAmount = wheelieCoolDown * wheelieFillMultiplier;
            }
        }
        else 
        {
            if (wheelieCoolDown > 0)
            {
                wheelieCoolDown -= Time.deltaTime;

                wheelieFillImage.fillAmount = wheelieCoolDown * wheelieFillMultiplier;
            }
            else
            {
                WheelieLeft();
            }
        }
    }

    private void WheeliePressed()
    {
        if (wheelieCoolDown >= timeToFillWheelie)
        {
            isWheelie = true;
            if (wheelieRoutine != null)
            {
                StopCoroutine(wheelieRoutine);
            }
            wheelieRoutine = StartCoroutine(WheeliePressedAsync());
        }
    }

    private void WheelieLeft()
    {
        isWheelie = false;
        if (wheelieRoutine != null)
        {
            StopCoroutine(wheelieRoutine);
        }
        wheelieRoutine = StartCoroutine(WheeliePressedLeft());
    }

    private IEnumerator WheeliePressedAsync()
    {
        Quaternion angle = Quaternion.Euler(-30f, 0, 0);
        while (true)
        {
            if (bikeMesh.eulerAngles.x > angle.x)
                bikeMesh.rotation = Quaternion.Lerp(bikeMesh.rotation, angle, 10f * Time.deltaTime);

            if (bikeMesh.position.y < 0.5f)
            {
                bikeMesh.position = Vector3.Lerp(bikeMesh.position, new Vector3(bikeMesh.position.x, 0.5f, bikeMesh.position.z), 10f * Time.deltaTime);
            }

            if (bikeMesh.eulerAngles.x > angle.x && bikeMesh.position.y > 0.5f)
            {
                bikeMesh.rotation = Quaternion.Euler(-30, 0, 0);
                bikeMesh.position = new Vector3(bikeMesh.position.x, 0.5f, bikeMesh.position.z);
                break;
            }
            yield return null;
        }
    }

    private IEnumerator WheeliePressedLeft()
    {
        while (true)
        {
            //transform.rotation = Quaternion.Lerp(transform.rotation, Quaternion.identity, 10f * Time.deltaTime);

            //if (transform.eulerAngles.x > Quaternion.identity.x)
            //{
            //    transform.rotation = Quaternion.identity;
            //    break;
            //}

            if (bikeMesh.rotation.x < 0)
                bikeMesh.rotation = Quaternion.Lerp(bikeMesh.rotation, Quaternion.identity, 10f * Time.deltaTime);

            if (bikeMesh.position.y > 0f)
            {
                bikeMesh.position = Vector3.Lerp(bikeMesh.position, new Vector3(bikeMesh.position.x, 0f, bikeMesh.position.z), 10f * Time.deltaTime);
            }

            if (bikeMesh.rotation.x > Quaternion.identity.x && bikeMesh.position.y < 0f)
            {
                bikeMesh.rotation = Quaternion.identity;
                bikeMesh.position = new Vector3(bikeMesh.position.x, 0f, bikeMesh.position.z);
                break;
            }

            yield return null;
        }
    }

    private void Horn()
    {

    }

    private Quaternion ConvertGyroRotation(Quaternion q)
    {
        return new Quaternion(q.x, q.y, -q.z, -q.w);
    }

    private void OnTriggerEnter(Collider collison)
    {
        if (canCarMove)
        {
            health = health - (damageMultiplier * speed);

            if (health <= damageAmount && speed >= maxSpeedForCollison)
            {
                canCarMove = false;
                CarAccident();
            }
            else
            {
                canCarMove = false; //Remove
                CarAccident(); //Remove
                if (health <= 0)
                {
                    canCarMove = false;
                }
            }
        }
    }

    private void CarAccident()
    {
        Vector3[] points = new Vector3[2];
        points[0] = new Vector3(cameraController.cameraTransform.position.x, cameraController.cameraTransform.position.y + 1f, cameraController.cameraTransform.position.z + 2);
        points[1] = new Vector3(cameraController.cameraTransform.position.x, cameraController.cameraTransform.position.y - 1f, cameraController.cameraTransform.position.z + 4);

        StartCoroutine(MoveAnimRoutine(cameraController.cameraTransform, points));
        //StartCoroutine(RotateXAnimRoutine(transform, 300));
    }

    private IEnumerator MoveAnimRoutine(Transform t, Vector3[] destination)
    {
        int count = destination.Length;
        int counter = 0;
        while (true)
        {
            t.position = Vector3.Lerp(t.position, destination[counter], 10 * Time.deltaTime);
            t.Rotate(0.5f, 0, 0);

            if (Vector3.Distance(t.position, destination[counter]) < 0.1f)
            {
                counter += 1;

                if(counter == count)
                {
                    break;
                }
            }

            yield return null;
        }

        yield return null;
    }

    private IEnumerator RotateXAnimRoutine(Transform t, float angle)
    {
        float currentAngle = t.eulerAngles.x;
        while(true)
        {
            currentAngle += 5;

            t.eulerAngles = Vector3.Lerp(t.eulerAngles, new Vector3(currentAngle, t.eulerAngles.y, t.eulerAngles.z), 1);

            if(currentAngle >= angle)
            {
                break;
            }

            yield return null;
        }

        yield return null;
    }
}


```

## CameraController.cs

```csharp
using System;
using System.Data;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using Unity.VisualScripting;
using UnityEngine;

public class CameraController : StudioBehaviour
{
    private GameObject playerModel;

    public Transform bike;
    public Transform cameraTransform;
    public float xAngleOffset;
    public float yAngleOffset;
    public float xOffset;
    public float yOffset;
    public float zOffset;
    public float maxCamAngle;
    public float cameraTurnSpeed;
    public Vector3 offset = Vector3.zero;

    private float angleMultiplier = 1;
    private float xOffsetMultiplier = 1;
    private float yOffsetMultiplier = 1;
    private float tilt = 0;

    private float wheelieAngleOffset = -0.1f;
    private float wheelieZOffset;
    private float wheelieYOffset;
    private float wheelieXOffset;
    private float rotationSensiOnWheelie;

    private void Start()
    {
        playerModel = GetGameObjectVariable("PlayerModel");
        bike = GetGameObjectVariable("Bike").transform;
        xOffset = GetFloatVariable("XOffset");
        yOffset = GetFloatVariable("YOffset");
        zOffset = GetFloatVariable("ZOffset");
        maxCamAngle = GetFloatVariable("MaxCamAngleControl");
        cameraTurnSpeed = GetFloatVariable("CameraTurnSpeed");
        xAngleOffset = GetFloatVariable("XAngleOffset");
        yAngleOffset = GetFloatVariable("YAngleOffset");

        wheelieAngleOffset = GetFloatVariable("WheelieAngleOffset");
        wheelieZOffset = GetFloatVariable("WheelieZOffset");
        wheelieYOffset = GetFloatVariable("WheelieYOffset");
        wheelieXOffset = GetFloatVariable("WheelieXOffset");
        rotationSensiOnWheelie = GetFloatVariable("RotationSensiOnWheelie");

        offset = new Vector3(0, yOffset, zOffset);

        cameraTransform = StudioController.GetMyController().GetControllerCamera().transform;

        playerModel.SetActive(false);

        cameraTransform.rotation = bike.rotation;
        cameraTransform.rotation = new Quaternion(cameraTransform.rotation.x + xAngleOffset, cameraTransform.rotation.y, cameraTransform.rotation.z, cameraTransform.rotation.w); 
    }

    public void SetAngleMultiplier(float maxTurnFactor)
    {
        angleMultiplier = maxCamAngle / maxTurnFactor;
        xOffsetMultiplier = xOffset / maxTurnFactor;
        yOffsetMultiplier = yAngleOffset / maxTurnFactor;
    }

    public void UpdateCamera()
    {
        //return;
        
        // Make the camera follow the bike
        cameraTransform.position = Vector3.Lerp(cameraTransform.position, bike.position + offset, 1f);
        //cameraTransform.rotation = bike.rotation;
    }

    public void AdjustAngle(float angleDiff, float sensi, bool isWheelie)
    {
        float angleX = 0;
        tilt = angleMultiplier * angleDiff;

        //tilt = Mathf.Clamp(tilt * cameraTurnSpeed * Time.deltaTime, -maxCamAngle, maxCamAngle);

        tilt = tilt * maxCamAngle;

        if (isWheelie)
        {
            offset.y = yOffset + (-yOffsetMultiplier * Mathf.Abs(angleDiff)) + wheelieYOffset;

            angleX = wheelieAngleOffset; /*Mathf.Clamp(offset.x + wheelieAngleChangeSpeed, 0, wheelieAngleOffset);*/
            offset.z = wheelieZOffset;
            offset.x = wheelieXOffset;
            sensi = rotationSensiOnWheelie;
        }   
        else
        {
            offset.y = yOffset + (-yOffsetMultiplier * Mathf.Abs(angleDiff));
            angleX = xAngleOffset;
            offset.z = zOffset;
            offset.x = xOffsetMultiplier * angleDiff;
            sensi = rotationSensiOnWheelie;
        }

        //cameraTransform.rotation = new Quaternion(cameraTransform.rotation.x, cameraTransform.rotation.y, tilt, cameraTransform.rotation.w);

        cameraTransform.rotation = Quaternion.Lerp(cameraTransform.rotation,
            new Quaternion(angleX, cameraTransform.rotation.y, tilt, cameraTransform.rotation.w), sensi * Time.deltaTime);
    }
}

```

## UIActionHandler.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class UIActionHandler : StudioBehaviour
{
    private int actionType;

    private Image fillImage;

    private void Start()
    {
        actionType = GetIntVariable("ActionType");

        var UI = GetTemplate(typeof(EditUITemplate)) as EditUITemplate;
        var instantiatedUI = UI.GetInstantiatedUI;
        GameObject button = StudioExtensions.FindDeepChild(instantiatedUI.transform, "ButtonAction").gameObject;

        if(actionType == 3)
        {
            fillImage = StudioExtensions.FindDeepChild(instantiatedUI.transform, "fill").GetComponent(typeof(Image)) as Image;
            BikeController.wheelieFillImage = fillImage;
            fillImage.fillAmount = 0;
        }

        EventTrigger eventTrigger = button.AddComponent(typeof(EventTrigger)) as EventTrigger;

        EventTrigger.Entry entryDown = new EventTrigger.Entry();
        entryDown.eventID = EventTriggerType.PointerDown;
        entryDown.callback.AddListener(OnButtonDown);
        eventTrigger.triggers.Add(entryDown);

        EventTrigger.Entry entryUp = new EventTrigger.Entry();
        entryUp.eventID = EventTriggerType.PointerUp;
        entryUp.callback.AddListener(OnButtonUp);
        eventTrigger.triggers.Add(entryUp);
        /*
        if (actionType == 1)
        {
            EventTrigger.Entry entryDown = new EventTrigger.Entry();
            entryDown.eventID = EventTriggerType.PointerDown;
            entryDown.callback.AddListener(x => BikeController.OnBoostAction(1));
            eventTrigger.triggers.Add(entryDown);

            EventTrigger.Entry entryUp = new EventTrigger.Entry();
            entryUp.eventID = EventTriggerType.PointerUp;
            entryUp.callback.AddListener(x => BikeController.OnBoostAction(0));
            eventTrigger.triggers.Add(entryUp);
        }
        else if (actionType == 2)
        {
            EventTrigger.Entry entryDown = new EventTrigger.Entry();
            entryDown.eventID = EventTriggerType.PointerDown;
            entryDown.callback.AddListener(x => BikeController.OnBrakeAction(1));
            eventTrigger.triggers.Add(entryDown);

            EventTrigger.Entry entryUp = new EventTrigger.Entry();
            entryUp.eventID = EventTriggerType.PointerUp;
            entryUp.callback.AddListener(x => BikeController.OnBrakeAction(0));
            eventTrigger.triggers.Add(entryUp);
        }*/
    }

    public void OnButtonDown(BaseEventData baseEventData)
    {
        if (actionType == 1)
        {
            BikeController.OnBoostHoldAction?.Invoke();
        }
        else if (actionType == 2)
        {
            BikeController.OnBrakeHoldAction?.Invoke();
        }
        else if (actionType == 3)
        {
            BikeController.OnClickWheelieHoldAction?.Invoke();
        }
        else if (actionType == 4)
        {
            BikeController.OnClickHornAction?.Invoke();
        }
    }

    public void OnButtonUp(BaseEventData baseEventData)
    {
        if (actionType == 1)
        {
            BikeController.OnBoostLeaveAction?.Invoke();
        }
        else if(actionType == 2)
        {
            BikeController.OnBrakeLeaveAction?.Invoke();
        }
        else if (actionType == 3)
        {
            BikeController.OnClickWheelieLeaveAction?.Invoke();
        }
    }
}


```
