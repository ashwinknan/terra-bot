# Terra Studio Effects Guide
#TerraStudio #GameDevelopment #VisualEffects #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#EffectsOverview #GameFeedback

Effects Logic Templates enhance game aesthetics and player feedback through visual and interactive elements.

| Logic Template | Description |
|----------------|-------------|
| [Stop Rotate](#stop-rotate) | Halts rotation of an object |
| [ShowUI](#showui) | Displays UI elements on screen |
| [Stop Animation](#stop-animation) | Stops ongoing animations |
| [Play Player's Animation](#play-players-animation) | Triggers player character animations |

## Stop Rotate
#RotationControl #ObjectBehavior #PrebuiltLogic #PrebuiltLogicComponents

Stop Rotate allows you to halt the rotation of any object based on specified triggers.

### Adding Stop Rotate Logic Template
1. Select the target asset
2. In the Inspector panel, click on Add Behavior
3. Choose Stop Rotate from the list

### Stop Rotate Parameters

| Parameter | Description |
|-----------|-------------|
| StopWhen | Trigger to stop rotation (broadcast, object touch, click) |
| Broadcast Data | Broadcast sent when rotation stops |
| Play SFX | Sound effect played when rotation stops |
| Play VFX | Visual effect displayed when rotation stops |

## ShowUI
#UserInterface #UIDisplay #PrebuiltLogic #PrebuiltLogicComponents #GameUI

ShowUI allows creators to display UI elements on screen in response to game events or player interactions.

### Adding ShowUI Logic Template
1. Go to the Logic Tab
2. Select Show UI Animation under "Effects"
3. Drag and drop onto the desired asset

### ShowUI Parameters

| Parameter | Description |
|-----------|-------------|
| Show On | Trigger for UI display |
| Animation | Animation type for UI appearance |
| Screen Position | Position of UI element on screen |
| UI Template | Pre-defined UI layout selection |
| Animation Duration | Duration of UI animation in seconds |
| Show for | Duration of UI display |
| Broadcast Data | Broadcast sent when UI is displayed |

## Stop Animation
#AnimationControl #ObjectBehavior #PrebuiltLogic #PrebuiltLogicComponents

Stop Animation halts the current animation of an object when triggered.

### Adding Stop Animation Logic Template
1. Go to the Logic Tab
2. Select Stop Animation under "Effects"
3. Drag and drop onto the desired asset

### Stop Animation Parameters

| Parameter | Description |
|-----------|-------------|
| Stop When | Trigger to stop animation |
| Broadcast | Broadcast sent when animation stops |

## Play Player's Animation
#PlayerAnimation #CharacterMovement #PrebuiltLogic #PrebuiltLogicComponents

Play Player's Animation activates predefined player animations based on specified triggers.

### Adding Play Player's Animation Logic Template
1. Go to the Logic Tab
2. Select Play Player's Animation under "Effects"
3. Drag and drop onto the desired asset

### Play Player's Animation Parameters

| Parameter | Description |
|-----------|-------------|
| Play On | Trigger to start player animation |
| Broadcast | Broadcast sent when animation starts |
| Animation | Selection of player animation to play |
| Reset Automatically | Toggle for automatic animation reset |

### Customization
For further customization, access the T# Wrappers:
- [PlayPlayerAnimationTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#playplayersanimationtemplate)
- [PlayerAnimationControlTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#playeranimationcontroltemplate)

