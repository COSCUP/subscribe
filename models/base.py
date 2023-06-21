''' DB Base '''
from typing import TYPE_CHECKING, Any

from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

import setting

if TYPE_CHECKING:
    class DBBase(Collection[dict[str, Any]]):
        ''' DBBase '''
        # pylint: disable=super-init-not-called,multiple-statements

        def __init__(self, name: str) -> None: ...
else:
    class DBBase(Collection):  # pylint: disable=abstract-method
        ''' DBBase class

        :param str name: collection name

        '''

        def __init__(self, name: str) -> None:
            client: Any = MongoClient(
                f'mongodb://{setting.MONGO_HOST}:{setting.MONGO_PORT}')[setting.MONGO_DBNAME]

            super().__init__(client, name)
