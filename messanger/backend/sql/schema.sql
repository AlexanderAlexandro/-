PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    last_seen_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('direct', 'group')),
    title TEXT,
    direct_pair_key TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (direct_pair_key IS NULL OR type = 'direct')
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_chats_direct_pair_key
ON chats(direct_pair_key)
WHERE direct_pair_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS chat_members (
    chat_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'owner')),
    joined_at TEXT NOT NULL,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_members_user_id
ON chat_members(user_id);

CREATE INDEX IF NOT EXISTS idx_chat_members_chat_id
ON chat_members(chat_id);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    body TEXT NOT NULL CHECK (length(body) > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_chat_created_at
ON messages(chat_id, created_at, id);

CREATE INDEX IF NOT EXISTS idx_messages_author_id
ON messages(author_id);

CREATE TRIGGER IF NOT EXISTS trg_messages_touch_chat_after_insert
AFTER INSERT ON messages
BEGIN
    UPDATE chats
    SET updated_at = NEW.created_at
    WHERE id = NEW.chat_id;
END;
