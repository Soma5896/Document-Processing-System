from app.services.classifier import DocumentClassifier

texts = [
    "Invoice for payment of $5000...",
    "This contract is made between...",
    "John Doe has skills in Python...",
    "Court case between X and Y...",
    "This financial report shows..."
]
labels = ['invoice', 'contract', 'resume', 'legal_doc', 'report']

classifier = DocumentClassifier()
classifier.train(texts, labels)
