# 📧 Email Automation MCP Server

An MCP (Model Context Protocol) server that enables AI assistants like Claude to send, search, and manage emails autonomously through standard IMAP/SMTP — works with Gmail, Outlook, and any standard email provider.

## Tech Stack

- **Python** + **FastMCP** for MCP server
- **SMTP** for sending emails
- **IMAP** for reading/searching emails
- Compatible with **Claude Desktop**, **Cursor**, and any MCP-enabled client

## Tools Exposed

| Tool | Description |
|---|---|
| `tool_send_email` | Send an email to one or more recipients |
| `tool_send_email_with_attachment` | Send email with a file attached |
| `tool_list_emails` | List recent emails from a folder |
| `tool_search_emails` | Search emails by keyword or sender |
| `tool_get_email` | Read full content of an email by ID |
| `tool_create_draft` | Save a draft without sending |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in your email credentials

# 3. Run the MCP server
python server.py
```

## Environment Variables

```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password     # Gmail: use App Password, not main password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
```

> **Gmail users**: Enable 2FA and create an [App Password](https://myaccount.google.com/apppasswords) for `EMAIL_PASSWORD`.

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "email-automation": {
      "command": "python",
      "args": ["/path/to/email-automation-mcp/server.py"]
    }
  }
}
```

## Example Usage (via Claude)

Once connected, you can ask Claude:
- *"Send an email to manager@company.com about the project status update"*
- *"Search my inbox for emails from the client about invoice"*
- *"Draft an email to the team about tomorrow's meeting"*
