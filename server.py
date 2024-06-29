from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from model import TextGenerationModel
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info("Запуск сервера")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.info("Создание генеративной модели")
txt_model = TextGenerationModel()


class ChatRequest(BaseModel):
    text: str
    id: int = -1


class TextRequest(BaseModel):
    text: str


class ModelParams(BaseModel):
    max_new_tokens: int = 0
    temperature: float = 0
    top_k: int = 0
    top_p: float = 0


@app.post('/set_model_params/')
async def set_model_params(model_params_request: ModelParams):
    txt_model.set_model_params(model_params_request.max_new_tokens,
                               model_params_request.temperature,
                               model_params_request.top_k,
                               model_params_request.top_p
                               )
    return JSONResponse(jsonable_encoder({"params_set": True}))


@app.get('/get_model_params/')
async def get_model_params():
    return JSONResponse(jsonable_encoder(txt_model.model_params))


@app.get('/get_retrievers_status/')
async def get_retrievers_status():
    return JSONResponse(jsonable_encoder(txt_model.retrievers_status))


@app.post('/activate_retriever/')
async def activate_retriever(name: TextRequest):
    if txt_model.activate_retriever(name.text):
        return JSONResponse(jsonable_encoder({"{name}".format(name=name.text): "activated"}))
    else:
        return JSONResponse(jsonable_encoder({"{name}".format(name=name.text): "not found"}))


@app.post('/deactivate_retriever/')
async def deactivate_retriever(name: TextRequest):
    if txt_model.deactivate_retriever(name.text):
        return JSONResponse(jsonable_encoder({"{name}".format(name=name.text): "deactivated"}))
    else:
        return JSONResponse(jsonable_encoder({"{name}".format(name=name.text): "not found"}))


@app.post('/change_retriever_name/')
async def change_retriever_name(old_name: TextRequest, new_name: TextRequest):
    if txt_model.change_retriever_name(old_name.text, new_name.text):
        return JSONResponse(jsonable_encoder({"info": "retriever {old_name} has been renamed -> {new_name}".format(old_name=old_name.text, new_name=new_name.text)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "retriever {old_name} hasnt been renamed".format(old_name=old_name.text)}))


@app.post('/remove_retriever/')
async def remove_retriever(name: TextRequest):
    if txt_model.remove_retriever(name.text):
        return JSONResponse(jsonable_encoder({"info": "retriever {name} has been removed".format(name=name.text)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "retriever {name} hasnt been removed".format(name=name.text)}))


@app.post('/add_text_in_retriever/')
async def add_text_in_retriever(name: TextRequest, text: TextRequest):
    if txt_model.add_text_in_retriever(name.text, text.text):
        return JSONResponse(jsonable_encoder({"info": "text has been added in {name}".format(name=name.text)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "text hasnt been added in {name}".format(name=name.text)}))


@app.post('/add_document_in_retriever/')
async def add_document_in_retriever(name: TextRequest, url: TextRequest):
    if txt_model.add_document_in_retriever(name.text, url.text):
        return JSONResponse(jsonable_encoder({"info": "document has been added -> {name}".format(name=name.text)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "documnt hasn't been added -> {name}"}))


@app.post('/create_retriever_from_document/')
async def create_retriever_from_document(url: TextRequest, retriever_name: TextRequest):
    if txt_model.create_retriever_from_document(url.text, retriever_name.text):
        return JSONResponse(jsonable_encoder({"info": "retriever {name} has been created".format(name=retriever_name.text)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "retriever hasnt been created"}))


@app.get('/get_chats_names/')
async def get_chats_names():
    return JSONResponse(jsonable_encoder(txt_model.chat_handler.chat_names()))


@app.post('/get_chat_history/')
async def get_chat_history(chat: ChatRequest):
    return JSONResponse(jsonable_encoder(txt_model.chat_handler(chat.id).chat_history))


@app.post('/remove_chat/')
async def remove_chat(chat: ChatRequest):
    if txt_model.chat_handler.remove_chat(chat.id):
        return JSONResponse(jsonable_encoder({"info": "chat {name} has been removed".format(name=chat.id)}))
    else:
        return JSONResponse(jsonable_encoder({"error": "chat hasnt been removed"}))


@app.post("/stream/")
async def stream(chat_request: ChatRequest):
    async def generate_responses():
        for generated_text in txt_model(chat_request.text, chat_request.id):
            yield f"{generated_text}\n"

    return StreamingResponse(generate_responses(), media_type="text/plain")
