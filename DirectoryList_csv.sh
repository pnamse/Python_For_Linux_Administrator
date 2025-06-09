#!/bin/bash

# -------- CONFIGURATION --------
ROOT_DIR="/your/target/directory"       # 🔁 Set this to your desired root
EMAIL_TO="recipient@example.com"        # 📧 Set recipient email
EMAIL_SUBJECT="📁 CSV Directory Report - $(date '+%Y-%m-%d %H:%M')"
CSV_FILE="/tmp/dir_report_$(date +%s).csv"

# -------- INIT CSV HEADER --------
echo "Directory,Permissions,Links,Owner,Group,Size,Date,Time,FullPath" > "$CSV_FILE"

# -------- FUNCTION TO LIST FILES --------
list_dir_contents() {
    local dir="$1"

    find "$dir" -mindepth 1 -maxdepth 1 -type f ! -name ".*" | while read -r filepath; do
        if [[ -f "$filepath" ]]; then
            stat_output=$(stat -c "%A %h %U %G %s %y" "$filepath")
            read -r perm links owner group size datetime <<< "$stat_output"
            date_val=$(echo "$datetime" | cut -d' ' -f1)
            time_val=$(echo "$datetime" | cut -d' ' -f2)
            echo "\"$dir\",\"$perm\",\"$links\",\"$owner\",\"$group\",\"$size\",\"$date_val\",\"$time_val\",\"$filepath\"" >> "$CSV_FILE"
        fi
    done
}

# -------- GENERATE REPORT --------
find "$ROOT_DIR" -type d ! -path '*/.*' | while read dir; do
    list_dir_contents "$dir"
done

# -------- SEND EMAIL --------
if command -v mailx >/dev/null 2>&1; then
    echo "Directory CSV report attached." | mailx -s "$EMAIL_SUBJECT" -a "$CSV_FILE" "$EMAIL_TO"
else
    echo "❌ mailx not found or not configured."
    exit 1
fi

# -------- CLEANUP (Optional) --------
# rm -f "$CSV_FILE"
