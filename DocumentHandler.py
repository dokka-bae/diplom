import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


class DocumentHandler:
    def __init__(self, url: str) -> None:
        self.__extract_text(url)
        self.__text_processing()

    def __extract_text(self, url) -> None:
        logging.info(f"Обработка документа {url}")
        document = docx.Document(url)
        texts = []
        for paragraph in document.paragraphs:
            texts.append(paragraph.text)
        self.__text = "".join(texts)

    def __text_processing(self) -> None:
        logging.info(f"Разбиение текста документа на чанки")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
        )
        self.__cleared_documents = text_splitter.create_documents([
                                                                  self.__text])

    @property
    def documents(self) -> list:
        return self.__cleared_documents
