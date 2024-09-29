# Terra Studio PlayerStats Guide
#TerraStudio #GameDevelopment #PlayerStats #LogicTemplates

## Overview
#PlayerStatsOverview #GameMechanics

PlayerStats Logic Templates manage various aspects of player statistics and interactions in the game.

| Logic Template | Description |
|----------------|-------------|
| [Update Score](#update-score) | Updates a specific score group to a new specified value |
| [Reset Score](#reset-score) | Resets the specified score group to zero |
| [Increase Player HP](#increase-player-hp) | Increases the player Health value by the specific amount |
| [Decrease Player HP](#decrease-player-hp) | Decreases the player Health value by a specific amount |
| [Reset Player Health](#reset-player-health) | Resets the player Health value to zero |
| [Level Up](#level-up) | Guides the Level Mapper on how to increase a property's level to the next tier |
| [Update Magnet](#update-magnet) | Changes the magnet range for the player's collection |
| [Stop Player Movement](#stop-player-movement) | Stops or starts the player movements |
| [Change Player Speed](#change-player-speed) | Changes the speed of movement of the player |

## Update Score
#ScoreUpdate #GameProgression #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Update Score allows you to adjust the game score based on specific conditions.

### Adding Update Score Logic Template
1. Go to the Logic Tab
2. Select Update Score under "PlayerStats"
3. Drag and drop it onto the desired asset

### Update Score Parameters

| Parameter | Description |
|-----------|-------------|
| Update When | Trigger for score update |
| Score Group | Score group to be updated |
| Operator | Mathematical operator for score change |
| Update By | Value to change score by |
| Broadcast | Broadcast to send after score update |

### Customization
For further customization, access the T# Wrapper: [UpdateScoreTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#updatescoretemplate)

## Reset Score
#ScoreReset #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Reset Score allows you to set a player's score back to zero.

### Adding Reset Score Logic Template
1. Go to the Logic Tab
2. Select Reset Score under "PlayerStats"
3. Drag and drop it onto the desired asset

### Reset Score Parameters

| Parameter | Description |
|-----------|-------------|
| Update When | Trigger for score reset |
| Score Group | Score group to be reset |
| Broadcast | Broadcast to send after score reset |

### Customization
For further customization, access the T# Wrapper: [ResetScoreTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#resetscoretemplate)

## Increase Player HP
#HealthIncrease #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Increase Player HP boosts the player's health when triggered.

### Adding Increase Player HP Logic Template
1. Go to the Logic Tab
2. Select Increase Player HP under "PlayerStats"
3. Drag and drop it onto the desired asset

### Increase Player HP Parameters

| Parameter | Description |
|-----------|-------------|
| When | Trigger for health increase |
| By Point | Amount to increase health by |
| Play SFX | Sound effect to play on health increase |
| Play VFX | Visual effect to play on health increase |
| Broadcast | Broadcast to send after health increase |

## Decrease Player HP
#HealthDecrease #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Decrease Player HP reduces the player's health when triggered.

### Adding Decrease Player HP Logic Template
1. Go to the Logic Tab
2. Select Decrease Player HP under "PlayerStats"
3. Drag and drop it onto the desired asset

### Decrease Player HP Parameters

| Parameter | Description |
|-----------|-------------|
| When | Trigger for health decrease |
| By Point | Amount to decrease health by |
| Play SFX | Sound effect to play on health decrease |
| Play VFX | Visual effect to play on health decrease |
| Broadcast | Broadcast to send after health decrease |

## Reset Player Health
#HealthReset #PlayerRevival #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Reset Player Health fully restores the player's health when triggered.

### Adding Reset Player Health Logic Template
1. Go to the Logic Tab
2. Select Reset Player Health under "PlayerStats"
3. Drag and drop it onto the desired asset

### Reset Player Health Parameters

| Parameter | Description |
|-----------|-------------|
| When | Trigger for health reset |
| Play SFX | Sound effect to play on health reset |
| Play VFX | Visual effect to play on health reset |
| Broadcast | Broadcast to send after health reset |

## Level Up
#LevelProgression #CharacterGrowth #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Level Up is used to upgrade different in-game assets based on upgrade paths defined in the Level Mapper.

### Adding Level Up Logic Template
1. Go to the Logic Tab
2. Select Level Mapper under "PlayerStats"
3. Drag and drop it onto the desired asset

### Level Up Parameters

| Parameter | Description |
|-----------|-------------|
| Level up when | Trigger for level up |
| Sound Effect on Start | Sound effect to play on level up |
| Visual Effect on Start | Visual effect to play on level up |
| Manager group | Score group for level up decision |
| Broadcast Success | Broadcast to send on successful level up |
| Broadcast Fails | Broadcast to send on failed level up |
| Execute Times | Number of times to execute behavior |

## Update Magnet
#MagnetRange #ItemCollection #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Update Magnet increases the player's magnetic range for collecting items.

### Adding Update Magnet Logic Template
1. Go to the Logic Tab
2. Select Update Magnet under "PlayerStats"
3. Drag and drop it onto the desired asset

### Update Magnet Parameters

| Parameter | Description |
|-----------|-------------|
| Change Magnet When | Trigger for magnet range change |
| Radius | Updated radius for magnet range |
| Play SFX | Sound effect to play on magnet update |
| Play VFX | Visual effect to play on magnet update |
| Broadcast Data | Broadcast to send after magnet update |

### Customization
For further customization, access the T# Wrapper: [ChangeMagnetTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#changemagnettemplate)

## Stop Player Movement
#PlayerMovement #MovementControl #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Stop Player Movement halts the player's motion in the game environment.

### Adding Stop Player Movement Logic Template
1. Go to the Logic Tab
2. Select Stop Player Movement under "PlayerStats"
3. Drag and drop it onto the desired asset

### Stop Player Movement Parameters

| Parameter | Description |
|-----------|-------------|
| Start When | Trigger for stopping player movement |
| Play SFX | Sound effect to play when player stops |
| Play VFX | Visual effect to play when player stops |
| Broadcast | Broadcast to send when player stops |

## Change Player Speed
#PlayerSpeed #MovementModification #PlayerStats #PrebuiltLogic #PrebuiltLogicComponents

Change Player Speed alters the speed of the player's movement.

### Adding Change Player Speed Logic Template
1. Go to the Logic Tab
2. Select Change Player Speed under "PlayerStats"
3. Drag and drop it onto the desired asset

### Change Player Speed Parameters

| Parameter | Description |
|-----------|-------------|
| Change On When | Trigger for speed change |
| Modifier | Type of speed modification |
| Speed | Value to apply to current speed |
| SFX / VFX | Sound and visual effects to play on speed change |
| Broadcast | Broadcast to send after speed change |

### Customization
For further customization, access the T# Wrapper: [ChangePlayerSpeedTemplate](../scripting-custom-logic-components/t-logic-component-template-wrappers.md#changeplayerspeedtemplate)

