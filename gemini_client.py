import os
import json
import logging
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
import re

class VaguenessAnalysis(BaseModel):
    """Pydantic model for structured vagueness analysis response."""
    enhanced_items: List[Dict[str, Any]]
    confidence: float
    additional_suggestions: List[str]

class RiskAnalysis(BaseModel):
    """Pydantic model for structured risk analysis response."""
    enhanced_risks: List[Dict[str, Any]]
    business_impact_assessment: str
    mitigation_priority: str

class QualityAnalysis(BaseModel):
    """Pydantic model for structured quality analysis response."""
    grammar_issues: List[Dict[str, Any]]
    style_suggestions: List[Dict[str, Any]]
    clarity_improvements: List[Dict[str, Any]]
    overall_assessment: str

class GeminiClient:
    """
    Client for interfacing with Google Gemini API for SoW document analysis.
    Provides AI-powered enhancement for vagueness detection, risk assessment, and quality checking.
    """
    
    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"  # Use the latest model
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_vagueness_batch(self, vague_items: List[Dict[str, Any]], 
                               full_text: str) -> List[Dict[str, Any]]:
        """
        Enhance vagueness analysis using AI to provide better context and suggestions.
        
        Args:
            vague_items: List of detected vague items from rule-based analysis
            full_text: Complete document text for context
            
        Returns:
            Enhanced list of vague items with AI-powered suggestions
        """
        try:
            # Prepare the prompt for Gemini
            prompt = self._create_vagueness_analysis_prompt(vague_items, full_text)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for more consistent analysis
                    max_output_tokens=2048
                )
            )
            
            if response.text:
                enhanced_items = self._parse_vagueness_response(response.text, vague_items)
                return enhanced_items
            else:
                self.logger.warning("Empty response from Gemini for vagueness analysis")
                return vague_items
                
        except Exception as e:
            self.logger.error(f"Error in vagueness analysis: {str(e)}")
            return vague_items  # Return original items if AI enhancement fails
    
    def analyze_contract_risks(self, risk_items: List[Dict[str, Any]], 
                              full_text: str) -> List[Dict[str, Any]]:
        """
        Enhance risk analysis using AI to provide business impact assessment and mitigation strategies.
        
        Args:
            risk_items: List of detected risk items
            full_text: Complete document text for context
            
        Returns:
            Enhanced risk items with AI insights
        """
        try:
            prompt = self._create_risk_analysis_prompt(risk_items, full_text)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Very low temperature for consistent risk assessment
                    max_output_tokens=3072
                )
            )
            
            if response.text:
                enhanced_risks = self._parse_risk_response(response.text, risk_items)
                return enhanced_risks
            else:
                self.logger.warning("Empty response from Gemini for risk analysis")
                return risk_items
                
        except Exception as e:
            self.logger.error(f"Error in risk analysis: {str(e)}")
            return risk_items
    
    def analyze_document_quality(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze document quality using AI for grammar, style, and clarity issues.
        
        Args:
            text: Document text to analyze
            
        Returns:
            List of quality issues detected by AI
        """
        try:
            prompt = self._create_quality_analysis_prompt(text)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=2048
                )
            )
            
            if response.text:
                quality_issues = self._parse_quality_response(response.text)
                return quality_issues
            else:
                self.logger.warning("Empty response from Gemini for quality analysis")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in quality analysis: {str(e)}")
            return []
    
    def _create_vagueness_analysis_prompt(self, vague_items: List[Dict[str, Any]], 
                                        full_text: str) -> str:
        """Create a structured prompt for vagueness analysis."""
        
        # Limit full text to avoid token limits
        text_preview = full_text[:3000] + "..." if len(full_text) > 3000 else full_text
        
        vague_items_text = []
        for i, item in enumerate(vague_items[:10], 1):  # Limit to 10 items
            vague_items_text.append(f"{i}. \"{item.get('text', '')}\" (Context: {item.get('context', '')[:100]})")
        
        prompt = f"""
You are an expert contract analyst specializing in Statement of Work (SoW) documents for fixed-price projects. 
Your task is to analyze vague language that could lead to scope creep and provide specific, actionable suggestions.

DOCUMENT PREVIEW:
{text_preview}

DETECTED VAGUE LANGUAGE:
{chr(10).join(vague_items_text)}

For each vague item, provide:
1. A specific suggestion to make the language more precise
2. An explanation of why the current language is risky for fixed-price projects
3. A confidence score (0.0-1.0) for your assessment

Focus on:
- Converting vague quantities to specific numbers or bounded ranges
- Replacing subjective terms with measurable criteria
- Identifying hidden scope expansion risks
- Suggesting client-friendly but protective language

Respond in JSON format with this structure:
{{
  "enhanced_items": [
    {{
      "original_text": "text here",
      "specific_suggestion": "detailed suggestion here",
      "risk_explanation": "why this is risky",
      "suggested_replacement": "exact replacement text",
      "confidence": 0.9
    }}
  ],
  "overall_assessment": "brief summary of document's vagueness level"
}}
        """
        
        return prompt
    
    def _create_risk_analysis_prompt(self, risk_items: List[Dict[str, Any]], 
                                   full_text: str) -> str:
        """Create a structured prompt for risk analysis."""
        
        text_preview = full_text[:3000] + "..." if len(full_text) > 3000 else full_text
        
        risk_items_text = []
        for i, item in enumerate(risk_items[:8], 1):  # Limit to 8 items
            risk_items_text.append(f"{i}. \"{item.get('text', '')}\" - {item.get('description', '')} (Risk Level: {item.get('risk_level', 'Unknown')})")
        
        prompt = f"""
You are a senior contract attorney specializing in fixed-price software development projects. 
Analyze the following scope creep risks and provide business impact assessment and mitigation strategies.

DOCUMENT PREVIEW:
{text_preview}

IDENTIFIED RISKS:
{chr(10).join(risk_items_text)}

For each risk, provide:
1. Business impact assessment (financial, timeline, relationship)
2. Specific mitigation strategy
3. Suggested contract language to address the risk
4. Priority level for addressing this risk before contract signing

Focus on:
- Quantifying potential financial impact
- Providing legally sound mitigation strategies
- Suggesting contract amendments that protect vendor while remaining fair to client
- Identifying which risks are deal-breakers vs. manageable

Respond in JSON format with this structure:
{{
  "enhanced_risks": [
    {{
      "original_text": "risky text here",
      "business_impact": "detailed impact assessment",
      "financial_impact": "potential cost impact",
      "mitigation_strategy": "specific mitigation approach",
      "suggested_contract_language": "exact contract text suggestion",
      "priority": "Critical/High/Medium/Low",
      "confidence": 0.9
    }}
  ],
  "overall_risk_assessment": "summary of document's overall risk level"
}}
        """
        
        return prompt
    
    def _create_quality_analysis_prompt(self, text: str) -> str:
        """Create a structured prompt for quality analysis."""
        
        # Limit text to avoid token limits
        text_preview = text[:4000] + "..." if len(text) > 4000 else text
        
        prompt = f"""
You are a professional editor specializing in business and legal documents. 
Analyze the following Statement of Work document for grammar, style, clarity, and professionalism.

DOCUMENT TEXT:
{text_preview}

Identify and categorize issues in these areas:
1. Grammar errors (subject-verb agreement, tense consistency, etc.)
2. Style issues (passive voice overuse, wordy phrases, unclear sentences)
3. Clarity problems (ambiguous references, unclear antecedents, confusing structure)
4. Professionalism concerns (informal language, inconsistent tone)

For each issue found, provide:
- The problematic text
- The type of issue
- A specific correction or improvement
- The severity (High/Medium/Low)

Focus on issues that could:
- Create misunderstandings between parties
- Reduce the document's professional credibility
- Make the document harder to understand or enforce

Respond in JSON format with this structure:
{{
  "issues": [
    {{
      "type": "Grammar Error",
      "text": "problematic text",
      "description": "explanation of the issue", 
      "suggestion": "specific correction",
      "severity": "High",
      "line_context": "surrounding context"
    }}
  ],
  "summary": "overall quality assessment",
  "improvement_priority": "most important areas to address"
}}
        """
        
        return prompt
    
    def _parse_vagueness_response(self, response_text: str, 
                                 original_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the AI response for vagueness analysis."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                enhanced_items = parsed_response.get('enhanced_items', [])
                
                # Merge AI insights with original items
                enhanced_list = []
                for original_item in original_items:
                    enhanced_item = original_item.copy()
                    
                    # Find matching AI analysis
                    for ai_item in enhanced_items:
                        if (ai_item.get('original_text', '').lower() in 
                            original_item.get('text', '').lower()):
                            enhanced_item.update({
                                'ai_suggestion': ai_item.get('specific_suggestion', ''),
                                'risk_explanation': ai_item.get('risk_explanation', ''),
                                'suggested_replacement': ai_item.get('suggested_replacement', ''),
                                'ai_confidence': ai_item.get('confidence', 0.5)
                            })
                            break
                    
                    enhanced_list.append(enhanced_item)
                
                return enhanced_list
            else:
                self.logger.warning("Could not extract JSON from vagueness analysis response")
                return original_items
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse vagueness analysis JSON: {str(e)}")
            return original_items
        except Exception as e:
            self.logger.error(f"Error parsing vagueness response: {str(e)}")
            return original_items
    
    def _parse_risk_response(self, response_text: str, 
                           original_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the AI response for risk analysis."""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                enhanced_risks = parsed_response.get('enhanced_risks', [])
                
                # Merge AI insights with original items
                enhanced_list = []
                for original_item in original_items:
                    enhanced_item = original_item.copy()
                    
                    # Find matching AI analysis
                    for ai_item in enhanced_risks:
                        if (ai_item.get('original_text', '').lower() in 
                            original_item.get('text', '').lower()):
                            enhanced_item.update({
                                'business_impact': ai_item.get('business_impact', ''),
                                'financial_impact': ai_item.get('financial_impact', ''),
                                'mitigation': ai_item.get('mitigation_strategy', ''),
                                'suggested_contract_language': ai_item.get('suggested_contract_language', ''),
                                'ai_priority': ai_item.get('priority', 'Medium'),
                                'ai_confidence': ai_item.get('confidence', 0.5)
                            })
                            break
                    
                    enhanced_list.append(enhanced_item)
                
                return enhanced_list
            else:
                self.logger.warning("Could not extract JSON from risk analysis response")
                return original_items
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse risk analysis JSON: {str(e)}")
            return original_items
        except Exception as e:
            self.logger.error(f"Error parsing risk response: {str(e)}")
            return original_items
    
    def _parse_quality_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the AI response for quality analysis."""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                issues = parsed_response.get('issues', [])
                
                # Convert to the expected format
                quality_issues = []
                for issue in issues:
                    quality_issues.append({
                        'type': f"AI {issue.get('type', 'Quality Issue')}",
                        'severity': issue.get('severity', 'Medium'),
                        'text': issue.get('text', ''),
                        'description': issue.get('description', ''),
                        'suggestion': issue.get('suggestion', ''),
                        'context': issue.get('line_context', ''),
                        'ai_generated': True
                    })
                
                return quality_issues
            else:
                self.logger.warning("Could not extract JSON from quality analysis response")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse quality analysis JSON: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing quality response: {str(e)}")
            return []
    
    def generate_redline_suggestions(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """
        Generate redline suggestions for contract improvements.
        
        Args:
            text: Original document text
            issues: List of issues to address
            
        Returns:
            Redlined text with suggestions
        """
        try:
            prompt = f"""
You are a contract attorney helping to redline a Statement of Work to minimize scope creep risk.

ORIGINAL TEXT (first 2000 characters):
{text[:2000]}

KEY ISSUES TO ADDRESS:
{chr(10).join([f"- {issue.get('description', issue.get('text', ''))}" for issue in issues[:5]])}

Provide specific redline suggestions in this format:
ORIGINAL: "exact text from document"
REDLINED: "improved text with specific, measurable language"
REASON: "why this change reduces scope creep risk"

Focus on:
- Adding specific quantities and limits
- Defining clear acceptance criteria
- Adding "not included" clauses
- Converting vague terms to measurable standards
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1500
                )
            )
            
            return response.text if response.text else "Unable to generate redline suggestions."
            
        except Exception as e:
            self.logger.error(f"Error generating redline suggestions: {str(e)}")
            return "Error generating redline suggestions."
