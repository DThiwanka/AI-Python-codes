import asyncio
import websockets
import json

async def fetch_data_from_websocket():
    url = "wss://1xbet.com/games-frame/sockets/crash?whence=50&fcountry=208&ref=1&gr=70&appGuid=games-web-app-unknown&lng=en&access_token=eyJhbGciOiJFUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiI1MC85Nzg5OTI5NDEiLCJwaWQiOiIxIiwianRpIjoiMC85MmE3MjY1ZDIyNDExNmNlZjU3Zjk2MGQ4N2U5ZTllOTc1YmU3NTQ1NTAwZGYyNjQyZDg4MDFmZGRkODIxYjE3IiwiYXBwIjoiTkEiLCJpbm5lciI6InRydWUiLCJuYmYiOjE3NDQxMDkwNTcsImV4cCI6MTc0NDEyMzQ1NywiaWF0IjoxNzQ0MTA5MDU3fQ.i7Lj3aAZWdWe_KwDi3TAk52vgUbosakmAGhvxBbaYYVYelz13rcH-5dQ9wQk1g-N8Ub8S9VyFrCXZTJ6jK7Xpg"
    
    # Headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Origin": "https://1xbet.com",
        "Referer": "https://1xbet.com/",
    }
    
    try:
        # Connect to the WebSocket server with headers
        async with websockets.connect(url, extra_headers=headers) as websocket:
            print(f"Connected to WebSocket server: {url}")
            
            # Prepare the message you want to send to the server
            # This could be a specific event or command. Replace with the actual expected message
            message = {
                "event": "join_game",  # Example of event
                "data": {"user_id": "12345", "game": "crash"}
            }
            
            # Sending the message to the server
            await websocket.send(json.dumps(message))  # Send as JSON
            
            # Wait for a response from the server
            response = await websocket.recv()
            print(f"Received message: {response}")
            
            # You can process the response as needed
            response_data = json.loads(response)
            print(f"Parsed Response: {response_data}")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the WebSocket connection
asyncio.get_event_loop().run_until_complete(fetch_data_from_websocket())
