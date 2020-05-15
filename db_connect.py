import pymongo
import ssl
import config

mongo = pymongo.MongoClient(config.mongoclient, ssl_cert_reqs=ssl.CERT_NONE)
