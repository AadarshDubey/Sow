from typing import Dict, List, Any
import re
from gemini_client import GeminiClient

class RiskAssessor:
    """
    Assesses potential scope creep risks and their impact on fixed-price projects.
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # High-risk phrases that commonly lead to scope creep
        self.high_risk_patterns = [
            r'\b(?:as\s+per\s+client\s+requirements?|according\s+to\s+client\s+requirements?)\b',
            r'\b(?:additional\s+work\s+may\s+be\s+performed|extra\s+work\s+may\s+be\s+done)\b',
            r'\b(?:including\s+but\s+not\s+limited\s+to)\b',
            r'\b(?:and\s+any\s+other|plus\s+any\s+other|and\s+other\s+related)\b',
            r'\b(?:as\s+needed|when\s+needed|if\s+needed|where\s+needed)\b',
            r'\b(?:may\s+require\s+additional|might\s+need\s+extra)\b',
            r'\b(?:subject\s+to\s+change|may\s+be\s+modified)\b',
            r'\b(?:to\s+be\s+determined|tbd|to\s+be\s+decided)\b'
        ]
        
        # Medium-risk patterns
        self.medium_risk_patterns = [
            r'\b(?:approximately|roughly|about|around)\s+\d+',
            r'\b(?:up\s+to|at\s+least|minimum\s+of|maximum\s+of)\b',
            r'\b(?:may\s+include|might\s+include|could\s+include)\b',
            r'\b(?:where\s+applicable|if\s+applicable|as\s+applicable)\b',
            r'\b(?:reasonable\s+efforts?|best\s+efforts?)\b',
            r'\b(?:appropriate|suitable|adequate)\b',
            r'\d+\s*[-–]\s*\d+(?!\s*(?:days|hours|minutes|seconds|years))',  # Ranges without clear bounds
            r'\b(?:standard|typical|normal|usual)\b'
        ]
        
        # Low-risk patterns (still worth flagging)
        self.low_risk_patterns = [
            r'\b(?:generally|usually|typically|normally)\b',
            r'\b(?:comprehensive|complete|full|thorough)\b',
            r'\b(?:various|multiple|several|few)\b',
            r'\b(?:high\s+quality|professional\s+grade)\b'
        ]
        
        # Deliverable-specific risks
        self.deliverable_risks = [
            r'(?:build|create|develop)\s+(?:databases?|systems?|applications?)\s*(?:as\s+needed|#|\btbd\b)',
            r'(?:reports?|dashboards?|interfaces?)\s*(?:\d+\s*[-–]\s*\d+|as\s+required)',
            r'(?:testing|documentation|training)\s+(?:as\s+needed|if\s+required)',
            r'(?:maintenance|support|updates?)\s+(?:ongoing|as\s+needed)'
        ]
    
    def assess_risks(self, document_data: Dict[str, Any], use_ai: bool = True) -> Dict[str, Any]:
        """
        Main method to assess scope creep risks in the document.
        
        Args:
            document_data: Parsed document data
            use_ai: Whether to use AI for enhanced risk analysis
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            text = document_data.get('raw_text', '')
            sections = document_data.get('sections', {})
            
            # Detect risk patterns
            risk_items = []
            
            # High-risk patterns
            risk_items.extend(self._detect_risk_patterns(
                text, self.high_risk_patterns, 'High', 'Scope Expansion Risk'
            ))
            
            # Medium-risk patterns
            risk_items.extend(self._detect_risk_patterns(
                text, self.medium_risk_patterns, 'Medium', 'Ambiguous Specification'
            ))
            
            # Low-risk patterns
            risk_items.extend(self._detect_risk_patterns(
                text, self.low_risk_patterns, 'Low', 'Vague Language'
            ))
            
            # Deliverable-specific risks
            risk_items.extend(self._detect_risk_patterns(
                text, self.deliverable_risks, 'High', 'Deliverable Risk'
            ))
            
            # Analyze sections for structural risks
            structural_risks = self._analyze_structural_risks(sections)
            risk_items.extend(structural_risks)
            
            # AI-enhanced risk analysis
            if use_ai and risk_items:
                risk_items = self._enhance_with_ai_analysis(text, risk_items)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(risk_items)
            
            # Generate mitigation strategies
            mitigations = self._generate_mitigation_strategies(risk_items)
            
            # Create priority rankings
            priority_risks = self._prioritize_risks(risk_items)
            
            results = {
                'risk_score': risk_score,
                'risk_items': risk_items,
                'total_risks': len(risk_items),
                'risk_breakdown': self._categorize_by_risk_level(risk_items),
                'priority_risks': priority_risks,
                'mitigation_strategies': mitigations,
                'ai_enhanced': use_ai,
                'risk_categories': self._categorize_by_type(risk_items)
            }
            
            return results
            
        except Exception as e:
            return {
                'risk_score': 0,
                'risk_items': [],
                'error': f"Risk assessment failed: {str(e)}"
            }
    
    def _detect_risk_patterns(self, text: str, patterns: List[str], 
                             risk_level: str, category: str) -> List[Dict[str, Any]]:
        """
        Detect risk patterns in the text.
        
        Args:
            text: Document text
            patterns: List of regex patterns to search for
            risk_level: Risk level (High, Medium, Low)
            category: Risk category
            
        Returns:
            List of detected risk items
        """
        items = []
        lines = text.split('\n')
        
        for pattern in patterns:
            for line_num, line in enumerate(lines):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Get broader context for risk assessment
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 3)
                    context_lines = lines[context_start:context_end]
                    
                    # Analyze the impact potential
                    impact = self._assess_impact(match.group(), context_lines, risk_level)
                    
                    item = {
                        'risk_level': risk_level,
                        'category': category,
                        'text': match.group().strip(),
                        'context': ' '.join(context_lines).strip(),
                        'line_number': line_num + 1,
                        'description': self._describe_risk(match.group(), category),
                        'impact': impact,
                        'likelihood': self._assess_likelihood(match.group(), context_lines)
                    }
                    items.append(item)
        
        return items
    
    def _analyze_structural_risks(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Analyze structural risks in document organization.
        
        Args:
            sections: Document sections
            
        Returns:
            List of structural risk items
        """
        structural_risks = []
        
        # Check deliverables section for risks
        deliverables_text = sections.get('deliverables', '').lower()
        if deliverables_text:
            # Look for unbounded deliverables
            if re.search(r'(?:reports?|documents?|files?)\s*(?:as\s+needed|when\s+required)', deliverables_text):
                structural_risks.append({
                    'risk_level': 'High',
                    'category': 'Unbounded Deliverables',
                    'text': 'Deliverables section contains open-ended commitments',
                    'context': deliverables_text[:200],
                    'description': 'Deliverables without clear quantity limits',
                    'impact': 'High - unlimited work commitment',
                    'likelihood': 'High'
                })
        
        # Check scope section for boundary issues
        scope_text = sections.get('scope', '').lower()
        if scope_text:
            if not re.search(r'(?:not\s+included|out\s+of\s+scope|excluded)', scope_text):
                structural_risks.append({
                    'risk_level': 'Medium',
                    'category': 'Missing Exclusions',
                    'text': 'Scope section lacks clear exclusions',
                    'context': scope_text[:200],
                    'description': 'No explicit "out of scope" items defined',
                    'impact': 'Medium - unclear boundaries',
                    'likelihood': 'Medium'
                })
        
        # Check for change control presence
        change_control_text = sections.get('change_control', '').lower()
        if not change_control_text or len(change_control_text.strip()) < 50:
            structural_risks.append({
                'risk_level': 'High',
                'category': 'Missing Change Control',
                'text': 'Weak or missing change control process',
                'context': change_control_text or 'No change control section found',
                'description': 'No formal process for handling scope changes',
                'impact': 'High - uncontrolled scope expansion',
                'likelihood': 'High'
            })
        
        return structural_risks
    
    def _enhance_with_ai_analysis(self, text: str, risk_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use AI to enhance risk analysis with contextual understanding.
        
        Args:
            text: Full document text
            risk_items: List of detected risk items
            
        Returns:
            Enhanced risk items with AI insights
        """
        try:
            # Process high-priority risks first
            high_priority_items = [item for item in risk_items if item['risk_level'] == 'High']
            
            if high_priority_items:
                enhanced_items = self.gemini_client.analyze_contract_risks(high_priority_items, text)
                
                # Merge enhanced analysis back
                enhanced_dict = {item['text']: item for item in enhanced_items}
                
                for item in risk_items:
                    if item['text'] in enhanced_dict:
                        enhanced_item = enhanced_dict[item['text']]
                        item.update({
                            'mitigation': enhanced_item.get('mitigation', ''),
                            'business_impact': enhanced_item.get('business_impact', ''),
                            'ai_confidence': enhanced_item.get('confidence', 0.5)
                        })
            
            return risk_items
            
        except Exception as e:
            # Return original items if AI enhancement fails
            return risk_items
    
    def _assess_impact(self, risk_text: str, context_lines: List[str], risk_level: str) -> str:
        """
        Assess the potential business impact of a risk.
        
        Args:
            risk_text: The risky text
            context_lines: Surrounding context
            risk_level: Base risk level
            
        Returns:
            Impact assessment string
        """
        context = ' '.join(context_lines).lower()
        risk_lower = risk_text.lower()
        
        # High impact scenarios
        if any(term in risk_lower for term in ['additional work', 'as needed', 'client requirements']):
            return 'High - Unlimited scope expansion possible'
        
        if any(term in context for term in ['deliverable', 'payment', 'milestone', 'deadline']):
            if risk_level == 'High':
                return 'High - Affects project deliverables and timeline'
            elif risk_level == 'Medium':
                return 'Medium - May affect project delivery'
        
        # Default impact based on risk level
        impact_mapping = {
            'High': 'High - Significant scope creep risk',
            'Medium': 'Medium - Moderate expansion risk',
            'Low': 'Low - Minor clarification needed'
        }
        
        return impact_mapping.get(risk_level, 'Medium - Uncertain impact')
    
    def _assess_likelihood(self, risk_text: str, context_lines: List[str]) -> str:
        """
        Assess the likelihood that this risk will materialize.
        
        Args:
            risk_text: The risky text
            context_lines: Surrounding context
            
        Returns:
            Likelihood assessment string
        """
        risk_lower = risk_text.lower()
        
        # High likelihood terms
        high_likelihood_terms = [
            'as needed', 'client requirements', 'additional work',
            'may include', 'tbd', 'to be determined'
        ]
        
        if any(term in risk_lower for term in high_likelihood_terms):
            return 'High'
        
        # Medium likelihood terms
        medium_likelihood_terms = [
            'approximately', 'about', 'around', 'up to',
            'may require', 'might need', 'if applicable'
        ]
        
        if any(term in risk_lower for term in medium_likelihood_terms):
            return 'Medium'
        
        return 'Low'
    
    def _describe_risk(self, risk_text: str, category: str) -> str:
        """
        Provide a description of the specific risk.
        
        Args:
            risk_text: The risky text
            category: Risk category
            
        Returns:
            Risk description
        """
        risk_lower = risk_text.lower()
        
        risk_descriptions = {
            'as per client requirements': 'Client can expand scope by changing requirements',
            'additional work may be performed': 'Open commitment to undefined extra work',
            'including but not limited to': 'List can be expanded indefinitely',
            'as needed': 'Work quantity not bounded - unlimited potential',
            'tbd': 'Undefined scope creates expansion risk',
            'may include': 'Optional items may become required',
            'approximately': 'Estimate can be exceeded without clear limits',
            'up to': 'Upper bound may be treated as minimum',
            'reasonable efforts': 'Subjective standard allows scope expansion',
            'appropriate': 'Client defines what is appropriate'
        }
        
        # Find specific description
        for key_phrase, description in risk_descriptions.items():
            if key_phrase in risk_lower:
                return description
        
        # Category-based default descriptions
        category_defaults = {
            'Scope Expansion Risk': 'Language allows for unlimited scope expansion',
            'Ambiguous Specification': 'Specification lacks clear boundaries',
            'Deliverable Risk': 'Deliverable definition creates expansion risk',
            'Vague Language': 'Unclear language may lead to misunderstandings',
            'Unbounded Deliverables': 'No clear limit on deliverable quantity',
            'Missing Change Control': 'No process to control scope changes'
        }
        
        return category_defaults.get(category, 'Undefined risk that may impact project scope')
    
    def _calculate_risk_score(self, risk_items: List[Dict[str, Any]]) -> float:
        """
        Calculate overall risk score (0-100, where 100 is highest risk).
        
        Args:
            risk_items: List of risk items
            
        Returns:
            Risk score as float
        """
        if not risk_items:
            return 0.0
        
        # Weight risks by level
        risk_weights = {'High': 10, 'Medium': 5, 'Low': 2}
        total_weighted_risk = sum(risk_weights.get(item['risk_level'], 2) for item in risk_items)
        
        # Normalize to 0-100 scale (assuming 10 high-risk items = 100% risk)
        max_possible_risk = 100  # 10 high-risk items
        risk_score = min(100.0, (total_weighted_risk / max_possible_risk) * 100)
        
        return round(risk_score, 1)
    
    def _generate_mitigation_strategies(self, risk_items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate mitigation strategies for identified risks.
        
        Args:
            risk_items: List of risk items
            
        Returns:
            List of mitigation strategy dictionaries
        """
        mitigations = []
        
        # Group risks by type for consolidated mitigation advice
        risk_groups = {}
        for item in risk_items:
            category = item.get('category', 'General')
            if category not in risk_groups:
                risk_groups[category] = []
            risk_groups[category].append(item)
        
        mitigation_templates = {
            'Scope Expansion Risk': {
                'strategy': 'Define explicit scope boundaries and exclusions',
                'action': 'Add "Out of Scope" section listing what is NOT included',
                'urgency': 'Critical - Fix before contract signing'
            },
            'Ambiguous Specification': {
                'strategy': 'Replace vague terms with specific, measurable criteria',
                'action': 'Convert all approximations to exact numbers or ranges with clear bounds',
                'urgency': 'High - Clarify during contract negotiation'
            },
            'Deliverable Risk': {
                'strategy': 'Quantify all deliverables with specific counts and acceptance criteria',
                'action': 'Replace phrases like "as needed" with "up to X items" with additional work billable',
                'urgency': 'Critical - Essential for fixed-price projects'
            },
            'Unbounded Deliverables': {
                'strategy': 'Set clear limits on all deliverables and define additional work process',
                'action': 'Specify maximum quantities and make excess work billable at agreed rates',
                'urgency': 'Critical - Unlimited deliverables kill profitability'
            },
            'Missing Change Control': {
                'strategy': 'Implement formal change control process',
                'action': 'Add section defining how scope changes are requested, evaluated, and approved',
                'urgency': 'Critical - Essential for scope management'
            }
        }
        
        for category, items in risk_groups.items():
            if category in mitigation_templates:
                template = mitigation_templates[category]
                mitigations.append({
                    'category': category,
                    'affected_items': len(items),
                    'strategy': template['strategy'],
                    'action': template['action'],
                    'urgency': template['urgency']
                })
        
        return mitigations
    
    def _prioritize_risks(self, risk_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize risks by impact and likelihood.
        
        Args:
            risk_items: List of risk items
            
        Returns:
            List of top priority risks
        """
        # Score risks based on level and likelihood
        def risk_priority_score(item):
            risk_level_scores = {'High': 3, 'Medium': 2, 'Low': 1}
            likelihood_scores = {'High': 3, 'Medium': 2, 'Low': 1}
            
            risk_score = risk_level_scores.get(item.get('risk_level', 'Low'), 1)
            likelihood_score = likelihood_scores.get(item.get('likelihood', 'Low'), 1)
            
            return risk_score * likelihood_score
        
        # Sort by priority score (highest first)
        sorted_risks = sorted(risk_items, key=risk_priority_score, reverse=True)
        
        # Return top 10 or all if less than 10
        return sorted_risks[:10]
    
    def _categorize_by_risk_level(self, risk_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize risks by their risk level.
        
        Args:
            risk_items: List of risk items
            
        Returns:
            Dictionary with risk level counts
        """
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        
        for item in risk_items:
            risk_level = item.get('risk_level', 'Low')
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        return risk_counts
    
    def _categorize_by_type(self, risk_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize risks by their type/category.
        
        Args:
            risk_items: List of risk items
            
        Returns:
            Dictionary with risk type counts
        """
        type_counts = {}
        
        for item in risk_items:
            category = item.get('category', 'Unknown')
            type_counts[category] = type_counts.get(category, 0) + 1
        
        return type_counts
