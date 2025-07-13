## 🧩 Frontend Overview

This is a React-based frontend that interacts with a Move smart contract on the **Endless blockchain** via the **Luffa Wallet**. It provides a demo interface for a number guessing game and handles wallet connection, game creation, game discovery, and guess submission.

### 🔧 Key Features

- **🔗 Wallet Connection**  
  Uses `@luffalab/luffa-endless-sdk` to connect to the user's Luffa Wallet and listen for connect/disconnect/account-change events.

- **🎮 Start New Game**  
  Calls the smart contract function `start_game` to begin a new game session with a hidden number.

- **📡 Game Discovery**  
  Invokes the smart contract function `get_active_game_ids` to retrieve currently available game sessions.

- **🎯 Submit Guess**  
  Submits a number guess (1–100) via the `submit_guess` function and listens to event logs to determine if the player won or lost.

- **📊 Result Display**  
  Dynamically shows:
  - Connected wallet address
  - List of active game IDs
  - The player’s guess
  - Result status (`🎉 You Won!`, `😞 You Lost`)
  - The actual hidden number

### 🛠 Tech Stack

- React
- [@luffalab/luffa-endless-sdk](https://www.npmjs.com/package/@luffalab/luffa-endless-sdk)
- [@endlesslab/endless-ts-sdk](https://www.npmjs.com/package/@endlesslab/endless-ts-sdk)
- CSS modules
- Endless Blockchain (Testnet)

## 📦 Running the Project

1. Enter the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
