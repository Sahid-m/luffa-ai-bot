# 🧠 LuffaBot AI Assistant Demo

This is a demo project that integrates a LangGraph-powered AI assistant with the Luffa Bot platform. It listens to user messages, understands what users want, and calls the right tools — like starting a vote, generating images, or booking a hotel — all through chat.

> ⚠️ Some tools are currently placeholders (like video downloading and hotel booking), but the structure is ready for real use cases.

---

## 🚀 Features

- **Multi-tool AI agent** powered by `LangGraph` (ReAct agent style)
- **Luffa Bot integration** – interacts directly with users in group or direct messages
- **Custom tools included:**
  - `initiate_vote`: Start a vote in a group
  - `count_vote_result`: Show current vote results
  - `generate_image`: Generate an image using a custom model
  - `download_video`: (placeholder) Download videos from YouTube or Twitter
  - `transcribe`: (placeholder) Transcribe and summarize videos
  - `book_hotel`: (placeholder) Simulate a hotel booking

---

## 🛠 Tech Stack

- Python
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://www.langchain.com/)
- FastAPI
- [Luffa Bot API](https://robot.luffa.im/docManagement/developGuide)
- [tmpfiles.org (for hosting media files)](https://tmpfiles.org/)
- Python 3.11 (recommended)

---

## 📦 Running the Project

Enter the project root directory (where `app/` and `README.md` are located):

1. Rename the environment config file and fill in necessary values:
   ```
   cp .env.example .env
   # Then open .env and fill in your API keys or other required settings
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app from the project root directory:
   ```
   python -m uvicorn app.main:app --reload
   ```

## 💡 How It Works

1. Users send a message to the bot (e.g. “Start a vote in group Arz7KwQDd9m with options Rock, Paper, Scissors”).
2. The AI agent processes the message using a custom prompt that enforces strict rules:
   - Use user text exactly
   - Never assume missing arguments
   - Ask for clarification when needed
3. If the agent decides to use a tool, it calls it with the parsed arguments.
4. The result is returned to the user via the Luffa Bot.

---

## 📝 Notes

- **Image & Video support**: LuffaBot currently doesn’t support sending media files directly. Use `upload_to_tmpfiles` in [utils.py](app/utils.py) to share a URL instead.
- **Memory-only**: `vote_option_map` and `message_queue` are in-memory. For real-world use, move them to a database.
- **Extensible**: Want to use OpenAI or other APIs? You can easily swap out or expand the tools.

---

## 📌 TODOs

- Implement actual video download and transcription logic
- Add persistent storage (e.g. SQLite or Redis)
- Improve front-end display (if needed)
- Add more robust validation for inputs

---

## 🤝 Contributing

Feel free to fork, experiment, and build on top of this! PRs welcome.
