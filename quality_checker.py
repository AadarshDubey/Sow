from typing import Dict, List, Any, Tuple
import re
import string
from collections import defaultdict
from gemini_client import GeminiClient

class QualityChecker:
    """
    Checks document quality including grammar, formatting, consistency, and professionalism.
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # Common spelling mistakes in business documents
        self.common_mistakes = {
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'definately': 'definitely',
            'accomodate': 'accommodate',
            'untill': 'until',
            'sucessful': 'successful',
            'neccessary': 'necessary',
            'acheive': 'achieve',
            'maintainance': 'maintenance'
        }
        
        # Inconsistent technology naming patterns
        self.tech_terms = {
            'aws': 'AWS',
            'sql': 'SQL',
            'api': 'API',
            'json': 'JSON',
            'xml': 'XML',
            'html': 'HTML',
            'css': 'CSS',
            'javascript': 'JavaScript',
            'python': 'Python',
            'java': 'Java',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes'
        }
        
        # Professional language replacements
        self.unprofessional_terms = {
            'asap': 'as soon as possible',
            'fyi': 'for your information',
            'btw': 'by the way',
            'gonna': 'going to',
            'wanna': 'want to',
            'kinda': 'kind of',
            'sorta': 'sort of',
            'stuff': 'items/materials',
            'things': 'components/elements',
            'guys': 'team members'
        }
    
    def check_quality(self, document_data: Dict[str, Any], use_ai: bool = True) -> Dict[str, Any]:
        """
        Main method to check document quality across multiple dimensions.
        
        Args:
            document_data: Parsed document data
            use_ai: Whether to use AI for enhanced quality analysis
            
        Returns:
            Dictionary containing quality analysis results
        """
        try:
            text = document_data.get('raw_text', '')
            formatting = document_data.get('formatting', {})
            
            quality_issues = []
            
            # Check spelling and common mistakes
            spelling_issues = self._check_spelling(text)
            quality_issues.extend(spelling_issues)
            
            # Check capitalization consistency
            capitalization_issues = self._check_capitalization(text)
            quality_issues.extend(capitalization_issues)
            
            # Check formatting consistency
            formatting_issues = self._check_formatting(text, formatting)
            quality_issues.extend(formatting_issues)
            
            # Check professional language
            professionalism_issues = self._check_professionalism(text)
            quality_issues.extend(professionalism_issues)
            
            # Check grammar patterns
            grammar_issues = self._check_basic_grammar(text)
            quality_issues.extend(grammar_issues)
            
            # AI-enhanced quality analysis
            if use_ai and text.strip():
                ai_issues = self._ai_quality_analysis(text)
                quality_issues.extend(ai_issues)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(quality_issues, len(text.split()))
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(quality_issues)
            
            results = {
                'quality_score': quality_score,
                'issues': quality_issues,
                'total_issues': len(quality_issues),
                'issue_breakdown': self._categorize_issues(quality_issues),
                'suggestions': suggestions,
                'ai_enhanced': use_ai,
                'readability_metrics': self._calculate_readability_metrics(text)
            }
            
            return results
            
        except Exception as e:
            return {
                'quality_score': 0,
                'issues': [],
                'error': f"Quality check failed: {str(e)}"
            }
    
    def _check_spelling(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for common spelling mistakes.
        
        Args:
            text: Document text
            
        Returns:
            List of spelling issue dictionaries
        """
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            words = re.findall(r'\b\w+\b', line.lower())
            
            for word in words:
                if word in self.common_mistakes:
                    issues.append({
                        'type': 'Spelling Error',
                        'severity': 'Medium',
                        'text': word,
                        'suggestion': self.common_mistakes[word],
                        'line_number': line_num + 1,
                        'description': f'"{word}" should be "{self.common_mistakes[word]}"',
                        'context': line.strip()
                    })
        
        return issues
    
    def _check_capitalization(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for capitalization consistency, especially for technology terms.
        
        Args:
            text: Document text
            
        Returns:
            List of capitalization issue dictionaries
        """
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            words = re.findall(r'\b\w+\b', line)
            
            for word in words:
                word_lower = word.lower()
                if word_lower in self.tech_terms and word != self.tech_terms[word_lower]:
                    issues.append({
                        'type': 'Capitalization Error',
                        'severity': 'Low',
                        'text': word,
                        'suggestion': self.tech_terms[word_lower],
                        'line_number': line_num + 1,
                        'description': f'Technology term "{word}" should be "{self.tech_terms[word_lower]}"',
                        'context': line.strip()
                    })
        
        # Check for inconsistent capitalization of the same word
        word_variations = defaultdict(set)
        for word in re.findall(r'\b[A-Za-z]+\b', text):
            if len(word) > 3:  # Only check longer words
                word_variations[word.lower()].add(word)
        
        for word_lower, variations in word_variations.items():
            if len(variations) > 1 and word_lower not in self.tech_terms:
                # Find the most common capitalization
                variation_counts = defaultdict(int)
                for variation in variations:
                    variation_counts[variation] += text.count(variation)
                
                most_common = max(variation_counts.items(), key=lambda x: x[1])[0]
                
                for variation in variations:
                    if variation != most_common:
                        issues.append({
                            'type': 'Inconsistent Capitalization',
                            'severity': 'Low',
                            'text': variation,
                            'suggestion': most_common,
                            'description': f'Use consistent capitalization: "{most_common}" (most common form)',
                            'context': f'Found variations: {", ".join(variations)}'
                        })
        
        return issues
    
    def _check_formatting(self, text: str, formatting_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check formatting consistency and best practices.
        
        Args:
            text: Document text
            formatting_info: Formatting information from parser
            
        Returns:
            List of formatting issue dictionaries
        """
        issues = []
        lines = text.split('\n')
        
        # Check for inconsistent bullet point styles
        bullet_styles = []
        for line in lines:
            stripped = line.strip()
            if re.match(r'^[-•*◦]\s+', stripped):
                bullet_char = stripped[0]
                bullet_styles.append(bullet_char)
        
        if len(set(bullet_styles)) > 1:
            most_common_bullet = max(set(bullet_styles), key=bullet_styles.count)
            issues.append({
                'type': 'Inconsistent Bullets',
                'severity': 'Medium',
                'text': f'Multiple bullet styles: {set(bullet_styles)}',
                'suggestion': f'Use consistent bullet style: "{most_common_bullet}"',
                'description': 'Document uses multiple bullet point styles',
                'context': f'Found styles: {", ".join(set(bullet_styles))}'
            })
        
        # Check for missing numbering in what appears to be a numbered list
        potential_numbered_items = []
        for line_num, line in enumerate(lines):
            stripped = line.strip()
            # Look for lines that start with words that suggest they should be numbered
            if re.match(r'^(?:first|second|third|next|then|finally|lastly)\b', stripped, re.IGNORECASE):
                potential_numbered_items.append((line_num + 1, stripped))
        
        if len(potential_numbered_items) >= 2:
            issues.append({
                'type': 'Missing Numbering',
                'severity': 'Medium',
                'text': 'Sequential items without numbers',
                'suggestion': 'Add numbering to sequential items (1., 2., 3., etc.)',
                'description': 'Items appear to be in sequence but lack numbering',
                'context': f'Found {len(potential_numbered_items)} sequential items'
            })
        
        # Check for excessive line breaks
        empty_line_sequences = []
        empty_count = 0
        for line in lines:
            if not line.strip():
                empty_count += 1
            else:
                if empty_count > 2:
                    empty_line_sequences.append(empty_count)
                empty_count = 0
        
        if empty_line_sequences:
            issues.append({
                'type': 'Excessive Line Breaks',
                'severity': 'Low',
                'text': f'Found {len(empty_line_sequences)} instances of 3+ consecutive empty lines',
                'suggestion': 'Use consistent spacing (1-2 empty lines maximum)',
                'description': 'Too many consecutive empty lines affect readability',
                'context': f'Max consecutive empty lines: {max(empty_line_sequences)}'
            })
        
        return issues
    
    def _check_professionalism(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for unprofessional language and suggest improvements.
        
        Args:
            text: Document text
            
        Returns:
            List of professionalism issue dictionaries
        """
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            words = re.findall(r'\b\w+\b', line.lower())
            
            for word in words:
                if word in self.unprofessional_terms:
                    issues.append({
                        'type': 'Unprofessional Language',
                        'severity': 'Medium',
                        'text': word,
                        'suggestion': self.unprofessional_terms[word],
                        'line_number': line_num + 1,
                        'description': f'Replace informal "{word}" with "{self.unprofessional_terms[word]}"',
                        'context': line.strip()
                    })
        
        # Check for excessive use of exclamation points
        exclamation_count = text.count('!')
        total_sentences = len(re.findall(r'[.!?]+', text))
        if total_sentences > 0 and (exclamation_count / total_sentences) > 0.1:
            issues.append({
                'type': 'Excessive Punctuation',
                'severity': 'Low',
                'text': f'{exclamation_count} exclamation points in {total_sentences} sentences',
                'suggestion': 'Use exclamation points sparingly in professional documents',
                'description': 'Too many exclamation points reduce professionalism',
                'context': f'Ratio: {exclamation_count/total_sentences:.1%}'
            })
        
        return issues
    
    def _check_basic_grammar(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for basic grammar issues using pattern matching.
        
        Args:
            text: Document text
            
        Returns:
            List of grammar issue dictionaries
        """
        issues = []
        lines = text.split('\n')
        
        # Common grammar patterns
        grammar_patterns = [
            (r'\bit\'s\b.*\bown\b', 'Possible confusion: "it\'s" (it is) vs "its" (possessive)'),
            (r'\byour\s+welcome\b', 'Should be "you\'re welcome" (you are welcome)'),
            (r'\bwho\'s\b.*\b(?:car|book|house)\b', 'Possible confusion: "who\'s" (who is) vs "whose" (possessive)'),
            (r'\bthen\b.*\bthan\b|\bthan\b.*\bthen\b', 'Check "then" (time) vs "than" (comparison) usage'),
            (r'\beffect\b.*\baffect\b|\baffect\b.*\beffect\b', 'Check "effect" (noun) vs "affect" (verb) usage'),
            (r'\ba\s+(?:unique|honest|hour)', 'Use "an" before words starting with vowel sounds'),
            (r'\ban\s+(?:user|university|european)', 'Use "a" before words starting with consonant sounds')
        ]
        
        for line_num, line in enumerate(lines):
            for pattern, description in grammar_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'Grammar Check',
                        'severity': 'Medium',
                        'text': line.strip()[:50] + '...' if len(line.strip()) > 50 else line.strip(),
                        'suggestion': 'Review grammar usage',
                        'line_number': line_num + 1,
                        'description': description,
                        'context': line.strip()
                    })
        
        # Check for sentence fragments (very basic check)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                # Very basic check: sentence should have a verb
                words = sentence.split()
                has_verb = any(word.lower() in ['is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'can', 'should', 'must', 'do', 'does', 'did'] for word in words)
                
                if not has_verb and len(words) > 3:
                    issues.append({
                        'type': 'Possible Fragment',
                        'severity': 'Low',
                        'text': sentence[:50] + '...' if len(sentence) > 50 else sentence,
                        'suggestion': 'Verify this is a complete sentence',
                        'description': 'Sentence may be missing a verb or be incomplete',
                        'context': sentence
                    })
        
        return issues
    
    def _ai_quality_analysis(self, text: str) -> List[Dict[str, Any]]:
        """
        Use AI to perform advanced quality analysis.
        
        Args:
            text: Document text
            
        Returns:
            List of AI-detected quality issues
        """
        try:
            # Use AI for grammar, style, and clarity analysis
            ai_issues = self.gemini_client.analyze_document_quality(text)
            return ai_issues
        except Exception as e:
            # Return empty list if AI analysis fails
            return []
    
    def _calculate_quality_score(self, issues: List[Dict[str, Any]], word_count: int) -> float:
        """
        Calculate overall quality score based on issues found.
        
        Args:
            issues: List of quality issues
            word_count: Total word count in document
            
        Returns:
            Quality score (0-100, where 100 is perfect)
        """
        if word_count == 0:
            return 0.0
        
        # Weight issues by severity
        severity_weights = {'High': 5, 'Medium': 3, 'Low': 1}
        total_penalty = sum(severity_weights.get(issue.get('severity', 'Low'), 1) for issue in issues)
        
        # Calculate penalty per 100 words
        penalty_per_hundred = (total_penalty / word_count) * 100
        
        # Base score is 100, subtract penalties
        quality_score = max(0.0, 100.0 - (penalty_per_hundred * 2))  # Multiply by 2 to make penalties more significant
        
        return round(quality_score, 1)
    
    def _generate_improvement_suggestions(self, issues: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate improvement suggestions based on identified issues.
        
        Args:
            issues: List of quality issues
            
        Returns:
            List of improvement suggestion dictionaries
        """
        suggestions = []
        
        # Group issues by type
        issue_groups = defaultdict(list)
        for issue in issues:
            issue_type = issue.get('type', 'General')
            issue_groups[issue_type].append(issue)
        
        suggestion_templates = {
            'Spelling Error': 'Review document with spell-check tool and correct identified errors',
            'Capitalization Error': 'Standardize capitalization of technology terms and proper nouns',
            'Inconsistent Capitalization': 'Use consistent capitalization throughout the document',
            'Inconsistent Bullets': 'Choose one bullet style and use consistently',
            'Missing Numbering': 'Add numbering to sequential or hierarchical lists',
            'Excessive Line Breaks': 'Remove excessive empty lines and use consistent spacing',
            'Unprofessional Language': 'Replace informal language with professional business terms',
            'Grammar Check': 'Review grammar and consider professional proofreading',
            'Possible Fragment': 'Ensure all sentences are complete with subject and verb'
        }
        
        for issue_type, issue_list in issue_groups.items():
            if issue_type in suggestion_templates:
                suggestions.append({
                    'category': issue_type,
                    'count': len(issue_list),
                    'suggestion': suggestion_templates[issue_type],
                    'priority': self._get_suggestion_priority(issue_type),
                    'examples': [issue.get('text', '') for issue in issue_list[:3]]  # Show up to 3 examples
                })
        
        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 2))
        
        return suggestions
    
    def _get_suggestion_priority(self, issue_type: str) -> str:
        """
        Get priority level for suggestion based on issue type.
        
        Args:
            issue_type: Type of quality issue
            
        Returns:
            Priority level (High, Medium, Low)
        """
        high_priority = ['Spelling Error', 'Grammar Check', 'Unprofessional Language']
        medium_priority = ['Capitalization Error', 'Inconsistent Bullets', 'Missing Numbering']
        
        if issue_type in high_priority:
            return 'High'
        elif issue_type in medium_priority:
            return 'Medium'
        else:
            return 'Low'
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize issues by type for summary statistics.
        
        Args:
            issues: List of quality issues
            
        Returns:
            Dictionary with issue type counts
        """
        issue_counts = defaultdict(int)
        
        for issue in issues:
            issue_type = issue.get('type', 'Unknown')
            issue_counts[issue_type] += 1
        
        return dict(issue_counts)
    
    def _calculate_readability_metrics(self, text: str) -> Dict[str, Any]:
        """
        Calculate basic readability metrics.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with readability metrics
        """
        if not text.strip():
            return {}
        
        # Count sentences, words, and syllables (approximated)
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        
        # Simple syllable approximation: count vowel groups
        syllable_count = 0
        for word in text.split():
            word = re.sub(r'[^a-zA-Z]', '', word.lower())
            if word:
                syllables = len(re.findall(r'[aeiouy]+', word))
                syllables = max(1, syllables)  # Every word has at least 1 syllable
                syllable_count += syllables
        
        # Calculate metrics
        if sentences > 0 and words > 0:
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllable_count / words
            
            # Simple readability approximation (lower is easier to read)
            readability_score = (avg_sentence_length * 1.015) + (avg_syllables_per_word * 84.6) - 206.835
            
            return {
                'average_sentence_length': round(avg_sentence_length, 1),
                'average_syllables_per_word': round(avg_syllables_per_word, 2),
                'readability_score': round(readability_score, 1),
                'total_sentences': sentences,
                'total_words': words,
                'readability_level': self._interpret_readability_score(readability_score)
            }
        
        return {
            'total_sentences': sentences,
            'total_words': words
        }
    
    def _interpret_readability_score(self, score: float) -> str:
        """
        Interpret readability score into human-readable level.
        
        Args:
            score: Readability score
            
        Returns:
            Readability level description
        """
        if score >= 90:
            return 'Very Easy'
        elif score >= 80:
            return 'Easy'
        elif score >= 70:
            return 'Fairly Easy'
        elif score >= 60:
            return 'Standard'
        elif score >= 50:
            return 'Fairly Difficult'
        elif score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
