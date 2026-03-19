import joblib

class ColumnMapper:
    def __init__(self):
        self.model = joblib.load("mapper_model.pkl")
        self.vectorizer = joblib.load("mapper_vectorizer.pkl")

    def map_columns(self, columns):
        mapped = {}
        for col in columns:
            vec = self.vectorizer.transform([col])
            predicted = self.model.predict(vec)[0]
            mapped[col] = predicted
        return mapped