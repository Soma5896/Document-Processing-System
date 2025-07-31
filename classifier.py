from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

class DocumentClassifier:
    def __init__(self):
        # Initialize TF-IDF + Multinomial Logistic Regression pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,        # Keep top 5000 terms
                ngram_range=(1, 2),       # Unigrams + bigrams
                stop_words='english'      # Remove common stopwords
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,            # Ensure convergence
                solver='lbfgs',           # Solver that supports multinomial
            ))
        ])

    def train(self, texts, labels, model_path='document_LGClassifier.pkl'):
        """
        Train the classification model and save it to disk.

        Args:
            texts (List[str]): List of input documents
            labels (List[str]): Corresponding labels
            model_path (str): File path to save the model
        """
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, model_path)

    def load_model(self, model_path='document_LGClassifier.pkl'):
        """
        Load a previously trained model from disk.
        """
        self.pipeline = joblib.load(model_path)

    def classify(self, text: str, threshold: float = 0.0) -> dict:
        """
        Predict the document category with confidence.

        Args:
            text (str): Document text
            threshold (float): Optional minimum confidence threshold

        Returns:
            dict: {'category': str, 'confidence': float}
        """
        probabilities = self.pipeline.predict_proba([text])[0]
        predicted_class = self.pipeline.predict([text])[0]
        confidence = max(probabilities)

        if confidence < threshold:
            return {'category': 'uncertain', 'confidence': confidence}

        return {'category': predicted_class, 'confidence': confidence}

   
