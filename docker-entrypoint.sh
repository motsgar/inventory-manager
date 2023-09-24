#!/bin/sh

set -eo pipefail

echo "Initializing database..."
python src/db_init.py
echo "Database initialized!"

exec "$@"