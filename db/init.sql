CREATE USER postgres SUPERUSER;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'coremsappuser') THEN
        CREATE USER coremsappuser WITH PASSWORD 'coremsapppnnl' LOGIN;
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'coremsapp') THEN
        CREATE DATABASE coremsapp;
    END IF;
END
$$;

\c coremsapp

GRANT ALL PRIVILEGES ON DATABASE coremsapp TO coremsappuser;
ALTER DATABASE coremsapp OWNER TO coremsappuser;