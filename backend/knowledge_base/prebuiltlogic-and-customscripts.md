# Adding Logic Components to Asset Game Objects
#LogicComponents #GameInteractivity #TerraStudio

To make our game interactive, we introduce Components, which brings the game to life and changes a simple, static game into an engaging world that reacts to what the player does.

There are two ways to use Components in Terra Studio:

1. Using pre-built logic components
2. Scripting custom logic components

## Using Pre-built Logic Components
#PrebuiltLogic #GameMechanics

### What is a pre-built logic component?
#PrebuiltLogicComponents #GameLogic

A pre-built logic component is always added to an Asset GameObject. It contains pre-built instructions on how the Player and the other GameObjects in the game should behave. Here are some important things to remember about pre-built logic components:

1. A pre-built logic component is always added to an Asset GameObject.
2. Execution of a pre-built logic component is always triggered by a Start Event
3. A pre-built logic component can affect not only the Asset GameObject to which it is attached, but also other GameObjects

### Start Events for Pre-built Logic Components
#EventTriggers #GameEvents

Pre-built logic components in Terra Studio start executing when any of the five events listed below occur:

| Start Event Name | Logic Template Component is executed when |
|------------------|-------------------------------------------|
| Game Start | The game starts |
| Mouse Click | You click the mouse |
| Player Touch / Player Collide | The Player touches or collides with the Asset's collider. |
| Other Object Touch | The other Asset's collider touches the collider of the asset to which the Logic Template is attached |
| Broadcast Listened | A specified game signal is generated in the game. |

### How to add Pre-built Logic Components
#AddingComponents #PrebuiltLogic #GameDesign

To add a pre-built logic component to an asset and customise it, follow these steps:

1. Select the Asset GameObject in the scene editor or through the `Layers` Panel.
2. Click the `Logic` tab in the Quick Access Menu on the left
3. You'll see a Logic Selector with all the possible logic templates 
4. Choose the logic template you want and drag and drop into the Asset
5. The logic component has been added to the asset game object. 
6. You can configure the logic component's properties by selecting the Advanced Mode toggle button and editing the various accessible fields.
7. Once you make changes, click the `Save` button in the main toolbar. 

These components can either be executed simultaneously (in parallel) or in a sequence (one after the other). The key to controlling this execution order lies in using Broadcasts.

### List of Available Pre-built Logic Components
#PrebuiltLogicComponents #GameFunctionality

Terra Studio has a wide selection of pre-built logic components for you to choose from. A pre-built logic component can be added to any Asset GameObject and configured to elicit the interactivity you want in the game. The table below shows a list of pre-built logic components and a short description of what they do. A detailed description of each pre-built logic component is given in the respective logic component page. 

[All tables for Scene Management, Mechanics, Actions, Conditionals, Triggers, Effects, and PlayerStats are included here]

## Scripting your own component in T#
#CustomScripting #TSharpScripting

Terra Creator Studio enables experienced game developers to implement custom logic using a scripting language called T# (T-Sharp). T# is very similar to Unity's C#, making it easy for Unity developers to learn. The links below provide detailed guidance on writing T-Sharp code:

[Basics of Scripting in T#](../scripting-custom-logic-components/creating-and-using-t-scripts.md)

[Unsupported Functionalities in T#](../scripting-custom-logic-components/unsupported-functionalities-in-t.md) 

## Hybrid Approach - Pre-built Logic Components + Custom Script Components
#HybridApproach #FlexibleGameDesign

Logic Components, including both pre-built and custom script components, are useful for both beginners and experienced developers. For beginners, pre-built logic components reduce the need for extensive coding knowledge. For senior developers, they eliminate the need to write code from scratch for simple game interactions and save time and effort.

The limitation of pre-built logic components is the inflexibility in customizing interactions, as only exposed properties are editable from the editor. We address this by providing wrappers for pre-built logic components, customizable via T-Sharp code. These wrappers expose all editable properties to the developer, allowing for more complex interactions than the editor interface permits.

You can read more about how to access the pre-built logic components through T-Sharp code in the documentation for [Logic Component Template Wrappers](../scripting-custom-logic-components/t-logic-component-template-wrappers.md). 

