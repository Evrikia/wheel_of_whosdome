# 🎮 Wheel of Whosdome — Telegram Game Bot

**Wheel of Whosdome** is a fun and interactive Telegram group game bot where participants answer random questions.
It’s designed for groups, encouraging social interaction, humor, and intrigue!

---

## 🚀 Features

* 🕹️ **Two Game Modes**

  * 🎭 *Intrigue Mode* — adds mystery and personal questions for daring players.
  * 🎲 *Normal Mode* — general, fun, and friendly questions.
* 👥 **Player Registration System** — automatic player registration with join buttons.
* 💬 **Interactive Gameplay** — random player selection and questions.
* ⏳ **Timed Registration** — 60-second registration period before the game starts.
* 🔄 **Reset Functionality** — allows moderators to restart a game anytime.
* 🧭 **Command-based Controls** — all gameplay via simple Telegram commands.

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/wheel_of_whosdome.git
   cd wheel_of_whosdome
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Telegram bot token**

   Open the file and replace:

   ```python
   API_TOKEN = 'TELEGRAM BOT API TOKEN'
   ```

   with your bot’s actual token (get it from [@BotFather](https://t.me/BotFather)).

4. **Add your question files**

   Create two text files in the same directory:

   * `questions.txt` — for the **normal mode** questions
   * `questions1.txt` — for the **intrigue mode** questions

   Each question should be on a new line.


5. **Run the bot**

   ```bash
   python whosdome_bot.py.py
   ```

---

## 💬 Commands

| Command         | Description                                          |
| --------------- | ---------------------------------------------------- |
| `/start_game`   | Start a new game and choose mode (Intrigue / Normal) |
| `/join_game`    | Join the ongoing game                                |
| `/leave_game`   | Leave the current game                               |
| `/members`      | Show the number of current players                   |
| `/question`     | Ask a random question to a random player             |
| `/reset_game`   | Reset or stop the current game                       |
| `/instructions` | Show help message with all commands                  |

---

## 🧩 How It Works

1. **Start the Game**
   A user types `/start_game` in a group.
   The bot asks to choose a mode (🎭 Intrigue or 🎲 Normal).

2. **Registration Phase**
   Players join by pressing the “🎮 Присоединиться” button within 60 seconds.

3. **Game Phase**

   * The bot randomly picks a player and a question when `/question` is used.
   * Mentions are clickable so everyone sees who must answer!

4. **Ending / Resetting**

   * `/reset_game` resets the session.
   * The game also auto-resets if not enough players join.

---

## ⚙️ Project Structure

```
wheel-of-whosdome/
├── whosdome_bot.py.py               # Main game logic
├── questions.txt        # Normal mode questions
├── questions1.txt       # Intrigue mode questions
├── README.md            # Documentation
```

---

## 🛡️ Notes

* The bot **only works in group chats** — it blocks private usage.
* All messages automatically delete where appropriate to keep chats clean.
* Built with ❤️ using [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

---

## 💡 Ideas for Improvement

* Add admin-only controls (e.g., restrict /reset_game).
* Add leaderboard or scoring.
* Allow custom question sets per chat.
* Support multilingual question packs.

---

## 📜 License

This project is open-source and distributed under the **MIT License**.
Feel free to modify and improve it!
