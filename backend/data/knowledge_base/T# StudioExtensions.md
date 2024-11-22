# StudioExtensions

## Type
Functions

### **StudioExtensions**

This class provides static methods for various utility functions within the Terra Studio environment.

### **Properties and Methods in StudioExtensions**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| Method | `SetCurrentScore` | Sets the current score for a specified group. |
| Method | `GetCurrentScore` | Gets the current score for a specified group. |
| Method | `DestroyObject` | Destroys the specified GameObject. *(Deprecated: Use `StudioBehavior.Destroy()` instead)* |
| Method | `LoadScene` | Loads the specified scene by name. |
| Method | `GetAllScenes` | Returns a list of all scenes. |
| Method | `GetCurrentScene` | Returns the name of the current scene. |
| Method | `GetColorFromHex` | Converts a hex string to a Color. |
| Method | `FindDeepChild` | Finds a child transform by name, searching recursively. |

### **Usage Example**

```csharp
public class UtilityFunctionsExample : StudioBehavior
{
    void ExecuteUtilityFunctions()
    {
        // Set the current score for a group
        StudioExtensions.SetCurrentScore("group1", 100);

        // Get the current score for a group
        int score = StudioExtensions.GetCurrentScore("group1");

        // Destroy a GameObject (deprecated)
        StudioExtensions.DestroyObject(gameObject);

        // Load a scene by name
        StudioExtensions.LoadScene("SceneName");

        // Get all scenes. Remember to use TerraList and not List, since List is not supported
        TerraList allScenes = StudioExtensions.GetAllScenes();

        // Get the current scene name
        string currentScene = StudioExtensions.GetCurrentScene();

        // Convert a hex string to a Color
        Color color = StudioExtensions.GetColorFromHex("#FFFFFF");

        // Find a child transform by name
        Transform child = StudioExtensions.FindDeepChild(parentTransform, "ChildName");
    }
}
```