# Terra Studio Editor Workflows
#GameDevelopmentWorkflows #TerraStudio #SceneSetup #GameLogic

This guide covers essential workflows for setting up your game scene and adding logic to your game in Terra Studio.

## Setting up the game scene environment
#SceneSetup #EnvironmentDesign #GameWorld

Summary: Learn how to manage assets, SFX, particles, and scenes to create your game environment.

### Asset Management
#AssetManagement #3DModels #GameObjects #SceneOrganization

Asset management is crucial for building your game world. This section covers how to add, manipulate, and organize assets in your scene.

| Asset Action | Steps to Perform Action |
|--------------|--------------------------|
| Adding an Asset | 1. Quick Access Menu > `Asset` tab<br>2. Search for asset in library<br>3. Drag & drop desired asset to scene |
| Selecting an Asset | - Click on asset in scene (yellow highlight appears)<br>- Or: Layers > Select asset by name |
| Deleting an Asset | - Select asset > `Ctrl + Del` or `Cmd + Del`<br>- Or: Layers > Right Click on Asset > `Del` |
| Duplicating an Asset | - Layers > Right Click on Asset > `Duplicate`<br>- Or: Layers > Click Duplicate Icon |
| Renaming an Asset | Layers > Click Edit Icon > Rename asset |
| Making Asset Child of Another | Layers > Right Click and Drag to desired Parent Asset |
| Adding Empty Parent | Layers > Right Click on Asset > `Add Empty Parent` |
| Moving Asset in Layers | Layers > Right Click and Drag to desired location |
| Moving Asset in Scene | Select Asset > Click `Move` Icon > Select Axes > Use mouse |
| Scaling Asset | Select Asset > Click `Scale` Icon > Select Axes > Use mouse |
| Rotating Asset | Select Asset > Click `Rotate` Icon > Select Axes > Use mouse |

To add an asset to your scene:
```
1. Click on the Assets tab in the Quick Access Menu
2. Search for the desired asset
3. Drag and drop the asset into your scene
```

### SFX & Particle Management
#SoundEffects #ParticleEffects #AudioVisualEnhancement #GameAmbience

Sound effects and particles can greatly enhance the ambiance and visual appeal of your game. Here's how to manage them:

| Action | Steps to Perform |
|--------|-------------------|
| Adding SFX | 1. Quick Access Menu > `SFX` tab<br>2. Preview SFX with Play icon<br>3. Add SFX with + button |
| Customizing SFX | 1. Select SFX in `Layers`<br>2. Enable Advanced Mode<br>3. Customize in Inspector Panel |
| Adding VFX | 1. Quick Access Menu > `SFX` tab<br>2. Scroll through particles preview<br>3. Add particle VFX with + button |
| Customizing VFX | 1. Select Particle VFX in `Layers`<br>2. Enable Advanced Mode<br>3. Customize in Inspector Panel |

To add an SFX to your scene:
```
1. Click on the SFX tab in the Quick Access Menu
2. Preview the sound by clicking the Play icon
3. Click the + button to add the SFX to your scene
```

### Scene Management
#SceneManagement #LevelDesign #GameEnvironments

Proper scene management is essential for organizing your game levels and environments. Here's how to manage your scenes:

| Action | Steps to Perform |
|--------|-------------------|
| Adding New Scene | 1. Quick Access Menu > `Scenes` tab<br>2. Click + icon<br>3. Set name and press Enter |
| Loading Scene | 1. Quick Access Menu > `Scenes` tab<br>2. Double-click desired scene |
| Deleting Scene | 1. Quick Access Menu > `Scenes` tab<br>2. Press Delete icon next to scene |
| Setting Default Scene | 1. Load desired scene<br>2. Quick Access Menu > `Scenes` tab<br>3. Right-click current scene > `Set Default` |

To create a new scene:
```
1. Click on the Scenes tab in the Quick Access Menu
2. Click the + icon
3. Enter a name for your new scene and press Enter
```

## Adding Logic to the game
#GameLogic #Scripting #GameMechanics #Interactivity

Summary: Learn how to incorporate game logic through templates, scripts, and object variables.

Adding logic to your game brings it to life, defining how objects interact and respond to player input. Here's how to implement game logic:

| Logic Action | Steps to Perform |
|--------------|-------------------|
| Adding Logic Template | 1. Click asset<br>2. Quick Access Menu > `Logic` tab<br>3. Select Logic Template<br>4. Drag & drop to asset GameObject |
| Creating Script | 1. Quick Access Menu > `Scripts` tab<br>2. Click + button<br>3. Name script<br>4. Press Enter |
| Adding Script to Asset | 1. Click asset GameObject<br>2. Quick Access Menu > `Scripts` tab<br>3. Drag & drop script to asset<br>4. Script appears in Inspector Panel |
| Creating GameObject Variables | 1. Add script to asset<br>2. Use `Object Variables` tab in Inspector Panel<br>3. Fill in fields for String, Float, Int, GameObject |
| Opening/Editing Script | 1. Click Visual Studio Code icon in Debug Panel<br>2. Select script from project folder |

To add a logic template to an asset:
```
1. Select the asset in your scene
2. Click on the Logic tab in the Quick Access Menu
3. Drag and drop the desired logic template onto the asset
```

To create a new script:
```
1. Click on the Scripts tab in the Quick Access Menu
2. Click the + button
3. Enter a name for your new script and press Enter
```

