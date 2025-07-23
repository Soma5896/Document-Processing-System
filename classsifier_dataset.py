from app.services.classifier import DocumentClassifier

invoice_examples = [
    "Invoice dated March 10 for consulting services worth $1,200.",
    "Please find attached the invoice for your recent order of supplies.",
    "This invoice is generated for the software license renewal.",
    "Payment is due within 15 days from the invoice date.",
    "Invoice #45678 includes charges for web development.",
    "Billing summary: Total due $875 for January maintenance.",
    "Your invoice for quarterly audit services is attached.",
    "Kindly process the invoice for shipment and handling fees.",
    "Final invoice for mobile app development project.",
    "Enclosed invoice covers training services conducted in April."
]

contract_examples = [
    "This agreement is made and entered into by both parties on June 5.",
    "The contract outlines the terms of the employment offer.",
    "This legally binding contract is effective from July 1.",
    "Both organizations agree to the conditions set forth in this contract.",
    "Termination clauses are outlined in section 4 of the contract.",
    "The signed contract governs the leasing of equipment.",
    "The contractor agrees to deliver services as per this agreement.",
    "This document represents a mutual contract between client and vendor.",
    "Confidentiality terms are part of this contract.",
    "The partnership contract lasts for a period of two years."
]

legal_doc_examples = [
    "The court hereby rules in favor of the plaintiff.",
    "This legal document affirms the transfer of ownership.",
    "The defendant has violated section 8 of the labor law.",
    "This is a notarized copy of the legal proceedings.",
    "The document outlines terms of the legal settlement.",
    "Witness statements are included in the legal case file.",
    "Summons issued for the hearing on October 5.",
    "The case is dismissed due to lack of evidence.",
    "Legal counsel is advised to file a counter-motion.",
    "The judge’s verdict was recorded on page 12."
]

report_examples = [
    "Quarterly financial report indicates 15% growth.",
    "The report includes KPIs for all departments.",
    "This summary highlights customer feedback trends.",
    "Annual report shows increase in net profit margins.",
    "Market analysis report predicts positive Q4 outlook.",
    "Monthly sales report for Region A is attached.",
    "Performance report compares revenue vs. projections.",
    "Security incident report filed on March 22.",
    "Research report on renewable energy initiatives.",
    "Report generated from the employee satisfaction survey."
]

texts = invoice_examples + contract_examples + resume_examples + legal_doc_examples + report_examples
labels = (['invoice'] * len(invoice_examples) +
          ['contract'] * len(contract_examples) +
          ['resume'] * len(resume_examples) +
          ['legal_doc'] * len(legal_doc_examples) +
          ['report'] * len(report_examples))

classifier = DocumentClassifier()
classifier.train(texts, labels)
