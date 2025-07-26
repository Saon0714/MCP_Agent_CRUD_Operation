# MCP_Agent_CRUD_Operation

An intelligent conversational database management system that enables natural language interactions with MySQL databases using OpenAI's GPT-4 Turbo and Model Context Protocol (MCP).

## Features

- Natural language interface for MySQL database operations
- Uses OpenAI GPT-4 Turbo for intelligent query understanding
- Secure execution of SQL queries
- Easily extensible with custom MCP tools
- Connection testing utility

## Requirements

- Python 3.8+
- MySQL server
- OpenAI API key (for GPT-4 Turbo)
- pip packages: `mysql-connector-python`, `loguru`, `mcp` (and dependencies)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MCP_Agent_CRUD_Operation.git
   cd MCP_Agent_CRUD_Operation
   ```

2. **Install dependencies:**
   ```bash
   pip install mysql-connector-python loguru mcp
   ```

3. **Configure MySQL:**
   - Ensure a MySQL server is running.
   - Create a database named `ai_agent` (or update the code to use your database).
   - Update the credentials in `mcp_server.py` if needed.

## Usage

1. **Start the MCP server:**
   ```bash
   python mcp_server.py
   ```

2. **Test MySQL connection:**
   - The server will automatically test the connection on startup.

3. **Interact with the server:**
   - Use the MCP protocol (e.g., via compatible clients or tools) to send natural language queries or SQL commands.

## Example

```python
from mcp.client import MCPClient

client = MCPClient("Demo")
response = client.query_data("SELECT * FROM your_table;")
print(response)
```

## Customization

- Add new tools by decorating Python functions with `@mcp.tool()`.
- Modify database credentials in `mcp_server.py` as needed.

## Security

- Only trusted users should have access to the server.
- Validate or sanitize SQL queries as needed for your use case.

## License

MIT License

## Acknowledgements

- [OpenAI](https://openai.com/)
- [Model Context Protocol (MCP)](https://github.com/modelcontext/mcp)
