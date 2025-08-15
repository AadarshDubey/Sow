from typing import Dict, List, Any, Optional
import re
from gemini_client import GeminiClient

class VaguenessDetector:
    """
    Detects vague, non-specific, or ambiguous language that could lead to scope creep.
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # Vague quantity indicators
        self.vague_quantities = [
            r'\b(?:a\s+few|few|some|several|many|various|multiple)\b',
            r'\b(?:approximately|roughly|about|around|~)\s*\d+',
            r'\b(?:up\s+to|at\s+least|minimum\s+of|maximum\s+of)\b',
            r'\b(?:as\s+needed|if\s+needed|when\s+required|if\s+required)\b',
            r'\b(?:etc\.?|and\s+so\s+on|among\s+others)\b',
            r'[#]+|\bTBD\b|\bTBA\b',
            r'\d+\s*[-–]\s*\d+(?!\s*(?:days|hours|minutes|seconds))',  # Ranges without time units
        ]
        
        # Vague descriptive terms
        self.vague_descriptors = [
            r'\b(?:suitable|appropriate|reasonable|adequate|sufficient)\b',
            r'\b(?:high\s+quality|good\s+quality|professional)\b',
            r'\b(?:user-friendly|easy\s+to\s+use|intuitive)\b',
            r'\b(?:scalable|robust|efficient|optimal)\b',
            r'\b(?:comprehensive|complete|full|extensive)\b',
            r'\b(?:standard|typical|normal|regular|common)\b'
        ]
        
        # Scope expansion risks
        self.scope_risks = [
            r'\b(?:may\s+include|might\s+include|could\s+include)\b',
            r'\b(?:additional\s+work|extra\s+work|further\s+work)\b',
            r'\b(?:as\s+per\s+client|according\s+to\s+client|client\s+requirements?)\b',
            r'\b(?:and\s+other|plus\s+other|including\s+but\s+not\s+limited\s+to)\b',
            r'\b(?:where\s+applicable|if\s+applicable|as\s+applicable)\b'
        ]
        
        # Ambiguous nouns that need context
        self.ambiguous_nouns = [
            r'\btables?\b(?!\s+(?:and\s+chairs|of\s+contents))',  # Database vs furniture
            r'\bservers?\b(?!\s+(?:room|maintenance))',  # Physical vs software
            r'\bports?\b(?!\s+(?:of\s+call|authority))',  # Network vs shipping
            r'\brecords?\b(?!\s+(?:label|company))',  # Database vs music/documents
            r'\bdocuments?\b',  # Too generic without context
            r'\breports?\b',  # What kind of reports?
            r'\bsystems?\b',  # What kind of systems?
            r'\binterfaces?\b',  # User vs API vs hardware
        ]
    
    def detect_vagueness(self, document_data: Dict[str, Any], use_ai: bool = True) -> Dict[str, Any]:
        """
        Main method to detect vague language in the document.
        
        Args:
            document_data: Parsed document data
            use_ai: Whether to use AI for additional analysis
            
        Returns:
            Dictionary containing vagueness analysis results
        """
        try:
            text = document_data.get('raw_text', '')
            
            # Rule-based vagueness detection
            vague_items = []
            
            # Detect vague quantities
            vague_items.extend(self._detect_pattern_matches(
                text, self.vague_quantities, 'Vague Quantity'
            ))
            
            # Detect vague descriptors
            vague_items.extend(self._detect_pattern_matches(
                text, self.vague_descriptors, 'Vague Descriptor'
            ))
            
            # Detect scope expansion risks
            vague_items.extend(self._detect_pattern_matches(
                text, self.scope_risks, 'Scope Risk'
            ))
            
            # Detect ambiguous nouns
            vague_items.extend(self._detect_pattern_matches(
                text, self.ambiguous_nouns, 'Ambiguous Term'
            ))
            
            # AI-powered analysis if enabled
            if use_ai and vague_items:
                vague_items = self._enhance_with_ai_analysis(text, vague_items)
            
            # Calculate vagueness metrics
            total_words = len(text.split())
            vague_word_count = sum(len(item['text'].split()) for item in vague_items)
            vagueness_percentage = (vague_word_count / total_words) * 100 if total_words > 0 else 0
            
            # Generate suggestions
            suggestions = self._generate_specificity_suggestions(vague_items)
            
            results = {
                'vague_items': vague_items,
                'vagueness_percentage': vagueness_percentage,
                'total_vague_instances': len(vague_items),
                'suggestions': suggestions,
                'severity_breakdown': self._categorize_by_severity(vague_items),
                'ai_enhanced': use_ai
            }
            
            return results
            
        except Exception as e:
            return {
                'vague_items': [],
                'vagueness_percentage': 0,
                'error': f"Vagueness detection failed: {str(e)}"
            }
    
    def _detect_pattern_matches(self, text: str, patterns: List[str], 
                               category: str) -> List[Dict[str, Any]]:
        """
        Detect matches for specific patterns in text.
        
        Args:
            text: Document text
            patterns: List of regex patterns
            category: Category of vagueness
            
        Returns:
            List of detected vague items
        """
        items = []
        lines = text.split('\n')
        
        for pattern in patterns:
            for line_num, line in enumerate(lines):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Get context around the match
                    context_start = max(0, line_num - 1)
                    context_end = min(len(lines), line_num + 2)
                    context_lines = lines[context_start:context_end]
                    
                    item = {
                        'type': category,
                        'text': match.group(),
                        'context': ' '.join(context_lines).strip(),
                        'line_number': line_num + 1,
                        'position': match.start(),
                        'severity': self._assess_severity(match.group(), category),
                        'issue': self._describe_issue(match.group(), category)
                    }
                    items.append(item)
        
        return items
    
    def _enhance_with_ai_analysis(self, text: str, vague_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use AI to provide enhanced analysis and suggestions for vague items.
        
        Args:
            text: Full document text
            vague_items: List of detected vague items
            
        Returns:
            Enhanced vague items with AI suggestions
        """
        try:
            # Process items in batches to avoid token limits
            enhanced_items = []
            batch_size = 5
            
            for i in range(0, len(vague_items), batch_size):
                batch = vague_items[i:i+batch_size]
                enhanced_batch = self.gemini_client.analyze_vagueness_batch(batch, text)
                enhanced_items.extend(enhanced_batch)
            
            return enhanced_items
            
        except Exception as e:
            # Return original items if AI enhancement fails
            return vague_items
    
    def _assess_severity(self, text: str, category: str) -> str:
        """
        Assess the severity of a vague term.
        
        Args:
            text: The vague text
            category: Category of vagueness
            
        Returns:
            Severity level (High, Medium, Low)
        """
        text_lower = text.lower()
        
        # High severity terms that commonly cause scope creep
        high_severity_terms = [
            'as needed', 'if needed', 'when required', 'client requirements',
            'additional work', 'may include', 'and other', '#', 'tbd', 'tba',
            'including but not limited to'
        ]
        
        # Medium severity terms
        medium_severity_terms = [
            'some', 'few', 'several', 'various', 'multiple', 'comprehensive',
            'complete', 'appropriate', 'reasonable', 'standard'
        ]
        
        if any(term in text_lower for term in high_severity_terms):
            return 'High'
        elif any(term in text_lower for term in medium_severity_terms):
            return 'Medium'
        else:
            return 'Low'
    
    def _describe_issue(self, text: str, category: str) -> str:
        """
        Provide a description of why the text is problematic.
        
        Args:
            text: The vague text
            category: Category of vagueness
            
        Returns:
            Description of the issue
        """
        text_lower = text.lower()
        
        issue_descriptions = {
            'Vague Quantity': {
                'few': 'Undefined quantity - could be 2 or 20',
                'some': 'Unclear amount - needs specific number',
                'several': 'Ambiguous quantity - specify exact count',
                'many': 'Non-specific quantity - provide range or exact number',
                'various': 'Undefined variety - list specific items',
                '#': 'Placeholder symbol - replace with actual number',
                'tbd': 'To be determined - specify now to prevent scope creep',
                'approximately': 'Approximation allows for scope expansion',
                'as needed': 'Open-ended commitment - set clear limits'
            },
            'Vague Descriptor': {
                'appropriate': 'Subjective term - define specific criteria',
                'reasonable': 'Opinion-based - set measurable standards',
                'professional': 'Undefined quality level - specify requirements',
                'high quality': 'Subjective standard - define measurable criteria',
                'comprehensive': 'Scope can expand - define exact coverage',
                'standard': 'Unclear baseline - specify which standard'
            },
            'Scope Risk': {
                'may include': 'Optional scope that could become required',
                'additional work': 'Undefined extra work - creates billing issues',
                'client requirements': 'Open-ended client demands',
                'and other': 'Undefined additional items',
                'as applicable': 'Conditional scope that lacks clear boundaries'
            },
            'Ambiguous Term': {
                'default': 'Term needs context to be clearly understood'
            }
        }
        
        category_issues = issue_descriptions.get(category, {})
        
        # Find specific issue description
        for key_term, description in category_issues.items():
            if key_term in text_lower:
                return description
        
        # Return default description for category
        if category == 'Vague Quantity':
            return 'Quantity is not clearly specified'
        elif category == 'Vague Descriptor':
            return 'Description is subjective and measurable criteria are needed'
        elif category == 'Scope Risk':
            return 'Language creates risk of scope expansion'
        elif category == 'Ambiguous Term':
            return 'Term needs additional context for clarity'
        else:
            return 'Language is vague and could lead to misunderstandings'
    
    def _generate_specificity_suggestions(self, vague_items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate suggestions to make vague language more specific.
        
        Args:
            vague_items: List of detected vague items
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        
        suggestion_templates = {
            'few': 'Replace with specific number (e.g., "3-5" instead of "a few")',
            'some': 'Specify exact quantity (e.g., "4 reports" instead of "some reports")',
            'several': 'Define exact count (e.g., "6-8 databases" instead of "several databases")',
            'various': 'List specific items (e.g., "MySQL, PostgreSQL, and MongoDB" instead of "various databases")',
            '#': 'Replace with actual number (e.g., "3 servers" instead of "# servers")',
            'tbd': 'Define now to prevent scope disputes',
            'as needed': 'Set clear limits (e.g., "up to 5 additional reports if requested")',
            'appropriate': 'Define specific criteria (e.g., "meets SOC 2 compliance standards")',
            'comprehensive': 'Define scope boundaries (e.g., "covers all 12 identified modules")',
            'may include': 'Either include or exclude - avoid conditional language',
            'additional work': 'Define what additional work is billable vs included'
        }
        
        # Group similar items
        seen_texts = set()
        for item in vague_items:
            text_lower = item['text'].lower()
            
            # Skip if we've already provided a suggestion for this text
            if text_lower in seen_texts:
                continue
            seen_texts.add(text_lower)
            
            # Find matching suggestion
            suggestion_text = None
            for template_key, template_suggestion in suggestion_templates.items():
                if template_key in text_lower:
                    suggestion_text = template_suggestion
                    break
            
            if not suggestion_text:
                suggestion_text = f'Make "{item["text"]}" more specific and measurable'
            
            suggestions.append({
                'original_text': item['text'],
                'suggestion': suggestion_text,
                'severity': item.get('severity', 'Medium'),
                'type': item.get('type', 'Unknown')
            })
        
        return suggestions
    
    def _categorize_by_severity(self, vague_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize vague items by severity level.
        
        Args:
            vague_items: List of detected vague items
            
        Returns:
            Dictionary with severity counts
        """
        severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        
        for item in vague_items:
            severity = item.get('severity', 'Low')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return severity_counts
