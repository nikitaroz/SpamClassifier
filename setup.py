from common.database_connector import DatabaseConnector
from common.utils import get_labeled_files
#from common.message import Message
#from common.message_transformer import MessageTransformer
import joblib
db_connector = DatabaseConnector("db/spam.db")
db_connector.populate_schema("schema.sql")

pipeline = joblib.load("classifier/pipeline.pkl")
classifier = joblib.load("classifier/classifier.pkl")

vectorizer = pipeline["vectorizer"].named_transformers_["tdidf_body_vectorizer"]
coefs = classifier.coef_

features = []
for i in zip(vectorizer.get_feature_names(), coefs):
    features.append(i)

db_connector.populate_feature_table(features, commit=True)


data_files, class_labels = get_labeled_files(data_dir="classifier/data")

db_connector.populate_message_table(data_files[:100], class_labels[:100], commit=True)