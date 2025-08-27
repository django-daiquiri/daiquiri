countdown() {
    local seconds=$1
    local message=$2
    echo "$message"
    for i in $(seq $seconds -1 1); do
        echo "Starting in $i seconds... "
        sleep 1
    done
}


echo "Enter the path to your old PostgreSQL 13 database directory:"
read -p "Old database path: " OLD_DB_PATH


if [ ! -d "$OLD_DB_PATH" ]; then
    echo "Error: Directory '$OLD_DB_PATH' does not exist!"
    exit 1
fi


echo "Creating symlink 'old_database' pointing to '$OLD_DB_PATH'..."
ln -s "$OLD_DB_PATH" old_database

if [ $? -eq 0 ]; then
    echo "Symlink created successfully!"
else
    echo "Error: Failed to create symlink!"
    exit 1
fi


docker compose up pg13 -d
countdown 5 "Waiting for pg13 to start..."
docker exec pg13 pg_dumpall -U daiquiri_app -f /transfer/pg13.sql
docker compose down


docker compose up pg17 -d
countdown 10 "Waiting for pg17 to start..."
docker exec  pg17 psql -c "CREATE ROLE daiquiri_app SUPERUSER LOGIN;"
docker exec  pg17 psql -d postgres -c "CREATE DATABASE daiquiri_app OWNER daiquiri_app;"
docker exec pg17 psql -U daiquiri_app -f /transfer/pg13.sql
docker exec  pg17 psql -U daiquiri_app -d daiquiri_app -c "ALTER ROLE daiquiri_app WITH LOGIN PASSWORD 'daiquiri_app';"
docker compose down


echo "Cleaning up temporary files..."
rm -f old_database
rm -rf transfer


echo "Migration completed successfully!"
echo ""
echo "Your new PostgreSQL 17 database files are now located in the 'new_database' subdirectory."