import os
import pymongo

IS_PROD = os.environ["FLASK_ENV"].lower() != "development"
SECRET_KEY = os.environ["SECRET_KEY"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
MONGO_URL = os.environ["MONGO_URI"]

if IS_PROD:
    X509_CERT = os.environ["X509_CERT"]
    MONGO_CLIENT = pymongo.MongoClient(MONGO_URL,
                                       tls=True,
                                       tlsCertificateKeyFile=X509_CERT)
else:
    MONGO_CLIENT = pymongo.MongoClient(MONGO_URL)
