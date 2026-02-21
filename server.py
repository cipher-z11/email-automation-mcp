"""
Email Automation MCP Server
Allows AI assistants to send, draft, and manage emails autonomously.
"""
from mcp.server.fastmcp import FastMCP
from tools.email_tools import (
    send_email,
    send_email_with_attachment,
    list_emails,
    search_emails,
    get_email_by_id,
    create_draft,
)

mcp = FastMCP(
    name="email-automation",
    description="MCP server for autonomous email operations — send, draft, search, and read emails.",
)

# ── Register tools ────────────────────────────────────────────────────────────

@mcp.tool()
async def tool_send_email(to: str, subject: str, body: str, cc: str = "") -> dict:
    """
    Send an email to one or more recipients.

    Args:
        to: Recipient email address (or comma-separated list)
        subject: Email subject line
        body: Email body content (plain text or HTML)
        cc: Optional CC recipients (comma-separated)

    Returns:
        dict with status and message_id
    """
    return await send_email(to=to, subject=subject, body=body, cc=cc)


@mcp.tool()
async def tool_send_email_with_attachment(
    to: str, subject: str, body: str, file_path: str, cc: str = ""
) -> dict:
    """
    Send an email with a file attachment.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        file_path: Absolute path to the file to attach
        cc: Optional CC recipients
    """
    return await send_email_with_attachment(to=to, subject=subject, body=body, file_path=file_path, cc=cc)


@mcp.tool()
async def tool_list_emails(folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """
    List recent emails from a folder.

    Args:
        folder: Email folder name (INBOX, SENT, DRAFTS, SPAM)
        limit: Max number of emails to return (default 10, max 50)
    """
    return await list_emails(folder=folder, limit=min(limit, 50))


@mcp.tool()
async def tool_search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """
    Search emails by keyword, sender, or subject.

    Args:
        query: Search query string (e.g., "from:boss@company.com", "invoice")
        folder: Folder to search in
        limit: Max results to return
    """
    return await search_emails(query=query, folder=folder, limit=limit)


@mcp.tool()
async def tool_get_email(message_id: str) -> dict:
    """
    Get full content of a specific email by its message ID.

    Args:
        message_id: The unique message ID (from list_emails results)
    """
    return await get_email_by_id(message_id=message_id)


@mcp.tool()
async def tool_create_draft(to: str, subject: str, body: str) -> dict:
    """
    Save an email as a draft without sending it.

    Args:
        to: Recipient email address
        subject: Draft subject
        body: Draft body content
    """
    return await create_draft(to=to, subject=subject, body=body)


if __name__ == "__main__":
    mcp.run()
