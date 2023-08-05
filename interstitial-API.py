import asyncio
import httpx
import json
import logging
import time
from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse, FileResponse

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("api")

@app.post("/v1/chat/completions")
async def chat_completions(data: dict):
    try:
        modified_data = add_system_messages(data)
        logger.info(f"Sending data to destination API: {modified_data}")
        client = httpx.AsyncClient()

        async def content_generator():
            async with client.stream('POST', 'http://localhost:6789/v1/chat/completions', json=modified_data, timeout=180.0) as response:
                logger.info(f"Received response from destination API: {response.status_code}")

                if response.status_code != 200:
                    yield f"Error: {response.content}".encode()
                    return

                async for chunk in response.aiter_text():
                    try:
                        logger.debug(f"Received chunk from destination API: {chunk}")
                        yield chunk.encode()
                    except GeneratorExit:
                        logger.info("Client disconnected, closing stream.")
                        return

        return StreamingResponse(content_generator(), media_type="text/plain")
    except asyncio.TimeoutError:
        logger.error("The request to the destination API timed out.")
        return {"error": "The request timed out."}
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return {"error": str(e)}

def add_system_messages(data: dict) -> dict:
    messages = data.get('messages', [])
    if messages:
        last_user_msg_index = next(
            (i for i, msg in reversed(list(enumerate(messages))) if msg.get('role') == 'user'),
            None
        )
        if last_user_msg_index is not None:
            messages.insert(last_user_msg_index, {"content": "### Instructions:", "role": "system"})
            messages.insert(last_user_msg_index + 2, {"content": "### Response:", "role": "system"})
    return data


@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/v1/models")
async def models():
    data = {
        "max_tokens": 1,
        "messages": [{"content": "confirm receipt", "role": "user"}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:6789/v1/chat/completions', json=data, timeout=30.0)
        response_json = response.json()
        model_value = response_json.get('model')
        desired_string = model_value.split('/')[-1].split('.')[0]

        response_data = {
            "object": "list",
            "data": [{
                "id": desired_string,
                "object": "model",
                "created": 1683758102,
                "owned_by": "sanjai",
                "permission": [{
                    "id": "modelperm",
                    "object": "model_permission",
                    "created": 1690866609,
                    "allow_create_engine": False,
                    "allow_sampling": True,
                    "allow_logprobs": True,
                    "allow_search_indices": False,
                    "allow_view": True,
                    "allow_fine_tuning": False,
                    "organization": "*",
                    "group": None,
                    "is_blocking": False
                }],
                "root": desired_string,
                "parent": None
            }]
        }

        logger.info(f"Response data: {response_data}")

        return response_data

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")
