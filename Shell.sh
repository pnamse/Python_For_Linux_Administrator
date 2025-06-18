#!/bin/bash

# Get today's day and last day of this month
today=$(date +%d)
last_day=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d)

# Remove leading zeros to compare as numbers
today=$((10#$today))
last_day=$((10#$last_day))

if [ "$today" -eq "$last_day" ]; then
    echo "Running uptime on last day of month: $(date)" >> /var/log/uptime_last_day.log
    uptime >> /var/log/uptime_last_day.log
fi
