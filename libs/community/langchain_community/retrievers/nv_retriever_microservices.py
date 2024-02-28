from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.retrievers import BaseRetriever
import requests
import json
import base64
from langchain_community.utilities.nvretriever import fetch_collection_id



def encode_file_to_base64(filename: str) -> str:
    """Encode file content to base64."""
    with open(filename, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def is_pdf(filename: str) -> bool:
    """Check if the file is a PDF based on its extension."""
    return filename.lower().endswith(".pdf")
"""
def fetch_collection_id(collection_name, pipeline, endpoint_url):    
    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }

    json_data = {
        'name': collection_name,
        'pipeline': pipeline,
    }

    response = requests.post(endpoint_url, headers=headers, json=json_data)
    d=response.text
    outd=json.loads(d)
    return outd['collection']['id']  """


class NvidiaRetrieverMicroservice(BaseRetriever):
    """`NVIDIA Retrieval Microservice`.

    See URL_at_NVIDIA for more info.

    Args:
        collection_id: collection id        
        credentials_profile_name: The name of the profile in the ~/.aws/credentials
            or ~/.aws/config files, which has either access keys or role information
            specified. If not specified, the default credential profile or, if on an
            EC2 instance, credentials from IMDS will be used.
        endpoint_url :  http://localhost:port/v1/
        retrieval_config: Configuration for retrieval.

    Example:
        .. code-block:: python

            from langchain_community.retrievers import NvidiaRetrieverMicroservice

            retriever = NvidiaRetrieverMicroservice(
                collection_id="<collection_id>",
                collection_name="<my_named_collection>",
                endpoint_url ="http://localhost:port/v1/"
                },
            )
    """

    collection_name : str
    pipeline : str
    endpoint_url :str
    collection_id : str
    def __init__(self, collection_name, pipeline , endpoint_url, collection_id, **kwargs: Any) -> None:        
        super().__init__( collection_name=collection_name, pipeline=pipeline , endpoint_url=endpoint_url , collection_id=collection_id)

        self.collection_name = collection_name
        self.pipeline = pipeline
        self.endpoint_url = endpoint_url
        self.collection_id = fetch_collection_id(collection_name, pipeline, endpoint_url)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        headers = {
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
        }

        json_data = {
            'query': query,
        }

        response = requests.post(
            f"{self.endpoint_url}/{self.collection_id}/search",
            headers=headers,
            json=json_data,
        )
        results=response['chunks'][0]
        assert type(result)==dict
        
        documents = []
        for result in results:
            score=result['score']
            content=result['content']
            source_id = result['metadata']['source_id']
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source_id": source_id,
                        "score": score,
                    },
                )
            )

        return documents

    def upload_documents(self, file_path:str) -> str:
        
        metadata_dict={}
        # Construct the URL
        url = f"{self.endpoint_url}/{self.collection_id}/documents"
        

        # Check if the file is a PDF and encode it if it is
        if is_pdf(file_path):
            encoded_content: str = encode_file_to_base64(filename)
            format_type: str = "pdf"
        else:
            with open(file_path, "r") as file:
                encoded_content = file.read()
            format_type: str = "txt"

        # Prepare the payload
        payload = {
            "metadata": metadata_dict,
            "content": encoded_content,
            "format": format_type,
        }

        # Make the POST request
        response = requests.post(url, json=[payload])

        # Print response
        #print(type(response.status_code))  # noqa: T201
        if response.status_code == 200:
            d=response.json()
            #print(d)
            return True, d['documents'][0]['id']
        else:
            print(f"{response.status_code} please visit NVIDIA Retriever Microservice user guide : abc_url for further debugging")
            return False, None


    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents (List[Document]: Documents to add to the vectorstore.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        # TODO: Handle the case where the user doesn't provide ids on the Collection
        fname_ls = [doc.page_content for doc in documents]
        f_path_ls = [doc.metadata['source'] for doc in documents]
        ids=[]
        for f_path in f_path_ls:
            flag, idx =self.upload_documents(f_path)
            if flag:            
                ids.append(idx)
        return ids

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:

        headers = {
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
        }

        json_data = {
            'query': query,
        }

        response = requests.post(f'{self.endpoint_url}/{self.collection_id}/search', headers=headers, json=json_data)
        #print(response.status_code, type(response.status_code))
        if response.status_code == 200:
            d=response.json()
            #print(d)
            ls=d['chunks']
            doc_ls=[]
            for l in ls:
                
                content=l["content"]
                metadata=l["metadata"]
                metadata['score']=l['score']                       
                doc=Document(page_content=content , metadata={"metadata": metadata})
                doc_ls.append(doc)

            return doc_ls
        else:
            print(f"{response.status_code} please visit NVIDIA Retriever Microservice user guide : abc_url for further debugging")
            return []

