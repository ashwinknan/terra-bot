# StudioLeaderboard

## Type
Functions

StudioLeaderboard class can you help you implement Terra’s leaderboard mechanic on the Terra Client app

### **Studio Leaderboard**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| Method | Set | Sets a leaderboard entry with a unique key and a float value. Logs and displays a toast message on the Studio (non-client app) for the set action. |
| Parameters | a_strKey | Unique key name for the leaderboard entry. |
| Parameters | a_fValue | The float value to associate with the specified key. |
| Method | TryGet | Retrieves the leaderboard value for the current user associated with a specified key. Logs and displays a toast message on the Studio for the get action. |
| Parameters | a_strKey | Unique key name to retrieve the leaderboard value. |
| Parameters | out a_fValue | Output parameter to hold the retrieved float value if found. |
| Returns | bool | Returns true if the leaderboard data was successfully retrieved; otherwise, returns false. |
| Method | ShowLeaderboard | Displays the leaderboard on the client app. On the Studio, it shows a dummy UI with a close button and logs/shows a toast message. |
| Parameters | callbackOnClose | An Action delegate that is invoked when the leaderboard close button is clicked. |