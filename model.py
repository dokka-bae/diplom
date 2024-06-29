import torch
from RetrieverHandler import RetrieverHandler
from ChatHandler import ChatHandler
from Chat import Pair
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM, TextStreamer
from user_template import user_template
from chat_template import chat_template
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log",  filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

chats_path = "./chats"


class ModelParams(BaseModel):
    max_new_tokens: int = 512
    temperature: float = 0.3
    top_k: int = 50
    top_p: float = 0.95


class TextGenerationModel:
    def __init__(self) -> None:
        self.__retriever_handler: RetrieverHandler = RetrieverHandler()
        self.__chats_handler: ChatHandler = ChatHandler(chats_path)
        self._model_pipeline = self.__load_model()
        self.__model_params: ModelParams = ModelParams()

    @property
    def retrievers_status(self) -> dict:
        return {"data": self.__retriever_handler.get_retrievers_status()}

    @property
    def model_params(self) -> dict:
        return {
            "max_new_tokens": self.__model_params.max_new_tokens,
            "temperature": self.__model_params.temperature,
            "top_k": self.__model_params.top_k,
            "top_p": self.__model_params.top_p,
        }

    @property
    def chat_handler(self) -> ChatHandler:
        return self.__chats_handler

    def activate_retriever(self, name: str) -> bool:
        try:
            self.__retriever_handler[name].status = True
            logging.info(f"Активация базы знаний {name}")
            return True
        except:
            pass
        else:
            logging.error(f"Активация базы знаний {name} не удалась")
            return False

    def deactivate_retriever(self, name: str) -> bool:
        try:
            self.__retriever_handler[name].status = False
            logging.info(f"Деактивация базы знаний {name}")
            return True
        except:
            pass
        else:
            logging.error(f"Дективация базы знаний {name} не удалась")
            return False

    def change_retriever_name(self, old_name: str, new_name: str) -> bool:
        return self.__retriever_handler.change_retriever_name(old_name, new_name)

    def remove_retriever(self, name: str) -> bool:
        return self.__retriever_handler.remove_retriever(name)

    def add_text_in_retriever(self, name: str, text: str) -> bool:
        return self.__retriever_handler.add_text_in_retriever(name, text)

    def add_document_in_retriever(self, name: str, url: str) -> bool:
        return self.__retriever_handler.add_document_in_retriever(name, url)

    def create_retriever_from_document(self, name: str, url: str) -> bool:
        return self.__retriever_handler.create_retriever_from_document(name, url)

    def set_model_params(self, max_new_tokens: int = 0, temperature: float = 0, top_k: int = 0, top_p: int = 0) -> None:
        if max_new_tokens != 0:
            logging.info(
                f"Изменение параметра max_new_tokens {self.__model_params.max_new_tokens} -> {max_new_tokens}")
            self.__model_params.max_new_tokens = max_new_tokens
        if temperature != 0:
            logging.info(
                f"Изменение параметра temperature {self.__model_params.temperature} -> {temperature}")
            self.__model_params.temperature = temperature
        if top_k != 0:
            logging.info(
                f"Изменение параметра top_k {self.__model_params.top_k} -> {top_k}")
            self.__model_params.top_k = top_k
        if top_p != 0:
            logging.info(
                f"Изменение параметра top_p {self.__model_params.top_p} -> {top_p}")
            self.__model_params.top_p = top_p

    def __load_model(self):
        logging.info("Загрузка модели")
        self.__model = AutoModelForCausalLM.from_pretrained(
            './model',
            torch_dtype=torch.bfloat16
        )
        logging.info(f"Загрузка токенизатора")
        self.__tokenizer = AutoTokenizer.from_pretrained('./tokenizer')
        logging.info(f"Создание стримера")
        streamer = TextStreamer(
            self.__tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        logging.info(f"Создание конвейера")
        return pipeline(
            'text-generation',
            model=self.__model,
            tokenizer=self.__tokenizer,
            device='cuda:0',
            streamer=streamer
        )

    def __generate_chat_name(self, user_prompt: str) -> str:
        prompt: str = chat_template.format(question=user_prompt)
        generator = self._model_pipeline(
            prompt,
            max_new_tokens=24,
            do_sample=True,
            temperature=0.15,
            top_k=10,
            top_p=0.92,
            num_return_sequences=1,
            return_full_text=False,
        )
        chat_name: str = ""
        for output in generator:
            chat_name += f"{output['generated_text']} "
        if "Chat Name " in chat_name:
            chat_name[chat_name.index("Chat Name"):]
        return chat_name.strip('\n')[:-1]

    def __call__(self, question: str, id: int = -1):
        logging.info("Генерация текста")
        chat_name: str = ""
        if id == -1:
            logging.info(f"Генерация имени нового чата")
            chat_name = self.__generate_chat_name(question)
            id = self.__chats_handler.create_chat(chat_name)
        else:
            chat_name = self.__chats_handler(id)
        docs: str = self.__retriever_handler(question)
        prompt: str = user_template.format(
            context=docs, question=question, chat_name=chat_name)

        # генерация
        generator = self._model_pipeline(
            prompt,
            max_new_tokens=self.__model_params.max_new_tokens,
            do_sample=True,
            temperature=self.__model_params.temperature,
            top_k=self.__model_params.top_k,
            top_p=self.__model_params.top_p,
            num_return_sequences=1,
            return_full_text=False,
        )
        generated_text: str = ""
        for output in generator:
            generated_text += f"{output['generated_text']} "
            yield output['generated_text']

        self.__chats_handler(id).add_pair(
            Pair(
                user=question,
                bot=generated_text
            )
        )
