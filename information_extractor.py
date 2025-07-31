import spacy
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO) # Set logging level to INFO
logger = logging.getLogger(__name__) # Get a logger for this module

class InformationExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"): #spacy's pre-trained english model
        """
        Initialize the Information Extractor with spaCy model and regex patterns.
        
        Args:
            model_name (str): Name of the spaCy model to load
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Successfully loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
            raise OSError(f"spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
        
        # Enhanced regex patterns for various data types
        self.patterns = {
            # Email patterns
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # Phone number patterns (US/International)
            'phone': r'(?:\+?1[-.\s]?)?(?:\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            'phone_international': r'\+(?:[0-9] ?){6,14}[0-9]',
            
            # Currency and amount patterns
            'currency_usd': r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'currency_euro': r'€\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'amount_decimal': r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b',
            'amount_simple': r'\b\d+(?:\.\d{2})?\b',
            
            # Date patterns (various formats)
            'date_slash': r'\b\d{1,2}[/]\d{1,2}[/]\d{2,4}\b',
            'date_dash': r'\b\d{1,2}[-]\d{1,2}[-]\d{2,4}\b',
            'date_iso': r'\b\d{4}-\d{2}-\d{2}\b',
            'date_text': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            
            # Invoice specific patterns
            'invoice_number': r'(?:Invoice|Inv\.?)\s*(?:Number|No\.?|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)',
            'po_number': r'PO\s*(?:Number|No\.?|#)?\s*[:\-]?\s*([A-Z0-9\-]+)',
            'order_number': r'Order\s*(?:Number|No\.?|#)?\s*[:\-]?\s*([A-Z0-9\-]+)',
            
            # Tax patterns
            'tax_rate': r'(?:Tax|VAT|GST|Sales\s+Tax)\s*(?:\([^)]*\))?\s*[:\-]?\s*(\d+(?:\.\d+)?%)',
            'tax_amount': r'(?:Tax|VAT|GST|Sales\s+Tax)\s*(?:\([^)]*\))?\s*[:\-]?\s*[£$€¥]?\s*(\d{1,3}(?:[,\.]\d{3})*(?:\.\d{2})?)',
            
            # Address patterns
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'address': r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl)\b',
            
            # Website and social media
            'website': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            'social_media': r'@[A-Za-z0-9_]+',
            
            # Business identification
            'ein_tax_id': r'\b\d{2}-\d{7}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            
            # Terms and conditions
            'payment_terms': r'(?:Net\s+\d+|within\s+(\d+)\s+days|Payment due in\s+(\d+))',
            'discount_terms': r'(\d+(?:\.\d+)?)%\s+(?:discount|off)',
        }
       

        # Document type specific extractors
        self.document_extractors = {
            'invoice': self.extract_invoice_data,
            'contract': self.extract_contract_data,
            'resume': self.extract_resume_data,
            'legal_doc': self.extract_legal_data,
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities and structured data from text using spaCy and regex.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Dict containing extracted entities and patterns
        """
        if not text or not text.strip():
            return {}
        
        try:
            doc = self.nlp(text)
            
            # Initialize entity dictionary
            entities = {
                # spaCy named entities
                'PERSON': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'PERSON'])),
                'ORG': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'ORG'])),
                'MONEY': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'MONEY'])),
                'DATE': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'DATE'])),
                'GPE': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'GPE'])),  # Countries, cities, states
                'CARDINAL': list(set([ent.text.strip() for ent in doc.ents if ent.label_ == 'CARDINAL'])),  # Numbers
                
                # Regex extracted patterns
                'emails': [],
                'phones': [],
                'currencies': [],
                'dates_structured': [],
                'addresses': [],
                'websites': [],
                'business_ids': [],
                'invoice_details': {},
            }
            # ✅ Clean up bad date matches (e.g., ZIP codes, single numbers)
            entities['DATE'] = [
                d for d in entities['DATE']
                if not re.fullmatch(r'\d{3,5}', d)  # remove ZIP-like
                and not re.fullmatch(r'\d{1,2}', d)  # remove loose digits
            ]
            
            # Extract using regex patterns
            for pattern_name, pattern in self.patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    if pattern_name == 'email':
                        entities['emails'].extend(matches)
                    elif pattern_name in ['phone', 'phone_international']:
                        entities['phones'].extend(matches)
                    elif pattern_name.startswith('currency_') or pattern_name.startswith('amount_'):
                        entities['currencies'].extend(matches)
                    elif pattern_name.startswith('date_'):
                        entities['dates_structured'].extend(matches)
                    elif pattern_name == 'address':
                        entities['addresses'].extend(matches)
                    elif pattern_name == 'website':
                        entities['websites'].extend(matches)
                    elif pattern_name in ['ein_tax_id', 'ssn']:
                        entities['business_ids'].extend(matches)
                    elif pattern_name in ['invoice_number', 'po_number', 'order_number']:
                        entities['invoice_details'][pattern_name] = matches
            
            # Remove duplicates and empty strings
            for key in entities:
                if isinstance(entities[key], list):
                    entities[key] = list(set([item.strip() for item in entities[key] if item and item.strip()]))
            
            # Add confidence scores and metadata
            entities['extraction_metadata'] = {
                'total_entities_found': sum(len(v) if isinstance(v, list) else len(v) if isinstance(v, dict) else 0 for v in entities.values()),
                'text_length': len(text),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            return {'error': f"Entity extraction failed: {str(e)}"}
    
    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Extract invoice-specific information from text.
        
        Args:
            text (str): Invoice text content
            
        Returns:
            Dict containing structured invoice data
        """
        entities = self.extract_entities(text)
        
        invoice_data = {
            # Basic invoice information
            'vendor_name': self._get_vendor_name(text, entities),
            'customer_name': self._get_customer_name(text, entities),
            'invoice_number': self._get_invoice_number(text),
            'po_number': self._get_po_number(text),
            # ...existing code...
            'order_number': self._extract_single_pattern(text, self.patterns['order_number']),
            
            # Financial information
            'total_amount': self._get_total_amount(text, entities),
            'subtotal': self._get_subtotal(text),
            'tax_amount': self._extract_single_pattern(text, self.patterns['tax_amount']),
            'tax_rate': self._extract_single_pattern(text, self.patterns['tax_rate']),
            
            # Dates
            'invoice_date': self._get_invoice_date(text, entities),
            'due_date': self._get_due_date(text, entities),
            
            # Contact information
            'vendor_email': entities.get('emails', [None])[0] if entities.get('emails') else None,
            'vendor_phone': entities.get('phones', [None])[0] if entities.get('phones') else None,
            'vendor_address': self._get_vendor_address(text, entities),
            
            # Payment information
            'payment_terms': self._extract_single_pattern(text, self.patterns['payment_terms']),
            'discount_terms': self._extract_single_pattern(text, self.patterns['discount_terms']),
            
            # Line items (simplified extraction)
            'line_items': self._extract_line_items(text),
            
            # Additional metadata
            'currency_detected': self._detect_currency(text),
            'confidence_score': self._calculate_invoice_confidence(text, entities)
        }
        
        return invoice_data
    
    def extract_contract_data(self, text: str) -> Dict[str, Any]:
        """Extract contract-specific information."""
        entities = self.extract_entities(text)
        
        contract_data = {
            'parties': entities.get('ORG', []) + entities.get('PERSON', []),
            'dates': entities.get('DATE', []),
            'effective_date': self._find_contract_date(text, 'effective'),
            'expiration_date': self._find_contract_date(text, 'expir'),
            'contract_value': self._get_total_amount(text, entities),
            'payment_terms': self._extract_single_pattern(text, self.patterns['payment_terms']),
            'contract_type': self._identify_contract_type(text)
        }
        
        return contract_data
    
    def extract_resume_data(self, text: str) -> Dict[str, Any]:
        """Extract resume-specific information."""
        entities = self.extract_entities(text)
        
        resume_data = {
            'candidate_name': self._extract_candidate_name(text),
            'email': entities.get('emails', [None])[0],
            'phone': entities.get('phones', [None])[0],
            'skills': self._extract_skills(text),
            'education': self._extract_education(text),
            'experience_years': self._extract_experience_years(text),
            'previous_companies': self._extract_companies(text,entities),
            'locations': entities.get('GPE', [])
        }
        
        return resume_data
    
    def extract_legal_data(self, text: str) -> Dict[str, Any]:
        """Extract legal document information."""
        entities = self.extract_entities(text)
        
        legal_data = {
            'parties_involved': entities.get('PERSON', []) + entities.get('ORG', []),
            'case_numbers': self._extract_case_numbers(text),
            'court_names': self._extract_court_names(text),
            'legal_dates': entities.get('DATE', []),
            'monetary_amounts': entities.get('MONEY', []),
            'document_type': self._identify_legal_document_type(text)
        }
        
        return legal_data
    
    
    # Helper methods
    def _extract_companies(self, text: str, entities: Dict) -> List[str]:
        """Extract previous companies with better filtering."""
        companies = []
        
        # Get organizations from entities but filter better
        orgs = entities.get('ORG', [])
        
        # Expanded blacklist of non-company terms
        blacklist_keywords = [
            'university', 'school', 'college', 'institute', 'academy',
            'react', 'css', 'html', 'node', 's3', 'javascript', 'python',
            'aws', 'azure', 'gcp', 'mysql', 'postgresql', 'mongodb',
            'professional summary', 'bachelor', 'master', 'certification',
            'developer', 'engineer', 'manager', 'analyst', 'designer',
            'api', 'rest', 'sql', 'json', 'xml', 'http', 'https',
            'git', 'docker', 'kubernetes', 'jenkins'
        ]
        
        for org in orgs:
            org_clean = org.strip()
            org_lower = org_clean.lower()
            
            # Skip if too short or contains blacklisted terms
            if len(org_clean) < 3:
                continue
                
            if any(keyword in org_lower for keyword in blacklist_keywords):
                continue
                
            # Skip if it looks like a section header
            if org_clean.endswith(':') or '\n' in org_clean:
                continue
                
            # Skip if it's all caps (likely acronym/tech term)
            if org_clean.isupper() and len(org_clean) < 10:
                continue
                
            companies.append(org_clean)
        
        # Also extract from experience section manually
        experience_section = re.search(r'(?:Professional\s+)?Experience:(.+?)(?=Education:|Certifications:|$)', 
                                     text, re.DOTALL | re.IGNORECASE)
        if experience_section:
            exp_text = experience_section.group(1)
            # Look for company names in job entries (pattern: Job Title | Company Name | Location)
            job_patterns = [
                r'\|\s*([^|\n]+?)\s*\|',  # Between pipes
                r'(?:at\s+|@\s+)([A-Z][^,\n]+?)(?:\s*,|\s*\n|\s*$)',  # After "at" or "@"
            ]
            
            for pattern in job_patterns:
                matches = re.findall(pattern, exp_text)
                for match in matches:
                    clean_match = match.strip()
                    if len(clean_match) > 2 and not any(kw in clean_match.lower() for kw in blacklist_keywords):
                        companies.append(clean_match)
        
        return list(set(companies))  # Remove duplicates
    """
    def _get_vendor_name(self, text: str, entities: Dict) -> Optional[str]:
        for org in entities.get('ORG', []):
            if "brand" in org.lower() or "company" in org.lower() or "name" in org.lower():
                return org
        return entities.get('ORG', [None])[0]
    """
    def _get_vendor_name(self, text: str, entities: Dict) -> Optional[str]:
        """Extract vendor name from invoice text and entities."""
        # 1. Try labeled fields
        match = re.search(r'Vendor:\s*(.+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 2. Try ORG with known prefixes
        for org in entities.get('ORG', []):
            if any(kw in org.lower() for kw in ['brand', 'company', 'inc', 'corp', 'ltd', 'llc']):
                return org.strip()

        # 3. Fallback: first ORG or top 5 lines
        if entities.get('ORG'):
            return entities['ORG'][0]

        lines = text.strip().split('\n')
        for line in lines[:5]:
            if any(word in line.lower() for word in ['corporation', 'inc.', 'solutions', 'technologies']):
                return line.strip()

        return None

    def _extract_candidate_name(self, text: str) -> Optional[str]:
        lines = text.strip().split('\n')
        for line in lines:
            if line.strip() and not any(c in line for c in [':', '|', '@']):
                return line.strip()
        return None

    def _get_customer_name(self, text: str, entities: Dict) -> Optional[str]:
        """Extract customer name from invoice - FIXED VERSION"""

        # Step 1: Look for explicit invoice/bill to patterns
        patterns = [
            r'Invoice\s+to:\s*([A-Z][a-zA-Z\s]+?)(?:\s+Invoice|\s+\d|\n|$)',
            r'Bill\s+to:\s*([A-Z][a-zA-Z\s]+?)(?:\s+Invoice|\s+\d|\n|$)',
            r'Customer:\s*([A-Z][a-zA-Z\s]+?)(?:\s+Invoice|\s+\d|\n|$)',
            r'Client:\s*([A-Z][a-zA-Z\s]+?)(?:\s+Invoice|\s+\d|\n|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common suffixes that get accidentally captured
                name = re.sub(r'\s+(Invoice|Bill|Customer|Client).*$', '', name, flags=re.IGNORECASE)
                return name

        # Step 2: Fall back to PERSON entities, but filter out common false positives
        persons = entities.get('PERSON', [])
        if persons:
            # Filter out names that are likely not customers
            filtered_persons = [
                p for p in persons
                if not any(word in p.lower() for word in ['brand', 'company', 'corp', 'inc', 'ltd'])
            ]
            if filtered_persons:
                return filtered_persons[0]

        return None

    def _get_vendor_address(self, text: str, entities: Dict) -> Optional[str]:
        """Extract vendor address - FIXED VERSION"""
        # Look for address patterns near the vendor name/top of document
        lines = text.split('\n')
        
        # Find lines that look like addresses (contain street indicators)
        address_patterns = [
            r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl)\b',
            r'[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl)\s+[A-Za-z0-9\s,.-]*'
        ]
        
        for line in lines[:15]:  # Check first 15 lines for vendor info
            for pattern in address_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    address = match.group(0).strip()
                    # Make sure it's not the invoice number mixed in
                    if not re.match(r'^\d{4,6}', address):  # Not starting with long number
                        return address
        
        # Fallback to entities but filter out obvious false positives
        addresses = entities.get('addresses', [])
        for addr in addresses:
            # Filter out addresses that start with invoice numbers
            if not re.match(r'^\d{4,6}', addr):
                return addr
        
        return None
   
    def _get_total_amount(self, text: str, entities: Dict) -> Optional[str]:
        """Extract total amount from document."""

        # Improved patterns with multiple currencies and formats
        total_patterns = [
        r'\bTotal:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'\bGrand\s+Total:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'\bAmount\s+Due:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'\bFinal\s+Amount:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'\bBalance\s+Due:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]

        # Try patterns in order
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

        # Fallback: find largest amount that appears near "total" keywords
        money_entities = entities.get('MONEY', [])
        currencies = entities.get('currencies', [])
        all_amounts = money_entities + currencies

        if all_amounts:
            # Score amounts by proximity to total keywords
            best_amount = None
            best_score = -1

            for amount in all_amounts:
                numeric = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?', str(amount))
                if numeric:
                    for num in numeric:
                        # Check if this amount appears near total keywords
                        total_context = rf'.{{0,100}}(?:Total|Amount\s+Due|Grand\s+Total).{{0,100}}{re.escape(num)}.{{0,100}}'
                        if re.search(total_context, text, re.IGNORECASE | re.DOTALL):
                            try:
                                amount_value = float(num.replace(',', ''))
                                if amount_value > best_score:
                                    best_score = amount_value
                                    best_amount = num
                            except ValueError:
                                continue

            if best_amount:
                return best_amount

            # Final fallback: largest amount
            numeric_amounts = []
            for amount in all_amounts:
                numeric = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?', str(amount))
                numeric_amounts.extend(numeric)

            if numeric_amounts:
                max_amount = max(numeric_amounts, key=lambda x: float(x.replace(',', '')))
                return max_amount

        return None
    def _get_subtotal(self, text: str) -> Optional[str]:
        """Extract subtotal amount."""
        subtotal_pattern = r'(?:Subtotal|Sub-total|Sub\s+Total):\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        match = re.search(subtotal_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _get_invoice_date(self, text: str, entities: Dict) -> Optional[str]:
        """Extract invoice date - IMPROVED VERSION"""
        # More comprehensive date patterns
        date_patterns = [
            r'Invoice\s*Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Date\s*[:\-]?\s*(\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4})',  # handles spaces
            r'Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Issued\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Date\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})',
            r'Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})'  # January 5, 2020
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                # Clean up extra spaces
                date_str = re.sub(r'\s+', ' ', date_str)
                return date_str
                
        # Look for dates in common positions (near beginning of document)
        lines = text.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            # Look for standalone dates
            date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', line)
            if date_match:
                return date_match.group(1)
        
        return None
    
    def _get_due_date(self, text: str, entities: Dict) -> Optional[str]:
        """Extract due date."""
        due_date_pattern = r'(?:Due\s+Date|Payment\s+Due):\s*([^\n]+)'
        match = re.search(due_date_pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_single_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Extract first match of a regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
   
    def _get_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from document."""
        patterns = [
            r'Invoice\s+Number:\s*([A-Z0-9\-/]+)',
            r'Invoice\s+No\.?:\s*([A-Z0-9\-/]+)',
            r'Invoice\s+#:\s*([A-Z0-9\-/]+)',
            r'Inv\.?\s+No\.?:\s*([A-Z0-9\-/]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _get_po_number(self, text: str) -> Optional[str]:
        """Extract PO number from document."""
        patterns = [
            r'PO\s+Number:\s*([A-Z0-9\-/]+)',
            r'P\.?O\.?\s+No\.?:\s*([A-Z0-9\-/]+)',
            r'Purchase\s+Order:\s*([A-Z0-9\-/]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_line_items(self, text: str) -> List[Dict[str, str]]:
        """Extract line items from invoice - COMPLETELY REWRITTEN"""
        line_items = []
        lines = text.split('\n')
        
        # Find the table section - look for headers
        table_start = -1
        table_end = -1

        for i, line in enumerate(lines):
            # Look for table headers
            if re.search(r'Item\s+Description.*Price.*Qty.*Total', line, re.IGNORECASE):
                table_start = i + 1
                break
            elif re.search(r'Description.*Price.*Quantity.*Amount', line, re.IGNORECASE):
                table_start = i + 1
                break

        if table_start == -1:
            # Fallback: look for lines with item patterns
            for i, line in enumerate(lines):
                if re.match(r'\s*\d+\s+[A-Za-z]', line):  # starts with number then text
                    table_start = i
                    break

        if table_start == -1:
            return []

        # Find table end (look for totals section)
        for i in range(table_start, len(lines)):
            if re.search(r'Sub\s*Total|Thank\s*you|Terms|Payment', lines[i], re.IGNORECASE):
                table_end = i
                break

        if table_end == -1:
            table_end = len(lines)

        # Extract line items from table section
        for i in range(table_start, table_end):
            line = lines[i].strip()
            if not line:
                continue

            # Pattern for: number + description + price + quantity + total
            pattern = r'^(\d+)\s+(.+?)\s+\$?(\d+\.?\d*)\s+(\d+)\s+\$?(\d+\.?\d*)$'
            match = re.match(pattern, line)

            if match:
                line_items.append({
                    'item_number': match.group(1),
                    'description': match.group(2).strip(),
                    'unit_price': match.group(3),
                    'quantity': match.group(4),
                    'amount': match.group(5)
                })
            else:
                # Alternative pattern - more flexible
                # Look for any line with description and dollar amounts
                amounts = re.findall(r'\$(\d+\.?\d*)', line)
                if len(amounts) >= 2 and re.search(r'[A-Za-z]', line):
                    # Extract description (everything before first dollar amount)
                    desc_match = re.match(r'^(\d+\s+)?(.+?)\s+\$', line)
                    if desc_match:
                        description = desc_match.group(2).strip()
                        # Try to find quantity
                        qty_pattern = r'\$\d+\.?\d*\s+(\d+)\s+\$'
                        qty_match = re.search(qty_pattern, line)
                        quantity = qty_match.group(1) if qty_match else '1'

                        line_items.append({
                            'item_number': desc_match.group(1).strip() if desc_match.group(1) else str(len(line_items) + 1),
                            'description': description,
                            'unit_price': amounts[0],
                            'quantity': quantity,
                            'amount': amounts[-1]  # Last amount is usually the total
                        })

        return line_items

    def _detect_currency(self, text: str) -> str:
        """Detect the primary currency used in the document."""
        if re.search(r'\$', text):
            return 'USD'
        elif re.search(r'€', text):
            return 'EUR'
        elif re.search(r'£', text):
            return 'GBP'
        elif re.search(r'¥', text):
            return 'JPY'    
        elif re.search(r'\b(?:R|Rs|INR)\b', text):
            return 'INR'
        else: 
            return 'USD'  # Default
    
    def _calculate_invoice_confidence(self, text: str, entities: Dict) -> float:
        """Calculate confidence score for invoice extraction."""
        score = 0.0
        
        # Check for key invoice indicators
        if re.search(r'invoice', text, re.IGNORECASE):
            score += 0.3
        if entities.get('ORG'):
            score += 0.2
        if entities.get('currencies') or entities.get('MONEY'):
            score += 0.2
        if entities.get('DATE') or entities.get('dates_structured'):
            score += 0.1
        if entities.get('emails'):
            score += 0.1
        if re.search(r'(?:total|amount|due)', text, re.IGNORECASE):
            score += 0.1
        
        return min(score, 1.0)
    
    # Additional helper methods for other document types
    def _find_contract_date(self, text: str, date_type: str) -> Optional[str]:
        """Find specific contract dates."""
        pattern = rf'{date_type}[^a-zA-Z0-9]?[\s:]*([A-Za-z]+\s+\d{{1,2}},\s+\d{{4}}|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _identify_contract_type(self, text: str) -> Optional[str]:
        """Identify the type of contract."""
        contract_types = {
            'employment': r'employment|job|position|salary',
            'service': r'service|consulting|agreement',
            'purchase': r'purchase|buy|sale|vendor',
            'lease': r'lease|rent|rental|tenant',
            'license': r'license|licensing|intellectual'
        }
        
        for contract_type, pattern in contract_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return contract_type
        
        return 'general'
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text."""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'HTML', 'CSS', 'React', 'Node.js',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Communication',
            'Leadership', 'Problem Solving', 'Teamwork', 'Microsoft Office'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information."""
        education_pattern = r'(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|M\.A\.|B\.A\.|MBA)[^\n]*'
        matches = re.findall(education_pattern, text, re.IGNORECASE)
        return matches
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience."""
        experience_pattern = r'(\d+)\s*\+?\s*years?(?:\s+of\s+experience)?'
        match = re.search(experience_pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_case_numbers(self, text: str) -> List[str]:
        """Extract legal case numbers."""
        case_pattern = r'(?:Case|Docket|File)\s+(?:No\.?|Number)?\s*:?\s*([A-Z0-9-]+)'
        matches = re.findall(case_pattern, text, re.IGNORECASE)
        return matches
    
    def _extract_court_names(self, text: str) -> List[str]:
        """Extract court names."""
        court_pattern = r'([A-Z][a-z]+\s+(?:Court|District|Circuit|Supreme)[^\n]*)'
        matches = re.findall(court_pattern, text)
        return matches
    
    def _identify_legal_document_type(self, text: str) -> Optional[str]:
        """Identify type of legal document."""
        legal_types = {
            'contract': r'contract|agreement|terms',
            'lawsuit': r'lawsuit|complaint|motion',
            'will': r'will|testament|estate',
            'patent': r'patent|invention|intellectual',
            'license': r'license|permit|authorization'
        }
        
        for doc_type, pattern in legal_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return doc_type
        
        return 'legal_document'
    
    def extract_by_document_type(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract information based on document type.
        
        Args:
            text (str): Document text
            document_type (str): Type of document (invoice, contract, resume, etc.)
            
        Returns:
            Dict containing extracted information specific to document type
        """
        if document_type in self.document_extractors:
            return self.document_extractors[document_type](text)
        else:
            logger.warning(f"Unknown document type: {document_type}. Using general extraction.")
            return self.extract_entities(text)
