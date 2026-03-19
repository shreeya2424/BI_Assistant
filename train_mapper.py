import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("column_mapping_dataset.csv")

X = df["column_name"].astype(str)
y = df["label"].astype(str)

vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 5))
X_vectors = vectorizer.fit_transform(X)

model = RandomForestClassifier(n_estimators=300, random_state=42)
model.fit(X_vectors, y)

joblib.dump(model, "mapper_model.pkl")
joblib.dump(vectorizer, "mapper_vectorizer.pkl")

print("✅ Model files created")