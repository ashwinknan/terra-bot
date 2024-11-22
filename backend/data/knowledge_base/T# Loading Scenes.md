# Loading Scenes

## Type
Functions

### **Load Scene**

The Load Scene logic template enables you to transition from one game environment (scene)  to another, such as progressing from one level to the next or exploring a new area.

To add the Load Scene logic template, follow these steps:

1. Go to the Logic Tab.
2. Select Load Scene under the header "Game".
3. Drag and drop it onto the desired asset.

You can customize the below-mentioned parameters according to your requirements:

| Parameter | Description |
| --- | --- |
| `Load Scene When` | Choose from this dropdown when to transition to a different scene:
• **Broadcast Listened**: After the object receives a broadcast message.
• **Player Touch**: When the player touches the object.
• **Other Object Touch**: When another object touches the object.
• **Clicked**: When you click on the object. |
| `Scenes to Load` | Click the + button to choose the next scene to load when the trigger condition is met. It displays a list of all available scenes in the game. |
| `Can Repeat Previous Level` | Toggle that specifies whether the player can repeat the previous level |

While there is no pre-built  T# Wrapper available to customize the Load Scene Logic Template you can write your own code in T# to implement this logic from scratch.

### 

| Method | `LoadScene` | Loads the specified scene by name. |
| --- | --- | --- |
| Method | `GetAllScenes` | Returns a list of all scenes. |
| Method | `GetCurrentScene` | Returns the name of the current scene. |

```csharp

public class UtilityFunctionsExample : StudioBehavior
{
    void ExecuteUtilityFunctions()
    {
        // Load a scene by name
        StudioExtensions.LoadScene("SceneName");

        // Get all scenes. Remember to use TerraList and not List, since List is not supported
        TerraList allScenes = StudioExtensions.GetAllScenes();

        // Get the current scene name
        string currentScene = StudioExtensions.GetCurrentScene();
    }
}
```