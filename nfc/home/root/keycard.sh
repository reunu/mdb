#!/bin/sh
redis-cli HSET keycard authentication passed > /dev/null
redis-cli HSET keycard type scooter > /dev/null
redis-cli HSET keycard uid 11111111111111 > /dev/null
redis-cli PUBLISH keycard authentication > /dev/null
redis-cli EXPIRE keycard 10 > /dev/null
echo "Keycard script executed"
