# Coroutines

## Type
Ruleset

Coroutines are methods that can pause execution temporarily and resume in the following frame, which lets you distribute tasks across multiple frames. This approach is useful for procedural animations or sequential events over time, especially if they don’t need to happen every frame.

It’s important to note that coroutines are not separate threads; they still run on the main thread, so synchronous operations can still block other actions in the app. Use coroutines for managing long asynchronous tasks, but avoid blocking operations to keep performance smooth.

### **Basic Coroutine Example**

To illustrate, consider gradually reducing an object’s opacity until it becomes invisible. Here’s a non-coroutine version that runs within a single frame:

```csharp
void Fade() {
    Color c = renderer.material.color;
    for (float alpha = 1f; alpha >= 0; alpha -= 0.1f) {
        c.a = alpha;
        renderer.material.color = c;
    }
}

```

This approach doesn’t achieve the intended fade effect, as the loop completes in one frame and the object becomes invisible instantly. Instead, you can use a coroutine to spread the fading across frames:

```csharp
IEnumerator Fade() {
    Color c = renderer.material.color;
    for (float alpha = 1f; alpha >= 0; alpha -= 0.1f) {
        c.a = alpha;
        renderer.material.color = c;
        yield return null;
    }
}

```

The `yield return null` line pauses the coroutine and resumes in the next frame, allowing Terra Studio to update the alpha gradually.

### **Starting a Coroutine with a Key Press**

To run this coroutine, call `StartCoroutine(Fade())` in response to a condition, such as a key press:

```csharp
void Update() {
    if (Input.GetKeyDown("f")) {
        StartCoroutine(Fade());
    }
}

```

### **Adding a Time Delay**

You can delay coroutine execution by using `WaitForSeconds`, which pauses the coroutine for a specified time before resuming:

```csharp
IEnumerator Fade() {
    Color c = renderer.material.color;
    for (float alpha = 1f; alpha >= 0; alpha -= 0.1f) {
        c.a = alpha;
        renderer.material.color = c;
        yield return new WaitForSeconds(.1f);
    }
}

```

### **Reducing Update Frequency**

Some tasks, like checking the distance of nearby objects, don’t need to run every frame. For example:

```csharp
bool ProximityCheck() {
    for (int i = 0; i < enemies.Length; i++) {
        if (Vector3.Distance(transform.position, enemies[i].transform.position) < dangerDistance) {
            return true;
        }
    }
    return false;
}

```

Running this in every frame could impact performance with many enemies. Instead, a coroutine can perform this check at intervals:

```csharp
IEnumerator DoCheck() {
    for(;;) {
        if (ProximityCheck()) {
            // Perform some action here
        }
        yield return new WaitForSeconds(.1f);
    }
}

```

### **Limitations: Coroutines in `Start`**

Using `IEnumerator Start()` as a coroutine entry point is not allowed with T#. Instead, define the coroutine in a separate method and call it from `Start()`:

```csharp
void Start() {
    StartCoroutine(MyCoroutine());
}

IEnumerator MyCoroutine() {
    yield return new WaitForSeconds(1);
    // Your code here
}

```

Using coroutines helps manage operations over time without relying solely on the `Update` method, allowing for more controlled and efficient task management.