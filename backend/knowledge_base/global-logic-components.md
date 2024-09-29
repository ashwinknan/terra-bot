# Adding Global Logic Components
#GlobalLogic #GameSystems #TerraStudio

Global Logic Components affect the overall game and not just individual GameObjects. These components run in the background but significantly influence the entire gameplay experience. All these components are accessible by clicking on the Essentials button in the Quick Access Menu. The Builder Panel then shows a list of all Game systems.

## Game Timer
#GameTimer #GameplayTiming #PrebuiltLogicComponents

The Game Timer component is a critical system that manages time-related aspects within the game. It functions as a timer that integrates with game logic. This component is particularly useful in games involving countdowns or time-limited challenges, ensuring precise control over gameplay duration.

### Adding a Game Timer
#AddingTimer #GameSetup

To add a game timer, follow these steps: 

* Select the joystick icon in the Main Tool bar 
* Click on Game Timer

You can now see the Game Timer's properties in the Inspector Panel on the right. The game timer also shows up on the Essentials Tab in the Quick Access Menu

### Configuring the Game Timer
#TimerConfiguration #GameSettings

You can configure the following properties of the game timer in the Inspector Panel: 

| Parameter | Description |
|-----------|-------------|
| `Duration Input` | Enter the time in seconds for how long the timer should run. |
| `Timer Type` | Choose between counting up towards a target time (Count Up) or counting down from a set time (Count Down). |
| `Generate Broadcast on Completion` | Generate either a Game Win signal, a Game Lose signal, or a Custom Broadcast Signal once the timer is complete. |
| `Advanced` | Configure a broadcast signal based on either a specific time or a repeat interval. |
| `Show UI Toggle` | Choose to display the timer on-screen or keep it running silently in the background. |

### Customizing Game Timer Behavior using T#
#TimerCustomization #TSharpScripting

You can also customize the game timer by accessing its T# wrapper - InGameTimerTemplate This template manages in-game timer functionality. 

#### Properties and Methods in InGameTimerTemplate

| Type | Name | Description |
|------|------|-------------|
| Property | TimerType | Get the type of timer. |
| Property | CurrentTime | Get the current time from the in-game timer handler. |
| Property | IsUIShown | Check if the UI associated with the timer is currently shown. |
| Event | OnTimerUpdated | Event triggered when the timer is updated. |

#### Usage Example for InGameTimerTemplate

```csharp
public class TimerManager : StudioBehavior
{
    void ManageTimer()
    {
        // Accessing the wrapper
        InGameTimerTemplate template = (GetTemplate(typeof(InGameTimerTemplate)) as InGameTimerTemplate);

        // Accessing the TimerType property
        TimerType timerType = template.TimerType; // Getting the type of timer

        // Accessing the CurrentTime property
        float currentTime = template.CurrentTime; // Getting the current time

        // Checking if the UI is shown
        bool isUIShown = template.IsUIShown; // Checking if the UI associated with the timer is currently shown

        // Subscribing to the OnTimerUpdated event
        template.OnTimerUpdated += OnTimerUpdatedHandler; // Subscribe to the event

        // Unsubscribing from the OnTimerUpdated event
        template.OnTimerUpdated -= OnTimerUpdatedHandler; // Unsubscribe from the event
    }

    void OnTimerUpdatedHandler(float updatedTime)
    {
        // Handle timer updated event
    }
}
```

## Score
#ScoreSystem #GameMetrics #PrebuiltLogicComponents

The Score system tracks how players perform in a game, showing their competition level and progress. Every game automatically includes a primary score group called the Main Score_GameScore. This group becomes active when you use certain pre-built logic components to change scores.

### Score Groups
#ScoreGroups #PerformanceTracking

A score group is a system used to track various scores within a game, allowing you to monitor multiple achievements or performance metrics independently. For example, a game might have separate score groups for different objectives, such as collecting different types of items or completing various tasks.

### Creating & Updating Score Groups
#ScoreManagement #GameDesign

You can create a new score group only when you add one of the five mentioned logic components. In the editable properties of the behavior, you'll find a "Score Group" option. Here, you can choose to update the existing "Main Score_GameScore" or create a new custom score group by selecting Custom.

### Configuring Score Groups
#ScoreConfiguration #UISettings

You can further configure Score Groups by selecting Essentials from the Quick Access Menu and clicking on the relevant score group you want to customize. Here are the options available:

* **ShowUI Toggle Button**: Shows the score on the game screen when this is turned on.
* **UI Prefab Dropdown**: This option lets you choose from a dropdown menu the UI templates where ShowUI will display the score. These templates are predetermined.
* **Persistent Toggle**: Allows you to keep the same score group total when moving from one level to the next. If not chosen, the score group starts over at zero with each new level.
* **Save Best Score Toggle**: When selected, this saves the player's highest score.
* **Show Best ScoreUI Toggle**: When you turn on the "Save Best Score" option, it displays your highest score on the game screen.
* **BestScore UI PreFab Dropdown**: This lets you choose the UI templates that should display the highest score in ShowUI.

#### Properties and Methods in GameScoreTemplate

| Type | Name | Description |
|------|------|-------------|
| Property | CurrentScore | Get or set the current score. |
| Property | BestScore | Get or set the best score achieved. |
| Property | IsScoreUIShown | Check if the score UI is currently displayed. |
| Property | IsBestScoreCalculated | Check if the best score calculation is enabled. |
| Event | OnScoreModified | Event triggered when the score is modified. |

## Health
#HealthSystem #PlayerStats #PrebuiltLogicComponents

The Health system is a background system that tracks the player health. There are only three pre-built logic components that can affect player health - the Increase Player HP, the Decrease Player HP and the Reset Player Health components. By default, the player health is set to a value of 100. When the player health becomes zero, the player is respawned to the last checkpoint in the game, unless configured otherwise.

To configure the Health System, click on Essentials in the Quick Access Menu and select PlayerHealth. You can then configure the following properties of the Health system:

* **Auto Heal Rate**: Turn on Auto Heal and choose how fast the Health should go up every second.
* **Generate a Broadcast when Player Health becomes zero**: You can create a broadcast for winning a game, losing a game, or a custom message.

## Game Progress
#GameProgress #ProgressionSystem #PrebuiltLogicComponents

The Game Progress System tracks the player's advancement in the game according to predefined progress points. It provides players with a sense of achievement and progression as they play. Multiple progress points can be added through the inspector panel, allowing for greater customization and flexibility in the game's structure.

To add a game progress system:

1. From the main toolbar at the top of the editor screen, select "GameProgress" to add the game system to the Essentials tab.
2. In the builder menu on the left side of the screen, navigate to the "Essential" tab.
3. Find the "GameProgress" system in the builder panel.
4. Click on "GameProgress" to open the inspector panel.
5. In the inspector panel, you can customize the parameters according to your needs and preferences.

| Parameters | Description |
|------------|-------------|
| Progress start | This parameter helps you define the point the game progress will be tracked. |
| Progress points | List of different milestones in the game |
| Persistent | Game progress can be made persistent by checking the checkbox |
| Broadcast at points | Broadcast can be triggered when player reaches a particular milestone |
| Broadcast On Completion | Broadcast can be triggered when player reaches the final milestone. |

## Level Mapper
#LevelMapper #UpgradeSystem #PrebuiltLogicComponents

The Level Mapper game system is designed for customizing the upgrade paths of objects within a game. This can include example use-cases like weapon evolution, building upgrades, and character progression.

To add Level mapper:

1. From the main toolbar at the top of the editor screen, select "LevelUpgrader" to add the game system to the Essentials tab.
2. In the builder menu on the left side of the screen, navigate to the "Essential" tab.
3. Find the "LevelMapper" system in the builder panel.
4. Click on "LevelMapper" to open the inspector panel.
5. In the inspector panel, you can customize the parameters according to your needs and preferences.

| Parameter | Description |
|-----------|-------------|
| Group | Custom name allows the game to keep track of the variables that helps level up the game. |
| Cost Type | The parameter that helps achieve the next level |
| Resource Tag | This is the parameter whose value will be affected once we achieve level up. |
| Value | Update in the property of the group name after you achieve level upgrade |
| Currency | Cost of upgrading to a new level |

## Customer Manager
#CustomerManager #TycoonGames #PrebuiltLogicComponents

Customer manager is a game system used to spawn and manage the customer. This is a game system mostly used in the tycoon games.

To add this game system, follow these steps:

1. Navigate to the essentials tab from the builder menu.
2. Click on "Customer Manager".
3. In the Inspector panel, you can customize the below-mentioned parameters according to your requirements:

| Parameter | Description |
|-----------|-------------|
| Customer Manager When | This dropdown list allows to specify when new customers will be spawned. It can be triggered either on game start or on any broadcast. |
| Broadcast data | This dropdown can be used to add any broadcast at every customer being spawned. |
| Delay between | This Field can be used to add a delay between spawning of each round of customer. |
| Level | This section is used to adjust the rate at which customers are spawned in progressive manner. you can create multiples levels and define the range of customer spawned for each level. |
| Difficulty | You need to define "X" and "Y' values. the number of customer spawned will lie between these values. once the number of customer spawned reaches the "Max spawn" value, the level will get upgraded and next level block will get executed |
| Max spawn | You can specify here the max number of customer that can be spawned in each level |

## Order Generator
#OrderGenerator #TycoonGameplay #PrebuiltLogicComponents

Order Generator is a game system responsible for generating order for each customer based on the availability of items in the store. This is a game system mostly used in the tycoon games.

To add this game system, follow these steps:

1. Navigate to the essentials tab from the builder menu.
2. Click on "Customer Manager".
3. In the Inspector panel, you can customize the below-mentioned parameters according to your requirements:

| Parameter | Description |
|-----------|-------------|
| Type | This dropdown list is used to specify the type of order. It can either be a storage or a service. |
| Maximum number in an order | This field can be used to specify the maximum number of items that an order can have. |
| Items | |
| Group | |
| Cost | |
| Data | This section is used to adjust the number of item per order at each specific level. you can create multiples levels and define the range of items that each order should contain at any specific level. |
| Difficulty | You need to define "X" and "Y' values. the number of items in the order will lie between these values. once the number of items reaches the "Threshold" value, the level will get upgraded and next level block will get executed |
| Max spawn | You can specify here the max number of items that can be added in order at each level. |

## Path Finder
#PathFinder #AINavigation #PrebuiltLogicComponents

Path finder is a game system that is used to define the area in which the customer can move. This is a game system mostly used in the tycoon games.

To add this game system, follow these steps:

1. Navigate to the essentials tab from the builder menu.
2. Click on "Customer Manager".
3. In the Inspector panel, you can customize the below-mentioned parameters according to your requirements:

| Parameter | Description |
|-----------|-------------|
| Path finder UI initializes when | |
| Lowest point | This coordinate is used to define one of the coordinates of the diagonal of the rectangular area in which the customers can move. |
| Highest point | This coordinate is used to define the other coordinate of the diagonal of the rectangular area in which the customers can move. |
| Navmesh accur | |
| Obstacle avoiding distance offset | This field can be used to define the distance that the player would maintain from the obstacle |
| Minimum height | This field is used to define the minimum height below which any structure in the player's path would be considered as obstacle |
| Maximum height | This field is used to define the maximum height below which any structure in the player's path would be considered as obstacle and player needs to avoid. |
| POI distance offset | This field is used to define the distance that player need to maintain from POI in the game. |
| Broadcast | Choose to enter a broadcast that can be used as a trigger for any other behavior. |

