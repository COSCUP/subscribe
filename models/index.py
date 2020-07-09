from models.subscriberdb import SubscriberLoginTokenDB
from models.subscriberdb import SubscriberReadDB


if __name__ == '__main__':
    SubscriberLoginTokenDB().index()
    SubscriberReadDB().index()
