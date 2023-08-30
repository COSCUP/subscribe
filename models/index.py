''' index '''
from models.subscriberdb import (SubscriberDB, SubscriberLoginTokenDB,
                                 SubscriberReadDB)

if __name__ == '__main__':
    SubscriberDB().index()
    SubscriberLoginTokenDB().index()
    SubscriberReadDB().index()
