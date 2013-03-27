-- 
-- The archiver database schema.
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

