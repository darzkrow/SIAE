-- Create role if it doesn't exist and create the gsih_user database owned by that role
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gsih_user') THEN
    CREATE ROLE gsih_user LOGIN;
  END IF;
END
$$;

-- Create the database if it does not exist and set owner
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gsih_user') THEN
    PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE gsih_user');
  END IF;
END
$$;

-- Attempt to set owner (ignore errors if role doesn't exist yet)
ALTER DATABASE gsih_user OWNER TO gsih_user;
