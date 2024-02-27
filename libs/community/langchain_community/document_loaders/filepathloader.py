import os
from typing import Any, List, Optional

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseLoader


class BasicFilePathLoader(BaseLoader):
    """Load a query result from `a folder path`.

    The is a basic loader which loads filename into list of type Document, where the page_content is the name of the file and the metadata contains the full path to the files

    Args:
        Supports only load.
    """

    def __init__(
        self, folder_dir: str, **kwargs: Any
    ):
        self.folder_dir = folder_dir        

    def load(self) -> List[Document]:
        file_ls=os.listdir(self.folder_dir)
        doc_ls=[]
        for file_name in file_ls:
            file_path=os.path.join(self.folder_dir, file_name)
            if os.path.exists(file_path):
                doc =  Document(page_content=file_name , metadata={"source": file_path})
                doc_ls.append(doc)
        
        return doc_ls
