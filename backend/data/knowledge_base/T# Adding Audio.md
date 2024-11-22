# Audio

## Type
Functions

## **SFX**

To infuse your game with more life and interactivity, sound effects (SFX) play a crucial role. Here's how to seamlessly integrate them into your game.

### **Selecting and Adding SFX**

- **Navigate to the Builder Menu:** Start by opening the Quick Access Menu and selecting the `SFX` option. This will reveal a catalog of available sound effects suitable for your game's atmosphere and mechanics.
- **Preview SFX:** Ensure your selected SFX aligns with your vision by using the play button for a quick preview. This step is essential before setting the sound effect in stone.
- **Add Sound Effects:** Spot the `+` icon next to your chosen SFX in the list. Clicking this will automatically add the sound effect into your game's environment.

### **Configuring SFX**

Once an SFX is added, it appears in the Layers panel. Here, you can select it to view all its configurable properties in the Inspector Panel. These are the properties you can change in the panel to get the sound effect you want :

- **SoundFx When:** Decide when the sound effect starts playing, either at the beginning of the game or after a specific event.
- **Pause on/Un-Pause on:** This dropdown helps you specify the game events (e.g., Game Start, Game Lose, Game Win) that will pause or resume the SFX playback.
- **Can Loop:** This toggle option for the sound to play continuously in a loop.
- **AudioPitch:** Alter the sound's pitch.
- **Volume of Sound:** Control the sound intensity at the source.
- **Is 3D Audio:** Toggle this to determine if the sound's properties change with distance, mimicking natural sound behavior. Disabling this makes the sound's volume and pitch uniform regardless of the listener's location relative to the source. Once this is active, you can specify
    - **Max Distance:** This helps you set the furthest distance at which the sound can be heard from its source.
    - **Minimum Distance:** Establishes the closest distance to the source needed to hear the sound, applicable when 3D audio is enabled.

You can also choose to customize sound effects through the SoundFxTemplate T# wrapper which manages sound effects within the game, allowing customization of volume, pitch, 3D audio settings, distance ranges, looping capabilities, and pause/resume events.

### **Properties and Methods in SoundFxTemplate**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| **Property** | Volume | Get or set the volume. |
| **Property** | Pitch | Get or set the pitch. |
| **Property** | Is3DAudio | Get or set whether the sound is 3D audio. |
| **Property** | MinDistance | Get or set the minimum distance for 3D audio. |
| **Property** | MaxDistance | Get or set the maximum distance for 3D audio. |
| **Property** | CanLoop | Get or set whether the sound can loop. |
| **Property** | PauseOn | Get or set the event on which the sound pauses. |
| **Property** | ResumeOn | Get or set the event on which the sound resumes. |
| **Event** | OnPaused | Event triggered when the sound is paused. |
| **Event** | OnResumed | Event triggered when the sound is resumed. |

### **Usage Example for SoundFxTemplate**

```csharp
public class SoundManager : StudioBehavior
{
    void ConfigureSound()
    {
        // Accessing the wrapper
        SoundFxTemplate template = (GetTemplate(typeof(SoundFxTemplate)) as SoundFxTemplate);

        // Accessing and setting properties
        float volume = template.Volume; // Getting volume
        template.Volume = 0.5f; // Setting volume

        float pitch = template.Pitch; // Getting pitch
        template.Pitch = 1.0f; // Setting pitch

        bool is3DAudio = template.Is3DAudio; // Checking if 3D audio
        template.Is3DAudio = true; // Enabling 3D audio

        float minDistance = template.MinDistance; // Getting minimum distance
        template.MinDistance = 1.0f; // Setting minimum distance

        float maxDistance = template.MaxDistance; // Getting maximum distance
        template.MaxDistance = 50.0f; // Setting maximum distance

        bool canLoop = template.CanLoop; // Checking if looping
        template.CanLoop = true; // Enabling looping

        string pauseOn = template.PauseOn; // Getting pause event
        template.PauseOn = "PlayerDeath"; // Setting pause event

        string resumeOn = template.ResumeOn; // Getting resume event
        template.ResumeOn = "PlayerRespawn"; // Setting resume event

        // Subscribing to events
        template.OnPaused += OnSoundPaused;
        template.OnResumed += OnSoundResumed;

        // Unsubscribing from events
        template.OnPaused -= OnSoundPaused;
        template.OnResumed -= OnSoundResumed;
    }

    void OnSoundPaused()
    {
        // Your code here
    }

    void OnSoundResumed()
    {
        // Your code here
    }
}
```