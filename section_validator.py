from typing import Dict, List, Any
import re

class SectionValidator:
    """
    Validates that the SoW document contains all required sections according to company standards.
    """
    
    def __init__(self):
        # Define required sections for a complete SoW
        self.required_sections = {
            'objectives': 'Project Objectives/Goals',
            'scope': 'Scope of Work',
            'deliverables': 'Deliverables/Outcomes',
            'timeline': 'Timeline/Milestones',
            'acceptance_criteria': 'Acceptance Criteria',
            'assumptions': 'Assumptions & Dependencies',
            'pricing': 'Pricing & Payment Terms',
            'change_control': 'Change Control Process'
        }
        
        # Keywords that indicate each section type
        self.section_keywords = {
            'objectives': [
                'objective', 'objectives', 'goal', 'goals', 'purpose', 
                'aim', 'mission', 'vision', 'target'
            ],
            'scope': [
                'scope', 'project scope', 'scope of work', 'work scope',
                'what is included', 'what will be done', 'project boundaries'
            ],
            'deliverables': [
                'deliverable', 'deliverables', 'outcome', 'outcomes',
                'output', 'outputs', 'result', 'results', 'end product'
            ],
            'timeline': [
                'timeline', 'schedule', 'milestone', 'milestones',
                'deadline', 'deadlines', 'duration', 'timeframe',
                'project schedule', 'delivery schedule'
            ],
            'acceptance_criteria': [
                'acceptance', 'acceptance criteria', 'acceptance test',
                'success criteria', 'completion criteria', 'sign-off',
                'approval criteria', 'quality standards'
            ],
            'assumptions': [
                'assumption', 'assumptions', 'dependencies', 'dependency',
                'constraint', 'constraints', 'prerequisites', 'conditions'
            ],
            'pricing': [
                'pricing', 'payment', 'payment terms', 'cost', 'costs',
                'budget', 'fee', 'fees', 'price', 'rates', 'billing'
            ],
            'change_control': [
                'change', 'changes', 'change control', 'change management',
                'modification', 'modifications', 'variation', 'variations',
                'scope change', 'amendments'
            ]
        }
    
    def validate_sections(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the document contains all required sections.
        
        Args:
            document_data: Parsed document data from DocumentParser
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Get document text and sections
            text = document_data.get('raw_text', '').lower()
            detected_sections = document_data.get('sections', {})
            
            # Check for presence of each required section
            sections_present = {}
            section_details = {}
            
            for section_key, section_name in self.required_sections.items():
                is_present, details = self._check_section_presence(
                    text, detected_sections, section_key
                )
                sections_present[section_name] = is_present
                section_details[section_key] = details
            
            # Calculate completeness score
            present_count = sum(sections_present.values())
            total_required = len(self.required_sections)
            completeness_score = (present_count / total_required) * 100
            
            # Identify missing sections
            missing_sections = [
                name for name, present in sections_present.items() 
                if not present
            ]
            
            # Generate recommendations
            recommendations = self._generate_section_recommendations(missing_sections)
            
            # Create validation results
            validation_results = {
                'completeness_score': completeness_score,
                'sections_present': sections_present,
                'missing_sections': missing_sections,
                'section_details': section_details,
                'recommendations': recommendations,
                'total_required_sections': total_required,
                'sections_found': present_count
            }
            
            return validation_results
            
        except Exception as e:
            return {
                'completeness_score': 0,
                'sections_present': {},
                'missing_sections': list(self.required_sections.values()),
                'error': f"Section validation failed: {str(e)}"
            }
    
    def _check_section_presence(self, text: str, detected_sections: Dict[str, str], 
                               section_key: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if a specific section is present in the document.
        
        Args:
            text: Document text (lowercase)
            detected_sections: Sections detected by parser
            section_key: Key for the section type
            
        Returns:
            Tuple of (is_present, details_dict)
        """
        keywords = self.section_keywords.get(section_key, [])
        
        # Check if section was explicitly detected by parser
        explicit_section = detected_sections.get(section_key)
        if explicit_section and len(explicit_section.strip()) > 20:
            return True, {
                'detection_method': 'explicit_section',
                'content_length': len(explicit_section),
                'content_preview': explicit_section[:200] + '...' if len(explicit_section) > 200 else explicit_section
            }
        
        # Check for keyword presence in text
        keyword_matches = []
        for keyword in keywords:
            pattern = rf'\b{re.escape(keyword)}\b'
            matches = re.findall(pattern, text)
            if matches:
                keyword_matches.extend(matches)
        
        # Determine if section is present based on keyword density
        if keyword_matches:
            # Look for substantial content around keywords
            has_content = self._check_content_around_keywords(text, keywords)
            return has_content, {
                'detection_method': 'keyword_matching',
                'matched_keywords': list(set(keyword_matches)),
                'keyword_count': len(keyword_matches),
                'has_substantial_content': has_content
            }
        
        return False, {
            'detection_method': 'not_found',
            'searched_keywords': keywords
        }
    
    def _check_content_around_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if there's substantial content around section keywords.
        
        Args:
            text: Document text
            keywords: List of keywords to search for
            
        Returns:
            Boolean indicating if substantial content exists
        """
        for keyword in keywords:
            pattern = rf'.*\b{re.escape(keyword)}\b.*'
            matches = re.findall(pattern, text)
            
            for match in matches:
                # Check if the line containing the keyword has substantial content
                # or if the following lines contain related content
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if keyword in line.lower():
                        # Check current line and next few lines for content
                        content_lines = lines[i:i+5]  # Check next 5 lines
                        combined_content = ' '.join(content_lines)
                        
                        # Remove the keyword line and check remaining content
                        remaining_content = ' '.join(content_lines[1:])
                        
                        # Consider it substantial if there's meaningful content
                        if len(remaining_content.split()) > 10:
                            return True
        
        return False
    
    def _generate_section_recommendations(self, missing_sections: List[str]) -> List[Dict[str, str]]:
        """
        Generate recommendations for missing sections.
        
        Args:
            missing_sections: List of missing section names
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        section_templates = {
            'Project Objectives/Goals': {
                'priority': 'High',
                'template': 'Define clear, measurable objectives for the project. Example: "Increase system performance by 25%" or "Reduce processing time to under 2 seconds".',
                'reason': 'Without clear objectives, project success cannot be measured and scope can easily expand.'
            },
            'Scope of Work': {
                'priority': 'Critical',
                'template': 'Explicitly define what work will be performed and, equally important, what is NOT included. Use bullet points for clarity.',
                'reason': 'This is the most important section for preventing scope creep. Must be specific and bounded.'
            },
            'Deliverables/Outcomes': {
                'priority': 'Critical',
                'template': 'List specific, quantified deliverables with clear descriptions. Example: "3 AWS Redshift databases, each with 5-10 tables" instead of "databases as needed".',
                'reason': 'Vague deliverables are the #1 cause of scope creep in fixed-price projects.'
            },
            'Timeline/Milestones': {
                'priority': 'High',
                'template': 'Provide specific dates or durations for key milestones. Include buffer time for reviews and approvals.',
                'reason': 'Clear timelines prevent endless revisions and help control project scope.'
            },
            'Acceptance Criteria': {
                'priority': 'High',
                'template': 'Define specific, testable criteria for each deliverable. Example: "System must process 1000 records in under 30 seconds with 99.9% accuracy".',
                'reason': 'Prevents disputes over when deliverables are "complete" and acceptable.'
            },
            'Assumptions & Dependencies': {
                'priority': 'Medium',
                'template': 'List all assumptions about client resources, data availability, and external dependencies.',
                'reason': 'Documents conditions necessary for project success and provides protection if assumptions prove incorrect.'
            },
            'Pricing & Payment Terms': {
                'priority': 'High',
                'template': 'Clearly state total cost, payment schedule, and what triggers additional charges.',
                'reason': 'Prevents billing disputes and clarifies when additional work becomes billable.'
            },
            'Change Control Process': {
                'priority': 'Critical',
                'template': 'Define how scope changes will be requested, evaluated, and approved. Include impact on timeline and cost.',
                'reason': 'Essential for managing scope creep. All changes must go through formal process.'
            }
        }
        
        for section in missing_sections:
            if section in section_templates:
                template_info = section_templates[section]
                recommendations.append({
                    'section': section,
                    'priority': template_info['priority'],
                    'recommendation': template_info['template'],
                    'reason': template_info['reason']
                })
        
        # Sort by priority
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
