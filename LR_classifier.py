from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib 

class DocumentClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1,2))),
            ('classifier', LogisticRegression(max_iter=1000))
        ])
    
    def train(self, texts, labels):
        """Train the classifier."""
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, 'document_LGClassifier.pkl')
    
    def load_model(self):
        """Load the trained model."""
        self.pipeline = joblib.load('document_LGClassifier.pkl')

    def classify(self, text):
        """Predict category with confidence."""
        probabilities = self.pipeline.predict_proba([text])[0]
        predicted_class = self.pipeline.predict([text])[0]
        confidence = max(probabilities)
        
        return {'category': predicted_class, 'confidence': confidence}
