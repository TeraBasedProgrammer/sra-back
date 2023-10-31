#!/bin/sh

echo "DB Connection --- Establishing . . ."

while ! nc -z postgres 5432; do

    echo "DB Connection -- Failed!"

    sleep 1

    echo "DB Connection -- Retrying . . ."

done

echo "DB Connection --- Successfully Established!"

exec "$@"
