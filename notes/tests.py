from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import User, Note, NoteLink, TaskMeta, Tag


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a user with telegram_id."""
        user = User.objects.create_user(
            telegram_id=123456789,
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.telegram_id, 123456789)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_user_str(self):
        """Test User string representation."""
        user = User.objects.create_user(telegram_id=123456789, username='testuser')
        self.assertEqual(str(user), 'testuser')


class TagModelTest(TestCase):
    """Test cases for Tag model."""
    
    def test_create_tag(self):
        """Test creating a tag."""
        tag = Tag.objects.create(name='Python', color='#3776ab')
        self.assertEqual(tag.name, 'Python')
        self.assertEqual(tag.color, '#3776ab')
        self.assertEqual(str(tag), 'Python')


class NoteModelTest(TestCase):
    """Test cases for Note model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(telegram_id=123456789, username='testuser')
        self.tag = Tag.objects.create(name='Django')
    
    def test_create_note(self):
        """Test creating a basic note."""
        note = Note.objects.create(
            title='Test Note',
            content='# This is a test\n\nSome markdown content',
            note_type='note',
            owner=self.user
        )
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.note_type, 'note')
        self.assertEqual(note.owner, self.user)
        self.assertFalse(note.is_archived)
        self.assertFalse(note.is_deleted)
    
    def test_note_with_tags(self):
        """Test creating a note with tags."""
        note = Note.objects.create(
            title='Tagged Note',
            content='Content',
            owner=self.user
        )
        note.tags.add(self.tag)
        self.assertEqual(note.tags.count(), 1)
        self.assertIn(self.tag, note.tags.all())


class NoteLinkModelTest(TestCase):
    """Test cases for NoteLink model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(telegram_id=123456789, username='testuser')
        self.note1 = Note.objects.create(
            title='Note 1',
            content='Content 1',
            owner=self.user
        )
        self.note2 = Note.objects.create(
            title='Note 2',
            content='Content 2',
            owner=self.user
        )
    
    def test_create_note_link(self):
        """Test creating a link between notes."""
        link = NoteLink.objects.create(
            source_note=self.note1,
            target_note=self.note2,
            link_type='reference'
        )
        self.assertEqual(link.source_note, self.note1)
        self.assertEqual(link.target_note, self.note2)
        self.assertEqual(link.link_type, 'reference')
    
    def test_note_relationships(self):
        """Test note relationships through links."""
        NoteLink.objects.create(
            source_note=self.note1,
            target_note=self.note2,
            link_type='parent'
        )
        
        # Test outgoing links
        self.assertEqual(self.note1.outgoing_links.count(), 1)
        
        # Test incoming links
        self.assertEqual(self.note2.incoming_links.count(), 1)


class TaskMetaModelTest(TestCase):
    """Test cases for TaskMeta model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(telegram_id=123456789, username='testuser')
        self.task_note = Note.objects.create(
            title='Task Note',
            content='Task content',
            note_type='task',
            owner=self.user
        )
    
    def test_create_task_meta(self):
        """Test creating task metadata."""
        task_meta = TaskMeta.objects.create(
            note=self.task_note,
            priority='high',
            status='todo',
            due_date=timezone.now() + timedelta(days=7)
        )
        self.assertEqual(task_meta.note, self.task_note)
        self.assertEqual(task_meta.priority, 'high')
        self.assertEqual(task_meta.status, 'todo')
        self.assertIsNotNone(task_meta.due_date)
    
    def test_task_meta_one_to_one(self):
        """Test one-to-one relationship with Note."""
        TaskMeta.objects.create(
            note=self.task_note,
            priority='medium',
            status='in_progress'
        )
        
        # Access task_meta from note
        self.assertEqual(self.task_note.task_meta.priority, 'medium')
        self.assertEqual(self.task_note.task_meta.status, 'in_progress')
