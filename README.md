<img width="187" alt="screen shot 2018-08-02 at 13 24 28" src="https://user-images.githubusercontent.com/6051207/43603188-ddb415d0-9657-11e8-8ec0-32d60a4c2fef.png">

# Tallyfy API Support

This is a public repository aimed specifically at developers using the Tallyfy API. 

## About Tallyfy

Tallyfy is an AI-powered workflow management platform with the mission to "Run AI-powered operations and save 2 hours per person every day." Our API-first architecture means the web application itself uses the same public REST API available to developers.

**Core Products:**
- **[Tallyfy Pro](https://tallyfy.com/products/pro/)**: Complete workflow automation platform
- **[Tallyfy Answers](https://tallyfy.com/products/answers/)**: AI-powered search solution with vector database
- **[Tallyfy Denizen](https://tallyfy.com/products/denizen/)**: Location-based royalty-free photo API service  
- **[Tallyfy Manufactory](https://tallyfy.com/products/manufactory/)**: Events lifecycle engine for data science teams

Tallyfy transforms every approval, task, business process, SOP, playbook, form or document into a repeatable, predictable blueprint with AI-native automation.

## API Documentation & Resources

- **API Documentation**: https://go.tallyfy.com/api (requires authentication)
- **Product Information**: https://tallyfy.com/products/
- **Support Documentation**: https://support.tallyfy.com
- **General Information**: https://tallyfy.com

## Getting Help

- **API Questions**: Please post them here as GitHub issues!
- **General Support**: Contact support@tallyfy.com
- **Security Issues**: See [SECURITY.md](SECURITY.md) for vulnerability reporting

## Quick Start for Developers

### Authentication
The Tallyfy API uses OAuth2 authentication with three methods:
1. **Personal Access Tokens**: Get from Settings > Integrations > REST API
2. **Application Tokens** (Enterprise): Client ID/Secret for server-to-server
3. **OAuth Flow** (Enterprise): Standard authorization flow

### Required Headers
```http
Accept: application/json
Authorization: Bearer {your_access_token}
X-Tallyfy-Client: APIClient
```

### Rate Limits
- 100 requests per minute per organization
- 1,000 requests per hour per organization

### API Terminology
| API Term | UI Term | Description |
|----------|---------|-------------|
| `checklists` | Blueprints | Workflow templates |
| `runs` | Processes | Active workflow instances |
| `captures` | Task form fields | Data collection points |
| `preruns` | Kick-off form fields | Process initialization data | 

# Repository Contents

## Backup Blueprints

The `Backup Blueprints` folder contains sample Python utilities for backing up and restoring your Tallyfy blueprints:

- **`export_blueprints.py`**: Export all blueprints from your organization to JSON files
- **`import_blueprints.py`**: Import blueprints from JSON files to your organization  
- **`credentials.txt`**: Template file for storing your API credentials
- **`blueprints/`**: Directory where exported blueprint JSON files are stored

### Setup Instructions

1. Install Python 3 and the required dependency:
   ```bash
   pip3 install requests
   ```

2. Configure your credentials in `credentials.txt`:
   ```
   organization_id:your_org_id_here
   access_token:your_access_token_here
   ```

3. Run the export script:
   ```bash
   python3 "Backup Blueprints/export_blueprints.py"
   ```

4. Run the import script (if needed):
   ```bash
   python3 "Backup Blueprints/import_blueprints.py"
   ```

**Note**: These are community contributions provided as examples. Test thoroughly before using in production environments.

### Important Security Notes

- Never commit actual credentials to version control
- The provided `credentials.txt` contains placeholder values only
- Use environment variables or secure configuration management for production use

## Example API Usage

### Basic Blueprint Retrieval
```python
import requests

headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer your_access_token',
    'X-Tallyfy-Client': 'APIClient'  # Required header
}

response = requests.get(
    'https://api.tallyfy.com/organizations/{org_id}/checklists', 
    headers=headers
)

blueprints = response.json()
```

### File Upload to Task
```python
# Step 1: Upload file
files = {'file': open('document.pdf', 'rb')}
upload_response = requests.post(
    'https://api.tallyfy.com/organizations/{org_id}/files',
    headers=headers,
    files=files
)
file_id = upload_response.json()['data']['id']

# Step 2: Attach to task (note the capital 'R' in 'Run')
attach_data = {
    'subject_type': 'Run',  # Case-sensitive!
    'subject_id': '{run_id}',
    'file_id': file_id
}

requests.put(
    'https://api.tallyfy.com/organizations/{org_id}/runs/{run_id}/tasks/{task_id}',
    headers=headers,
    json=attach_data
)
```

## Posting guidelines

1. No inappropriate/offensive language. We reserve the right to edit/remove any post which is deemed inappropriate or offensive by Tallyfy.

2. Check first that the issue you are reporting has not already been reported elsewhere. If it has been reported in another ticket, you may give that ticket a [+1] and/or comment additional helpful information so that we may deal with the issue in the most complete manner possible.

3. Avoid using any uniquely identifiable information in your posts/comments. This includes but is not limited to user ID's, org ID's, user emails, etc. To represent these identifiers in your tickets, we encourage you to user curly braces around the identifier’s name, such as `{org_id}` or `{user_id}`.

4. When reporting an issue, always include these pieces of information:<br>
  a. URL (with identifiers removed)<br>
  b. Verb (`GET`, `POST`, `UPDATE`, `DELETE`)<br>
  c. Request payload and headers<br>
  d. Response and response code<br>

## Example Issue Report

```markdown
**Issue**: File upload fails with validation error

**Endpoint**: `PUT /organizations/{org_id}/runs/{run_id}/tasks/{task_id}`

**Request Headers**:
```json
{
  "Accept": "application/json", 
  "Authorization": "Bearer {my_token}",
  "X-Tallyfy-Client": "APIClient",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "subject_type": "run",
  "subject_id": "{run_id}",
  "file_id": "{file_id}"
}
```

**Response**: HTTP 500 Internal Server Error

**Expected**: HTTP 200 with file successfully attached to task

**Additional Context**: File was uploaded successfully in Step 1, but attachment to task fails
```

## Common API Gotchas

Based on community experience, here are common issues to check:

1. **Missing X-Tallyfy-Client Header**: The `X-Tallyfy-Client: APIClient` header is mandatory for all requests
2. **Case-Sensitive subject_type**: Use `"Run"` (capital R), not `"run"` for file attachments  
3. **Rate Limiting**: Respect the 100 req/min and 1000 req/hour limits
4. **Pagination**: Always handle paginated responses for list endpoints
5. **Field Removal**: Remove system-generated fields before importing blueprints

## Enterprise Features

For enterprise customers, additional features are available:

- **Application Tokens**: Server-to-server authentication with client credentials
- **OAuth Flow**: Standard OAuth2 authorization for user consent
- **Webhooks**: Real-time event notifications for blueprint and process changes
- **Advanced Integrations**: Custom serverless functions and extended API access

Contact our sales team for enterprise features and pricing.

## Security and Compliance

Tallyfy maintains enterprise-grade security standards:

- **SOC 2 Type II** certified
- **GDPR** compliant  
- **Bank-grade security** with encryption at rest and in transit
- **Multi-tenant architecture** with organization-level data isolation
- **Regular security audits** and penetration testing

For security vulnerabilities, please follow our [Security Policy](SECURITY.md).

## Community and Support

- **GitHub Issues**: For API-specific questions and bug reports
- **Support Docs**: https://support.tallyfy.com for user guides
- **Product Updates**: Follow [@tallyfy](https://twitter.com/tallyfy) for announcements
- **Developer Community**: Join discussions in this repository

## API Status and Uptime

Monitor API status and uptime at our status page: https://status.tallyfy.com

For real-time API health checks, use the health endpoint:
```bash
GET https://api.tallyfy.com/health
```

---

**Tallyfy** - Run AI-powered operations and save 2 hours per person every day.

Visit [tallyfy.com](https://tallyfy.com) to learn more about our workflow automation platform.
