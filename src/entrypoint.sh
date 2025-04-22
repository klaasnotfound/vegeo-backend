#!/bin/bash
PG_CONN=postgresql://postgres:postgres@postgres:5432

# Wait for database to start
until runuser -l postgres -c "pg_isready -d $PG_CONN" 2>/dev/null; do
  echo >&2 "Waiting for Postgres DB ..."
  sleep 3
done

# Check if DB is empty
if [[ $(psql -d $PG_CONN/vegeo -c "SELECT * FROM pg_tables WHERE schemaname='public' AND tablename='region'" | grep -o "[0-9]\+ rows") == "0 rows" ]]; then
  echo "💾 Restoring DB backup ..."
  pg_restore -d $PG_CONN data/db/vegeo-db.dump -cC
  echo "✅ Done"
fi

# Start API server
echo "🏃 Starting API server ..."
fastapi run src/api.py
