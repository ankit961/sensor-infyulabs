#!/bin/bash
# Start the Cloud SQL Proxy
./cloud_sql_proxy -instances=sensor-reading-404008:asia-south1:sensor=tcp:5432 -ip_address_types=PUBLIC &

# Wait a few seconds to ensure the SQL Proxy has started
sleep 10

# Run the migrations
python manage.py db init
python manage.py db migrate
python manage.py db upgrade

# Kill the Cloud SQL Proxy process
kill $!
