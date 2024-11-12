# Variables
# Type
Ruleset

When you create a script in the Editor, Terra Studio automatically provides a template script for you to edit, which inherits from the `StudioBehaviour` class. Inheriting from the `StudioBehavior` class means your script can behave like a type of component, and you can attach it to GameObjects like any other component.

When your script inherits from `StudioBehaviour`, you can include properties and values in your script which you can then edit from the Editor Inspector , like you can with any other component.

Currently, in Terra Studio, you have add local variables to the Asset GameObject in the editor interface only.  To add a variable,

1. Add a script to the Asset GameObject
2. The Inspector Panel that appears on the right with show you both the script and the object variables tab.
3. Go to the Object Variables tab. There are four types of custom variables you can create:
    1. String
    2. Int
    3. Float
    4. GameObject
4. Click on the + icon next to the variable you want to add. Each variable needs to have a name and a value.

In Terra Studio, variables have local scope and can only be used in the scripts of the attached GameObject where they are defined.

Here is an example snippet code to use a variable declared in the editor:

```csharp
// The following script is attached to a GameObject where myName is added as an string Object Variable
// Let's say myName is set to 'Terra'
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class MainPlayer : StudioBehaviour
{
    private string myVar; // A strong variable created to access the strong variable created in the editor
    void Start ()
    {
        myVar = GetStringVariable("myName") // // Accesses the string variable 'myName' created in the editor
        Debug.Log("I am alive and my name is " + myVar);
        // The console will output "I am alive and my name is Terra"
        // Note that if myName is not added to the GameObject in the editor, this will throw up an error
    }
}
```