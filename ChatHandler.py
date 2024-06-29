import os
from typing import Dict, List
from Chat import Chat
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


class ChatHandler:
    def __init__(self, path) -> None:
        self.__path: str = path
        self.__chats: Dict = dict()
        self.load_chats()

    def load_chats(self) -> None:
        logging.info("Загрузка чатов")
        dirs: List[str] = os.listdir(self.__path)
        for file in dirs:
            chat = Chat(self.__path+'/'+file)
            chat.load_chat()
            self.__chats[chat.id] = chat
        logging.info(f"Загружено чатов {len(dirs)}")

    def __call__(self, id: int) -> Chat:
        logging.info(f"Вызов чата id:{id}")
        return self.__chats[id]

    def create_chat(self, chat_name: str) -> int:
        logging.info(f"Создание чата {chat_name}")
        used_ids: List[int] = []
        logging.info(f"Генерация id чата {chat_name}")
        for chat in self.__chats.values():
            used_ids.append(chat.id)
        id: int = len(self.__chats)
        for i, chat in enumerate(self.__chats.values()):
            try:
                self.__chats[i]
            except:
                id = i
                break
        print(id)
        logging.info(f"Id чата {id} для {chat_name}")
        self.__chats[id] = Chat(chat_name=chat_name, id=id)
        return id

    def chat_names(self) -> List[str]:
        logging.info("Получение метаданных чатов")
        return [dict({"chat_name": chat[1].chat_name, "id": chat[0]}) for chat in self.__chats.items()]

    def remove_chat(self, id: int = 0) -> bool:
        try:
            os.remove(self.__chats[id].path)
            self.__chats.pop(id)
            logging.info(f"Чат {id} был удалён")
            return True
        except:
            logging.info(f"Чат {id} не был удалён")
            return False
