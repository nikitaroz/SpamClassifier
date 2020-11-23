import joblib
import nltk
from sklearn.model_selection import train_test_split

from common.database_connector import DatabaseConnector
from common.utils import get_labeled_files


pipeline = joblib.load("classifier/pipeline.pkl")
classifier = joblib.load("classifier/classifier.pkl")


#nltk.download('words')
#nltk.download("stopwords")

db_connector = DatabaseConnector("db/spam.db", pipeline, classifier)
db_connector.populate_schema("schema.sql")

data_files, class_labels = get_labeled_files(data_dir="classifier/data")
_, test_files, _, y_test = train_test_split(data_files, class_labels,
                                                            test_size=0.2, random_state=44)


db_connector.populate_feature_table(commit=True)
db_connector.populate_message_table(test_files, y_test, commit=True)