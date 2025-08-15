from typing import Dict, List, Any
from datetime import datetime
import json

class ReportGenerator:
    """
    Generates comprehensive audit reports in various formats.
    """
    
    def __init__(self):
        pass
    
    def generate_report(self, audit_results: Dict[str, Any], include_redlines: bool = True) -> str:
        """
        Generate a comprehensive audit report.
        
        Args:
            audit_results: Complete audit results from all analyzers
            include_redlines: Whether to include redline suggestions
            
        Returns:
            Formatted report as string
        """
        try:
            report_sections = []
            
            # Header
            report_sections.append(self._generate_header(audit_results))
            
            # Executive Summary
            report_sections.append(self._generate_executive_summary(audit_results))
            
            # Detailed Findings
            report_sections.append(self._generate_detailed_findings(audit_results))
            
            # Risk Analysis
            report_sections.append(self._generate_risk_analysis(audit_results))
            
            # Quality Assessment
            report_sections.append(self._generate_quality_assessment(audit_results))
            
            # Recommendations
            report_sections.append(self._generate_recommendations(audit_results))
            
            # Redline Suggestions (if requested)
            if include_redlines:
                report_sections.append(self._generate_redline_suggestions(audit_results))
            
            # Appendix
            report_sections.append(self._generate_appendix(audit_results))
            
            return '\n\n'.join(report_sections)
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def _generate_header(self, audit_results: Dict[str, Any]) -> str:
        """Generate report header section."""
        doc_info = audit_results.get('document_info', {})
        
        header = f"""
{'='*80}
STATEMENT OF WORK (SoW) AUDIT REPORT
{'='*80}

Document Name: {doc_info.get('filename', 'Unknown')}
File Type: {doc_info.get('file_type', 'Unknown')}
Analysis Date: {datetime.fromisoformat(doc_info.get('analysis_date', datetime.now().isoformat())).strftime('%B %d, %Y at %I:%M %p')}
Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{'='*80}
        """.strip()
        
        return header
    
    def _generate_executive_summary(self, audit_results: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        # Calculate scores
        section_score = audit_results.get('section_validation', {}).get('completeness_score', 0)
        vagueness_analysis = audit_results.get('vagueness_analysis', {})
        vagueness_score = 100 - vagueness_analysis.get('vagueness_percentage', 100)
        risk_analysis = audit_results.get('risk_assessment', {})
        risk_score = 100 - risk_analysis.get('risk_score', 100)
        quality_score = audit_results.get('quality_check', {}).get('quality_score', 0)
        
        overall_score = (section_score + vagueness_score + risk_score + quality_score) / 4
        
        # Risk level assessment
        if overall_score >= 80:
            risk_level = "LOW"
            recommendation = "Document is well-structured with minimal scope creep risk. Minor refinements recommended."
        elif overall_score >= 60:
            risk_level = "MEDIUM" 
            recommendation = "Document has moderate risks that should be addressed before contract execution."
        else:
            risk_level = "HIGH"
            recommendation = "Document requires significant revisions to minimize scope creep and project risks."
        
        summary = f"""
EXECUTIVE SUMMARY
{'-'*50}

Overall Assessment Score: {overall_score:.0f}/100
Risk Level: {risk_level}

SCORE BREAKDOWN:
• Document Structure: {section_score:.0f}%
• Language Clarity: {vagueness_score:.0f}%
• Scope Control: {risk_score:.0f}%
• Professional Quality: {quality_score:.0f}%

RECOMMENDATION:
{recommendation}

KEY FINDINGS:
• {audit_results.get('section_validation', {}).get('sections_found', 0)}/{audit_results.get('section_validation', {}).get('total_required_sections', 8)} required sections present
• {vagueness_analysis.get('total_vague_instances', 0)} instances of vague language detected
• {risk_analysis.get('total_risks', 0)} scope creep risks identified
• {audit_results.get('quality_check', {}).get('total_issues', 0)} quality issues found
        """.strip()
        
        return summary
    
    def _generate_detailed_findings(self, audit_results: Dict[str, Any]) -> str:
        """Generate detailed findings section."""
        findings = []
        
        findings.append("DETAILED FINDINGS")
        findings.append("-" * 50)
        
        # Section Validation Findings
        section_results = audit_results.get('section_validation', {})
        findings.append("\n1. DOCUMENT STRUCTURE ANALYSIS")
        findings.append("   " + "="*40)
        
        missing_sections = section_results.get('missing_sections', [])
        if missing_sections:
            findings.append(f"\n   ❌ MISSING SECTIONS ({len(missing_sections)}):")
            for section in missing_sections:
                findings.append(f"      • {section}")
        
        present_sections = []
        for section, present in section_results.get('sections_present', {}).items():
            if present:
                present_sections.append(section)
        
        if present_sections:
            findings.append(f"\n   ✅ PRESENT SECTIONS ({len(present_sections)}):")
            for section in present_sections:
                findings.append(f"      • {section}")
        
        # Vagueness Analysis Findings  
        vagueness_results = audit_results.get('vagueness_analysis', {})
        findings.append(f"\n2. VAGUENESS ANALYSIS")
        findings.append("   " + "="*40)
        
        vague_items = vagueness_results.get('vague_items', [])
        if vague_items:
            findings.append(f"\n   Found {len(vague_items)} instances of vague language:")
            
            # Group by severity
            severity_groups = {'High': [], 'Medium': [], 'Low': []}
            for item in vague_items:
                severity = item.get('severity', 'Low')
                if severity in severity_groups:
                    severity_groups[severity].append(item)
            
            for severity in ['High', 'Medium', 'Low']:
                items = severity_groups[severity]
                if items:
                    findings.append(f"\n   {severity.upper()} SEVERITY ({len(items)} items):")
                    for item in items[:5]:  # Show top 5 per category
                        findings.append(f"      • \"{item.get('text', '')}\" - {item.get('issue', '')}")
                    if len(items) > 5:
                        findings.append(f"      ... and {len(items) - 5} more")
        else:
            findings.append("\n   ✅ No significant vague language detected.")
        
        return '\n'.join(findings)
    
    def _generate_risk_analysis(self, audit_results: Dict[str, Any]) -> str:
        """Generate risk analysis section."""
        risk_results = audit_results.get('risk_assessment', {})
        risk_items = risk_results.get('risk_items', [])
        
        analysis = []
        analysis.append("SCOPE CREEP RISK ANALYSIS")
        analysis.append("-" * 50)
        
        risk_score = risk_results.get('risk_score', 0)
        analysis.append(f"\nOverall Risk Score: {risk_score:.1f}/100 (Higher = More Risk)")
        
        if risk_score >= 70:
            risk_level = "CRITICAL"
            color = "🔴"
        elif risk_score >= 40:
            risk_level = "HIGH"
            color = "🟡"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
            color = "🟡"
        else:
            risk_level = "LOW"
            color = "🟢"
        
        analysis.append(f"Risk Level: {color} {risk_level}")
        
        # Risk breakdown
        risk_breakdown = risk_results.get('risk_breakdown', {})
        analysis.append(f"\nRisk Distribution:")
        analysis.append(f"• High Risk Items: {risk_breakdown.get('High', 0)}")
        analysis.append(f"• Medium Risk Items: {risk_breakdown.get('Medium', 0)}")
        analysis.append(f"• Low Risk Items: {risk_breakdown.get('Low', 0)}")
        
        # Priority risks
        priority_risks = risk_results.get('priority_risks', [])
        if priority_risks:
            analysis.append(f"\nTOP PRIORITY RISKS:")
            for i, risk in enumerate(priority_risks[:5], 1):
                risk_level = risk.get('risk_level', 'Unknown')
                risk_icon = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(risk_level, '⚪')
                analysis.append(f"{i}. {risk_icon} {risk.get('description', risk.get('text', ''))}")
                analysis.append(f"   Impact: {risk.get('impact', 'Unknown')}")
                if risk.get('mitigation'):
                    analysis.append(f"   Mitigation: {risk.get('mitigation')}")
                analysis.append("")
        
        return '\n'.join(analysis)
    
    def _generate_quality_assessment(self, audit_results: Dict[str, Any]) -> str:
        """Generate quality assessment section."""
        quality_results = audit_results.get('quality_check', {})
        
        assessment = []
        assessment.append("QUALITY ASSESSMENT")
        assessment.append("-" * 50)
        
        quality_score = quality_results.get('quality_score', 0)
        assessment.append(f"\nOverall Quality Score: {quality_score:.1f}/100")
        
        # Quality level interpretation
        if quality_score >= 90:
            quality_level = "EXCELLENT"
        elif quality_score >= 80:
            quality_level = "GOOD"
        elif quality_score >= 70:
            quality_level = "FAIR"
        elif quality_score >= 60:
            quality_level = "NEEDS IMPROVEMENT"
        else:
            quality_level = "POOR"
        
        assessment.append(f"Quality Level: {quality_level}")
        
        # Issue breakdown
        issue_breakdown = quality_results.get('issue_breakdown', {})
        total_issues = quality_results.get('total_issues', 0)
        
        if total_issues > 0:
            assessment.append(f"\nQuality Issues Found ({total_issues} total):")
            for issue_type, count in issue_breakdown.items():
                assessment.append(f"• {issue_type}: {count}")
        
        # Readability metrics
        readability = quality_results.get('readability_metrics', {})
        if readability:
            assessment.append(f"\nReadability Metrics:")
            assessment.append(f"• Average Sentence Length: {readability.get('average_sentence_length', 'N/A')} words")
            assessment.append(f"• Readability Level: {readability.get('readability_level', 'N/A')}")
            assessment.append(f"• Total Words: {readability.get('total_words', 'N/A')}")
            assessment.append(f"• Total Sentences: {readability.get('total_sentences', 'N/A')}")
        
        return '\n'.join(assessment)
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        recommendations = []
        recommendations.append("RECOMMENDATIONS")
        recommendations.append("-" * 50)
        
        # Section recommendations
        section_recs = audit_results.get('section_validation', {}).get('recommendations', [])
        if section_recs:
            recommendations.append("\n1. STRUCTURAL IMPROVEMENTS:")
            for i, rec in enumerate(section_recs, 1):
                recommendations.append(f"   {i}. {rec.get('section', 'Unknown Section')} - {rec.get('priority', 'Medium')} Priority")
                recommendations.append(f"      {rec.get('recommendation', '')}")
                recommendations.append(f"      Reason: {rec.get('reason', '')}")
                recommendations.append("")
        
        # Vagueness recommendations
        vagueness_suggestions = audit_results.get('vagueness_analysis', {}).get('suggestions', [])
        if vagueness_suggestions:
            recommendations.append("2. LANGUAGE CLARITY IMPROVEMENTS:")
            for i, suggestion in enumerate(vagueness_suggestions[:5], 1):  # Top 5
                recommendations.append(f"   {i}. Replace \"{suggestion.get('original_text', '')}\"")
                recommendations.append(f"      Suggestion: {suggestion.get('suggestion', '')}")
                recommendations.append("")
        
        # Risk mitigation
        risk_mitigations = audit_results.get('risk_assessment', {}).get('mitigation_strategies', [])
        if risk_mitigations:
            recommendations.append("3. RISK MITIGATION STRATEGIES:")
            for i, mitigation in enumerate(risk_mitigations, 1):
                recommendations.append(f"   {i}. {mitigation.get('category', 'General')} - {mitigation.get('urgency', 'Medium')}")
                recommendations.append(f"      Strategy: {mitigation.get('strategy', '')}")
                recommendations.append(f"      Action: {mitigation.get('action', '')}")
                recommendations.append("")
        
        # Quality improvements
        quality_suggestions = audit_results.get('quality_check', {}).get('suggestions', [])
        if quality_suggestions:
            recommendations.append("4. QUALITY IMPROVEMENTS:")
            for i, suggestion in enumerate(quality_suggestions, 1):
                recommendations.append(f"   {i}. {suggestion.get('category', 'General')} ({suggestion.get('count', 0)} instances)")
                recommendations.append(f"      Action: {suggestion.get('suggestion', '')}")
                recommendations.append("")
        
        return '\n'.join(recommendations)
    
    def _generate_redline_suggestions(self, audit_results: Dict[str, Any]) -> str:
        """Generate redline suggestions section."""
        redlines = []
        redlines.append("REDLINE SUGGESTIONS")
        redlines.append("-" * 50)
        redlines.append("\nThe following text revisions are recommended to improve clarity and reduce scope creep risk:")
        
        # Process vague items for redline suggestions
        vague_items = audit_results.get('vagueness_analysis', {}).get('vague_items', [])
        
        redline_count = 0
        for item in vague_items:
            if item.get('severity') in ['High', 'Medium'] and redline_count < 10:
                redline_count += 1
                
                redlines.append(f"\n{redline_count}. VAGUE LANGUAGE:")
                redlines.append(f"   Original: \"{item.get('text', '')}\"")
                redlines.append(f"   Context: {item.get('context', '')[:100]}...")
                redlines.append(f"   Issue: {item.get('issue', '')}")
                
                # Generate specific redline suggestion
                suggestion = self._generate_specific_redline(item)
                redlines.append(f"   Suggested Revision: {suggestion}")
                redlines.append("")
        
        # Process high-risk items
        risk_items = audit_results.get('risk_assessment', {}).get('priority_risks', [])
        
        for item in risk_items:
            if item.get('risk_level') == 'High' and redline_count < 15:
                redline_count += 1
                
                redlines.append(f"{redline_count}. SCOPE RISK:")
                redlines.append(f"   Original: \"{item.get('text', '')}\"")
                redlines.append(f"   Risk: {item.get('description', '')}")
                
                suggestion = self._generate_risk_redline(item)
                redlines.append(f"   Suggested Revision: {suggestion}")
                redlines.append("")
        
        if redline_count == 0:
            redlines.append("\nNo critical redline suggestions needed - document quality is acceptable.")
        
        return '\n'.join(redlines)
    
    def _generate_specific_redline(self, vague_item: Dict[str, Any]) -> str:
        """Generate a specific redline suggestion for a vague item."""
        text = vague_item.get('text', '').lower()
        
        redline_templates = {
            'few': 'Replace with specific number (e.g., "3-5 items")',
            'some': 'Specify exact quantity (e.g., "4 reports")',
            'several': 'Define exact count (e.g., "6-8 databases")',
            'various': 'List specific items (e.g., "MySQL, PostgreSQL, and MongoDB databases")',
            '#': 'Replace with actual number (e.g., "3 servers" instead of "# servers")',
            'as needed': 'Set clear limits (e.g., "up to 5 additional reports, if requested in writing")',
            'appropriate': 'Define specific criteria (e.g., "meeting SOC 2 Type II compliance standards")',
            'comprehensive': 'Define scope boundaries (e.g., "covering all 12 identified system modules")',
            'reasonable': 'Specify measurable standards (e.g., "within 2 business days")',
            'standard': 'Specify which standard (e.g., "following IEEE 802.11 wireless standards")'
        }
        
        for key, template in redline_templates.items():
            if key in text:
                return template
        
        return 'Make language more specific and measurable'
    
    def _generate_risk_redline(self, risk_item: Dict[str, Any]) -> str:
        """Generate a redline suggestion for a risk item."""
        text = risk_item.get('text', '').lower()
        
        if 'additional work' in text:
            return 'Define exactly what additional work is included vs. billable (e.g., "Additional work beyond the specified deliverables will be billed at $X per hour")'
        elif 'client requirements' in text:
            return 'Reference specific, documented requirements (e.g., "as defined in the attached requirements document v1.2")'
        elif 'may include' in text:
            return 'Either include in scope or explicitly exclude (e.g., "includes X, Y, and Z. Does not include A, B, or C")'
        elif 'as applicable' in text:
            return 'Define specific conditions (e.g., "when explicitly requested by client and approved in writing")'
        else:
            return 'Add specific boundaries and conditions to prevent scope expansion'
    
    def _generate_appendix(self, audit_results: Dict[str, Any]) -> str:
        """Generate appendix section."""
        appendix = []
        appendix.append("APPENDIX")
        appendix.append("-" * 50)
        
        # Analysis methodology
        appendix.append("\nA. ANALYSIS METHODOLOGY:")
        appendix.append("This audit was performed using AI-powered analysis combined with rule-based pattern matching.")
        appendix.append("The assessment covers four key areas:")
        appendix.append("1. Document Structure - Presence of required SoW sections")
        appendix.append("2. Language Clarity - Detection of vague or ambiguous terms")
        appendix.append("3. Scope Control - Identification of scope creep risks")
        appendix.append("4. Professional Quality - Grammar, formatting, and style review")
        
        # Scoring methodology
        appendix.append("\nB. SCORING METHODOLOGY:")
        appendix.append("• Structure Score: Percentage of required sections present")
        appendix.append("• Clarity Score: 100 minus vagueness percentage")
        appendix.append("• Risk Score: Weighted assessment of scope creep risks")
        appendix.append("• Quality Score: Assessment based on grammar, style, and formatting issues")
        appendix.append("• Overall Score: Average of all four component scores")
        
        # Risk categories
        appendix.append("\nC. RISK CATEGORIES:")
        appendix.append("• High Risk: Language that commonly leads to scope disputes")
        appendix.append("• Medium Risk: Ambiguous terms that may cause confusion")  
        appendix.append("• Low Risk: Minor clarity issues that should be addressed")
        
        # Contact information
        appendix.append("\nD. SUPPORT:")
        appendix.append("For questions about this audit report or assistance with contract revisions,")
        appendix.append("please contact your legal or contracts team.")
        
        appendix.append(f"\n{'-'*50}")
        appendix.append("End of Report")
        appendix.append(f"{'-'*50}")
        
        return '\n'.join(appendix)
