import mysql.connector
from loguru import logger
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely on MySQL database."""
    logger.info(f"Executing SQL query: {sql}")
    print("the sql query:",sql)
    conn = None
    cursor = None
    try:
        # Establish the connection
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='P@sssw0rd',
            database='ai_agent'
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        return "\n".join(str(row) for row in result)
    except mysql.connector.Error as e:
        return f"Error: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Add a specific function to test connection
@mcp.tool()
def test_connection() -> str:
    """Test if MySQL connection is working properly."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='P@sssw0rd',
            database='ai_agent'
        )
        if conn.is_connected():
            server_info = conn.get_server_info()
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return f"Successfully connected to MySQL Server version {server_info}\nDatabase: {database_name}"
        else:
            return "Connection failed"
    except mysql.connector.Error as e:
        return f"Error connecting to MySQL: {str(e)}"

@mcp.prompt()
def example_prompt(code: str) -> str:
    return f"Please review this code:\n\n{code}"

if __name__ == "__main__":
    print("Starting server...")
    print("Testing MySQL connection...")
    # Test connection before starting server
    connection_result = test_connection()
    print(connection_result)
    # Initialize and run the server
    mcp.run(transport="stdio")