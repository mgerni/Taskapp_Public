import os
import pymongo
import base64

def create_pem_from_base64(base64_string, filename):
    decoded_data = base64.b64decode(base64_string)

    # save to file
    with open(filename, "wb") as pem_file:
        pem_file.write(decoded_data)

IS_PROD = os.environ["FLASK_ENV"].lower() != "development"
SECRET_KEY = os.environ["SECRET_KEY"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
MONGO_URL = os.environ["MONGO_URI"]

if IS_PROD:
    X509_CERT = os.environ["X509"]
    create_pem_from_base64(X509_CERT, "certificate.pem")
    MONGO_CLIENT = pymongo.MongoClient(MONGO_URL,
                                       tls=True,
                                       tlsCertificateKeyFile="certificate.pem")
else:
    MONGO_CLIENT = pymongo.MongoClient(MONGO_URL)
