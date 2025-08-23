# 🎧 Auto Podcast Generator

This project turns ideas into spoken audio episodes using LLM + TTS, uploads them to **AWS S3**, and maintains a public **RSS feed** that can be used in any podcast player (including Android Auto).

---

## 🔒 .gitignore (IMPORTANT)

Make sure to add the following entries to your `.gitignore` to avoid exposing sensitive data:

```
.env
*.mp3
feed.xml
__pycache__/
.venv/
```

- `.env` → stores AWS and OpenAI credentials. **Never commit this file.**
- `*.mp3` → generated episode audio files.
- `feed.xml` → your auto-generated RSS feed.
- `.venv/` and `__pycache__/` → local environment/build folders.

---

## ⚙️ How It Works

1. You type a **prompt** in the Gradio interface.
2. A language model generates a **narrative/story/lesson**.
3. The text is converted to **MP3 audio** using OpenAI TTS.
4. The MP3 is uploaded to your **AWS S3 bucket**.
5. The RSS feed (`feed.xml`) is updated and also uploaded to S3.

You can subscribe to the RSS feed in any podcast app that supports custom feeds.

---

## 🚀 Running the Project

### Requirements

- Python 3.11+
- AWS account with S3 configured
- OpenAI API key
- Environment variables defined in `.env`:

```env
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-2
AWS_BUCKET_NAME=my-ai-podcast
```

### Setup

```bash
make setup
```

### Run the Gradio interface

```bash
make run
```

Open in your browser:  
[http://localhost:7860](http://localhost:7860)

---

## 📂 Project Structure

```
app/
 ├─ main.py          # Gradio UI + backend logic
 ├─ storage.py       # S3 upload functions
 ├─ rss_utils.py     # RSS feed creation and updates
 └─ prompts.py       # Prompt style definitions (PT/EN/ES)

tmp/                 # Temporary folder for MP3s
feed.xml             # RSS feed (auto-generated and uploaded to S3)
```

---

## 📡 RSS Feed

Each new episode updates the `feed.xml` file and uploads it to your S3 bucket.

Your public RSS feed URL will look like:

```
https://<your-bucket>.s3.<region>.amazonaws.com/rss/feed.xml
```

You can paste this into any podcast player that supports RSS feeds.

---

## 📝 Notes

- Upload a square **cover image** (1400×1400 to 3000×3000 px) to S3 and reference it in `rss_utils.py`.
- The generated feed is RSS 2.0 with iTunes extensions, compatible with all major podcast apps.
- You can run this locally or deploy as a Flask/Gradio service with minimal effort.
