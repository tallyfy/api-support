# Bulk Exports

Python scripts for bulk exporting Tallyfy data via the API.

## Setup

1. Copy `credentials.txt.template` to `credentials.txt`
2. Add your organization ID and access token
3. Install dependencies: `pip3 install requests`

## Scripts

### export_processes_csv.py

Exports all processes (runs) from your organization to CSV format.

**Usage:**
```bash
# Export all processes
python3 export_processes_csv.py

# Export only active processes
python3 export_processes_csv.py --status active

# Export only completed processes
python3 export_processes_csv.py --status complete

# Export processes from a specific template
python3 export_processes_csv.py --template YOUR_TEMPLATE_ID

# Custom output file
python3 export_processes_csv.py --output my_export.csv
```

**Output:**
- Creates CSV file in `exports/` directory
- One row per task in each process
- 49-column structure matching Tallyfy's native export format

**CSV Columns:**

| Group | Columns |
|-------|---------|
| Process Info (1-13) | name, id, status, created_at, completed_at, template_name, template_id, url, started_by, tags, summary, deadline, prerun_status |
| Task Info (14-27) | name, id, position, status, status_label, type, deadline, created_at, completed_at, started_at, is_approved, url, description, everyone_must_complete |
| Assignment (28-36) | assignees, assignee_count, guests, guest_count, groups, completer, completer_type, time_to_complete, overdue |
| Form Fields (37-40) | count, json, summary, has_file_uploads |
| Comments/Issues (41-49) | comments_count, has_issues, issues_count, last_comment, watchers_count, step_id, is_one_off, can_complete_only_assignees, is_completable |

## Getting Your Credentials

1. Log into Tallyfy
2. Navigate to Settings > Integrations > API Access
3. Copy your organization ID and access token

## Related Documentation

- [CSV Export Guide](https://tallyfy.com/products/pro/tracking-and-tasks/processes/how-can-i-export-tallyfy-processes-to-csv/)
- [CSV Structure Reference](https://tallyfy.com/products/pro/integrations/analytics/how-is-the-csv-file-structured-in-tallyfy/)
- [API Documentation](https://go.tallyfy.com/api)
