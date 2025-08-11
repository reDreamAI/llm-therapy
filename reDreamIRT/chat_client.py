import asyncio
import aiohttp
import sys
import uuid
import json


async def stream_chat():
    """Streaming chat client"""
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())  # Generate single user ID per session
    print("\nStreaming Chat initialized. Type 'quit' to exit.")
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")  # Show user ID like regular chat
    print("-" * 75)

    async with aiohttp.ClientSession() as session:
        while True:
            message = input("User: ").strip()
            print("-" * 75)

            if message.lower() == "quit":
                break

            try:
                for attempt in range(3):  # Add retry loop
                    try:
                        async with session.post(
                            "http://localhost:8000/chat/stream",
                            json={
                                "session_id": session_id,
                                "message": message,
                                "user_id": user_id,  # Reuse same user ID
                            },
                        ) as response:
                            if response.status != 200:
                                print(
                                    f"Error: Server returned status {response.status}"
                                )
                                continue

                            print("AI: ", end="", flush=True)
                            stages = []
                            async for line in response.content:
                                line = line.decode("utf-8")
                                if line.startswith("data: "):
                                    data = line[6:]
                                    if data.strip() == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data)
                                        if "content" in chunk:
                                            print(chunk["content"], end="", flush=True)
                                        if "stages" in chunk:
                                            stages = chunk["stages"]
                                    except json.JSONDecodeError:
                                        print(f"\nError decoding response: {data}")
                            break  # Successful completion

                    except (aiohttp.ClientError, json.JSONDecodeError) as e:
                        if attempt < 2:  # 0,1,2 = 3 attempts
                            print(f"Connection error (retry {attempt + 1}/3): {str(e)}")
                            await asyncio.sleep(1)
                        else:
                            raise

                print(f"\n| Stages: {' → '.join(stages)}")
                print("-" * 75)

            except Exception as e:
                print(f"Error: {str(e)}")
                print("-" * 75)


async def regular_chat():
    """Non-streaming chat client"""
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    print("\nChat initialized. Type 'quit' to exit.")
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    print("-" * 75)

    timeout = aiohttp.ClientTimeout(total=60)

    async def make_request(session, message, retries=3):
        for attempt in range(retries):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": message,
                }

                async with session.post(
                    "http://localhost:8000/chat", json=request_data, timeout=timeout
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    print(
                        f"Server error (status {response.status}): {await response.text()}"
                    )

            except aiohttp.ClientError as e:
                print(f"Connection error (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise

    async with aiohttp.ClientSession() as session:
        while True:
            message = input("User: ").strip()
            print("-" * 75)

            if message.lower() == "quit":
                break

            try:
                data = await make_request(session, message)
                if data:
                    print(f"AI: {data['response']}")
                    print(f"\n| Stages: {' → '.join(data['stages'])}")
                print("-" * 75)

            except Exception as e:
                print(f"Error: {str(e)}")
                print(f"Error type: {type(e)}")
                print("-" * 75)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stream":
        asyncio.run(stream_chat())
    else:
        asyncio.run(regular_chat())
