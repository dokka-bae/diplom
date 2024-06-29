import json
from typing import List, Dict
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


class Pair:
    def __init__(self, user: str, bot: str) -> None:
        self.user: str = user
        self.bot: str = bot


class Chat:
    def __init__(self, path: str = "", chat_name: str = "", id: int = 0) -> None:
        self.__path: str = path
        self.__chat_name: str = chat_name
        self.__chat_history: List[Dict] = []
        self.__id: int = id

    def load_chat(self) -> None:
        with open(self.__path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.__chat_name = data["chat_name"]
        self.__id = data["id"]
        self.__chat_history = data["chat_history"]
        logging.info(f"Загружен чат {self.__chat_name}")

    def add_pair(self, pair: Pair) -> None:
        self.__chat_history.append(
            {
                "user": pair.user,
                "bot": pair.bot
            }
        )
        logging.info(f"Добавление истории в чат {self.__chat_name}")
        if not self.__path:
            self.__path = "./chats" + '/' + str(self.__id) + '.json'
        with open(self.__path, 'w', encoding='utf-8') as file:
            file.write(json.dumps({"chat_name": self.__chat_name, "id": self.__id,
                       "chat_history": self.__chat_history}, ensure_ascii=False))
        logging.info(
            f"Сохранение истории чата {self.chat_name} -> {self.__path}")

    @property
    def chat_name(self) -> str:
        return self.__chat_name

    @property
    def id(self) -> int:
        return self.__id

    @chat_name.setter
    def chat_name(self, chat_name: str) -> None:
        self.__chat_name = chat_name

    @property
    def chat_history(self) -> List[Dict]:
        return self.__chat_history

    @property
    def path(self) -> str:
        return self.__path
