# T# Basics
## Type
Ruleset

## About T#

The behaviour of **GameObjects** is controlled by the **Components** that are attached to them. Although Studio’s pre-built components can be versatile, you will soon find you need to go beyond what they can provide to implement your own gameplay features. Unity allows you to create your own Components using **scripts**. These allow you to trigger game events, modify Component properties over time and respond to player input in any way you like.

Unity supports the T# programming language natively. T# uses the same syntax as the industry-standard language C#+

## **Creating & Using T# Scripts**

You can create and assign your own T# scripts inside the Terra Studio Editor itself. 

### **Creating a script in the Terra Studio Editor:**

1. Click the Scripts Tab in the left panel.
2. To add a new script:
    1.  Click the `+` icon
    2. Enter a name and press Enter
3.  Double-click the file to open it. Your script will compile and be ready.
4. The Visual Studio Code IDE will open all the scripts in the project
5. Locate your script in the Scripts Directory.
6. You can now edit the default code to achieve your desired game logic

## Anatomy of a Script File

When you double-click a script in Terra Studio, it will be opened in a text editor. By default, Terra Studio will use VS Code Editor:

The initial contents of the script file will look something like this:

```csharp
using System;
using System.Collections;
using Terra.Studio;
using Terra.Studio.Exposed;
using Terra.Studio.Exposed.Layers;
using UnityEngine;

public class MyFirstScript : StudioBehaviour
{
   //Use this for initialization
    private void Start()
    {
       
    }

    // Update is called once per frame
    private void Update()
    {
       
    }

    // Use this for listening to a broadcast
    public override void OnBroadcasted(string x)
    {
        
    }
}
```

A script makes its connection with the internal workings of Terra Studio by implementing a class which derives from the built-in class called `StudioBehavior`. 

Unlike Unity, Terra Studio uses `StudioBehavior` and not `MonoBehavior` 

The main things to note, however, are the three default functions defined inside the class. All the event functions you can use are elaborated here 

### Adding your Script to an Asset

A script only defines a blueprint for a Component and so none of its code will be activated until an instance of the script is attached to a GameObject. To enable this, attach a script to an asset. Here's how you can do it:

1. Select the asset to add the script.
2. Drag and drop the Script onto the asset.
3. Enable Advanced Mode. The Inspector Panel appears on the right.
4. Go to the Studio Machine tab in the Inspector panel. The added script will be selected by default.
5. You can change the script using the dropdown list containing all scripts in the project.