# Terra Studio Triggers Guide
#TerraStudio #GameDevelopment #Triggers #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#TriggersOverview #GameInteractions

Triggers are logic templates that initiate various game interactions. They are essential for creating responsive and interactive game environments.

| Logic Template | Description |
|----------------|-------------|
| [Collide](#collide) | Uses contact of collider of the player as a trigger and allows you to generate a broadcast |
| [Click](#click) | Uses mouse click as a trigger and allows you to generate broadcast |
| [Delay](#delay) | Introduces a delay of a specified time |

## Collide
#CollisionTrigger #BroadcastGeneration #PrebuiltLogic #PrebuiltLogicComponents

The Collide logic template sends a broadcast when an object collides with it or when a different object touches it.

### Adding Collide Logic Template
1. Go to the Logic Tab
2. Select Collide under "Triggers"
3. Drag and drop it onto the desired asset

### Collide Parameters

| Parameter | Description |
|-----------|-------------|
| Start On | Choose collision type: OnPlayerCollide or OtherObjectTouches |
| Play SFX | Sound effect to play on collision |
| Play VFX | Visual effect to play on collision |
| BroadcastData | Broadcast to send on collision |

## Click
#ClickTrigger #InteractiveObjects #PrebuiltLogic #PrebuiltLogicComponents

The Click logic template enables sending a broadcast when an asset is clicked.

### Adding Click Logic Template
1. Go to the Logic Tab
2. Select Click under "Triggers"
3. Drag and drop it onto the desired asset

### Click Parameters

| Parameter | Description |
|-----------|-------------|
| Play SFX | Sound effect to play on click |
| Play VFX | Visual effect to play on click |
| Broadcast Data | Broadcast to send on click |

## Delay
#DelayTrigger #TimedEvents #PrebuiltLogic #PrebuiltLogicComponents

The Delay logic template adds a time gap between broadcasts, creating a delay between events.

### Adding Delay Logic Template
1. Go to the Logic Tab
2. Select Delay under "Triggers"
3. Drag and drop it onto the desired asset

### Delay Parameters

| Parameter | Description |
|-----------|-------------|
| Listen To | Broadcast to listen for before creating delay |
| Delay Time | Duration of the delay in seconds |
| Broadcast | Broadcast to send after the delay |

### Customization
For further customization, access the T# Wrapper: [DelayBroadcastTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#delaybroadcasttemplate)
