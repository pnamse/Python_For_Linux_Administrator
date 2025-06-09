#!/bin/bash

# -------- CONFIGURATION --------
ROOT_DIR="/your/target/directory"     # 🔁 Change this
EMAIL_TO="recipient@example.com"      # 📧 Change this
EMAIL_SUBJECT="📂 Recursive Directory Report - $(date '+%Y-%m-%d %H:%M')"
HTML_FILE="/tmp/dir_report_$(date +%s).html"
CSV_FILE="/tmp/dir_report_$(date +%s).csv"
SEND_MODE="inline"

# -------- PARSE ARGUMENTS --------
if [[ "$1" == "--attach" ]]; then
  SEND_MODE="attach"
fi

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

# -------- INIT CSV --------
echo "Directory,Permissions,Links,Owner,Group,Size,Date,Time,Filename" > "$CSV_FILE"

# -------- FUNCTION TO ADD DIRECTORY REPORTS --------
list_dir_contents() {
    local dir="$1"

    ## HTML SECTION
    echo "<h2>$dir</h2>" >> "$HTML_FILE"
    echo "<table>" >> "$HTML_FILE"
    echo "<tr><th>Permissions</th><th>Links</th><th>Owner</th><th>Group</th><th>Size</th><th>Date</th><th>Time</th><th>Filename</th></tr>" >> "$HTML_FILE"

    # List non-hidden files only
    ls -ltrh "$dir" | grep -v '^total' | grep -v '/\.' | while read -r perm links owner group size date time filename; do
        # HTML row
        echo "<tr><td>$perm</td><td>$links</td><td>$owner</td><td>$group</td><td>$size</td><td>$date</td><td>$time</td><td>$filename</td></tr>" >> "$HTML_FILE"
        # CSV row
        echo "\"$dir\",\"$perm\",\"$links\",\"$owner\",\"$group\",\"$size\",\"$date\",\"$time\",\"$filename\"" >> "$CSV_FILE"
    done

    echo "</table>" >> "$HTML_FILE"
}

# -------- GENERATE REPORTS --------
find "$ROOT_DIR" -type d ! -path '*/.*' | while read dir; do
    list_dir_contents "$dir"
done

echo "</body></html>" >> "$HTML_FILE"

# -------- SEND EMAIL --------
if command -v mailx >/dev/null 2>&1; then
  if [[ "$SEND_MODE" == "inline" ]]; then
    mailx -s "$EMAIL_SUBJECT" -S "content-type=text/html" -a "$CSV_FILE" "$EMAIL_TO" < "$HTML_FILE"
  else
    echo "Directory report attached." | mailx -s "$EMAIL_SUBJECT" -a "$HTML_FILE" -a "$CSV_FILE" "$EMAIL_TO"
  fi
else
  echo "❌ mailx not installed or not configured."
  exit 1
fi

# -------- CLEANUP --------
rm -f "$HTML_FILE" "$CSV_FILE"
