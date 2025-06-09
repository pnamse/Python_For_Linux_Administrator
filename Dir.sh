#!/bin/bash

# -------- CONFIGURATION --------
ROOT_DIR="/your/target/directory"     # 🔁 Change this
EMAIL_TO="recipient@example.com"      # 📧 Change this
EMAIL_SUBJECT="📂 Recursive Directory Report - $(date '+%Y-%m-%d %H:%M')"
HTML_FILE="/tmp/dir_report_$(date +%s).html"

# -------- INIT HTML --------
cat <<EOF > "$HTML_FILE"
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; font-size: 14px; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
  th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
  th { background-color: #f2f2f2; }
  h2 { background-color: #007BFF; color: white; padding: 5px; }
</style>
</head>
<body>
<h1>Recursive Directory Report</h1>
<p>Generated on: $(date)</p>
EOF

# -------- FUNCTION TO ADD DIRECTORY TABLE --------
list_dir_contents_html() {
    local dir="$1"
    echo "<h2>$dir</h2>" >> "$HTML_FILE"
    echo "<table>" >> "$HTML_FILE"
    echo "<tr><th>Permissions</th><th>Links</th><th>Owner</th><th>Group</th><th>Size</th><th>Date</th><th>Time</th><th>Filename</th></tr>" >> "$HTML_FILE"

    # List non-hidden files only
    ls -ltrh "$dir" | grep -v '^total' | grep -v '/\.' | while read -r perm links owner group size date time filename; do
        echo "<tr><td>$perm</td><td>$links</td><td>$owner</td><td>$group</td><td>$size</td><td>$date</td><td>$time</td><td>$filename</td></tr>" >> "$HTML_FILE"
    done

    echo "</table>" >> "$HTML_FILE"
}

# -------- WALK THROUGH DIRECTORIES --------
find "$ROOT_DIR" -type d ! -path '*/.*' | while read dir; do
    list_dir_contents_html "$dir"
done

# -------- END HTML --------
echo "</body></html>" >> "$HTML_FILE"

# -------- SEND EMAIL --------
if command -v mailx >/dev/null 2>&1; then
    cat "$HTML_FILE" | mailx -a "Content-Type: text/html" -s "$EMAIL_SUBJECT" "$EMAIL_TO"
else
    echo "mailx not installed. Please install it to send HTML email."
fi

# -------- CLEANUP --------
rm -f "$HTML_FILE"
