# StudioPrefs

## Type
Functions

Studio Prefs class helps you save and retrieve any persistent data you may wish to store in your game, such as Player Level

### **Studio Prefs**

| **Type** | **Name** | **Description** |
| --- | --- | --- |
| Property | PrefPrefix | Retrieves a prefix string to use for PlayerPrefs keys based on the current game name or project ID, allowing project-specific preference storage. |
| Method | DeleteKey | Removes the specified key from PlayerPrefs if it exists; has no effect if the key does not exist. |
| Method | GetFloat | Retrieves the float value associated with the specified key from PlayerPrefs. |
| Method | GetFloat | Retrieves the float value associated with the specified key from PlayerPrefs, or a default value if the key does not exist. |
| Method | GetString | Retrieves the string value associated with the specified key from PlayerPrefs. |
| Method | GetString | Retrieves the string value associated with the specified key from PlayerPrefs, or a default value if the key does not exist. |
| Method | GetInt | Retrieves the integer value associated with the specified key from PlayerPrefs. |
| Method | GetInt | Retrieves the integer value associated with the specified key from PlayerPrefs, or a default value if the key does not exist. |
| Method | HasKey | Checks whether the specified key exists in PlayerPrefs; returns true if it exists, false otherwise. |
| Method | SetFloat | Sets a float value in PlayerPrefs for the specified key, which can later be retrieved using GetFloat. |
| Method | SetInt | Sets an integer value in PlayerPrefs for the specified key, which can later be retrieved using GetInt. |
| Method | SetString | Sets a string value in PlayerPrefs for the specified key, which can later be retrieved using GetString. |