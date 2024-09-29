# Terra Studio Actions Guide
#TerraStudio #GameDevelopment #Actions #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#ActionsOverview #GameObjectManipulation

Action Logic Templates provide various ways to manipulate game objects, enabling dynamic and interactive gameplay elements.

| Logic Template | Description |
|----------------|-------------|
| [Destroy](#destroy) | Removes the asset from the scene |
| [Set Position](#set-position) | Changes the asset's position |
| [Advance Instantiate](#advance-instantiate) | Spawns an instance of the player with advanced settings |
| [Grow / Shrink](#grow--shrink) | Increases or decreases the size of the asset |
| [Move](#move) | Moves the asset in a straight line to a new position |
| [Rotate](#rotate) | Rotates the asset about a chosen axis |
| [MoveTo Player](#moveto-player) | Moves the asset towards the player |
| [Rotate Oscillate](#rotate-oscillate) | Oscillates the asset about a specified axis |
| [Basic Instantiate](#basic-instantiate) | Spawns an instance of the player |
| [Bump](#bump) | Causes the asset to bounce back when collided with |

## Destroy
#ObjectDestruction #Actions #PrebuiltLogic #PrebuiltLogicComponents

The Destroy logic template removes assets from the game scene based on specified triggers.

### Adding Destroy Logic Template
1. Go to the Logic Tab
2. Select Destroy under "Action"
3. Drag and drop onto the desired asset

### Destroy Parameters

| Parameter | Description |
|-----------|-------------|
| Destroy When | Trigger for asset destruction |
| Play SFX | Sound effect played on destruction |
| Play VFX | Visual effect displayed on destruction |
| Broadcast Data | Broadcast sent when asset is destroyed |
| Destroy After | Time delay before asset disappears |

### Customization
For further customization, access the T# Wrapper: [DestroyTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#destroytemplate)

## Set Position
#ObjectPositioning #SceneManipulation #Actions #PrebuiltLogic #PrebuiltLogicComponents

Set Position allows you to change an asset's location in the game world.

### Adding Set Position Logic Template
1. Go to the Logic Tab
2. Select Set Position under "Action"
3. Drag and drop onto the desired asset

### Set Position Parameters

| Parameter | Description |
|-----------|-------------|
| Set Position on | Trigger for position change |
| Target | Destination coordinates (X, Y, Z) |
| Play SFX | Sound effect played on position change |
| Play VFX | Visual effect displayed on position change |
| Broadcast Data | Broadcast sent after position change |

### Customization
For further customization, access the T# Wrapper: [SetPositionTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#setpositiontemplate)

## Advance Instantiate
#AdvancedSpawning #DynamicObjectCreation #PrebuiltLogic #PrebuiltLogicComponents

Advance Instantiate allows for more complex spawning of asset instances during runtime.

### Adding Advance Instantiate Logic Template
1. Go to the Logic Tab
2. Select Advance Instantiate under "Action"
3. Drag and drop onto the desired asset

### Advance Instantiate Parameters

| Parameter | Description |
|-----------|-------------|
| Destroy When | Trigger for instance destruction |
| Play SFX | Sound effect played on instantiation |
| Play VFX | Visual effect displayed on instantiation |
| Broadcast Data | Broadcast sent on instantiation |
| Destroy After | Time delay before instance disappears |

## Grow / Shrink
#ObjectScaling #SizeManipulation #Actions #PrebuiltLogic #PrebuiltLogicComponents

Grow / Shrink allows you to dynamically change the size of an object.

### Adding Grow/Shrink Logic Template
1. Go to the Logic Tab
2. Select Grow/Shrink under "Action"
3. Drag and drop onto the desired asset

### Grow / Shrink Parameters

| Parameter | Description |
|-----------|-------------|
| Grow When | Trigger for size change |
| Scale by | Factor by which to change size |
| Speed | Rate of size change |
| Repeat | Number of times to execute |
| Repeat forever | Toggle for infinite repetition |
| Pause for | Duration between repetitions |
| Repeat type | Motion type (Ping Pong or Same Direction) |
| Broadcast | Broadcast sent after size change |
| Sound Effect on Start | Sound played at start of size change |
| Visual Effect on Start | Visual effect at start of size change |

### Customization
For further customization, access the T# Wrapper: [GrowTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#growtemplate)

## Move
#ObjectMovement #LinearMotion #Actions #PrebuiltLogic #PrebuiltLogicComponents

Move allows objects to travel in a straight line between two points.

### Adding Move Logic Template
1. Go to the Logic Tab
2. Select Move under "Action"
3. Drag and drop onto the desired asset

### Move Parameters

| Parameter | Description |
|-----------|-------------|
| Move When | Trigger for movement start |
| Speed | Movement speed |
| Loop-able | Toggle for back-and-forth movement |
| Interval | Delay between movements |
| Move By | Distance and direction of movement |
| Sound Effect on Start | Sound played at movement start |
| Visual Effect on Start | Visual effect at movement start |
| Broadcast on End | Broadcast sent when movement ends |
| Stop When | Trigger to stop movement |
| Resume When | Trigger to resume movement |

### Customization
For further customization, access the T# Wrapper: [MoveTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#movetemplate)

## Rotate
#ObjectRotation #AxisRotation #Actions #PrebuiltLogic #PrebuiltLogicComponents

Rotate causes objects to spin around their axis upon a specific trigger.

### Adding Rotate Logic Template
1. Go to the Logic Tab
2. Select Rotate under "Action"
3. Drag and drop onto the desired asset

### Rotate Parameters

| Parameter | Description |
|-----------|-------------|
| Rotate When | Trigger for rotation start |
| Rotation Axis | Axis of rotation (X, Y, Z) |
| Speed | Rotation speed |
| Direction | Clockwise or counterclockwise |
| Sound Effect on Start | Sound played at rotation start |
| Visual Effect on Start | Visual effect at rotation start |
| Stop When | Trigger to stop rotation |
| Restart When | Trigger to restart rotation |

### Customization
For further customization, access the T# Wrapper: [RotateTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#rotatetemplate)

## MoveTo Player
#PlayerTracking #DynamicMovement #PrebuiltLogic #PrebuiltLogicComponents

MoveToPlayer causes objects to move towards the player's position.

### Adding Move To Player Logic Template
1. Go to the Logic Tab
2. Select Move To Player under "Action"
3. Drag and drop onto the desired asset

### MoveTo Player Parameters

| Parameter | Description |
|-----------|-------------|
| MoveToPlayerWhen | Trigger for movement start |
| MoveSpeed | Speed of movement towards player |
| Offset | Distance offset from player |
| Play SFX | Sound effect during movement |
| Play VFX | Visual effect during movement |
| Cancel On | Trigger to stop movement |
| Cancel Type | Behavior on movement stop |
| Broadcast | Broadcast sent on player contact |

### Customization
For further customization, access the T# Wrapper: [MoveToPlayerTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#movetoplayertemplate)

## Rotate Oscillate
#OscillatingRotation #PendulumMotion #PrebuiltLogic #PrebuiltLogicComponents

Rotate Oscillate causes objects to swing back and forth around their axis.

### Adding Rotate Oscillate Logic Template
1. Go to the Logic Tab
2. Select Rotate Oscillate under "Action"
3. Drag and drop onto the desired asset

### Rotate Oscillate Parameters

| Parameter | Description |
|-----------|-------------|
| Rotate On | Trigger for oscillation start |
| Axis | Axis of oscillation (X, Y, Z) |
| Speed | Oscillation speed |
| Degrees | Angle of oscillation |
| Direction | Initial direction of oscillation |
| Repeat | Number of oscillations |
| Repeat Forever | Toggle for infinite oscillation |
| Sound Effect on Start | Sound played at oscillation start |
| Visual Effect on Start | Visual effect at oscillation start |
| Broadcast | Broadcast sent on oscillation end |
| Stop On | Trigger to stop oscillation |
| Restart On | Trigger to restart oscillation |

### Customization
For further customization, access the T# Wrapper: [RotateOscillateTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#rotateoscillatetemplate)

## Basic Instantiate
#ObjectSpawning #DynamicCreation #PrebuiltLogic #PrebuiltLogicComponents

Basic Instantiate allows for the spawning of identical objects at various locations during gameplay.

### Adding Basic Instantiate Logic Template
1. Go to the Logic Tab
2. Select Basic Instantiate under "Action"
3. Drag and drop onto the desired asset

### Basic Instantiate Parameters

| Parameter | Description |
|-----------|-------------|
| Instantiate On | Trigger for object spawning |
| Repeat On Event | Toggle for single spawn |
| No of instance | Number of objects to spawn |
| Position | Spawn location method |
| Randomise | Toggle for random spawn order |
| Play SFX | Sound effect on spawn |
| Play VFX | Visual effect on spawn |
| Broadcast | Broadcast sent on spawn |

## Bump
#CollisionResponse #ObjectInteraction #PrebuiltLogic #PrebuiltLogicComponents

Bump causes assets to bounce back when collided with.

### Adding Bump Logic Template
1. Go to the Logic Tab
2. Select Bump under "Action"
3. Drag and drop onto the desired asset

### Bump Parameters

| Parameter | Description |
|-----------|-------------|
| Force | Strength of the bump force |
| Play SFX | Sound effect on bump |
| Play VFX | Visual effect on bump |
| Broadcast Data | Broadcast sent on bump |
| Type | Bump type (Reflect or Deflect) |

