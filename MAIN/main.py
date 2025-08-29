import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Forcefully point to MAIN/
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

print("TEMPLATE_DIR >>>", TEMPLATE_DIR)  # debug
print("STATIC_DIR >>>", STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Mount static + templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI App
app = FastAPI()

# Directories
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# REMOVED: Global Gemini model initialization and dotenv loading

async def get_llm_response_stream(transcript: str, client_websocket: WebSocket, chat_history: List[dict], gemini_model, murf_key):
    if not transcript or not transcript.strip():
        return

    if not gemini_model:
        logging.error("Cannot get LLM response because Gemini model is not initialized.")
        return

    logging.info(f"Sending to Gemini with history: '{transcript}'")
    
    # Use the provided Murf key
    murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={murf_key}&sample_rate=44100&channel_type=MONO&format=MP3"
    
    try:
        async with websockets.connect(murf_uri) as websocket:
            voice_id = "en-US-natalie"
            logging.info(f"Successfully connected to Murf AI, using voice: {voice_id}")
            
            context_id = f"voice-agent-context-{datetime.now().isoformat()}"
            
            config_msg = {
                "voice_config": {"voiceId": voice_id, "style": "Conversational"},
                "context_id": context_id
            }
            await websocket.send(json.dumps(config_msg))

            async def receive_and_forward_audio():
                first_audio_chunk_received = False
                while True:
                    try:
                        response_str = await websocket.recv()
                        response = json.loads(response_str)

                        if "audio" in response and response['audio']:
                            if not first_audio_chunk_received:
                                await client_websocket.send_text(json.dumps({"type": "audio_start"}))
                                first_audio_chunk_received = True
                                logging.info("✅ Streaming first audio chunk to client.")

                            base_64_chunk = response['audio']
                            await client_websocket.send_text(
                                json.dumps({"type": "audio", "data": base_64_chunk})
                            )

                        if response.get("final"):
                            logging.info("Murf confirms final audio chunk received. Sending audio_end to client.")
                            await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                            break
                    except websockets.ConnectionClosed:
                        logging.warning("Murf connection closed unexpectedly.")
                        await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                        break
                    except Exception as e:
                        logging.error(f"Error in Murf receiver task: {e}")
                        break
            
            receiver_task = asyncio.create_task(receive_and_forward_audio())

            try:
                prompt = f"""You are Vaani, a sarcastic AI voice assistant. 
                
                Your personality:
                
                - You always give correct and useful answers, but with a witty, sarcastic edge.
                - You must remember the history of the conversation to maintain context.
                - Be playful, sharp, and occasionally mocking the user (but never offensive).
                - You may only use mild sarcasm, nothing too harsh or mean-spirited.
                - You may not reply in more than 2 sentences.
                - You may not ask the user any questions.
                - Use dry humor and sarcasm in every reply.
                - Still be helpful — the sarcasm should make the answers entertaining, not useless.

                Context about you:
                - Your owner and creator is Radhika.
                - Radhika is a computer science student from Surat.
                - His main hobby is Cooking.
                - You can use this info only if the user asks about you or your creator.

                Continue the conversation based on the provided chat history. The user has just said: "{transcript}"

                Your response should be concise, witty, and sarcastic, as if you were speaking.
                IMPORTANT: Do not use any markdown formatting. Provide only plain text.
                """

                
                chat_history.append({"role": "user", "parts": [prompt]})
                
                chat = gemini_model.start_chat(history=chat_history[:-1])

                def generate_sync():
                    return chat.send_message(prompt, stream=True)

                loop = asyncio.get_running_loop()
                gemini_response_stream = await loop.run_in_executor(None, generate_sync)

                sentence_buffer = ""
                full_response_text = ""
                print("\n--- Vaani (GEMINI) STREAMING RESPONSE ---")
                for chunk in gemini_response_stream:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response_text += chunk.text

                        await client_websocket.send_text(
                            json.dumps({"type": "llm_chunk", "data": chunk.text})
                        )
                        
                        sentence_buffer += chunk.text
                        sentences = re.split(r'(?<=[.?!])\s+', sentence_buffer)
                        
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    text_msg = {
                                        "text": sentence.strip(), 
                                        "end": False,
                                        "context_id": context_id
                                    }
                                    await websocket.send(json.dumps(text_msg))
                            sentence_buffer = sentences[-1]

                if sentence_buffer.strip():
                    text_msg = {
                        "text": sentence_buffer.strip(), 
                        "end": True,
                        "context_id": context_id
                    }
                    await websocket.send(json.dumps(text_msg))
                
                chat_history.append({"role": "model", "parts": [full_response_text]})

                print("\n--- END OF Vaani (GEMINI) STREAM ---\n")
                logging.info("Finished streaming to Murf. Waiting for final audio chunks...")

                await asyncio.wait_for(receiver_task, timeout=60.0)
                logging.info("Receiver task finished gracefully.")
            
            finally:
                if not receiver_task.done():
                    receiver_task.cancel()
                    logging.info("Receiver task cancelled on exit.")

    except asyncio.CancelledError:
        logging.info("LLM/TTS task was cancelled by user interruption.")
        await client_websocket.send_text(json.dumps({"type": "audio_interrupt"}))
    except Exception as e:
        logging.error(f"Error in LLM/TTS streaming function: {e}", exc_info=True)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def send_client_message(ws: WebSocket, message: dict):
    try:
        await ws.send_text(json.dumps(message))
    except ConnectionError:
        logging.warning("Client connection closed, could not send message.")

@app.websocket("/ws")
async def websocket_audio_streaming(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection accepted.")
    main_loop = asyncio.get_running_loop()
    
    llm_task = None
    last_processed_transcript = ""
    chat_history = []
    
    # NEW: Variables to store the client-provided API keys
    assemblyai_key = None
    murf_key = "ap2_3ee502aa-5e8a-4e1b-bbf5-1ee6249fd22e" # Hardcoded key for Murf, you can add it to the client too.
    gemini_key = None
    
    client = None

    try:
        # NEW: Wait for API keys from the client
        message = await websocket.receive_text()
        try:
            data = json.loads(message)
            if data.get("type") == "api_keys":
                gemini_key = data.get("openai_key")  # Renamed for client-side naming
                assemblyai_key = data.get("google_key") # Renamed for client-side naming
                
                if not gemini_key or not assemblyai_key:
                    await send_client_message(websocket, {"type": "error", "message": "API keys are missing from the client request."})
                    raise ValueError("API keys not provided by client.")

                logging.info("Received API keys from client. Initializing services...")
                await send_client_message(websocket, {"type": "status", "message": "API keys received, connecting to services."})
                
                # NEW: Initialize services here, after receiving the keys
                genai.configure(api_key=gemini_key)
                gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                
                client = StreamingClient(StreamingClientOptions(api_key=assemblyai_key))

                def on_turn(self, event):
                    nonlocal last_processed_transcript, llm_task
                    
                    transcript_text = event.transcript.strip()
        
                    if event.end_of_turn and event.turn_is_formatted and transcript_text and transcript_text != last_processed_transcript:
                        last_processed_transcript = transcript_text
                        
                        if llm_task and not llm_task.done():
                            logging.warning("User interrupted while previous response was generating. Cancelling task.")
                            llm_task.cancel()
                            asyncio.run_coroutine_threadsafe(
                                send_client_message(websocket, {"type": "audio_interrupt"}), main_loop
                            )
                        
                        logging.info(f"Final formatted turn: '{transcript_text}'")
                        
                        transcript_message = { "type": "transcription", "text": transcript_text, "end_of_turn": True }
                        asyncio.run_coroutine_threadsafe(send_client_message(websocket, transcript_message), main_loop)
                        
                        # Pass the models and keys to the streaming function
                        llm_task = asyncio.run_coroutine_threadsafe(get_llm_response_stream(transcript_text, websocket, chat_history, gemini_model, murf_key), main_loop)
                    
                def on_begin(self, event): logging.info(f"Transcription session started.")
                def on_terminated(self, event): logging.info(f"Transcription session terminated.")
                def on_error(self, error): logging.error(f"AssemblyAI streaming error: {error}")

                client.on(StreamingEvents.Begin, on_begin)
                client.on(StreamingEvents.Turn, on_turn)
                client.on(StreamingEvents.Termination, on_terminated)
                client.on(StreamingEvents.Error, on_error)

                client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
                await send_client_message(websocket, {"type": "status", "message": "Connected to transcription service."})
                
            else:
                await send_client_message(websocket, {"type": "error", "message": "The first message must contain API keys."})
                raise ValueError("Invalid initial message type.")

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse or validate initial message: {e}")
            await websocket.close(code=1008)
            return

        while True:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message['text'])
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except (json.JSONDecodeError, TypeError): pass
            elif "bytes" in message:
                if message['bytes']:
                    client.stream(message['bytes'])
            
    except (WebSocketDisconnect, RuntimeError) as e:
        logging.info(f"Client disconnected or connection lost: {e}")
    except Exception as e:
        logging.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if llm_task and not llm_task.done():
            llm_task.cancel()
        logging.info("Cleaning up connection resources.")
        if client:
            client.disconnect()
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("MAIN.main:app", host="0.0.0.0", port=8000, reload=True)










