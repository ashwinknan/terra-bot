# Particles

# Type
Functions

Particles allow you to add moving elements such as fire, beams, aurora lights etc within the game environment.

### **Selecting and Adding Particles**

- **Selecting the Particles:** Start by opening the Quick Access Menu and selecting the Particles option. This will reveal a catalog of available particle effects with their preview suitable for your game's atmosphere and mechanics.
- **Adding Particles :**Click on the effect you want and drag and drop it to the desired location in your game.

### **Customizing Particle Properties**

Once you have added a particle effect to the game, select it from the Layers Panel . You will be shown a list of customizable  properties in the Inspector Panel.

- **Particle VFX When:** Determines the condition under which the particle effect is activated. It can be triggered by a broadcast event or at the game's start.
- **Pause/Un-Pause on:** This dropdown allows you to select specific game events that will pause or resume the Sound Effects (SFX) playback. Options include events like Game Start, Game Lose, and Game Win.
- **Duration:** Sets the duration for which the particle effect will remain visible.
- **Delay Between:** Defines the delay interval between consecutive appearances of the particle effect.
- **Repeat Forever:** This Toggle, If enabled, the particle Visual Effects (VFX) will repeat continuously throughout the game.
- **Repeat Count:** Specifies the number of times the particle VFX will repeat.

You can also choose to customize particle effects through **ParticleEffectTemplate** which manages particle effects within the game, offering flexibility in configuration and event handling.

### **Properties and Methods in ParticleEffectTemplate**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| **Property** | RepeatCount | Get or set the number of times the particle effect repeats. |
| **Property** | PlayForever | Get or set whether continuous playback is enabled. |
| **Property** | Duration | Get or set the duration of the particle effect. |
| **Property** | Delay | Get or set the delay between repetitions of the effect. |
| **Event** | OnParticlePlayingCompleted | Event triggered when the particle effect playback completes. |

### **Usage Example for ParticleEffectTemplate**

Copy

```csharp
public class ParticleEffectController : StudioBehavior
{
    void ConfigureParticleEffect()
    {
        // Accessing the wrapper
        ParticleEffectTemplate template = (GetTemplate(typeof(ParticleEffectTemplate)) as ParticleEffectTemplate);

        // Accessing and setting the RepeatCount property
        int repeatCount = template.RepeatCount; // Getting repeat count
        template.RepeatCount = 3; // Setting repeat count

        // Accessing and setting the PlayForever property
        bool playForever = template.PlayForever; // Getting continuous playback status
        template.PlayForever = true; // Enabling continuous playback

        // Accessing and setting the Duration property
        float duration = template.Duration; // Getting effect duration
        template.Duration = 5.0f; // Setting effect duration

        // Accessing and setting the Delay property
        int delay = template.Delay; // Getting delay value
        template.Delay = 2; // Setting delay between repetitions

        // Subscribing to events
        template.OnParticlePlayingCompleted += HandleParticlePlayingCompleted;

        // Unsubscribing from events
        template.OnParticlePlayingCompleted -= HandleParticlePlayingCompleted;
    }

    void HandleParticlePlayingCompleted()
    {
        // Handle logic when particle effect playback completes here
    }
}
```