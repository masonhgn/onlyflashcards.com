# OnlyFlashcards.com

A Quizlet-like flashcard application built with Flask and MongoDB.

## Features

- Create and manage flashcard sets
- Add flashcards with front and back sides
- User authentication
- Public and private flashcard sets

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MongoDB:
   - Install MongoDB locally or use MongoDB Atlas
   - Update `.env` file with your MongoDB URI

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python app.py
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models/               # Database models
│   ├── __init__.py
│   ├── database.py       # MongoDB connection
│   ├── user.py           # User model
│   ├── flashcard_set.py  # FlashcardSet model
│   └── flashcard.py      # Flashcard model
├── routes/               # Flask routes (to be added)
├── templates/            # HTML templates (to be added)
├── static/               # CSS/JS files (to be added)
└── requirements.txt      # Python dependencies
```

## Models

### User
- username
- email
- password_hash
- created_at

### FlashcardSet
- title
- description
- user_id
- is_public
- created_at
- updated_at

### Flashcard
- front (front side text)
- back (back side text)
- set_id (belongs to a FlashcardSet)
- difficulty
- times_reviewed
- last_reviewed

