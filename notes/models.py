from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager for User model with telegram_id authentication."""
    
    def create_user(self, telegram_id, username=None, **extra_fields):
        """Create and save a User with the given telegram_id."""
        if not telegram_id:
            raise ValueError('The telegram_id must be set')
        
        user = self.model(telegram_id=telegram_id, username=username, **extra_fields)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, telegram_id, username=None, **extra_fields):
        """Create and save a SuperUser with the given telegram_id."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(telegram_id, username, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with Telegram authentication."""
    
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['telegram_id'], name='idx_telegram_id'),
        ]
    
    def __str__(self):
        return f"{self.username or self.telegram_id}"


class Tag(models.Model):
    """Tag model for categorizing notes."""
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    color = models.CharField(max_length=7, default="#808080", help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='idx_tag_name'),
        ]
    
    def __str__(self):
        return self.name


class Note(models.Model):
    """Note model with markdown content and different types."""
    
    NOTE_TYPE_CHOICES = [
        ('note', 'Note'),
        ('task', 'Task'),
        ('project', 'Project'),
    ]
    
    title = models.CharField(max_length=500, db_index=True)
    content = models.TextField(help_text="Markdown content")
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default='note',
        db_index=True
    )
    
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='notes'
    )
    
    tags = models.ManyToManyField(
        'Tag',
        related_name='notes',
        blank=True
    )
    
    # Self-referencing relationships through NoteLink
    linked_notes = models.ManyToManyField(
        'self',
        through='NoteLink',
        symmetrical=False,
        related_name='backlinks',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    is_archived = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        db_table = 'notes'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'note_type'], name='idx_owner_type'),
            models.Index(fields=['owner', 'created_at'], name='idx_owner_created'),
            models.Index(fields=['owner', 'updated_at'], name='idx_owner_updated'),
            models.Index(fields=['note_type', 'created_at'], name='idx_type_created'),
            models.Index(fields=['is_archived', 'is_deleted'], name='idx_archived_deleted'),
            models.Index(fields=['owner', 'is_deleted', 'is_archived'], name='idx_owner_status'),
        ]
    
    def __str__(self):
        return self.title


class NoteLink(models.Model):
    """Model for managing graph relationships between notes."""
    
    LINK_TYPE_CHOICES = [
        ('reference', 'Reference'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('related', 'Related'),
    ]
    
    source_note = models.ForeignKey(
        'Note',
        on_delete=models.CASCADE,
        related_name='outgoing_links'
    )
    
    target_note = models.ForeignKey(
        'Note',
        on_delete=models.CASCADE,
        related_name='incoming_links'
    )
    
    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPE_CHOICES,
        default='reference',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_links'
        verbose_name = 'Note Link'
        verbose_name_plural = 'Note Links'
        unique_together = ('source_note', 'target_note', 'link_type')
        indexes = [
            models.Index(fields=['source_note', 'link_type'], name='idx_source_link_type'),
            models.Index(fields=['target_note', 'link_type'], name='idx_target_link_type'),
            models.Index(fields=['source_note', 'target_note'], name='idx_source_target'),
        ]
    
    def __str__(self):
        return f"{self.source_note.title} -> {self.target_note.title} ({self.link_type})"


class TaskMeta(models.Model):
    """One-to-one metadata for Task type notes."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    note = models.OneToOneField(
        'Note',
        on_delete=models.CASCADE,
        related_name='task_meta',
        primary_key=True
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        db_index=True
    )
    
    due_date = models.DateTimeField(null=True, blank=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_meta'
        verbose_name = 'Task Metadata'
        verbose_name_plural = 'Task Metadata'
        indexes = [
            models.Index(fields=['status', 'priority'], name='idx_status_priority'),
            models.Index(fields=['due_date', 'status'], name='idx_due_status'),
            models.Index(fields=['priority', 'due_date'], name='idx_priority_due'),
        ]
    
    def __str__(self):
        return f"TaskMeta for {self.note.title}"
