# Configuring GameObjects
#GameObjectSetup #WorldBuilding #InteractiveElements

Once you have the Player configured, you then proceed to set up your interactive world - using GameObjects. There are three types of GameObjects we typically use to set up the game scene:

* **Asset GameObjects:** 3D elements, items, and structures, that players can see and interact with in the game world.
* **SFX GameObjects:** Auditory elements and sound effects
* **Particle GameObjects:** Visual effects like smoke, fire, and magical effects, adding depth and realism to the game's visual presentation.

Here is how you can set up each of the above blocks in your scene:

## Assets
#AssetGameObjects #3DElements #GameItems

### Viewing and Adding New Assets to the Scene
#AssetLibrary #SceneConstruction

Terra Studio has a thousands of pre-made assets for creators to use directly in their game without having to bother about creating their assets. Here are the steps you need to follow:

* Click on "Asset" in the Quick Access Menu.
* Select the "Library View" in the Asset Panel that shows up. You will be shown a library of all assets and their preview. You can search for your desired asset by
  * Typing Keywords in the Asset Search Bar
  * Filtering Assets by theme or category tags
* Once you find your desired asset, drag and drop it into the game workspace.

Currently you cannot import your own assets in the game. However, in an upcoming release cycle, you'll be able to upload your assets directly into the Terra Studio environment, making it easier than ever to personalise your games and bring your unique visions to life.

### Editing Asset Properties
#AssetCustomization #ObjectProperties

Once an Asset is added to the scene, you can click on it and view a list of its editable properties in the Inspector Panel. You can edit the following properties of the asset:

#### Editing Asset Initial Configuration
#InitialConfiguration #AssetTransformation

You can adjust the initial position, initial rotation and initial scale of the Asset by changing the values manually in the inspector panel or by adjusting the Configuration Gizmo next to the Asset

#### Editing Asset Appearance
#AssetAppearance #MaterialProperties

You can edit the asset's visual appearance by editing its material properties:

* _Color:_ Pick from the color wheel or set RGB values
* _Emission Color_: Pick from the color wheel or set RGB values
* _Texture_: Select from a list of available textures
* _Metallic_: Specify a numerical value between 0 to 1
* _Smoothness:_ Specify a numerical value between 0 to 1
* _Shader_: Select from a list of available shaders
* _Tiling_: Specify the X and Y tiling

#### Specifying Asset Collider
#Colliders #PhysicsInteraction

A Collider defines the physical boundaries of an object for collision detection. Colliders help determine when one object makes contact with another within a virtual space.

For any object in Terra Studio, you select from one of four types of collider shapes from the Inspector Panel dropdown:

* **Capsule:** Wraps the object in a capsule shape. Touching anywhere on the capsule counts as touching the object.
* **Sphere:** Surrounds the object with a spherical barrier. Touching the sphere means you've touched the object.
* **Box:** Encases the object in a box shape. Any contact with the box is like touching the object itself.
* **Mesh:** Follows the exact shape of the object. You have to touch the actual surface of the object to register a touch.

## SFX
#SoundEffects #AudioElements #GameAudio

To infuse your game with more life and interactivity, sound effects (SFX) play a crucial role. Here's how to seamlessly integrate them into your game.

### Selecting and Adding SFX
#SFXLibrary #AudioIntegration

* **Navigate to the Builder Menu:** Start by opening the Quick Access Menu and selecting the `SFX` option. This will reveal a catalog of available sound effects suitable for your game's atmosphere and mechanics.
* **Preview SFX:** Ensure your selected SFX aligns with your vision by using the play button for a quick preview. This step is essential before setting the sound effect in stone.
* **Add Sound Effects:** Spot the `+` icon next to your chosen SFX in the list. Clicking this will automatically add the sound effect into your game's environment.

### Configuring SFX
#SoundConfiguration #AudioProperties

Once an SFX is added, it appears in the Layers panel. Here, you can select it to view all its configurable properties in the Inspector Panel. These are the properties you can change in the panel to get the sound effect you want:

* **SoundFx When:** Decide when the sound effect starts playing, either at the beginning of the game or after a specific event.
* **Pause on/Un-Pause on:** This dropdown helps you specify the game events (e.g., Game Start, Game Lose, Game Win) that will pause or resume the SFX playback.
* **Can Loop:** This toggle option for the sound to play continuously in a loop.
* **AudioPitch:** Alter the sound's pitch.
* **Volume of Sound:** Control the sound intensity at the source.
* **Is 3D Audio:** Toggle this to determine if the sound's properties change with distance, mimicking natural sound behavior. Disabling this makes the sound's volume and pitch uniform regardless of the listener's location relative to the source. Once this is active, you can specify
  * **Max Distance:** This helps you set the furthest distance at which the sound can be heard from its source.
  * **Minimum Distance:** Establishes the closest distance to the source needed to hear the sound, applicable when 3D audio is enabled.

You can also choose to customize sound effects through the SoundFxTemplate T# wrapper which manages sound effects within the game, allowing customization of volume, pitch, 3D audio settings, distance ranges, looping capabilities, and pause/resume events.

#### Properties and Methods in SoundFxTemplate
#SoundFxTemplate #AudioProgramming

| Type     | Name       | Description                                        |
|----------|------------|----------------------------------------------------|
| Property | Volume     | Get or set the volume.                             |
| Property | Pitch      | Get or set the pitch.                              |
| Property | Is3DAudio  | Get or set whether the sound is 3D audio.          |
| Property | MinDistance| Get or set the minimum distance for 3D audio.      |
| Property | MaxDistance| Get or set the maximum distance for 3D audio.      |
| Property | CanLoop    | Get or set whether the sound can loop.             |
| Property | PauseOn    | Get or set the event on which the sound pauses.    |
| Property | ResumeOn   | Get or set the event on which the sound resumes.   |
| Event    | OnPaused   | Event triggered when the sound is paused.          |
| Event    | OnResumed  | Event triggered when the sound is resumed.         |

#### Usage Example for SoundFxTemplate
#SoundFxExample #AudioScripting

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

## Particles
#ParticleEffects #VisualEffects #GameAtmosphere

Particles allow you to add moving elements such as fire, beams, aurora lights etc within the game environment.

### Selecting and Adding Particles
#ParticleLibrary #EffectIntegration

* **Selecting the Particles:** Start by opening the Quick Access Menu and selecting the Particles option. This will reveal a catalog of available particle effects with their preview suitable for your game's atmosphere and mechanics.
* **Adding Particles:** Click on the effect you want and drag and drop it to the desired location in your game.

### Customizing Particle Properties
#ParticleCustomization #EffectProperties

Once you have added a particle effect to the game, select it from the Layers Panel. You will be shown a list of customizable properties in the Inspector Panel.

* **Particle VFX When:** Determines the condition under which the particle effect is activated. It can be triggered by a broadcast event or at the game's start.
* **Pause/Un-Pause on:** This dropdown allows you to select specific game events that will pause or resume the Sound Effects (SFX) playback. Options include events like Game Start, Game Lose, and Game Win.
* **Duration:** Sets the duration for which the particle effect will remain visible.
* **Delay Between:** Defines the delay interval between consecutive appearances of the particle effect.
* **Repeat Forever:** This Toggle, If enabled, the particle Visual Effects (VFX) will repeat continuously throughout the game.
* **Repeat Count:** Specifies the number of times the particle VFX will repeat.

You can also choose to customize particle effects through **ParticleEffectTemplate** which manages particle effects within the game, offering flexibility in configuration and event handling.

#### Properties and Methods in ParticleEffectTemplate
#ParticleEffectTemplate #VisualEffectProgramming

| Type     | Name                      | Description                                                |
|----------|--------------------------|------------------------------------------------------------|
| Property | RepeatCount              | Get or set the number of times the particle effect repeats. |
| Property | PlayForever              | Get or set whether continuous playback is enabled.          |
| Property | Duration                 | Get or set the duration of the particle effect.             |
| Property | Delay                    | Get or set the delay between repetitions of the effect.     |
| Event    | OnParticlePlayingCompleted| Event triggered when the particle effect playback completes.|

#### Usage Example for ParticleEffectTemplate
#ParticleEffectExample #VFXScripting

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

## Game Environment
#EnvironmentSetup #VisualAtmosphere #GameWorld

This feature allows you to modify the visual aspects of the game's environment, providing tools to enhance the aesthetic and mood of your game world. You can alter the following parameters of the skybox by selecting Essentials from the Quick Access Menu and the selecting GlobalRenderSettings in the Quick Access Panel. You will see the following editable parameters in the Inspector Panel.

| Property | Description |
|----------|-------------|
| `Skybox` | Adjusts the game's backdrop to give the illusion of a more expansive space. It's like changing the scenery outside a window to make a room feel bigger. |
| `Bloom`  | Creates a glow effect around bright areas in the game, simulating the way light behaves in the real world. It adds a touch of realism by making lights and reflections seem to spill over their boundaries. |
| `Vignette` | Applies a shading around the screen's edges, drawing the player's focus to the center. This effect can give your game a more dramatic and cinematic feel, as if you're peering through a lens. |
| `Fog`    | Introduces a misty overlay that can be adjusted for depth and density, perfect for setting a mysterious or eerie atmosphere. It's like adding a thin veil over the game world that can make far-off objects seem obscured and distant. |