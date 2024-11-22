# StudioUser
## Type
Functions

Studio User is a class that can be used to access user information for players playing your game made on Terra Studio on the Terra Client app

### **Studio User Class**

| Type | Name | Description |
| --- | --- | --- |
| Property | m_iTerraCoins | Dummy value of Terra Coins for Studio, set to 0 initially. |
| Method | GetUserName() | Gets the username for the player. |
| Method | GetUserAvatarImage() | Retrieves the avatar image of the player's current model as a Texture2D. |
| Method | GetUserAvatarCinematicImage() | Retrieves the cinematic avatar image of the player's current model as a Texture2D. |
| Method | GetUserAvatarModel() | Retrieves the user's avatar's 3D model as a GameObject. |
| Method | GetUserTerraCoins() | Gets the amount of Terra Coins the user currently has. |
| Method | SpendUserTerraCoins(int a_iTerraCoins) | Spends the specified amount of Terra Coins and returns true if successful, false otherwise. |
| Method | GiveUserTerraCoins(int a_iTerraCoins) | Adds a specified amount of Terra Coins to the user's balance. |
| Method | OnItemPurchased(string a_strItemID) | Notifies the client app or Studio when a user purchases an item by item ID. Logs a message if in Studio. |
| Method | MarkItemsPurchasable(string[] a_arrItemIDs) | Updates the client app with the IDs of items that are now available for purchase. Logs a message if in Studio. |
| Method | UpdateCurrentInGameCurrency(string a_strCurrencyID, int a_iCurrentCurrency) | Updates the client app with the user's current in-game currency based on the specified currency ID and amount. Logs if in Studio. |