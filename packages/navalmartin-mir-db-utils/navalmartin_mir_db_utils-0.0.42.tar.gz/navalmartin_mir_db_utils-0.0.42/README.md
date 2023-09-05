# mir-persistence-layer-utils

Utilities for the persistence layer when working with the _mir_ project. The official
PyPi package can be found <a href="https://pypi.org/project/navalmartin-mir-db-utils/">here</a>.

## Dependencies

- pymongo
- motor
- bcrypt
- pydantic
- httpx
- hurry.filesize
- python-dotenv
- psutil

## Installation

Installing the utilities via ```pip```

```
pip install navalmartin-mir-db-utils
```

For a specific version you can use

```
pip install navalmartin-mir-db-utils==x.x.x
```

You can uninstall the project via

```
pip uninstall navalmartin-mir-db-utils
```

## How to use

You can check which specific version you have installed by

```
import navalmartin_mir_db_utils
print(navalmartin_mir_db_utils.__version__)
```

### Create a session

```
from dotenv import load_dotenv
from navalmartin_mir_db_utils.dbs import MongoDBSession 

# laod configuration variables
# using the default .env

# load the MONGODB_URL
load_dotenv()

# assume that the MONGODB_NAME is not loaded
# so we need to set it manuall
session = MongoDBSession(db_name="my-db-name")

```
### Execute simple queries

You can use the session to execute simple queries as shown below

```
import asyncio
import bson
from navalmartin_mir_db_utils.dbs.mongodb_session import MongoDBSession
from navalmartin_mir_db_utils.crud.mongodb_crud_utils import ReadEntityCRUDAPI
from navalmartin_mir_db_utils.utils.exceptions import ResourceNotFoundException
from navalmartin_mir_db_utils.crud.crud_utils import get_one_result_or_raise

COLLECTION_NAME = "YOUR_COLLECTION_NAME"
MONGODB_URL = "YOUR_MONGODB_URL"
MONGO_DB_NAME_FROM = "YOUR_MONGODB_NAME"


async def query_db(mongodb_session: MongoDBSession, criteria: dict,
                   projection: dict,
                   collection_name: str):
    query_result = ReadEntityCRUDAPI.find(criteria=criteria, projection=projection,
                                          db_session=mongodb_session,
                                          collection_name=collection_name)
    docs = [doc async for doc in query_result]
    return docs


async def count_docs(mongodb_session: MongoDBSession, criteria: dict,
                     collection_name: str):
    query_result = await ReadEntityCRUDAPI.count_documents(criteria=criteria,
                                                           db_session=mongodb_session,
                                                           collection_name=collection_name)
    return query_result


async def query_db_or_raise(mongodb_session: MongoDBSession, criteria: dict,
                            projection: dict,
                            collection_name: str):
    query_result = await get_one_result_or_raise(crud_handler=ReadEntityCRUDAPI(collection_name=collection_name),
                                                 projection=projection,
                                                 criteria=criteria,
                                                 db_session=mongodb_session)

    return query_result


async def run_examples(mir_db_session_from: MongoDBSession):
    result = await query_db(mongodb_session=mir_db_session_from,
                            criteria={'_id': bson.ObjectId('63ebc9f94c092a48bd179ae7')},
                            projection={},
                            collection_name=COLLECTION_NAME)
    print(result)
    n_docs = await count_docs(mongodb_session=mir_db_session_from,
                              criteria={},
                              collection_name=COLLECTION_NAME)
    print(n_docs)

    try:
        result = await query_db_or_raise(mongodb_session=mir_db_session_from,
                                         criteria={'survey_idx': bson.ObjectId('63ad64252c853ee163fc6a63')},
                                         projection={'original_filename': 1},
                                         collection_name=COLLECTION_NAME)
    except ResourceNotFoundException as e:
        print(str(e))


def main():
    mir_db_session_from = MongoDBSession(mongodb_url=MONGODB_URL,
                                         db_name=MONGO_DB_NAME_FROM)

    asyncio.run(run_examples(mir_db_session_from=mir_db_session_from))

    
if __name__ == '__main__':
    main()

```

### Simple models

```
import datetime
from navalmartin_mir_db_utils.schemata import IndexedItemDataViewBase, UserDataViewBase


class MyIndexedItem(IndexedItemDataViewBase):
    pass


if __name__ == '__main__':
    mdb_json = {'_id': '123456',
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()}

    my_indexed_item = MyIndexedItem.build_from_mongodb_json(mdb_json=mdb_json)

    print(f"MyIndexedItem  {my_indexed_item}")
    print(f"MyIndexedItem fields set {my_indexed_item.__fields_set__}")

    user_data_json = {'_id': '123456',
                      'created_at': datetime.datetime.utcnow(),
                      'updated_at': datetime.datetime.utcnow(),
                      "name": "Alex",
                      "surname": "Giavaras",
                      "email": "alex@someemail.com"}

    user = UserDataViewBase.build_from_mongodb_json(mdb_json=user_data_json,
                                                    access_token="1236",
                                                    refresh_token="69878")

    print(f"User  {user}")
    print(f"User fields set {user.__fields_set__}")

```

### Run transactions

You can also run transactions.

```
from typing import Any
import bson
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference
import asyncio

from navalmartin_mir_db_utils.dbs.mongodb_session import MongoDBSession
from navalmartin_mir_db_utils.transanctions import run_transaction
from navalmartin_mir_db_utils.transanctions.decorators import with_transaction

IMAGES_COLLECTION_TO_READ = "YOUR_COLLECTION_NAME"
MONGODB_URL = "YOUR_MONGODB_URL"
MONGO_DB_NAME_FROM = "YOUR_MONGODB_NAME"

wc_majority = WriteConcern("majority", wtimeout=1000)
read_concern = ReadConcern("local")


async def read_images_callback(session: Any, kwargs: dict):
    db_name = kwargs['db_name']
    survey_idx = kwargs['survey_idx']
    projection = kwargs['projection']

    db = session.client.get_database(db_name)
    images_collection = db[IMAGES_COLLECTION_TO_READ]

    images = images_collection.find({'survey_idx': bson.ObjectId(survey_idx)},
                                    projection=projection,
                                    session=session)
    return images


async def transaction_result_handler(transaction_result: Any):
    images = [img async for img in transaction_result]
    return images
    
@with_transaction
async def execute_function(mir_db_session: MongoDBSession):
    return await run_transaction(mdb_session=mir_db_session,
                                 async_callback=read_images_callback,
                                 callback_args=callback_args,
                                 max_commit_time_ms=None,
                                 read_concern=read_concern,
                                 write_concern=wc_majority,
                                 read_preference=ReadPreference.PRIMARY,
                                 with_log=True,
                                 transaction_result_handler=transaction_result_handler)


if __name__ == '__main__':
    mir_db_session = MongoDBSession(mongodb_url=MONGODB_URL,
                                    db_name=MONGO_DB_NAME_FROM)

    callback_args = {'db_name': 'mir_db',
                     'survey_idx': '63ad64252c853ee163fc6a63',
                     'projection': {'original_filename': 1}}
    transaction_result = asyncio.run(execute_function(mdb_session=mir_db_session))
    print(transaction_result)

```

There is also a decorator available to run a transaction

```
from typing import Any
import bson
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference
import asyncio

from navalmartin_mir_db_utils.dbs.mongodb_session import MongoDBSession
from navalmartin_mir_db_utils.transanctions.decorators import use_async_transaction

IMAGES_COLLECTION_TO_READ = 'YOUR_COLLECTION_NAME'
MONGODB_URL = "YOUR_MONGODB_URL"
MONGO_DB_NAME_FROM = "YOUR_MONGODB_NAME"

wc_majority = WriteConcern("majority", wtimeout=1000)
read_concern = ReadConcern("local")

callback_args = {'db_name': 'mir_db',
                 'survey_idx': '63ad64252c853ee163fc6a63',
                 'projection': {'original_filename': 1}}


async def read_images_callback(session: Any, kwargs: dict):
    db_name = kwargs['db_name']
    survey_idx = kwargs['survey_idx']
    projection = kwargs['projection']

    db = session.client.get_database(db_name)
    images_collection = db[IMAGES_COLLECTION_TO_READ]

    images = images_collection.find({'survey_idx': bson.ObjectId(survey_idx)},
                                    projection=projection,
                                    session=session)
    return images


async def transaction_result_handler(transaction_result: Any):
    images = [img async for img in transaction_result]
    return images


@use_async_transaction(async_callback=read_images_callback,
                        callback_args=callback_args,
                        mdb_session=MongoDBSession(mongodb_url=MONGODB_URL, db_name=MONGO_DB_NAME_FROM),
                        write_concern=wc_majority,
                        read_concern=read_concern,
                        read_preference=ReadPreference.PRIMARY,
                        max_commit_time_ms=None,
                        with_log=True,
                        with_transaction_result=True,
                        transaction_result_handler=transaction_result_handler)
async def query_db(mongodb_session: MongoDBSession, **kwargs):
    transaction_result = kwargs['transaction_result']
    return transaction_result


if __name__ == '__main__':
    mir_db_session_from = MongoDBSession(mongodb_url=MONGODB_URL,
                                         db_name=MONGO_DB_NAME_FROM)

 
    print("Running transaction as decorator...")
    transaction_result = asyncio.run(query_db(mongodb_session=mir_db_session_from))
    print(transaction_result)

```

### Task monitoring

Some utilities exist to monitor a task

```
import time
import psutil
import datetime
import pprint
from navalmartin_mir_db_utils.schemata import TaskPerformanceResultSchema, TaskResultSchema


def sum_task(sleep_time: int, n_elements: int):
    time.sleep(sleep_time)

    total = sum([i for i in range(n_elements)])
    return total


if __name__ == '__main__':
    start_time = time.time()

    pp = pprint.PrettyPrinter(indent=4)
    task_performance = TaskPerformanceResultSchema()
    task_result = TaskResultSchema()

    sum = sum_task(sleep_time=3,
                   n_elements=1000000)

    task_result.results = [{'sum': sum}]

    virtual_mem_dict = dict(psutil.virtual_memory()._asdict())
    cpu_percentage = psutil.cpu_percent()

    pp.pprint(f"Task virtual memory dictionary: {virtual_mem_dict}")
    pp.pprint(f"Task CPU performance: {cpu_percentage}")

    end_time = time.time()
    task_performance.latency = end_time - start_time
    task_performance.ended_at = datetime.datetime.utcnow()
    task_performance.cpu_util = cpu_percentage
    task_performance.disk_util = virtual_mem_dict

    pp.pprint(f"Task performance: {task_performance}")
    pp.pprint(f"Task result: {task_result}")

```


