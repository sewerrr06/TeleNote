#!/usr/bin/env python
"""
Verification script to demonstrate TeleNote models and their relationships.
This script creates sample data and shows model usage.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telenote.settings_test')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from notes.models import User, Note, NoteLink, TaskMeta, Tag


def setup_database():
    """Setup the test database."""
    print("Setting up database...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("✓ Database ready\n")


def demonstrate_models():
    """Demonstrate the usage of TeleNote models."""
    
    print("=" * 60)
    print("TeleNote Models Demonstration")
    print("=" * 60)
    
    # 1. Create User
    print("\n1. Creating User with telegram_id authentication...")
    user = User.objects.create_user(
        telegram_id=123456789,
        username='demo_user',
        first_name='Demo',
        last_name='User'
    )
    print(f"   ✓ Created user: {user}")
    print(f"   - Telegram ID: {user.telegram_id}")
    print(f"   - Username: {user.username}")
    
    # 2. Create Tags
    print("\n2. Creating Tags...")
    tag_python = Tag.objects.create(name='Python', color='#3776ab')
    tag_django = Tag.objects.create(name='Django', color='#092e20')
    tag_important = Tag.objects.create(name='Important', color='#ff0000')
    print(f"   ✓ Created {Tag.objects.count()} tags")
    
    # 3. Create Notes
    print("\n3. Creating Notes...")
    
    # Regular note
    note1 = Note.objects.create(
        title='Getting Started with TeleNote',
        content='# TeleNote\n\nThis is a markdown-based knowledge base.',
        note_type='note',
        owner=user
    )
    note1.tags.add(tag_python, tag_django)
    print(f"   ✓ Created note: {note1.title}")
    
    # Project note
    note2 = Note.objects.create(
        title='TeleNote Backend Development',
        content='## Goals\n\n- Implement models\n- Create API\n- Deploy',
        note_type='project',
        owner=user
    )
    note2.tags.add(tag_django, tag_important)
    print(f"   ✓ Created project: {note2.title}")
    
    # Task note
    note3 = Note.objects.create(
        title='Review Django Models',
        content='Review and optimize the database models',
        note_type='task',
        owner=user
    )
    note3.tags.add(tag_django)
    print(f"   ✓ Created task: {note3.title}")
    
    # 4. Create NoteLinks (Graph relationships)
    print("\n4. Creating NoteLinks (Graph relationships)...")
    link1 = NoteLink.objects.create(
        source_note=note2,
        target_note=note1,
        link_type='reference'
    )
    link2 = NoteLink.objects.create(
        source_note=note3,
        target_note=note2,
        link_type='child'
    )
    print(f"   ✓ Created {NoteLink.objects.count()} note links")
    print(f"   - {note2.title} -> {note1.title} (reference)")
    print(f"   - {note3.title} -> {note2.title} (child)")
    
    # 5. Create TaskMeta
    print("\n5. Creating TaskMeta for task note...")
    task_meta = TaskMeta.objects.create(
        note=note3,
        priority='high',
        status='in_progress',
        due_date=timezone.now() + timedelta(days=3)
    )
    print(f"   ✓ Created task metadata")
    print(f"   - Priority: {task_meta.priority}")
    print(f"   - Status: {task_meta.status}")
    print(f"   - Due in: 3 days")
    
    # 6. Demonstrate queries
    print("\n6. Demonstrating Model Queries...")
    
    # User's notes
    user_notes = Note.objects.filter(owner=user)
    print(f"   ✓ User has {user_notes.count()} notes")
    
    # Task type notes
    tasks = Note.objects.filter(note_type='task')
    print(f"   ✓ Found {tasks.count()} task(s)")
    
    # Notes with specific tag
    django_notes = Note.objects.filter(tags=tag_django)
    print(f"   ✓ Found {django_notes.count()} note(s) with 'Django' tag")
    
    # Graph relationships
    outgoing = note2.outgoing_links.count()
    incoming = note2.incoming_links.count()
    print(f"   ✓ Note '{note2.title}' has {outgoing} outgoing and {incoming} incoming links")
    
    # Task metadata query
    high_priority_tasks = TaskMeta.objects.filter(priority='high', status='in_progress')
    print(f"   ✓ Found {high_priority_tasks.count()} high-priority in-progress task(s)")
    
    print("\n" + "=" * 60)
    print("✓ All models working correctly!")
    print("=" * 60)
    
    # Display model statistics
    print("\nModel Statistics:")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Notes: {Note.objects.count()}")
    print(f"  - NoteLinks: {NoteLink.objects.count()}")
    print(f"  - Tags: {Tag.objects.count()}")
    print(f"  - TaskMeta: {TaskMeta.objects.count()}")


if __name__ == '__main__':
    setup_database()
    demonstrate_models()
