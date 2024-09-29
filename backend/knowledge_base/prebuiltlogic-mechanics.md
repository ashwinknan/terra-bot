# Terra Studio Mechanics Guide
#TerraStudio #GameDevelopment #GameMechanics #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#MechanicsOverview #GameInteractions

Mechanics Logic Templates enable various interactions and behaviors for game objects, enhancing gameplay and player experiences.

| Logic Template | Description |
|----------------|-------------|
| [Collectable](#collectable) | Enables object collection by the player and score updates |
| [Teleport Player](#teleport-player) | Instantly moves the player to a new position |
| [Jump Pad](#jump-pad) | Enhances player's jump upon contact |
| [Carryable](#carryable) | Allows the player to carry an asset |
| [Deposit](#deposit) | Enables transferring carryable assets to storage |
| [Modify Carryable](#modify-carryable) | Adjusts the number of carried items |
| [Kill Player](#kill-player) | Respawns the player at the level start |
| [Hinge Joint](#hinge-joint) | Enables asset rotation around a defined axis |
| [Explosive Force](#explosive-force) | Applies force within a radius |
| [Add Force](#add-force) | Applies physics-based force to an object |
| [Treadmill](#treadmill) | Creates treadmill-like motion on contact |
| [Multi-Point Move](#multi-point-move) | Moves an asset through defined points |
| [Attach Object](#attach-object) | Parents one object to another |

## Collectable
#Collectables #ScoreSystem #PrebuiltLogic #PrebuiltLogicComponents

Collectables are objects that can be gathered by the player to increase score or achieve goals.

### Adding Collectable Logic Template
1. Go to the Logic Tab
2. Select Collectable under "Mechanics"
3. Drag and drop onto the desired asset

### Collectable Parameters

| Parameter | Description |
|-----------|-------------|
| Collect When | Trigger for collection (player touch, click, magnet range, proximity) |
| Sound Effect on Start | Sound played on collection |
| Visual Effect on Start | Visual effect on collection |
| Score Group | Score group for points contribution |
| Update Score By | Points awarded on collection |
| IsMultiLevel | Enable for value upgrade on level up |
| Broadcast On Collection | Broadcast sent on collection |

### Customization
For further customization, access the T# Wrapper: [CollectableTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#collectabletemplate)

## Teleport Player
#PlayerTeleportation #PositionChange #PrebuiltLogic #PrebuiltLogicComponents

Teleport Player instantly moves the player to a specified location.

### Adding Teleport Player Logic Template
1. Go to the Logic Tab
2. Select Teleport Player under "Mechanics"
3. Drag and drop onto the desired asset

### Teleport Player Parameters

| Parameter | Description |
|-----------|-------------|
| Teleport When | Trigger for teleportation |
| Teleport | Coordinates for teleportation destination |
| Loop-able | Enable looping between points |
| Interval | Delay between movements |
| Move By | Movement distance and axis |
| Sound Effect on Start | Sound played on teleportation |
| Visual Effect on Start | Visual effect on teleportation |
| Broadcast | Broadcast sent after teleportation |

### Customization
For further customization, access the T# Wrapper: [TeleportTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#teleporttemplate)

## Jump Pad
#JumpEnhancement #PlayerMovement #PrebuiltLogic #PrebuiltLogicComponents

Jump Pad increases the player's jump height upon contact.

### Adding Jump Pad Logic Template
1. Go to the Logic Tab
2. Select Jump Pad under "Mechanics"
3. Drag and drop onto the desired asset

### Jump Pad Parameters

| Parameter | Description |
|-----------|-------------|
| Play SFX | Sound effect on jump |
| Play VFX | Visual effect on jump |
| Jump Force | Multiplier for jump height |
| Broadcast Data | Broadcast sent on enhanced jump |

### Customization
For further customization, access the T# Wrapper: [JumpPadTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#jumppadtemplate)

## Carryable
#CarryableObjects #PlayerInteraction #PrebuiltLogic #PrebuiltLogicComponents

Carryable allows the player to pick up and carry game assets.

### Adding Carryable Logic Template
1. Go to the Logic Tab
2. Select Carryable under "Mechanics"
3. Drag and drop onto the desired asset

### Carryable Parameters

| Parameter | Description |
|-----------|-------------|
| Group | Category for carryable items |
| Carry on | Trigger for carrying (touch, click, magnet range, proximity) |
| Play SFX | Sound effect when carried |
| Play VFX | Visual effect when carried |
| Size of carriable | Size of the carried object |
| Score Group | Score group for points contribution |
| Lerp | Lerp settings |
| Lerp Time | Lerp duration |
| Score | Points awarded for carrying |
| IsMultiLevel | Enable for value upgrade on level up |
| Broadcast | Broadcast sent when carried |

## Deposit
#ResourceDeposit #AssetTransfer #PrebuiltLogic #PrebuiltLogicComponents

Deposit enables transferring carryable assets to a storage object.

### Adding Deposit Logic Template
1. Go to the Logic Tab
2. Select Deposit under "Mechanics"
3. Drag and drop onto the desired asset

### Deposit Parameters

| Parameter | Description |
|-----------|-------------|
| Deposit when | Trigger for deposit action |
| Take Resource | Asset group serving as currency |
| Persistent | Persistence toggle |
| Play SFX | Sound effect on deposit |
| Play VFX | Visual effect on deposit |
| Lerp | Lerp settings |
| Lerp Time | Lerp duration |
| Cost type | Type of cost for deposit |
| Size of carriable | Size of deposited object |
| Score Group | Score group for points contribution |
| Deposit rate | Rate of deposit |
| Of Amount | Amount to deposit |
| Score | Points awarded for deposit |
| IsMultiLevel | Enable for value upgrade on level up |
| limit | Deposit limit |
| Show Progress | Toggle to show deposit progress |
| Is Ascending | Toggle for ascending progress |
| Broadcast | Broadcast sent on deposit |
| Broadcast stack empty | Broadcast when deposit stack is empty |

## Modify Carryable
#CarryableModification #InventoryManagement #PrebuiltLogic #PrebuiltLogicComponents

Modify Carryable adjusts the number of items the player is carrying.

### Adding Modify Carryable Logic Template
1. Go to the Logic Tab
2. Select Modify Carryable under "Mechanics"
3. Drag and drop onto the desired asset

### Modify Carryable Parameters

| Parameter | Description |
|-----------|-------------|
| Modify When | Trigger for modification |
| Play VFX | Visual effect on modification |
| Play SFX | Sound effect on modification |
| Haptics | Haptic feedback settings |
| Modifier Group | Carryable group to modify |
| Execute Always | Toggle for continuous execution |
| Modifier | Type of modification (Add, Subtract, Multiply) |
| Modify By | Amount to modify by |

## Kill Player
#PlayerRespawn #GameMechanics #PrebuiltLogic #PrebuiltLogicComponents

Kill Player respawns the player at the last checkpoint or level start.

### Adding Kill Player Logic Template
1. Go to the Logic Tab
2. Select Kill Player under "Mechanics"
3. Drag and drop onto the desired asset

### Kill Player Parameters

| Parameter | Description |
|-----------|-------------|
| Play SFX | Sound effect on player death |
| Play VFX | Visual effect on player death |
| Broadcast On Respawn | Broadcast sent on player respawn |

### Customization
For further customization, access the T# Wrapper: [KillPlayerTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#killplayertemplate)

## Hinge Joint
#HingeMovement #ObjectRotation #PrebuiltLogic #PrebuiltLogicComponents

Hinge Joint allows an asset to rotate around a defined axis, simulating door-like movement.

### Adding Hinge Joint Logic Template
1. Go to the Logic Tab
2. Select Hinge Joint under "Mechanics"
3. Drag and drop onto the desired asset

### Hinge Joint Parameters

| Parameter | Description |
|-----------|-------------|
| Axis | Axis of rotation |
| Anchor | Anchor point for rotation |
| Can Spin Back | Toggle for reverse rotation |

## Explosive Force
#ExplosionMechanics #ForceApplication #PrebuiltLogic #PrebuiltLogicComponents

Explosive Force applies a sudden force to nearby objects within a specified radius.

### Adding Explosive Force Logic Template
1. Go to the Logic Tab
2. Select Explosive Force under "Mechanics"
3. Drag and drop onto the desired asset

### Explosive Force Parameters

| Parameter | Description |
|-----------|-------------|
| Explode When | Trigger for explosion |
| Force | Magnitude of explosive force |
| Radius | Radius of effect |
| Explode SFX | Sound effect on explosion |
| Explode VFX | Visual effect on explosion |
| Broadcast | Broadcast sent after explosion |

## Add Force
#PhysicsForce #ObjectMovement #PrebuiltLogic #PrebuiltLogicComponents

Add Force applies a physics-based force to an object, allowing it to move according to physics laws.

### Adding Add Force Logic Template
1. Go to the Logic Tab
2. Select Add Force under "Mechanics"
3. Drag and drop onto the desired asset

### Add Force Parameters

| Parameter | Description |
|-----------|-------------|
| Add Force When | Trigger for force application |
| Force | Magnitude and direction of force |
| Repeat Mode | Force repetition settings (Single, Repetitive, Periodic) |
| Period | Time period for periodic force |
| Play SFX | Sound effect on force application |
| Play VFX | Visual effect on force application |
| Broadcast | Broadcast sent after force application |

## Treadmill
#TreadmillMovement #ContinuousMotion #PrebuiltLogic #PrebuiltLogicComponents

Treadmill simulates a moving surface, affecting objects or the player upon contact.

### Adding Treadmill Logic Template
1. Go to the Logic Tab
2. Select Treadmill under "Mechanics"
3. Drag and drop onto the desired asset

### Treadmill Parameters

| Parameter | Description |
|-----------|-------------|
| Treadmill When | Trigger for treadmill activation |
| Play SFX | Sound effect on treadmill start |
| Play VFX | Visual effect on treadmill start |
| Treading Speed | Speed of treadmill movement |
| Treading Direction | Direction of treadmill movement |
| broadcastData | Broadcast sent on treadmill activation |

## Multi-Point Move
#PathMovement #ObjectTrajectory #PrebuiltLogic #PrebuiltLogicComponents

Multi-Point Move allows an asset to follow a predefined path of multiple points.

### Adding Multi-Point Move Logic Template
1. Go to the Logic Tab
2. Select Multi-Point Move under "Mechanics"
3. Drag and drop onto the desired asset

### Multi-Point Move Parameters

| Parameter | Description |
|-----------|-------------|
| Move On | Trigger for movement start |
| Points | Coordinates of path points |
| Speed | Movement speed |
| Turn To Points | Toggle for object orientation |
| Delay at Point | Pause duration at each point |
| Loop | Toggle for continuous movement |
| Is Curve | Toggle for curved path |
| Interpolate Types | Movement pattern (One Direction, Ping Pong) |
| Broadcast Type & Signal | Broadcast settings and timing |

### Customization
For further customization, access the T# Wrapper: [MoveBetweenPointsTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#movebetweenpointstemplate)

## Attach Object
#ObjectParenting #AssetHierarchy #PrebuiltLogic #PrebuiltLogicComponents

Attach Object parents one object to another, creating a hierarchical relationship.

### Adding Attach Object Logic Template
1. Go to the Logic Tab
2. Select Attach Object under "Mechanics"
3. Drag and drop onto the desired asset

### Attach Object Parameters

| Parameter | Description |
|-----------|-------------|
| AttachOn | Trigger for attachment |
| Attach_To | Target for attachment (Player or GameObject) |
| Attach To | Reference to target GameObject |
| KeepWorldPos | Toggle to maintain world position |
| Offset | Offset between parent and child objects |

