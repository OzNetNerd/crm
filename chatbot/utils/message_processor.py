"""Simple message processing utilities."""

from fastapi import WebSocket


async def handle_streaming_response(
    response_data: dict, websocket: WebSocket, ws_manager
):
    """Handle streaming response from chat handler."""
    stream = response_data["stream"]
    full_response = ""

    async for chunk in stream:
        if chunk["type"] == "chunk":
            # Send streaming chunk to client
            await ws_manager.send_message(
                {"type": "streaming_chunk", "text": chunk["text"]}, websocket
            )
            full_response += chunk["text"]

    # Send streaming complete signal
    await ws_manager.send_message(
        {"type": "streaming_complete", "message": full_response}, websocket
    )

    return full_response


async def handle_regular_response(response_text: str, websocket: WebSocket, ws_manager):
    """Handle non-streaming response."""
    await ws_manager.send_message(
        {"type": "bot_response", "message": response_text}, websocket
    )
