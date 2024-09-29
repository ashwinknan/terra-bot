# Terra Studio Conditionals Guide
#TerraStudio #GameDevelopment #Conditionals #PrebuiltLogic #PrebuiltLogicComponents

## Overview
#ConditionalsOverview #GameLogic #PrebuiltLogic #PrebuiltLogicComponents

Conditional Logic Templates enable complex decision-making and event triggering in game development, allowing for responsive and dynamic game behaviors.

| Logic Template | Description |
|----------------|-------------|
| [Switch](#switch) | Activates or deactivates behaviors based on associated triggers |
| [OR Gate](#or-gate) | Sends a broadcast signal when any one of the required conditions is met |
| [AND Gate](#and-gate) | Sends a broadcast signal only after all required conditions are met |
| [Tick](#tick) | Generates a broadcast at pre-defined times or intervals |

## Switch
#SwitchLogic #BehaviorControl #PrebuiltLogic #PrebuiltLogicComponents

The Switch logic template regulates asset behaviors by transmitting broadcasts to activate or deactivate them based on specific triggers.

### Adding Switch Logic Template
1. Go to the Logic Tab
2. Select Switch under "Conditionals"
3. Drag and drop onto the desired asset

### Switch Parameters

| Parameter | Description |
|-----------|-------------|
| Switch On | Trigger to turn the switch "on" |
| Sound Effect When On | Sound effect when switch is turned on |
| Visual Effect When On | Visual effect when switch is turned on |
| Broadcast After On | Broadcast sent when switch is turned on |
| Switch Off | Trigger to turn the switch "off" |
| Sound Effect When Off | Sound effect when switch is turned off |
| Visual Effect When Off | Visual effect when switch is turned off |
| Broadcast After Off | Broadcast sent when switch is turned off |

### Customization
For further customization, access the T# Wrapper: [SwitchTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#switchtemplate)

## OR Gate
#ORGate #ConditionalEvents #PrebuiltLogic #PrebuiltLogicComponents

The OR Gate triggers an event when any one of the defined conditions is met, useful for creating flexible event triggers.

### Adding OR Gate Logic Template
1. Go to the Logic Tab
2. Select OR Gate under "Conditionals"
3. Drag and drop onto the desired asset

### OR Gate Parameters

| Parameter | Description |
|-----------|-------------|
| Wait For (Listen for) | Broadcasts that are prerequisites for the operator |
| Broadcast Data | Broadcast sent when any prerequisite is met |

Note: You can directly use conditionals in T# without needing a wrapper for this logic template.

## AND Gate
#ANDGate #MultipleConditions #PrebuiltLogic #PrebuiltLogicComponents

The AND Gate triggers an event only after all specified conditions have been met, useful for creating complex event chains.

### Adding AND Gate Logic Template
1. Go to the Logic Tab
2. Select AND Gate under "Conditionals"
3. Drag and drop onto the desired asset

### AND Gate Parameters

| Parameter | Description |
|-----------|-------------|
| Wait For (Listen for) | Broadcasts that are prerequisites for the operator |
| Broadcast Data | Broadcast sent when all prerequisites are met |

Note: You can directly use conditionals in T# without needing a wrapper for this logic template.

## Tick
#TimerLogic #IntervalEvents #PrebuiltLogic #PrebuiltLogicComponents

The Tick logic template allows for customized timer functionality, including pausing and sending broadcasts at specific intervals.

### Adding Tick Logic Template
1. Go to the Logic Tab
2. Select Tick under "Conditionals"
3. Drag and drop onto the desired asset

### Tick Parameters

| Parameter | Description |
|-----------|-------------|
| Tick When | Start event for the timer |
| Stop When | Broadcast that stops the execution |
| Resume When | Broadcast that resumes the execution |
| Special Broadcasts | Time intervals for generating broadcasts |

### Customization
For further customization, access the T# Wrapper: [TickTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#ticktemplate)

