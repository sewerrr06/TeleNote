# TeleNote Database Design

## Overview
TeleNote uses a scalable, graph-based database design optimized for a knowledge base system with Telegram authentication.

## Data Models

### 1. User Model
**Purpose**: Custom user authentication via Telegram
- **Primary Key**: Auto-generated BigIntegerField
- **Unique Identifier**: `telegram_id` (BigIntegerField)
- **Authentication**: Uses telegram_id instead of username/email
- **Indexes**: 
  - `telegram_id` (unique, indexed) for fast authentication lookups

**Design Rationale**:
- Telegram IDs are guaranteed unique per user
- BigIntegerField accommodates Telegram's large numeric IDs
- Extends AbstractBaseUser for full Django auth integration

### 2. Note Model
**Purpose**: Core content storage with markdown support
- **Types**: note, task, project
- **Content**: TextField for markdown content
- **Relationships**:
  - ForeignKey to User (owner)
  - ManyToMany with Tag
  - Self-referencing ManyToMany through NoteLink

**Indexes** (for scalability):
- `owner + note_type`: Fast filtering of user's notes by type
- `owner + created_at`: Chronological note listing per user
- `owner + updated_at`: Recently updated notes per user
- `note_type + created_at`: Global type-based queries
- `is_archived + is_deleted`: Status filtering
- `owner + is_deleted + is_archived`: Combined user status queries

**Design Rationale**:
- Composite indexes optimize common query patterns
- Soft delete via `is_deleted` preserves data integrity
- `is_archived` allows hiding notes without deletion

### 3. NoteLink Model
**Purpose**: Graph relationships between notes
- **Link Types**: reference, parent, child, related
- **Relationships**: Self-referencing Note model

**Indexes** (for graph queries):
- `source_note + link_type`: Find all outgoing links of a type
- `target_note + link_type`: Find all incoming links of a type
- `source_note + target_note`: Direct relationship lookups
- **Unique Constraint**: (source_note, target_note, link_type)

**Design Rationale**:
- Self-referencing through table enables complex graph queries
- Indexes optimize bidirectional graph traversal
- Link types enable semantic relationships (Obsidian-like)
- Unique constraint prevents duplicate links

### 4. TaskMeta Model
**Purpose**: Extended metadata for task-type notes
- **Relationship**: OneToOne with Note (primary_key=True)
- **Fields**: priority, status, due_date, completed_at

**Indexes**:
- `status + priority`: Task board queries
- `due_date + status`: Deadline-based filtering
- `priority + due_date`: High-priority upcoming tasks

**Design Rationale**:
- OneToOne avoids cluttering Note table with task-specific fields
- Only created for task-type notes (saves storage)
- Composite indexes optimize task management queries

### 5. Tag Model
**Purpose**: Categorization and filtering
- **Unique**: Tag names
- **Color**: Hex color for UI representation

**Indexes**:
- `name` (unique, indexed): Fast tag lookups

**Design Rationale**:
- ManyToMany allows multiple tags per note
- Centralized tag storage prevents duplicates
- Color field enables rich UI representation

## Scalability Considerations

### 1. Index Strategy
- **Query-based indexing**: Indexes designed for common query patterns
- **Composite indexes**: Multi-column indexes for complex queries
- **Selective indexing**: Only frequently queried columns indexed

### 2. Graph Query Optimization
- Bidirectional indexes on NoteLink enable O(1) relationship lookups
- Self-referencing ManyToMany through table is PostgreSQL-optimized
- Link type filtering via indexed column

### 3. User-Scoped Queries
- Most queries scoped by `owner` field
- Composite indexes starting with `owner` enable partition-like behavior
- Reduces full table scans

### 4. Soft Deletes
- `is_deleted` and `is_archived` flags prevent data loss
- Indexed for fast filtering in queries
- Combined indexes with `owner` for user-scoped queries

### 5. Database Choice
- **PostgreSQL** (recommended): 
  - Superior indexing for graph queries
  - Better JSON support for future features
  - Advanced full-text search
- **SQLite** (development): 
  - Zero-configuration for testing
  - Full compatibility with PostgreSQL migrations

## Query Performance Examples

### Fast Queries (thanks to indexes)
```python
# User's active notes by type
Note.objects.filter(owner=user, note_type='task', is_deleted=False)

# Recently updated notes
Note.objects.filter(owner=user, is_archived=False).order_by('-updated_at')

# High-priority tasks due soon
TaskMeta.objects.filter(priority='high', status='todo', due_date__lte=deadline)

# Graph relationships
note.outgoing_links.filter(link_type='reference')
note.incoming_links.filter(link_type='parent')
```

### Optimized N+1 Query Prevention
```python
# Prefetch related data
notes = Note.objects.filter(owner=user).prefetch_related('tags', 'linked_notes')

# Select related for foreign keys
notes = Note.objects.select_related('owner').filter(note_type='task')

# Task with metadata
tasks = Note.objects.filter(note_type='task').select_related('task_meta')
```

## Future Scalability Options

1. **Partitioning**: Partition by `owner` for multi-tenant scaling
2. **Caching**: Redis for frequently accessed notes
3. **Full-Text Search**: PostgreSQL FTS or Elasticsearch for content search
4. **Read Replicas**: For high-read workloads
5. **Denormalization**: Materialized views for complex graph queries
6. **Connection Pooling**: PgBouncer for connection management

## Migration Strategy

All models are versioned via Django migrations:
- Initial migration: `0001_initial.py`
- Includes all indexes and constraints
- Safe to apply to empty or existing databases
- Rollback support via Django's migration system
