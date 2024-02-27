from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.retrievers import BaseRetriever
import requests


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

    collection_id: str
    endpoint_url: str
    
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
            f"{endpoint_url}/collections/{collection_id}/search",
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