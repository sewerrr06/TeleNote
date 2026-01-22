# TeleNote

A Telegram-based knowledge base system combining features from Notion and Obsidian.

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: PostgreSQL (recommended), SQLite (development)
- **Authentication**: Telegram ID-based authentication

## Features

- **Custom User Model**: Authentication via Telegram ID
- **Notes System**: Markdown-based notes with three types:
  - Regular Notes
  - Tasks
  - Projects
- **Graph Relationships**: Self-referencing note links for building knowledge graphs
- **Task Management**: Extended metadata for task-type notes (priority, status, due dates)
- **Tagging System**: Multi-tag support for organizing notes

## Models

### User
Custom user model with Telegram authentication:
- `telegram_id`: Unique Telegram ID (primary authentication field)
- `username`, `first_name`, `last_name`: User information
- Integrated with Django's authentication system

### Note
Main content model:
- `title`: Note title
- `content`: Markdown content
- `note_type`: note/task/project
- `owner`: Foreign key to User
- `tags`: Many-to-many relationship with Tag
- `linked_notes`: Self-referencing many-to-many through NoteLink

### NoteLink
Graph relationship model:
- `source_note`: Source note in the relationship
- `target_note`: Target note in the relationship
- `link_type`: reference/parent/child/related
- Enables building knowledge graphs

### TaskMeta
One-to-one extension for task-type notes:
- `priority`: low/medium/high/urgent
- `status`: todo/in_progress/blocked/completed/cancelled
- `due_date`: Optional deadline
- `completed_at`: Completion timestamp

### Tag
Categorization model:
- `name`: Unique tag name
- `color`: Hex color code for UI

## Database Design

The models are optimized for scalability with:
- **Indexes** on frequently queried fields (telegram_id, note_type, created_at, etc.)
- **Composite indexes** for common query patterns (owner + type, owner + created_at, etc.)
- **Graph optimization** with indexes on NoteLink source/target relationships
- **Unique constraints** to prevent duplicate links

## Setup

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `telenote/settings.py` or use environment variables

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Database Configuration

### PostgreSQL (Production)
Update `DATABASES` in `telenote/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'telenote_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### SQLite (Development)
For local development, you can use SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## API (Django REST Framework)

The project is set up with Django REST Framework for building RESTful APIs. You can create serializers and viewsets for each model to expose them via API endpoints.

## Admin Interface

All models are registered in the Django admin interface at `/admin/`:
- User management
- Note CRUD with inline TaskMeta for task-type notes
- NoteLink management for graph relationships
- Tag management
- TaskMeta standalone management

## License

This project is open source.