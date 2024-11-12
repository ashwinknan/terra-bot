# Event Functions
## Type
Ruleset


Event functions in T# control the behavior of GameObjects at specific points in their lifecycle. These functions allow for precise control over initialization, frame updates, physics interactions, and custom events triggered by broadcasts. Below is an overview of key event functions available in T# and their usage.

### **`Start()`**

Called once at the beginning of a GameObject’s lifecycle, typically used to set initial values, start timers, or establish component references.

```csharp
private void Start()
    {
      // Enter code to dictate what happens at the start of the game

    }
```

### **`Update()`**

Runs on every frame and is used to handle any changes or interactions that should update dynamically.

```csharp
private void Update()
    {
       // Enter code to tell what should happen on each frame
    }
```

### `FixedUpdate()`

Runs at a fixed interval and is designed for physics-based updates to ensure smoother and more accurate simulation. Frame rates may vary, but `FixedUpdate` remains consistent with the physics engine’s update cycle.

The **physics engine** also updates in discrete time steps in a similar way to the frame **rendering**. A separate event function called [FixedUpdate](https://docs.unity3d.com/2018.4/Documentation/ScriptReference/MonoBehaviour.FixedUpdate.html) is called just before each physics update. Since the physics updates and frame updates do not occur with the same frequency, you will get more accurate results from physics code if you place it in the FixedUpdate function rather than Update.

```csharp
void FixedUpdate() {
    Vector3 force = transform.forward * driveForce * Input.GetAxis("Vertical");
    __rigidbody__.AddForce(force);
}
```

### `LateUpdate()`

Called once per frame after all `Update()` and `FixedUpdate()` calls for all objects in the scene, making it useful for camera adjustments or overriding animations

```csharp
void LateUpdate() {
    Camera.main.transform.LookAt(target.transform);
}
```

### **`OnBroadcasted()`**

This runs whenever a broadcasted signal is listened to by the object

Copy

```csharp
// There is an object in the scene that generates the custom broadcast  "signal" is
public override void OnBroadcasted(string x)
    {
    // The code below executes doSomething when it listens to the broadcast 'signal'
        if(String.Equals(x,"signal")){
        doSomething();
        }

    }
```

Also look at creating a custom broadcast through code

## Unsupported Event Functions

In T#, some event functions common to Unity and other environments are not currently supported. These include:

- **`OnEnable`**: Typically called when a GameObject or Component becomes active, allowing initialisation or reset of states whenever an object is enabled. In T#, alternative initialisation might be handled directly in `Start()` or through custom logic.
- **`OnDisable`**: Usually called when a GameObject or Component is disabled, allowing cleanup or state-saving before deactivation. Since `OnDisable` is not available, consider using custom deactivation methods within your logic to manage state or cleanup as needed.
- **`IPointer` Events** (e.g., `IPointerClick`, `IPointerEnter`): These interfaces handle user input events like clicks or mouseovers, often used in UI components. Without these, input handling for UI or interactive elements must be managed through alternative means, such as checking for input conditions within `Update()` or broadcasting custom events.

> Note: In T#, you may need to use custom methods or rely on broadcast signals and manual input checking to mimic these unsupported events.
>