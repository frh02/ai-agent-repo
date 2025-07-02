from mcp.clients import MCPClient
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def main():
    # Connect to the MCP server
    client = MCPClient()
    await client.connect("stdio")  # or "sse" if using SSE transport
    
    try:
        # Test the Slack connection first
        print("Testing Slack connection...")
        result = await client.invoke("test_slack_connection")
        if not result["success"]:
            print(f"❌ Slack connection failed: {result['error']}")
            return

        # Read a Medium story
        url = "https://medium.com/data-science/developers-documentation-to-openapi-specification-d73a0c19e86c"
        print(f"\nReading Medium story from: {url}")
        content = await client.invoke("read_medium_story", {"url": url})
        
        if not content or "Error" in content:
            print(f"❌ Failed to read Medium story: {content}")
            return
            
        # Send the content to Slack
        print("\nSending story to Slack...")
        result = await client.invoke("send_to_slack", {
            "message": f"📢 Medium Story Content:\n\n{content}",
            "channel": "#ai-notifications-medium"
        })
        
        if result["success"]:
            print(f"✅ Message sent successfully to {result['channel']}")
        else:
            print(f"❌ Failed to send message: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
