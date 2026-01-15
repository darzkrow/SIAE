#!/bin/sh
set -e

# This script runs inside the Postgres container during initialization.
# It ensures the role and database 'gsih_user' exist and sets ownership.

echo "-> Checking for role gsih_user"
ROLE_EXISTS=$(psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='gsih_user';" || true)
if [ "$ROLE_EXISTS" != "1" ]; then
  echo "-> Creating role gsih_user"
  psql -U "$POSTGRES_USER" -d postgres -c "CREATE ROLE gsih_user LOGIN;"
else
  echo "-> Role gsih_user already exists"
fi

DB_EXISTS=$(psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='gsih_user';" || true)
if [ "$DB_EXISTS" != "1" ]; then
  echo "-> Creating database gsih_user"
  psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE gsih_user;"
else
  echo "-> Database gsih_user already exists"
fi

echo "-> Setting owner of gsih_user database to gsih_user (if possible)"
psql -U "$POSTGRES_USER" -d postgres -c "ALTER DATABASE gsih_user OWNER TO gsih_user;" || true

