import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import json
from datetime import datetime

# Import streamlit-extras components
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

from document_parser import DocumentParser
from report_generator import ReportGenerator
from audit_runner import run_audit


# =============================================================================
# CSS Loading Helper
# =============================================================================
def load_css(file_path: str) -> None:
    """Load external CSS file and inject into Streamlit app."""
    css_file = Path(file_path)
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {file_path}")


# =============================================================================
# UI Component Helpers
# =============================================================================
def render_tag(text: str, icon: str = "", variant: str = "") -> str:
    """Render a styled tag/badge component."""
    variant_class = f"tag-{variant}" if variant else ""
    icon_html = f'<span class="tag-icon">{icon}</span>' if icon else ""
    return f'<span class="tag {variant_class}">{icon_html}{text}</span>'


def render_metric_card(label: str, value: str, delta: str = None, delta_positive: bool = True) -> str:
    """Render a custom metric card with optional delta."""
    delta_html = ""
    if delta:
        delta_class = "metric-delta-positive" if delta_positive else "metric-delta-negative"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    return f'''
    <div class="metric-card card-hover">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    '''


def render_step_item(number: int, icon: str, text: str) -> str:
    """Render a single step item for the stepper component."""
    return f'''
    <div class="step">
        <span class="step-number">{number}</span>
        <div class="step-icon">{icon}</div>
        <div class="step-text">{text}</div>
    </div>
    '''


# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="SoW Audit Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS
load_css("assets/style.css")

# ===== TOP NAVIGATION BAR =====
st.markdown("""
<div class="top-nav">
    <div class="brand-logo">📋 SoW Audit Pro</div>
    <div class="nav-links">
        <a href="#" target="_blank">📚 Docs</a>
        <a href="https://github.com" target="_blank">⭐ GitHub</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== HERO SECTION =====
st.markdown("""
<div class="hero-section animate-slide-up">
    <h1 class="hero-title">Statement of Work Audit Assistant</h1>
    <p class="hero-subtitle">AI-Powered Contract Analysis Tool</p>
    <p class="hero-value-prop">📈 Review SoWs 5x faster while reducing scope-creep risk by up to 60%</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'document_content' not in st.session_state:
    st.session_state.document_content = None

# ===== CONFIGURATION CARD =====
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown('<div class="config-card-title">📤 Upload & Processing Options</div>', unsafe_allow_html=True)

col_upload, col_options = st.columns([1.2, 1], gap="large")

with col_upload:
    st.markdown('<div class="config-section-label">Document Upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a SoW document",
        type=['pdf', 'docx', 'txt'],
        help="Upload PDF, DOCX, or TXT files",
        label_visibility="collapsed"
    )
    st.markdown('<p class="helper-text">Supported formats: PDF, DOCX, TXT • Max size: 10MB</p>', unsafe_allow_html=True)
    
    # Show file info if uploaded
    if uploaded_file is not None:
        st.markdown(f"""
        <div class="file-info">
            <div class="file-info-item">
                <span class="file-info-label">File Name:</span>
                <span class="file-info-value">{uploaded_file.name}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">Size:</span>
                <span class="file-info-value">{uploaded_file.size / 1024:.1f} KB</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">Type:</span>
                <span class="file-info-value">{uploaded_file.type or 'Unknown'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_options:
    st.markdown('<div class="config-section-label">Processing Options</div>', unsafe_allow_html=True)
    
    enable_ai_analysis = st.checkbox("Enable AI-Powered Analysis", value=True)
    st.markdown('<p class="helper-text">Uses Google Gemini to understand context, detect subtle risks, and provide intelligent suggestions beyond keyword matching.</p>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    
    generate_redlines = st.checkbox("Generate Redline Suggestions", value=True)
    st.markdown('<p class="helper-text">Provides specific text improvements with before/after comparisons you can copy directly into your contract.</p>', unsafe_allow_html=True)

# Analyze button section
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])

with col_btn_center:
    if uploaded_file is not None:
        analyze_clicked = st.button("🔍 Analyze Document", type="primary", use_container_width=True)
    else:
        st.button("🔍 Analyze Document", type="primary", use_container_width=True, disabled=True)
        st.markdown('<p class="upload-info">👆 Upload a SoW document to start the audit</p>', unsafe_allow_html=True)
        analyze_clicked = False

st.markdown('</div>', unsafe_allow_html=True)

# ===== PROCESSING LOGIC =====
if uploaded_file is not None and analyze_clicked:
    with st.spinner("🤖 Multi-agent analysis in progress... This may take 1-2 minutes."):
        try:
            # Step 1: Parse document to extract text
            parser = DocumentParser()
            document_data = parser.parse_document(uploaded_file)
            st.session_state.document_content = document_data
            
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            progress_text.text("📄 Document parsed. Launching AI agents...")
            progress_bar.progress(10)
            
            # Step 2: Run the multi-agent audit pipeline via ADK
            progress_text.text("🔬 Agents analysing: sections → vagueness → risks → quality...")
            progress_bar.progress(30)
            
            audit_results = run_audit(
                document_text=document_data.get('raw_text', ''),
                filename=uploaded_file.name,
            )
            
            st.session_state.audit_results = audit_results
            
            progress_bar.progress(100)
            progress_text.text("Analysis complete!")
            st.success("✅ Multi-agent audit completed successfully!")
            
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

# ===== AUDIT RESULTS SECTION =====
if st.session_state.audit_results:
    results = st.session_state.audit_results
    
    st.markdown('<div class="results-section animate-slide-up">', unsafe_allow_html=True)
    
    # Use colored header from streamlit-extras
    colored_header(
        label="📊 Audit Results",
        description="Comprehensive analysis of your Statement of Work",
        color_name="blue-70"
    )
    
    # Calculate overall scores
    section_score = results['section_validation'].get('completeness_score', 0)
    vagueness_score = 100 - results['vagueness_analysis'].get('vagueness_percentage', 100)
    risk_score = 100 - results['risk_assessment'].get('risk_score', 100)
    quality_score = results['quality_check'].get('quality_score', 0)
    
    overall_score = (section_score + vagueness_score + risk_score + quality_score) / 4
    
    # Score dashboard with enhanced styling
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_score,
            title = {'text': "Overall Score", 'font': {'size': 14, 'color': '#555'}},
            number = {'font': {'size': 28, 'color': '#1f77b4'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': '#e0e0e0'},
                'bar': {'color': "#1f77b4"},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': '#e0e0e0',
                'steps': [
                    {'range': [0, 50], 'color': "#ffeaea"},
                    {'range': [50, 80], 'color': "#fff8e6"},
                    {'range': [80, 100], 'color': "#e8f5e9"}
                ],
                'threshold': {
                    'line': {'color': "#28a745", 'width': 3},
                    'thickness': 0.8,
                    'value': 90
                }
            }
        ))
        fig.update_layout(
            height=200, 
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif'}
        )
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
    
    # Apply streamlit-extras metric styling
    style_metric_cards(
        background_color="#ffffff",
        border_left_color="#1f77b4",
        border_color="#e0e0e0",
        box_shadow="0 2px 8px rgba(0,0,0,0.06)"
    )
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== FEATURE CARDS (shown when no results) =====
if not st.session_state.audit_results:
    st.markdown('<div class="feature-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="feature-section-title">Powerful Features for Contract Review</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="feature-card animate-slide-up">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">What We Detect</div>
            <ul class="feature-list">
                <li>Vague terms & ambiguous language</li>
                <li>Missing standard sections</li>
                <li>Scope creep risk indicators</li>
                <li>Inconsistent terminology</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card animate-slide-up delay-100">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Analysis Provided</div>
            <ul class="feature-list">
                <li>Structure completeness score</li>
                <li>Clarity & specificity rating</li>
                <li>Risk assessment with mitigation</li>
                <li>Actionable recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card animate-slide-up delay-200">
            <div class="feature-icon">✨</div>
            <div class="feature-title">AI Features</div>
            <ul class="feature-list">
                <li>Context-aware analysis</li>
                <li>Intelligent suggestions</li>
                <li>Automated redlining</li>
                <li>Professional tone preservation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How it works strip with enhanced stepper design
    st.markdown(f"""
    <div class="how-it-works">
        <div class="how-it-works-title">How It Works</div>
        <div class="step-container">
            {render_step_item(1, "📄", "Upload SoW")}
            <div class="step-arrow">→</div>
            {render_step_item(2, "🔬", "Run Analysis")}
            <div class="step-arrow">→</div>
            {render_step_item(3, "📝", "Export Redlines")}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Target audience with styled tags
    ideal_for_tags = [
        ("⚖️", "Legal Teams"),
        ("📋", "PMOs"),
        ("💼", "Consulting Firms"),
        ("🛒", "Procurement"),
    ]
    tags_html = " ".join([render_tag(text, icon) for icon, text in ideal_for_tags])
    
    st.markdown(f"""
    <div class="ideal-for">
        <strong>Ideal for:</strong>
        {tags_html}
    </div>
    """, unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("""
<div class="custom-footer">
    <p>Built with ❤️ using <strong>Streamlit</strong> + <strong>Gemini AI</strong></p>
    <div class="mt-3">
        <a href="https://github.com" target="_blank">⭐ GitHub Repo</a> • 
        <a href="#" target="_blank">📚 Documentation</a> • 
        <a href="#" target="_blank">🐛 Report Issue</a>
    </div>
</div>
""", unsafe_allow_html=True)
