MCP based implementation of MS Paint

Created MS Paint server based on MCP Protocol with two tools: Draw Rectangle and Add Text.

Provide input query such as: "Draw a rectangle on mspaint of size 500*200 and write 'Hello from Gemini!' inside it."

For this implementation change query in the paint_client.py:

if name == "main":

query = """Draw a rectangle on mspaint of size 500*200 and write 'Hello from Gemini!' inside it."""

response = asyncio.run(main(query = query))
print(f"\nFinal response from main: {response}")
Operate this when inside "src" directory

Run client with command: uv run clients/paint_client.py

You will need to set your .env file with GEMINI_API_KEY