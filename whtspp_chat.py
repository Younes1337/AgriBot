from dotenv import load_dotenv #type: ignore
load_dotenv()

from fastapi import FastAPI, Request #type: ignore
from fastapi.responses import JSONResponse, PlainTextResponse #type: ignore
import os
import httpx #type: ignore


############################ ENV variables ############################
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v17.0")
##############################################################################


async def send_message(to_number: str, message: str):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    playload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "text": {
            "body": message
        }
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=playload)
        return response.status_code, response.json()


app = FastAPI()

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return PlainTextResponse(content=challenge, status_code=200)
    
    return PlainTextResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return JSONResponse(content="No messages to process", status_code=200)
        
        message = messages[0]
        sender = message.get("from")

        if sender:
            status, body = await send_message(sender, "Welcome in AgriBot how can i help you?")
        
        return JSONResponse(content={"status": "ok"}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    