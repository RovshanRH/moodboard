PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS designers (
    id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL,
    bio TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    company TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS catalogs (
    id INTEGER PRIMARY KEY,
    designer_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (designer_id) REFERENCES designers(id) ON DELETE CASCADE,
    UNIQUE (designer_id, name)
);

CREATE TABLE IF NOT EXISTS moodboards (
    id INTEGER PRIMARY KEY,
    designer_id INTEGER NOT NULL,
    catalog_id INTEGER,
    client_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    background_color TEXT NOT NULL DEFAULT '#F4EFE6',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (designer_id) REFERENCES designers(id) ON DELETE CASCADE,
    FOREIGN KEY (catalog_id) REFERENCES catalogs(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS palette_colors (
    id INTEGER PRIMARY KEY,
    moodboard_id INTEGER NOT NULL,
    color TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (moodboard_id) REFERENCES moodboards(id) ON DELETE CASCADE
);
