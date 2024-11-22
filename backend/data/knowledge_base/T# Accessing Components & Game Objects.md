# Accessing Components and GameObjects
## Type
Functions

# Accessing Components and Objects in T#

In Terra Studio, manipulating GameObjects and their Component properties through scripts follows a similar workflow to Unity but has some unique syntax considerations, especially around generics and accessing components. This guide outlines how to access, modify, and reference Components in T#.

## Accessing Component Properties

**Components** control the behaviour of **GameObjects** in Terra Studio. In the Inspector, changing a Component property (e.g., the position of a Transform or the colour of a Renderer’s material) will alter the GameObject’s behaviour or appearance. However, using scripts, you can manipulate these properties dynamically over time or in response to player input.

### Getting Component Instances

In T#, accessing Components uses `GetComponent(typeof(ComponentType))` syntax instead of Unity’s generic version. Below are examples of common usage.

### Example 1: Accessing a Rigidbody and Setting Properties

```csharp
void Start()
{
    Rigidbody rb = (Rigidbody)GetComponent(typeof(Rigidbody));
    rb.mass = 10f; // Sets the Rigidbody's mass
}
```

In this example, `GetComponent(typeof(Rigidbody))` retrieves the Rigidbody instance attached to the GameObject, allowing access to its properties.

### Example 2: Calling Functions on a Component

Scripts not only set properties but can also call functions on Components. Here’s an example of applying force:

```csharp
void Start()
{
    Rigidbody rb = (Rigidbody)GetComponent(typeof(Rigidbody));
    rb.AddForce(Vector3.up * 10f); // Applies upward force
}

```

### Accessing Multiple Scripts on the Same GameObject

. For instance, to access a custom script:

```csharp
MyCustomScript customScript = (MyCustomScript)GetComponent(typeof(MyCustomScript));
customScript.CustomFunction();

```

If a requested Component does not exist on the GameObject, `GetComponent` will return `null`, which can cause runtime errors if not handled properly.

## Accessing Terra Studio Templates

Terra Studio provides wrappers to access and customize pre-built logic components.

To access the wrapper, we first declare a variable that helps retrieve the logic template component using the GetTemplate method.

```csharp
//This line retrieves a template of type CollectableTemplate using the GetTemplate method and then casts it to the CollectableTemplate type.
TemplateName template = (GetTemplate(typeof(TemplateName)) as TemplateName);
```

This variable allows you to access and modify the template's properties. We then use the variable to update the properties of the template:

```csharp
//Replace PropertyName with the property you want to change and newValue with the value you want to set.
template.PropertyName = newValue;
```

### **Specific Example**

The code below illustrates how to do this using the CollectableTemplate Wrapper, where we set the `Score` property of the `collectable` is set to `10`.

```csharp
// Example to access the Collectable template wrapper and then set the values of one of its exposed properties
CollectableTemplate collect = (GetTemplate(typeof(CollectableTemplate)) as CollectableTemplate);
collect.Score = 10; // Set the score property to 10
```

## Accessing Other GameObjects

It’s common for scripts to interact with other GameObjects. Terra Studio provides several ways to reference or locate other objects.

### Linking GameObjects with Public Variables

To link a GameObject in the Inspector, declare a `public GameObject` variable in your script. This variable will be visible in the Inspector, where you can drag a specific GameObject onto it:

```csharp
public class Enemy : StudioBehaviour
{
    public GameObject player;

    void Start()
    {
        transform.position = player.transform.position - Vector3.forward * 10f; // Start 10 units behind the player
    }
}

```

### Finding Child GameObjects

When managing multiple related GameObjects (e.g., waypoints or enemies), you can organize them as children under a parent GameObject and access them through the parent’s Transform:

```csharp
using Terra.Studio;

public class WaypointManager : StudioBehaviour
{
    public Transform[] waypoints;

    void Start()
    {
        waypoints = new Transform[transform.childCount];
        int i = 0;

        foreach (Transform t in transform)
        {
            waypoints[i++] = t; // Populate array with child waypoints
        }
    }
}

```

### Locating Specific Child Objects by Name

To find a specific child GameObject, use `transform.Find("ChildName")`. This is particularly useful when a child GameObject (like a weapon) can be added or removed during gameplay:

```csharp
Transform weapon = transform.Find("Weapon"); // Finds the "Weapon" child if it exists

```

This function is helpful for managing modular objects or items that change dynamically in the scene

[Accessing Components and GameObjects Summary](https://www.notion.so/Accessing-Components-and-GameObjects-Summary-12faacb38a9380629cdbd8789c1480fa?pvs=21)