# Terra Studio Scene Management Guide
#TerraStudio #GameDevelopment #SceneManagement #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#SceneManagementOverview #GameLogic

Scene Management Logic Template components are pre-built components aimed to help game developers readily build logic that affect the entire scene.

| Logic Template | Description |
|----------------|-------------|
| [Checkpoint](#checkpoint) | Restarts the game from a specific point if you fail a challenge or lose a life |
| [Update Timer](#update-timer) | Updates the timer to a new specified value |
| [Reset Timer](#reset-timer) | Resets the timer to zero |
| [Load Scene](#load-scene) | Loads a New Scene |
| [Random Level Selector](#random-level-selector) | Loads a random new scene on game start instead of the default scene |

## Checkpoint
#GameCheckpoint #ProgressSaving #PrebuiltLogic #PrebuiltLogicComponents

Checkpoints allow players to restart from a specific point after failing a challenge or losing a life.

### Adding Checkpoint Logic Template
1. Go to the Logic Tab
2. Select Checkpoint under "Game"
3. Drag and drop it onto the desired asset

### Checkpoint Parameters

| Parameter | Description |
|-----------|-------------|
| Play SFX | Sound effect to play at checkpoint |
| Play VFX | Visual effect to play at checkpoint |
| BroadcastData | Broadcast to send when reaching checkpoint |

### Customization
For further customization, access the T# Wrapper: [CheckpointTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#checkpointtemplate)

## Update Timer
#TimerUpdate #GameEvents #PrebuiltLogic #PrebuiltLogicComponents

The Update Timer template is used to handle changes in the game timer based on events.

### Adding Update Timer Logic Template
1. Go to the Logic Tab
2. Select Update Timer under "Game"
3. Drag and drop it onto the desired asset

### Update Timer Parameters

| Parameter | Description |
|-----------|-------------|
| Update When | Trigger for timer update (Player Touches, Other Object Touches, Clicked, Broadcast Listened) |
| Operation | Operator to modify timer (Add, Subtract, Multiply, Divide) |
| Update By | Quantity to modify timer by |
| Sound Effect on Start | Sound effect to play when timer updates |
| Visual Effect on Start | Visual effect to play when timer updates |
| Broadcast on Update | Broadcast to send when timer updates |
| Execute always | Toggle for continuous execution |

### Customization
For further customization, access the T# Wrapper: [UpdateTimerTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#updatetimertemplate)

## Reset Timer
#TimerReset #GameMechanics #PrebuiltLogic #PrebuiltLogicComponents

The Reset Timer behavior resets the game timer to its initial value.

### Adding Reset Timer Logic Template
1. Go to the Logic Tab
2. Select Reset Timer under "Game"
3. Drag and drop it onto the desired asset

### Reset Timer Parameters

| Parameter | Description |
|-----------|-------------|
| Reset When | Trigger for timer reset (Player Touches, Other Object Touches, Clicked, Broadcast Listened) |
| Broadcast | Broadcast to send when timer resets |

## Load Scene
#SceneLoading #LevelProgression #PrebuiltLogic #PrebuiltLogicComponents

The Load Scene logic template enables transitioning from one game environment to another.

### Adding Load Scene Logic Template
1. Go to the Logic Tab
2. Select Load Scene under "Game"
3. Drag and drop it onto the desired asset

### Load Scene Parameters

| Parameter | Description |
|-----------|-------------|
| Load Scene When | Trigger for scene loading |
| Scenes to Load | Select next scene to load |
| Can Repeat Previous Level | Toggle for repeating previous level |

## Random Level Selector
#RandomLevels #GameVariety #PrebuiltLogic #PrebuiltLogicComponents

The Random Level Selector Logic Template allows random loading of a scene from a predefined list.

### Adding Random Level Selector Logic Template
1. Go to the Logic Tab
2. Select Random Level Selector
3. Drag and drop it onto the desired asset

### Random Level Selector Parameters

| Parameter | Description |
|-----------|-------------|
| When | Trigger for random level selection (On Game Start, On Broadcast Listened) |
| Scenes | Selection of scenes to randomly choose from |

