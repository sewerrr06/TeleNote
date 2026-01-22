from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Note, NoteLink, TaskMeta, Tag


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('telegram_id', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""
    
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']
    ordering = ['name']


class TaskMetaInline(admin.StackedInline):
    """Inline admin for TaskMeta."""
    model = TaskMeta
    can_delete = False
    fields = ['priority', 'status', 'due_date', 'completed_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin interface for Note model."""
    
    list_display = ['title', 'note_type', 'owner', 'created_at', 'updated_at', 'is_archived', 'is_deleted']
    list_filter = ['note_type', 'is_archived', 'is_deleted', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'note_type', 'owner')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Status', {
            'fields': ('is_archived', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    inlines = []
    
    def get_inlines(self, request, obj=None):
        """Show TaskMeta inline only for task type notes."""
        if obj and obj.note_type == 'task':
            return [TaskMetaInline]
        return []


@admin.register(NoteLink)
class NoteLinkAdmin(admin.ModelAdmin):
    """Admin interface for NoteLink model."""
    
    list_display = ['source_note', 'target_note', 'link_type', 'created_at']
    list_filter = ['link_type', 'created_at']
    search_fields = ['source_note__title', 'target_note__title']
    ordering = ['-created_at']


@admin.register(TaskMeta)
class TaskMetaAdmin(admin.ModelAdmin):
    """Admin interface for TaskMeta model."""
    
    list_display = ['note', 'priority', 'status', 'due_date', 'completed_at']
    list_filter = ['priority', 'status', 'due_date']
    search_fields = ['note__title']
    ordering = ['due_date']
