# Mountain Climb 4x4 - Car Controller Documentation
## Type
EXAMPLE

## Overview
Physics-based 4x4 vehicle controller designed for challenging off-road terrain navigation on mobile platforms.

## Core Systems

### Vehicle Physics
- **Rigid Body Dynamics**:
  - Realistic collision handling
  - Terrain response system
  - Weight distribution simulation

- **Environmental Interaction**:
  - Variable friction coefficients
  - Gravity effects
  - Terrain-specific handling

### Control Interface

#### Basic Controls
- **Acceleration**:
  - Touch-and-hold system
  - Variable power output
  - Terrain-adaptive response

- **Steering**:
  - Virtual joystick system
  - Quick-turn response
  - Adaptive handling

- **Additional Controls**:
  - Brake system
  - Reverse functionality
  - Camera view toggle

### Feedback Systems

#### Visual Feedback
- **HUD Elements**:
  - Speedometer
  - Gear indicator
  - Damage display
  - Status indicators

#### Enhanced Feedback
- **Haptic System**:
  - Acceleration feedback
  - Collision response
  - Braking vibration

- **Effects**:
  - Particle systems
  - Sound design
  - Environmental effects

### Technical Requirements
- Performance optimization
- Device compatibility
- Physics stability
- Collision accuracy

---

# Code Implementation

## CameraController.cs

```csharp
using System;
using System.Collections;
using CMF;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using Unity.VisualScripting;
using UnityEngine;

public class CameraController : StudioBehaviour
{

    private Camera renderCamera;
    private Transform cameraParent;
    private StudioController studioController;

    //Editor References
    private float distance;
    private float height;
    private float heightDamping;
    private float rotationDamping;

    private GameObject followTarget;
    private bool justLookAtTarget;
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        _init();
        _getMainCameraReference();
        _followCar();
    }

    /// <summary>
    /// Initializes the starting variables and references
    /// </summary>
    private void _init(){
        studioController = StudioController.GetMyController();
        distance = GetFloatVariable("Distance");
        height = GetFloatVariable("Height");
        heightDamping = GetFloatVariable("HeightDamping");
        rotationDamping = GetFloatVariable("RotationDamping");

        //Hide the default player mesh
        GameObject player = GetGameObjectVariable("Player");
        player.SetActive(false);

        //Freeze the default player movement
        studioController.GetPlayerData().AllowPlayerMovement(false);

        justLookAtTarget = false;
    }



    /// <summary>
    /// Gets the main camera and its parent references
    /// </summary>
    private void _getMainCameraReference(){
        renderCamera = studioController.GetControllerCamera();
        cameraParent = renderCamera.transform.parent;
    }

    /// <summary>
    /// Set the follow target
    /// </summary>
    private void _followCar(){
        followTarget = GetGameObjectVariable("FollowTarget");
    }


    // Gets called every frame
    private void FixedUpdate()
    {   
        //Make sure that there is a target to follow
        if(followTarget == null)
            return;

        if(!justLookAtTarget)
            _smoothLookAndFollow();
        else
            _lookAtTargetOnly();
    }

    private void _smoothLookAndFollow(){

       // Calculate the desired position based on the car's position and offset
        Vector3 desiredPosition = followTarget.transform.position + followTarget.transform.rotation * new Vector3(0, height, distance);

        // Smoothly move the camera towards the desired position
        renderCamera.transform.position = Vector3.Lerp(renderCamera.transform.position, desiredPosition, heightDamping * Time.fixedDeltaTime);

        // Determine the target rotation to match the car's forward direction
        //Quaternion targetRotation = Quaternion.LookRotation(followTarget.transform.forward);

        // Smoothly rotate the camera towards the target rotation
        //cameraParent.transform.rotation = Quaternion.Slerp(cameraParent.transform.rotation, targetRotation, rotationDamping * Time.fixedDeltaTime);

        // Optional: Align the camera to face the car's forward direction
        renderCamera.transform.LookAt(followTarget.transform);
    }


    private void _lookAtTargetOnly(){
        renderCamera.transform.LookAt(followTarget.transform);
    }


    public override void OnBroadcasted(string x)
    {
        if(x == "CarFlipped")
            _unfollowCar();
    }

    private void _unfollowCar(){
        justLookAtTarget = true;
    }
}


```

## OffRoadVehicleController.cs

```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using Unity.VisualScripting;
using UnityEngine;

public class OffRoadVehicleController : StudioBehaviour
{
    private BoxCollider carBodyCollider;
    private Rigidbody carBodyRB;
    private List<GameObject> carWheels = new List<GameObject>();

    private float flipThresholdAngle = 70f;  // Threshold angle to consider the car flipped
    void Start()
    {
        _initialize();

        _detectWheels();

        _addDrivableWheels();
    }

    /// <summary>
    /// Initialize the basic parameters to make a drivable car
    /// </summary>
    private void _initialize()
    {
        carBodyCollider = gameObject.AddComponent<BoxCollider>();
        carBodyRB = gameObject.AddComponent<Rigidbody>();
        carBodyRB.mass = 1000;
    }

    /// <summary>
    /// Detect all the wheels available in the car
    /// </summary>
    private void _detectWheels()
    {
        for(int i =0; i < transform.childCount; i++)
        {
            Transform meshT = transform.GetChild(i);
            carWheels.Add(meshT.gameObject);
        }
    }


    private void _addDrivableWheels()
    {
        for(int i=0; i < carWheels.Count; i++)
        {
            //Assuming that first two wheels can steer
            GameObject wheel = new GameObject();
            WheelCollider wc = wheel.AddComponent<WheelCollider>();
            
            //Make the newly added wheel as the child of the car
            wheel.transform.SetParent(transform, false);
            wheel.gameObject.name = "DW_" + i.ToString();

            //Position the newly created wheel colliders at the position of their respective wheel mesh
            wheel.transform.position = carWheels[i].transform.position;

            //Set up the wheel parameters
            _setupWheel(wc);

            //Make the wheel mesh as the child of the newly created wheel
            carWheels[i].transform.SetParent(wheel.transform, true);
        }
    }

    /// <summary>
    /// Sets up the wheel collider parameters
    /// </summary>
    /// <param name="wc"></param>
    private void _setupWheel(WheelCollider wc)
    {
        Debug.Log("Setting up wheels");
        wc.center = Vector3.zero;
        wc.mass = 20;
        wc.radius = 0.37f;
        wc.wheelDampingRate = 0.25f;
        wc.suspensionDistance = 0.35f;
        wc.forceAppPointDistance = 0.7774484f;

        //Suspension settings
        JointSpring jS = wc.suspensionSpring;
        jS.spring = 4870.133f;
        jS.damper = 1570.37f;
        jS.targetPosition = 0.5f;
        wc.suspensionSpring = jS;

        //Setup friction
        WheelFrictionCurve friction = wc.forwardFriction;
        friction.extremumSlip = 0.4f;
        friction.extremumValue = 1;
        friction.asymptoteSlip = 0.8f;
        friction.asymptoteValue = 1;
        friction.stiffness = 1;
        wc.forwardFriction = friction;

        WheelFrictionCurve sidewaysFriction = wc.sidewaysFriction;
        sidewaysFriction.extremumSlip = 0.2f;
        sidewaysFriction.extremumValue = 1;
        sidewaysFriction.asymptoteSlip = 0.5f;
        sidewaysFriction.asymptoteValue = 0.75f;
        sidewaysFriction.stiffness = 1;
        wc.sidewaysFriction = sidewaysFriction;
    }

    private void Update(){
        _checkIfFlipped();
    }

    /// <summary>
    /// Checks if the car is flipped or tilted
    /// </summary>
    private void _checkIfFlipped(){
        // Calculate the angle between the car's up vector and the world up vector
        float angle = Vector3.Angle(transform.up, Vector3.up);

        // Check if the angle exceeds the threshold
        if (angle > flipThresholdAngle)
        {
            //Broadcast a signal that has flipped
            Broadcast("CarFlipped");
        }
    }

    /// <summary>
    /// Check if the body of the car is hit by something
    /// </summary>
    /// <param name="other"></param>
    private void OnCollisionEnter(Collision other){
        //This function will be primarily used for situations where we want to track if the car has fallen down
        if(other.gameObject.name == "GroundPlane"){
            Debug.Log("Game Over");
        }
    }
}


```

## ScreenController.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class ScreenController : StudioBehaviour
{
    // Gets called at the start of the lifecycle of the GameObject
    private void Start()
    {
        //Set the orientation of the screen to landscape
        Screen.orientation = ScreenOrientation.LandscapeLeft;
    }
}


```

## Vehicle_UI_Motor_Controls.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class Vehicle_UI_Motor_Controls : StudioBehaviour
{

    private Button ownerButton;
    private EventTrigger buttonEvent;
    // Gets called at the start of the lifecycle of the GameObject

    private void Start()
    {
       _init();
       _setupEventTriggers();
    }


    /// <summary>
    /// Initialize the required variables, basically gets the reference to the button
    /// </summary>
    private void _init(){
        ownerButton = (Button)gameObject.GetComponent(typeof(Button)) as Button;
    }

    /// <summary>
    /// Add dynamic event triggers
    /// </summary>
    private void _setupEventTriggers(){
        //Add event handlers
        buttonEvent = gameObject.AddComponent(typeof(EventTrigger)) as EventTrigger;

        // Create the PointerDown entry
        EventTrigger.Entry pointerDownEntry = new EventTrigger.Entry();
        pointerDownEntry.eventID = EventTriggerType.PointerDown;
        pointerDownEntry.callback.AddListener((data) => { OnButtonPressed(); });
        buttonEvent.triggers.Add(pointerDownEntry);

        // Create the PointerUp entry
        EventTrigger.Entry pointerUpEntry = new EventTrigger.Entry();
        pointerUpEntry.eventID = EventTriggerType.PointerUp;
        pointerUpEntry.callback.AddListener((data) => { OnButtonReleased(); });
        buttonEvent.triggers.Add(pointerUpEntry);
    }

    /// <summary>
    /// Listen to the event triggers
    /// </summary>
    private void OnButtonPressed(){
        string buttonType = GetStringVariable("Button_Type");
        
        switch(buttonType){
            case "ACC":
                Broadcast("CarAccelerate");
                break;

            case "BKD":
                Broadcast("CarReverse");
                break;

            case "BRK":
                Broadcast("CarBrake");
                break;

            default:
                Debug.Log("Unsupported UI Button Type");
                break;
        }
    }

    /// <summary>
    /// Reset the input when the button is released
    /// </summary>
    private void OnButtonReleased(){
        Broadcast("ResetCarInput");
    }
}


```

## Vehicle_UI_SteeringController.cs

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class Vehicle_UI_SteeringController : StudioBehaviour
{
    private Graphic wheel;

    private RectTransform wheelTR;
    private Vector2 centerPoint;

    public float maximumSteeringAngle;
    public float wheelReleasedSpeed;
    public float valueMultiplier;

    private float wheelAngle;
    private float wheelPrevAngle;

    private bool wheelBeingHeld;

    private float m_value;
    public float Value { get { return m_value; } }

    public float Angle { get { return wheelAngle; } }

    private void Start()
    {
        
        _init();
        _addEventListeners();
    }

    /// <summary>
    /// Makes the initial value set up
    /// </summary>
    private void _init(){
        wheel = (Graphic) gameObject.GetComponent(typeof(Graphic)) as Graphic;
        wheelTR = wheel.rectTransform;
        maximumSteeringAngle = 200f;
        wheelReleasedSpeed  = 350f;
        valueMultiplier = 1f;
        wheelAngle = 0f;
        wheelPrevAngle = 0f;
        wheelBeingHeld = false;
    }

    /// <summary>
    /// Adds the event listeners on the steering wheel graphics to make it respond to touches
    /// </summary>
    private void _addEventListeners(){
        // Add an EventTrigger component to the steering wheel if it doesn’t already have one
        EventTrigger trigger = wheelTR.gameObject.AddComponent<EventTrigger>();

        // Add PointerDown event
        EventTrigger.Entry pointerDownEntry = new EventTrigger.Entry();
        pointerDownEntry.eventID = EventTriggerType.PointerDown;
        pointerDownEntry.callback.AddListener((data) => { OnPointerDown((PointerEventData)data); });
        trigger.triggers.Add(pointerDownEntry);

        // Add PointerUp event
        EventTrigger.Entry pointerUpEntry = new EventTrigger.Entry();
        pointerUpEntry.eventID = EventTriggerType.PointerUp;
        pointerUpEntry.callback.AddListener((data) => { OnPointerUp((PointerEventData)data); });
        trigger.triggers.Add(pointerUpEntry);

        // Add Drag event
        EventTrigger.Entry dragEntry = new EventTrigger.Entry();
        dragEntry.eventID = EventTriggerType.Drag;
        dragEntry.callback.AddListener((data) => { OnDrag((PointerEventData)data); });
        trigger.triggers.Add(dragEntry);
    }

    private void Update()
    {
        // If the wheel is released, reset the rotation
        // to initial (zero) rotation by wheelReleasedSpeed degrees per second
        if( !wheelBeingHeld && wheelAngle != 0f )
        {
            float deltaAngle = wheelReleasedSpeed * Time.deltaTime;
            if( Mathf.Abs( deltaAngle ) > Mathf.Abs( wheelAngle ) )
                wheelAngle = 0f;
            else if( wheelAngle > 0f )
                wheelAngle -= deltaAngle;
            else
                wheelAngle += deltaAngle;
        }

        // Rotate the wheel image
        wheelTR.localEulerAngles = new Vector3( 0f, 0f, -wheelAngle );

        m_value = wheelAngle * valueMultiplier / maximumSteeringAngle;
    }

    // Called when the wheel is first touched
    private void OnPointerDown(PointerEventData eventData)
    {
        // Executed when mouse/finger starts touching the steering wheel
        wheelBeingHeld = true;
        centerPoint = RectTransformUtility.WorldToScreenPoint( eventData.pressEventCamera, wheelTR.position);
        wheelPrevAngle = Vector2.Angle( Vector2.up, eventData.position - centerPoint );
        UpdateWheelAngle(eventData.position);
    }

    // Called when the wheel is released
    private void OnPointerUp(PointerEventData eventData)
    {
        wheelBeingHeld = false;
        Broadcast("CurrentCarSteering-0-NA");
    }

    // Called continuously while dragging
    private void OnDrag(PointerEventData eventData)
    {
        if (wheelBeingHeld)
        {
            UpdateWheelAngle(eventData.position);


            if(m_value > 0){
                Broadcast("CurrentCarSteering-" + m_value.ToString() + "-RT");
            }else{
                float tempVal = m_value * -1;
                Broadcast("CurrentCarSteering-" + tempVal.ToString() + "-LT");
            }
            
        }
    }

    // Update the angle of the wheel based on touch position
    private void UpdateWheelAngle(Vector2 touchPosition)
    {
        // Executed when mouse/finger is dragged over the steering wheel
			Vector2 pointerPos = touchPosition;

			float wheelNewAngle = Vector2.Angle( Vector2.up, pointerPos - centerPoint );

			// Do nothing if the pointer is too close to the center of the wheel
			if( ( pointerPos - centerPoint ).sqrMagnitude >= 400f )
			{
				if( pointerPos.x > centerPoint.x )
					wheelAngle += wheelNewAngle - wheelPrevAngle;
				else
					wheelAngle -= wheelNewAngle - wheelPrevAngle;
			}

			// Make sure wheel angle never exceeds maximumSteeringAngle
			wheelAngle = Mathf.Clamp( wheelAngle, -maximumSteeringAngle, maximumSteeringAngle );
			wheelPrevAngle = wheelNewAngle;
    }

    // Retrieve the steering angle for car control, normalized between -1 and 1
    public float GetSteeringAngle()
    {
        return 0f;
    }
}


```

## Wheel.cs

```csharp
using System;
using System.Collections;
using System.Numerics;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class Wheel : StudioBehaviour
{
    private int canSteer;
    private int maxSteering;
    private int maxBrakeTorque;

    private WheelCollider wheelOwner;
    private bool canReceiveInputs;

    private bool uiAcceleration;
    private bool uiBrakes;
    private bool uiReverse;
    private int carDirection;

    private float inputSteering;

    private void Start()
    {
        canReceiveInputs = false;
        maxSteering = GetIntVariable("MaxSteerAngle");
        canSteer = GetIntVariable("CanSteer");
        maxBrakeTorque = GetIntVariable("MaxBrakeTorque");
        resetInputs();
        StartCoroutine(IReferenceWheel());
    }

    /// <summary>
    /// Coroutine to get the intial WheelCollider references of the car
    /// </summary>
    /// <returns></returns>
    IEnumerator IReferenceWheel() {
        yield return new WaitForSeconds(1.5f);
        wheelOwner = transform.GetComponentInParent<WheelCollider>();
        canReceiveInputs = true;
    }

    private void Update()
    {
        if(!canReceiveInputs)
            return;
        _accelerate();
        _steer();
        _brakes();
        _updateVisuals();
    }


    /// <summary>
    /// Makes the car accelerate in the given direction
    /// </summary>
    private void _accelerate()
    {
        if (uiAcceleration == true && canReceiveInputs)
        {
            //wheelOwner.motorTorque = 300 * Input.GetAxis("Vertical") * carDirection;
            wheelOwner.motorTorque = 300 * carDirection;
        }else if(uiReverse == true && canReceiveInputs){
            wheelOwner.motorTorque = 300 * carDirection;
        }else{
            wheelOwner.motorTorque = 0;
        }
    }

    /// <summary>
    /// Makes the car steer left or right based on the given input
    /// </summary>
    private void _steer()
    {
        if (canSteer == 0)
            return;
        float angle = maxSteering * inputSteering;
        wheelOwner.steerAngle = angle;
    }

    /// <summary>
    /// Apply brakes to the car when the input is given
    /// </summary>
    private void _brakes(){
        if(uiBrakes == true)
            wheelOwner.brakeTorque = maxBrakeTorque;
        else
            wheelOwner.brakeTorque = 0;
    }

    /// <summary>
    /// Make the car wheel mesh follow the wheel velocity
    /// </summary>
    private void _updateVisuals()
    {
        // Update visual wheels if any.
        if (canReceiveInputs && wheelOwner.transform.childCount > 0)
        {
            UnityEngine.Quaternion q;
            UnityEngine.Vector3 p;
            wheelOwner.GetWorldPose(out p, out q);

            // Assume that the only child of the wheelcollider is the wheel shape.
            Transform shapeTransform = wheelOwner.transform.GetChild(0);

            shapeTransform.position = p;
            shapeTransform.rotation = q;
        }
    }


    /// <summary>
    /// Responsible for resetting the input state of the car
    /// </summary>
    private void resetInputs(){
        uiAcceleration = false;
        uiBrakes = false;
        uiReverse = false;
        carDirection = -1;
        inputSteering = 0;
    }


    // Listen to broadcasts for Handling UI inputs
    public override void OnBroadcasted(string x)
    {
        _listenToButtonInputBroadcast(x);
        _listenToSteeringInputBroadcast(x);
    }


    private void _listenToButtonInputBroadcast(String x){
        switch(x){
            case "CarAccelerate":
                uiAcceleration = true;
                carDirection = -1;
            break;

            case "CarReverse":
                uiReverse = true;
                carDirection = 1;
            break;

            case "CarBrake":
                uiBrakes = true;
            break;

            case "ResetCarInput":
                resetInputs();
            break;
        }
    }

    private void _listenToSteeringInputBroadcast(String steeringAngle){
        string[] splitVal = steeringAngle.Split("-");
        if(splitVal.Length > 1)
        {
            //Found valid broadcast data
            if(splitVal[2] == "RT")
                inputSteering = float.Parse(splitVal[1]);
            else if(splitVal[2] == "LT")
                inputSteering = float.Parse(splitVal[1]) * -1;
            else
                inputSteering = 0;
        }
    }

}


```
