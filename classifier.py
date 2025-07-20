from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
import joblib

class DocumentClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1,2))),
            ('svm', SVC(probability=True, kernel='linear'))
        ])
        self.categories = ['invoice', 'contract', 'resume', 'legal_doc', 'report']
    
    def train(self, texts, labels):
        """Train the classifier"""
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, 'document_classifier.pkl')
    
    def load_model(self):
        self.pipeline = joblib.load('document_classifier.pkl')
    
    def classify(self, text):
        """Predict class with confidence"""
        probabilities = self.pipeline.predict_proba([text])[0]
        predicted_class = self.pipeline.predict([text])[0]
        confidence = max(probabilities)
        return {'category': predicted_class, 'confidence': confidence}
'''
        return {
            'category': predicted_class,
            'confidence': confidence,
            'all_probabilities': dict(zip(self.categories, probabilities))
        }

'''
