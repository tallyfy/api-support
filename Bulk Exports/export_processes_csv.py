#!/usr/bin/env python3
"""
Tallyfy Bulk Process CSV Export

Exports all processes (runs) from a Tallyfy organization to CSV format.
The CSV structure matches Tallyfy's native export format (49 columns).

Usage:
    python3 export_processes_csv.py [--status active|complete|all] [--template TEMPLATE_ID]

Requirements:
    pip3 install requests

Credentials:
    Create a credentials.txt file with:
        organization_id:{your_org_id}
        access_token:{your_access_token}
"""

import requests
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "https://api.tallyfy.com"
OUTPUT_DIR = "exports"

def read_credentials():
    """Read organization ID and access token from credentials.txt"""
    credentials_path = Path(__file__).parent / "credentials.txt"
    if not credentials_path.exists():
        print("ERROR: credentials.txt not found")
        print("Create a file with:")
        print("  organization_id:{your_org_id}")
        print("  access_token:{your_access_token}")
        sys.exit(1)

    org_id = None
    access_token = None

    with open(credentials_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("organization_id:"):
                org_id = line.split(":", 1)[1].strip()
            elif line.startswith("access_token:"):
                access_token = line.split(":", 1)[1].strip()

    if not org_id or not access_token:
        print("ERROR: Missing organization_id or access_token in credentials.txt")
        sys.exit(1)

    return org_id, access_token


def get_headers(access_token):
    """Return API request headers"""
    return {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'X-Tallyfy-Client': 'APIClient'
    }


def fetch_all_processes(org_id, headers, status_filter=None, template_filter=None):
    """
    Fetch all processes from the organization with pagination support.

    Args:
        org_id: Organization ID
        headers: Request headers
        status_filter: Optional filter - 'active', 'complete', or None for all
        template_filter: Optional template ID to filter by

    Returns:
        List of process objects
    """
    processes = []
    api_url = f"{API_BASE}/organizations/{org_id}/runs"

    params = {"with": "tasks,checklist"}
    if status_filter and status_filter != "all":
        params["status"] = status_filter
    if template_filter:
        params["checklist_id"] = template_filter

    print(f"Fetching processes from {org_id}...")
    page = 1

    while api_url:
        print(f"  Page {page}...", end=" ")
        response = requests.get(api_url, headers=headers, params=params if page == 1 else None)

        if response.status_code != 200:
            print(f"\nERROR: API returned {response.status_code}")
            print(response.text)
            break

        data = response.json()
        page_processes = data.get('data', [])
        processes.extend(page_processes)
        print(f"found {len(page_processes)} processes")

        # Handle pagination
        pagination = data.get('meta', {}).get('pagination', {})
        if pagination.get('current_page', 0) < pagination.get('total_pages', 0):
            api_url = pagination.get('links', {}).get('next')
            page += 1
        else:
            api_url = None

    print(f"Total processes fetched: {len(processes)}")
    return processes


def fetch_process_details(org_id, run_id, headers):
    """Fetch full details for a single process including tasks and form fields"""
    api_url = f"{API_BASE}/organizations/{org_id}/runs/{run_id}"
    params = {"with": "tasks,tasks.captures,checklist"}

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('data', {})
    return None


def format_datetime(dt_string):
    """Format ISO datetime to readable format"""
    if not dt_string:
        return ""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_string


def process_to_csv_rows(process, org_id, headers):
    """
    Convert a process to CSV rows.

    Returns one row per task in the process.
    Matches Tallyfy's native 49-column CSV structure.
    """
    rows = []

    # Get process-level data
    process_name = process.get('name', '')
    process_id = process.get('id', '')
    process_status = process.get('status', '')
    process_created = format_datetime(process.get('created_at', ''))
    process_completed = format_datetime(process.get('completed_at', ''))

    # Get template data
    checklist = process.get('checklist', {}) or {}
    template_name = checklist.get('title', '')
    template_id = checklist.get('id', '')

    # Get tasks
    tasks = process.get('tasks', [])
    if not tasks:
        tasks = []

    for task in tasks:
        row = {
            # Process info (columns 1-13)
            'process_name': process_name,
            'process_id': process_id,
            'process_status': process_status,
            'process_created_at': process_created,
            'process_completed_at': process_completed,
            'template_name': template_name,
            'template_id': template_id,
            'process_url': f"https://go.tallyfy.com/organizations/{org_id}/runs/{process_id}",
            'process_started_by': process.get('starter', {}).get('email', '') if process.get('starter') else '',
            'process_tags': ','.join([t.get('title', '') for t in process.get('tags', [])]),
            'process_summary': process.get('summary', ''),
            'process_deadline': format_datetime(process.get('deadline', '')),
            'process_prerun_status': process.get('prerun_status', ''),

            # Task info (columns 14-27)
            'task_name': task.get('title', ''),
            'task_id': task.get('id', ''),
            'task_position': task.get('position', ''),
            'task_status': task.get('status', ''),
            'task_status_label': task.get('status_label', task.get('status', '')),
            'task_type': task.get('task_type', ''),
            'task_deadline': format_datetime(task.get('deadline', '')),
            'task_created_at': format_datetime(task.get('created_at', '')),
            'task_completed_at': format_datetime(task.get('completed_at', '')),
            'task_started_at': format_datetime(task.get('started_at', '')),
            'task_is_approved': str(task.get('is_approved', '')),
            'task_url': f"https://go.tallyfy.com/organizations/{org_id}/runs/{process_id}/tasks/{task.get('id', '')}",
            'task_description': task.get('summary', ''),
            'task_everyone_must_complete': str(task.get('everyone_must_complete', False)),

            # Assignment info (columns 28-36)
            'assignees': ','.join([u.get('email', '') for u in task.get('users', [])]),
            'assignee_count': len(task.get('users', [])),
            'guests': ','.join([g.get('email', '') for g in task.get('guests', [])]),
            'guest_count': len(task.get('guests', [])),
            'groups': ','.join([gr.get('name', '') for gr in task.get('groups', [])]),
            'completer': task.get('completer', {}).get('email', '') if task.get('completer') else '',
            'completer_type': 'user' if task.get('completer') else ('guest' if task.get('completer_guest_id') else ''),
            'time_to_complete_minutes': '',  # Calculated field
            'overdue': 'yes' if task.get('deadline') and task.get('status') != 'completed' and task.get('deadline') < datetime.now().isoformat() else 'no',

            # Form field info (columns 37-40)
            'form_fields_count': len(task.get('captures', [])),
            'form_fields_json': json.dumps(task.get('captures', [])),
            'form_fields_summary': '; '.join([f"{c.get('alias', '')}: {c.get('value', '')}" for c in task.get('captures', []) if c.get('value')]),
            'has_file_uploads': 'yes' if any(c.get('field_type') == 'file' for c in task.get('captures', [])) else 'no',

            # Comments and issues (columns 41-49)
            'comments_count': task.get('comments_count', 0),
            'has_issues': 'yes' if task.get('has_issues') else 'no',
            'issues_count': task.get('issues_count', 0),
            'last_comment': '',  # Would need separate API call
            'watchers_count': len(task.get('watchers', [])),
            'step_id': task.get('step_id', ''),
            'is_one_off_task': 'yes' if not task.get('step_id') else 'no',
            'can_complete_only_assignees': str(task.get('can_complete_only_assignees', False)),
            'is_completable': str(task.get('is_completable', True))
        }
        rows.append(row)

    # If no tasks, still create one row for the process
    if not rows:
        row = {
            'process_name': process_name,
            'process_id': process_id,
            'process_status': process_status,
            'process_created_at': process_created,
            'process_completed_at': process_completed,
            'template_name': template_name,
            'template_id': template_id,
            'process_url': f"https://go.tallyfy.com/organizations/{org_id}/runs/{process_id}",
            'process_started_by': process.get('starter', {}).get('email', '') if process.get('starter') else '',
            'process_tags': ','.join([t.get('title', '') for t in process.get('tags', [])]),
            'process_summary': process.get('summary', ''),
            'process_deadline': format_datetime(process.get('deadline', '')),
            'process_prerun_status': process.get('prerun_status', ''),
            'task_name': '(No tasks)',
            'task_id': '',
            'task_position': '',
            'task_status': '',
            'task_status_label': '',
            'task_type': '',
            'task_deadline': '',
            'task_created_at': '',
            'task_completed_at': '',
            'task_started_at': '',
            'task_is_approved': '',
            'task_url': '',
            'task_description': '',
            'task_everyone_must_complete': '',
            'assignees': '',
            'assignee_count': 0,
            'guests': '',
            'guest_count': 0,
            'groups': '',
            'completer': '',
            'completer_type': '',
            'time_to_complete_minutes': '',
            'overdue': '',
            'form_fields_count': 0,
            'form_fields_json': '[]',
            'form_fields_summary': '',
            'has_file_uploads': 'no',
            'comments_count': 0,
            'has_issues': 'no',
            'issues_count': 0,
            'last_comment': '',
            'watchers_count': 0,
            'step_id': '',
            'is_one_off_task': '',
            'can_complete_only_assignees': '',
            'is_completable': ''
        }
        rows.append(row)

    return rows


def export_to_csv(processes, org_id, headers, output_file=None):
    """
    Export processes to a single combined CSV file.

    Args:
        processes: List of process objects
        org_id: Organization ID (for URLs)
        headers: API headers (for detail fetches if needed)
        output_file: Output filename (default: exports/processes_{timestamp}.csv)
    """
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(OUTPUT_DIR, f"processes_{timestamp}.csv")

    # CSV column order (49 columns)
    fieldnames = [
        # Process info (1-13)
        'process_name', 'process_id', 'process_status', 'process_created_at',
        'process_completed_at', 'template_name', 'template_id', 'process_url',
        'process_started_by', 'process_tags', 'process_summary', 'process_deadline',
        'process_prerun_status',
        # Task info (14-27)
        'task_name', 'task_id', 'task_position', 'task_status', 'task_status_label',
        'task_type', 'task_deadline', 'task_created_at', 'task_completed_at',
        'task_started_at', 'task_is_approved', 'task_url', 'task_description',
        'task_everyone_must_complete',
        # Assignment info (28-36)
        'assignees', 'assignee_count', 'guests', 'guest_count', 'groups',
        'completer', 'completer_type', 'time_to_complete_minutes', 'overdue',
        # Form field info (37-40)
        'form_fields_count', 'form_fields_json', 'form_fields_summary', 'has_file_uploads',
        # Comments and issues (41-49)
        'comments_count', 'has_issues', 'issues_count', 'last_comment',
        'watchers_count', 'step_id', 'is_one_off_task', 'can_complete_only_assignees',
        'is_completable'
    ]

    all_rows = []
    total = len(processes)

    print(f"\nProcessing {total} processes...")
    for i, process in enumerate(processes, 1):
        print(f"  [{i}/{total}] {process.get('name', 'Unnamed')[:50]}...")
        rows = process_to_csv_rows(process, org_id, headers)
        all_rows.extend(rows)

    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✓ Exported {len(all_rows)} rows to: {output_file}")
    print(f"  Processes: {total}")
    print(f"  Tasks: {len(all_rows)}")

    return output_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Export Tallyfy processes to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 export_processes_csv.py                    # Export all processes
    python3 export_processes_csv.py --status active    # Export only active processes
    python3 export_processes_csv.py --status complete  # Export only completed processes
    python3 export_processes_csv.py --template ABC123  # Export processes from specific template
        """
    )
    parser.add_argument('--status', choices=['active', 'complete', 'all'], default='all',
                        help='Filter by process status (default: all)')
    parser.add_argument('--template', type=str, default=None,
                        help='Filter by template ID')
    parser.add_argument('--output', type=str, default=None,
                        help='Output filename (default: exports/processes_{timestamp}.csv)')

    args = parser.parse_args()

    # Read credentials
    org_id, access_token = read_credentials()
    headers = get_headers(access_token)

    # Fetch processes
    processes = fetch_all_processes(org_id, headers, args.status, args.template)

    if not processes:
        print("No processes found matching criteria")
        return

    # Export to CSV
    export_to_csv(processes, org_id, headers, args.output)


if __name__ == "__main__":
    main()
