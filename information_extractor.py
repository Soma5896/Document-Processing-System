import spacy
import re
from datetime import datetime

class InformationExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'amount': r'\$?\d+[,.]?\d*\.?\d{2}',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
    
    def extract_entities(self, text):
        """Extract named entities and structured data"""
        doc = self.nlp(text)
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'MONEY': [],
            'DATE': []
        }
        
        # Extract spaCy entities
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Extract using regex patterns
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            entities[pattern_name] = matches
        
        return entities
    
    def extract_invoice_data(self, text):
        """Extract invoice-specific information"""
        entities = self.extract_entities(text)
        
        invoice_data = {
            'vendor': entities.get('ORG', [None])[0],
            'amount': entities.get('amount', [None])[0],
            'date': entities.get('date', [None])[0],
            'email': entities.get('email', [None])[0],
            'phone': entities.get('phone', [None])[0]
        }
        
        return invoice_data

