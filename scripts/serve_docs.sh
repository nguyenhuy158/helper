fswatch -o . | while read; do
    pkill -f "mkdocs serve"  # kill server cũ
    mkdocs serve &
done
