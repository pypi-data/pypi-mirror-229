import requests
import json
import warnings
from tenacity import retry, wait_exponential, stop_after_attempt
from tqdm import tqdm
import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

API_URL = "https://api.pigeonsai.com/api/v1"
GET_DB_INFO_API = "https://api.pigeonsai.com/api/v1/sdk/get-db-info"
base_url_search = "http://upsert.pigeonsai.com/search"
base_url_add = "http://upsert.pigeonsai.com/add"
SEARCH_URL = "http://upsert.pigeonsai.com/search"
base_url = "http://upsert.pigeonsai.com"



@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
def post_request(url, headers, data):
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception("Request failed with status code: {}".format(response.status_code))
    return response


class PigeonsDBError(Exception):
    pass


class PigeonsDB:
    __connection = None
    __index_p = None

    @staticmethod
    def init(dbname, API_KEY=None):
        if API_KEY == None:
            API_KEY = os.getenv('PIGEONSAI_API_KEY')
        if not API_KEY:
            raise ValueError("Missing PIGEONSAI_API_KEY")
        if not dbname:
            raise ValueError("Missing Database Name")
        index_p, connect = _get_db_info(api_key=API_KEY, dbname=dbname)
        logger.info("Initialized Connection")
        if connect:
            PigeonsDB.__connection = connect
            PigeonsDB.__index_p = index_p
            
        else:
            raise PigeonsDBError("API key or DB name not found")


    def search(query, k=5, nprobe=10, namespace="documents", metadata_filters=None, keywords=None, rerank=False, auto_encode=True) -> list:
        
        if PigeonsDB.__connection is None:
            logger.error("Connection to PigeonsDB is not initialized. Please initialize the connection before proceeding.")
            return
        
        if auto_encode == False and not isinstance(query, list):
            logger.error("When 'auto_encode' is set to False, the 'query' must be a list of vectors. Please provide a list of vectors as the query.")
            return
        
        if auto_encode == True and not isinstance(query, str):
            logger.error("When 'auto_encode' is set to True, the 'query' must be a string. Please provide a string as the query.")
            return
        
        if auto_encode == False and rerank == True:
            logger.warning("Warning: When 'auto_encode' is False PigeonsDB is not able to rerank on keywords, since a string is not passed in.")        
                
        url = SEARCH_URL
        
        
        headers = {"Content-Type": "application/json"}
        data = {
            "connection": PigeonsDB.__connection,
            "index_path": PigeonsDB.__index_p,
            "query_text": query,
            "nprobe": nprobe,
            "k": k,
            "namespace": namespace,
            "metadata_filters": metadata_filters,
            "keywords": keywords,
            "rerank": rerank,
            "encode":auto_encode
        }

        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        res = json.loads(response.text)
            
        if keywords:
            filtered_res = []
            for item in res:
                if all(keyword in item['text'] for keyword in keywords):
                    filtered_res.append(item)
            return filtered_res

        return res



    @staticmethod
    @retry(wait=wait_exponential(multiplier=1, min=2, max=60), stop=stop_after_attempt(5))
    def add(documents: list, vectors=None, namespace: str = "documents" ,metadata_list=None, encode=False):
        
        if vectors is None and encode == False:
            logger.error("When 'encode' is False, 'vectors' cannot be None.")
            return
                
        if encode == False:
            if len(vectors) != len(documents):
                logger.error("The number of vectors and documents must be equal.")
                return 

            chunk_size = 100
            chunks = [documents[i:i + chunk_size] for i in range(0, len(documents), chunk_size)]
            vector_chunks = [vectors[i:i + chunk_size] for i in range(0, len(vectors), chunk_size)]  # Chunk vectors

            print(chunks, vector_chunks)
            
            for chunk, vector_chunk in zip(tqdm(chunks), vector_chunks):
                url = base_url_add
                headers = {"Content-Type": "application/json"}
                data = {
                    "connection": PigeonsDB.__connection,
                    "index_path": PigeonsDB.__index_p,
                    "documents": chunk,
                    "vectors": vector_chunk,  # Use vector_chunk here
                    "namespace": namespace,
                    "metadata_list": metadata_list,
                    "encode":encode
                }
                try:
                    response = post_request(url, headers, data)
                    logger.info(response)
                except Exception as e:
                    logger.error(e)
                    return response.status_code
                
        else:
            
            chunk_size = 100
            chunks = [documents[i:i + chunk_size] for i in range(0, len(documents), chunk_size)]
            
            for chunk in tqdm(chunks):
                url = base_url_add
                headers = {"Content-Type": "application/json"}
                data = {
                    "connection": PigeonsDB.__connection,
                    "index_path": PigeonsDB.__index_p,
                    "documents": chunk,
                    "namespace": namespace,
                    "metadata_list": metadata_list,
                    "encode":encode
                }
                response = requests.post(url, headers=headers, data=json.dumps(data))
                print(response)
                logger.info(response.status_code)


    @staticmethod
    def delete(object_ids: list, namespace="documents"):

        if PigeonsDB.__connection is None:
            raise PigeonsDBError("Connection not initialized.")
        url = f"{base_url}/delete"
        headers = {"Content-Type": "application/json"}
        data = {
            "connection": PigeonsDB.__connection,
            "index_path": PigeonsDB.__index_p,
            "object_ids": object_ids,
            "namespace": namespace,

        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(response.json())


    @staticmethod
    def delete_by_metadata(metadata_filters: list, namespace="documents"):
        if PigeonsDB.__connection is None:
            raise PigeonsDBError("Connection not initialized.")
        url = f"{base_url}/delete_by_metadata"
        headers = {"Content-Type": "application/json"}
        data = {
            "connection": PigeonsDB.__connection,
            "index_path": PigeonsDB.__index_p,
            "metadata_filters": metadata_filters,
            "namespace": namespace,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(response.json())


def _get_db_info(api_key: str, dbname: str):
    url = GET_DB_INFO_API
    headers = {"Content-Type": "application/json"}
    data = {"api_key": api_key, "dbname": dbname}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        raise PigeonsDBError("API_KEY or db_name doesn't match.")

    db_info = response.json().get('DB info', {})
    index_p = db_info.get('s3_identifier')
    keys = ['dbname', 'user', 'password', 'host']
    connect = {key: db_info.get(key) for key in keys}

    return index_p, connect

