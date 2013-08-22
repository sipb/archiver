-- 
-- The archiver database schema.
--
-- Note: this schema is not complete yet and it is prone to change
--

--
-- Content-addressed storage
--
CREATE TABLE data_objects (
    -- Hash of the data object used to identify it. This is a SHA-384 hash
    -- of the object, encoded in base 64 with "_" and "-" as last characters.
    -- The choice of the hash length is due to the fact that 384 = 64 * 6.
    hash binary(64) NOT NULL PRIMARY KEY,

    -- The key used to sort objects in order of their addition. This is useful,
    -- e.g. when doing incremental backups.
    order_key int unsigned NOT NULL AUTO_INCREMENT,

    -- Metadata like compression status of the object if we ever decide
    -- we need compression. Stored in JSON.
    properties varbinary(1024) NOT NULL,

    -- Data itself!
    value longblob NOT NULL,

    UNIQUE INDEX order_key (order_key)
) ENGINE=InnoDB;

--
-- References to external objects used for authorization
--
CREATE TABLE acls (
    -- ACL ID
    id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,

    -- Type/name pair uniquely identifies the external ACL
    -- Type column is used for identifying the backend
    type binary(16) NOT NULL,
    name varbinary(256) NOT NULL,

    -- ACL parameters, if needed
    value tinyblob NOT NULL,

    UNIQUE INDEX typename (type(16),name(256))
) ENGINE=InnoDB;

-- ACL 1 is a special value for publicly readable lists
INSERT INTO acls VALUES (0, 'all', 'all', '');

--
-- Mailing list archives themselves.
--
CREATE TABLE archives (
    -- Unique archive ID
    id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,

    -- Unique archive string ID
    name varbinary(255) NOT NULL,

    -- The informational description of the mailing list
    description blob NOT NULL default '',

    -- Indicates whether the mail arriving here should be archived or discarded
    active bool NOT NULL,

    -- Indicates if the list is deleted
    deleted bool NOT NULL,

    -- Access control lists for ownership, moderation and read access
    owner_acl int unsigned NOT NULL,
    mod_acl int unsigned NOT NULL,
    read_acl int unsigned NOT NULL,

    UNIQUE INDEX name (name),
    INDEX name_lookup (deleted, name),

    INDEX owner_acl(owner_acl, deleted, name),
    INDEX mod_acl(mod_acl, deleted, name),
    INDEX read_acl(read_acl, deleted, name),
    FOREIGN KEY (owner_acl) REFERENCES acls (id),
    FOREIGN KEY (mod_acl) REFERENCES acls (id),
    FOREIGN KEY (read_acl) REFERENCES acls (id)
) ENGINE=InnoDB;

--
-- Allows to redirect all access requests from aliases to real lists.
--
CREATE TABLE archive_aliases (
    alias varbinary(255) NOT NULL PRIMARY KEY,
    archive int unsigned NOT NULL,

    INDEX archive (archive),
    FOREIGN KEY (archive) REFERENCES archives (id)
) ENGINE=InnoDB;

--
-- Contains the metadata for all the archived messages
--
CREATE TABLE messages (
	-- The unique message ID.
    id bigint unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,

	archive int unsigned NOT NULL,

	-- The timestamp of when the message has arrived into archive in UTC
    timestamp datetime NOT NULL,

	deleted bool NOT NULL,

	message_id VARBINARY(512) NOT NULL,

	sender VARBINARY(255) NOT NULL,

	-- A JSON description of the message MIME tree. Contains
	-- the references to all the data objects which actually
	-- have the contents of the email.
	tree mediumblob NOT NULL,

	INDEX archive_chronological(archive, deleted, timestamp),
	INDEX archive_chronological_all(archive, timestamp),
	INDEX message_id(message_id(255)),
	FOREIGN KEY (archive) REFERENCES archives (id)
) ENGINE=InnoDB;

--
-- Contains the headers for all the messages.
--
-- Note: since there is no primary key in that table, it does not work with ORM.
--
CREATE TABLE headers (
	-- To make ORM happy
	id bigint unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,

	message bigint unsigned NOT NULL,

	-- While there is no fixed limit of email header name length,
	-- I am reasonably convinced that if you get it over 1024 characters,
	-- you are screwed ("Doctor, it hurts when I do this").
	name varbinary(1024) NOT NULL,

	-- This is limited to 2^16 bytes. Again, there's no standartized limits,
	-- but if you get over 64 KiB in your header, you are doing it wrong.
	value blob NOT NULL,

	INDEX message_header(message, name),
	FOREIGN KEY (message) REFERENCES messages (id)
) ENGINE=InnoDB;

CREATE TABLE parties (
	id bigint unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,

	message bigint unsigned NOT NULL,

	type ENUM('From', 'To', 'Cc', 'Bcc') NOT NULL,

	-- The email address limit is 254. See RFC 3696 and relevant errata.
	-- Also, http://stackoverflow.com/questions/386294/maximum-length-of-a-valid-email-address
	address varbinary(255) NOT NULL,

	value varbinary(512) NOT NULL,

	INDEX message_party(message, type),
	FOREIGN KEY (message) REFERENCES messages (id)
) ENGINE=InnoDB;

