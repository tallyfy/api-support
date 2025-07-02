# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a public support repository for developers using the Tallyfy API. It serves as:
- A place for developers to report API issues and questions
- A resource for sample code and utilities
- A security vulnerability reporting channel

## Key Resources

- **API Documentation**: https://go.tallyfy.com/api
- **Support Documentation**: https://support.tallyfy.com
- **General Information**: https://tallyfy.com

## Development Commands

The repository contains Python utility scripts for backing up Tallyfy blueprints:

```bash
# Install dependencies
pip3 install requests

# Run export script
python3 "Backup Blueprints/export_blueprints.py"

# Run import script
python3 "Backup Blueprints/import_blueprints.py"
```

## Architecture and Code Structure

### API Integration Pattern

The Python scripts demonstrate interaction with Tallyfy's REST API:

1. **Authentication**: Bearer token authentication stored in `credentials.txt`:
   ```
   organization_id:{org_id}
   access_token:{token}
   ```

2. **Key API Endpoint**: 
   - `https://api.tallyfy.com/organizations/{org_id}/checklists`
   - GET: Retrieve blueprints (with pagination support)
   - POST: Create new blueprints

3. **Request Headers**:
   ```python
   headers = {
       'Accept': 'application/json',
       'Authorization': 'Bearer {access_token}'
   }
   ```

4. **Pagination Handling**: Check `meta.pagination` in responses and follow `links.next`

5. **Blueprint Import**: Remove system-generated fields before importing:
   - id, owner_id, created_by, alias, steps_count, industry_tags, topic_tags
   - folder_id, kickoff_title, kickoff_description, started_processes
   - created_at, last_updated, archived_at

## Issue Reporting Guidelines

When reporting API issues, include:
- URL (with identifiers replaced by `{org_id}`, `{user_id}`, etc.)
- HTTP Verb (GET, POST, UPDATE, DELETE)
- Request payload and headers
- Response and response code

## Security

Report security vulnerabilities via SECURITY.md process, not as public issues.