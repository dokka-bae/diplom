from langchain.vectorstores import FAISS
from DocumentHandler import DocumentHandler
from langchain_core.documents import Document
from typing import List
import torch
import os
import shutil
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


class Retriever:
    def __init__(self, name: str, retriever, status: bool = True) -> None:
        self.name = name
        self.status = status
        self.retriever = retriever

    def __call__(self, question: str) -> str:
        logging.info(f"Поиск документа в базе знаний {self.name}")
        if self.status:
            return " ".join([doc.page_content for doc in self.retriever.invoke(question)])
        return ""

    def __eq__(self, name: str) -> bool:
        if self.name == name:
            return True
        return False


class RetrieverHandler:
    def __init__(self, path='./database') -> None:
        self.__path = path
        self.__retrievers: list = []
        self.__load_retrievers()

    def __load_retrievers(self) -> None:
        logging.info(f"Загрузка слоя эмбеддинга")
        self.__embeddings = torch.load(
            '{path}/embeddings/embeddings.pt'.format(path=self.__path),
            map_location=torch.device('cuda:0')
        )
        dirs: List[str] = os.listdir(
            '{path}/knowladge'.format(path=self.__path))
        logging.info(f"Загрузка баз знаний")
        for data in dirs:
            retriever = FAISS.load_local(
                "{path}/knowladge/{data}".format(data=data, path=self.__path),
                self.__embeddings,
                allow_dangerous_deserialization=True
            ).as_retriever(
                search_kwargs={'k': 1}
            )
            self.__retrievers.append(Retriever(data, retriever))
            logging.info(f"Загружена база знаний {data}")
        logging.info(f"Загружено баз знаний {len(dirs)}")

    def get_retrievers_status(self) -> list:
        logging.info(f"Получение статуса активности баз знаний")
        return [{"name": retriever.name, "active_status": retriever.status} for retriever in self.__retrievers]

    def change_retriever_name(self, old_name: str, new_name: str) -> bool:
        try:
            os.rename('{path}/knowladge/{data}'.format(path=self.__path,
                                                       data=old_name), '{path}/knowladge/{data}'.format(path=self.__path,
                                                                                                        data=new_name))
            self.__getitem__(old_name).name = new_name
            logging.info(
                f"Изменение имени базы знаний {old_name} -> {new_name}")
            return True
        except:
            logging.error(
                f"Изменение имени базы знаний {old_name} -> {new_name} не удалось")
            return False

    def remove_retriever(self, name: str) -> bool:
        try:
            shutil.rmtree(
                '{path}/knowladge/{data}'.format(path=self.__path, data=name))
            self.__retrievers.remove(name)
            logging.info(f"Удаление базы знаний {name}")
            return True
        except:
            logging.error(f"Удаление базы знаний {name} не удалось")
            return False

    def add_text_in_retriever(self, name: str, text: str) -> bool:
        try:
            self.__getitem__(name).retriever.add_documents([Document(text)])
            logging.info(f"Добавление документа в базу знаний {name}")
            return True
        except:
            logging.error(
                f"Добавление документа в базу знаний {name} не удалось")
            return False

    def add_document_in_retriever(self, name: str, url: str) -> bool:
        try:
            doc_handler = DocumentHandler(url)
            self.__getitem__(name).retriever.add_documents(
                doc_handler.documents)
            logging.info(f"Добавление документов -> {name}")
            return True
        except:
            logging.error(f"Ошибка добавления документов -> {name}")
            return False

    def create_retriever_from_document(self, name: str, url: str) -> bool:
        try:
            doc_handler = DocumentHandler(url)
            db = FAISS.from_documents(doc_handler.documents, self.__embeddings)
            db.save_local("{path}/knowladge/{data}".format(data=name,
                          path=self.__path))
            retriever = db.as_retriever(search_kwargs={'k': 1})
            self.__retrievers.append(Retriever(name, retriever))
            logging.info(
                f"Создание базы знаний {name} из документов {url}")
            return True
        except:
            logging.error(
                f"Создание базы знаний {name} из документов {url} не удалось")
            return False

    def __call__(self, question: str):
        docs = []
        for retriever in self.__retrievers:
            docs.append(retriever(question))
        return " ".join([doc for doc in docs])

    def __getitem__(self, name: str):
        for retriever in self.__retrievers:
            if retriever.name == name:
                return retriever
        return None
