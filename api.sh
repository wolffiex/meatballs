#!/bin/bash
# Output the HTTP headers for SSE
echo "Content-Type: text/event-stream"
echo "Cache-Control: no-cache"
echo "Connection: keep-alive"
echo "" # End of headers
run () {
    local file=$1
    local eventname=$(basename "$file" .sql) 
    emit() {
        local data="$1"
        printf "event: %s\ndata: %s\n\n" "$eventname" "$data"
    }

    {
        while IFS= read -r line; do
            emit "$line"
        done < <(psql -h "$DB_HOST" -d monitoring -t -A -q -f "${file}")

        emit "null"
    }
}

run "sql/summary.sql"  &
run "sql/two_days.sql" &
wait

# Send a stream_stop event with no data
echo "event: stream_stop"
echo "data:" # No data after 'data:'
echo "" # End of event
