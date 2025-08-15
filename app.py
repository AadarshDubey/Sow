import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import json
from datetime import datetime

from document_parser import DocumentParser
from section_validator import SectionValidator
from vagueness_detector import VaguenessDetector
from risk_assessor import RiskAssessor
from quality_checker import QualityChecker
from report_generator import ReportGenerator

# Configure page
st.set_page_config(
    page_title="SoW Audit Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📋 Statement of Work (SoW) Audit Assistant")
st.markdown("""
**AI-Powered Contract Analysis Tool**  
Upload your Statement of Work documents to detect scope creep risks, vague language, and improve contract clarity.
""")

# Initialize session state
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'document_content' not in st.session_state:
    st.session_state.document_content = None

# Sidebar for file upload
st.sidebar.header("📁 Document Upload")
uploaded_file = st.sidebar.file_uploader(
    "Choose a SoW document",
    type=['pdf', 'docx', 'txt'],
    help="Upload PDF, DOCX, or TXT files"
)

# Processing options
st.sidebar.header("🔧 Processing Options")
enable_ai_analysis = st.sidebar.checkbox("Enable AI-Powered Analysis", value=True, help="Use Google Gemini for intelligent contract analysis")
generate_redlines = st.sidebar.checkbox("Generate Redline Suggestions", value=True, help="Provide specific text improvement suggestions")

# Main content area
if uploaded_file is not None:
    # Display file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Name", uploaded_file.name)
    with col2:
        st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("File Type", uploaded_file.type)
    
    # Process button
    if st.button("🔍 Analyze Document", type="primary"):
        with st.spinner("Processing document..."):
            try:
                # Parse document
                parser = DocumentParser()
                document_data = parser.parse_document(uploaded_file)
                st.session_state.document_content = document_data
                
                # Initialize analyzers
                section_validator = SectionValidator()
                vagueness_detector = VaguenessDetector()
                risk_assessor = RiskAssessor()
                quality_checker = QualityChecker()
                report_generator = ReportGenerator()
                
                # Run analysis
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                # Step 1: Section validation
                progress_text.text("Validating document structure...")
                progress_bar.progress(20)
                section_results = section_validator.validate_sections(document_data)
                
                # Step 2: Vagueness detection
                progress_text.text("Detecting vague language...")
                progress_bar.progress(40)
                vagueness_results = vagueness_detector.detect_vagueness(document_data, enable_ai_analysis)
                
                # Step 3: Risk assessment
                progress_text.text("Assessing scope creep risks...")
                progress_bar.progress(60)
                risk_results = risk_assessor.assess_risks(document_data, enable_ai_analysis)
                
                # Step 4: Quality check
                progress_text.text("Checking language quality...")
                progress_bar.progress(80)
                quality_results = quality_checker.check_quality(document_data, enable_ai_analysis)
                
                # Step 5: Generate report
                progress_text.text("Generating audit report...")
                progress_bar.progress(100)
                
                audit_results = {
                    'document_info': {
                        'filename': uploaded_file.name,
                        'file_type': uploaded_file.type,
                        'analysis_date': datetime.now().isoformat()
                    },
                    'section_validation': section_results,
                    'vagueness_analysis': vagueness_results,
                    'risk_assessment': risk_results,
                    'quality_check': quality_results
                }
                
                st.session_state.audit_results = audit_results
                
                progress_text.text("Analysis complete!")
                st.success("Document analysis completed successfully!")
                
            except Exception as e:
                error_msg = str(e)
                if "No text could be extracted" in error_msg:
                    st.error("📄 **PDF Processing Issue**")
                    st.warning("The uploaded PDF couldn't be processed. This might happen if:")
                    st.write("• The PDF contains only images (scanned documents)")
                    st.write("• The PDF is password-protected or encrypted")
                    st.write("• The PDF is corrupted or in an unsupported format")
                    st.info("💡 **Suggestion:** Try converting your PDF to a Word document (.docx) or plain text (.txt) file.")
                elif "unsupported file" in error_msg.lower():
                    st.error("📁 **Unsupported File Format**")
                    st.info("Please upload a PDF (.pdf), Word document (.docx), or plain text (.txt) file.")
                else:
                    st.error(f"🚨 **Processing Error:** {error_msg}")
                    st.info("Please try uploading a different document or contact support if the issue persists.")
                
                # Show detailed error in expander for debugging
                with st.expander("🔧 Technical Details (for debugging)"):
                    st.exception(e)

# Display results if available
if st.session_state.audit_results:
    results = st.session_state.audit_results
    
    st.header("📊 Audit Results")
    
    # Calculate overall scores
    section_score = results['section_validation'].get('completeness_score', 0)
    vagueness_score = 100 - results['vagueness_analysis'].get('vagueness_percentage', 100)
    risk_score = 100 - results['risk_assessment'].get('risk_score', 100)
    quality_score = results['quality_check'].get('quality_score', 0)
    
    overall_score = (section_score + vagueness_score + risk_score + quality_score) / 4
    
    # Score dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_score,
            title = {'text': "Overall Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Structure", f"{section_score:.0f}%", 
                 delta=f"{section_score-75:.0f}%" if section_score != 75 else None)
    
    with col3:
        st.metric("Clarity", f"{vagueness_score:.0f}%", 
                 delta=f"{vagueness_score-75:.0f}%" if vagueness_score != 75 else None)
    
    with col4:
        st.metric("Risk Level", f"{100-risk_score:.0f}%", 
                 delta=f"{75-risk_score:.0f}%" if risk_score != 25 else None,
                 delta_color="inverse")
    
    with col5:
        st.metric("Quality", f"{quality_score:.0f}%", 
                 delta=f"{quality_score-75:.0f}%" if quality_score != 75 else None)
    
    # Tabs for detailed results
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Structure", "❓ Vagueness", "⚠️ Risks", "✏️ Quality", "📄 Report"])
    
    with tab1:
        st.subheader("Document Structure Analysis")
        
        section_results = results['section_validation']
        
        # Required sections checklist
        st.write("**Required Sections Checklist:**")
        for section, present in section_results.get('sections_present', {}).items():
            if present:
                st.success(f"✅ {section}")
            else:
                st.error(f"❌ {section} - MISSING")
        
        # Missing sections
        missing_sections = section_results.get('missing_sections', [])
        if missing_sections:
            st.warning(f"**Missing {len(missing_sections)} required sections:**")
            for section in missing_sections:
                st.write(f"• {section}")
    
    with tab2:
        st.subheader("Vague Language Detection")
        
        vagueness_results = results['vagueness_analysis']
        
        # Vague terms found
        vague_items = vagueness_results.get('vague_items', [])
        if vague_items:
            st.warning(f"Found {len(vague_items)} instances of vague language:")
            
            for item in vague_items:
                with st.expander(f"📍 {item.get('type', 'Vague term')}: '{item.get('text', '')}'"):
                    st.write(f"**Context:** {item.get('context', 'N/A')}")
                    st.write(f"**Issue:** {item.get('issue', 'N/A')}")
                    if item.get('suggestion'):
                        st.write(f"**Suggested fix:** {item.get('suggestion')}")
        else:
            st.success("No vague language detected!")
    
    with tab3:
        st.subheader("Scope Creep Risk Assessment")
        
        risk_results = results['risk_assessment']
        
        # Risk items
        risk_items = risk_results.get('risk_items', [])
        if risk_items:
            st.warning(f"Found {len(risk_items)} potential scope creep risks:")
            
            for item in risk_items:
                risk_level = item.get('risk_level', 'Medium')
                color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(risk_level, '🟡')
                
                with st.expander(f"{color} {risk_level} Risk: {item.get('description', '')}"):
                    st.write(f"**Text:** {item.get('text', 'N/A')}")
                    st.write(f"**Impact:** {item.get('impact', 'N/A')}")
                    if item.get('mitigation'):
                        st.write(f"**Mitigation:** {item.get('mitigation')}")
        else:
            st.success("No significant scope creep risks detected!")
    
    with tab4:
        st.subheader("Language Quality Analysis")
        
        quality_results = results['quality_check']
        
        # Quality issues
        issues = quality_results.get('issues', [])
        if issues:
            st.warning(f"Found {len(issues)} quality issues:")
            
            for issue in issues:
                issue_type = issue.get('type', 'Unknown')
                with st.expander(f"✏️ {issue_type}: {issue.get('description', '')}"):
                    st.write(f"**Text:** {issue.get('text', 'N/A')}")
                    if issue.get('suggestion'):
                        st.write(f"**Suggested fix:** {issue.get('suggestion')}")
        else:
            st.success("No significant quality issues detected!")
    
    with tab5:
        st.subheader("Complete Audit Report")
        
        # Generate downloadable report
        report_gen = ReportGenerator()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("📄 Generate Detailed Report"):
                with st.spinner("Generating comprehensive report..."):
                    report_content = report_gen.generate_report(results, generate_redlines)
                    st.session_state.report_content = report_content
        
        with col2:
            if hasattr(st.session_state, 'report_content'):
                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state.report_content,
                    file_name=f"sow_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        # Display report preview
        if hasattr(st.session_state, 'report_content'):
            st.text_area("Report Preview", st.session_state.report_content, height=400)

else:
    # Landing page content
    st.info("👆 Upload a Statement of Work document to begin analysis")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔍 What We Detect")
        st.write("""
        • Vague terms ("few", "some", "#")
        • Missing standard sections
        • Scope creep risks
        • Grammar and formatting issues
        • Inconsistent terminology
        """)
    
    with col2:
        st.subheader("📊 Analysis Provided")
        st.write("""
        • Structure completeness score
        • Clarity and specificity rating
        • Risk assessment with mitigation
        • Professional quality review
        • Actionable recommendations
        """)
    
    with col3:
        st.subheader("✨ AI Features")
        st.write("""
        • Context-aware analysis
        • Intelligent suggestions
        • Risk prediction
        • Automated redlining
        • Professional tone preservation
        """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Google Gemini AI")
