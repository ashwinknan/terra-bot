# StudioAnalytics

# Type
Functions

### **Studio Analytics**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| **Method** | **SetGameAnalyticsPrefs** | Sets game level analytics using multiple string values. Logs and displays a toast message on the Studio (non-client app) for the set action. |
| **Param** | **levels** | Analytics Variable 1 (game level). |
| **Param** | **value1** | Analytics Variable 2. |
| **Param** | **value2** | Analytics Variable 3. |
| **Param** | **value3** | Analytics Variable 4. |
| **Param** | **value4** | Analytics Variable 5. |
| **Param** | **value5** | Analytics Variable 6. |
| **Method** | **SetPrimarySessionScore** | Sets the primary leaderboard metric for the user's score in the current session. Logs and displays a toast message on the Studio for the set action. |
| **Param** | **a_fScore** | The score that the user achieved in the current session. |
| **Method** | **UpdateFunnelStep** | Updates the funnel step for client analytics. Logs and displays a toast message on the Studio for the update action. |
| **Param** | **a_iStepID** | The index of the funnel step to be updated. |