# Haptics

# **T# Haptics & Extensions**

### **StudioHaptics**

This class provides static methods to play different haptic feedback patterns. It uses the Lofelt Nice Vibrations library to trigger haptic feedback on supported devices.

### **Properties and Methods in StudioHaptics**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| Method | `PlayHapticSelection` | Plays the haptic feedback for selection. |
| Method | `PlayHapticSuccess` | Plays the haptic feedback for success. |
| Method | `PlayHapticWarning` | Plays the haptic feedback for warning. |
| Method | `PlayHapticFailure` | Plays the haptic feedback for failure. |
| Method | `PlayHapticLightImpact` | Plays the haptic feedback for light impact. |
| Method | `PlayHapticMediumImpact` | Plays the haptic feedback for medium impact. |
| Method | `PlayHapticHeavyImpact` | Plays the haptic feedback for heavy impact. |
| Method | `PlayHapticRigidImpact` | Plays the haptic feedback for rigid impact. |
| Method | `PlayHapticSoftImpact` | Plays the haptic feedback for soft impact. |

### **Usage Example**

```csharp
public class HapticFeedbackExample : StudioBehavior
{
    void TriggerHapticFeedback()
    {
        // Play haptic feedback for selection
        StudioHaptics.PlayHapticSelection();

        // Play haptic feedback for success
        StudioHaptics.PlayHapticSuccess();

        // Play haptic feedback for warning
        StudioHaptics.PlayHapticWarning();

        // Play haptic feedback for failure
        StudioHaptics.PlayHapticFailure();

        // Play haptic feedback for light impact
        StudioHaptics.PlayHapticLightImpact();

        // Play haptic feedback for medium impact
        StudioHaptics.PlayHapticMediumImpact();

        // Play haptic feedback for heavy impact
        StudioHaptics.PlayHapticHeavyImpact();

        // Play haptic feedback for rigid impact
        StudioHaptics.PlayHapticRigidImpact();

        // Play haptic feedback for soft impact
        StudioHaptics.PlayHapticSoftImpact();
    }
}
```