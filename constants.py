"""
Constants and configuration values for the SoW Audit Assistant application.
"""

# Application Configuration
APP_NAME = "SoW Audit Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Contract Analysis Tool for Statement of Work Documents"

# Supported File Types
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'txt']
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Scoring Thresholds
SCORE_EXCELLENT = 90
SCORE_GOOD = 80
SCORE_FAIR = 70
SCORE_NEEDS_IMPROVEMENT = 60

# Risk Level Thresholds
RISK_CRITICAL = 70
RISK_HIGH = 40
RISK_MEDIUM = 20

# Document Structure - Required Sections
REQUIRED_SECTIONS = {
    'objectives': 'Project Objectives/Goals',
    'scope': 'Scope of Work',
    'deliverables': 'Deliverables/Outcomes',
    'timeline': 'Timeline/Milestones',
    'acceptance_criteria': 'Acceptance Criteria',
    'assumptions': 'Assumptions & Dependencies',
    'pricing': 'Pricing & Payment Terms',
    'change_control': 'Change Control Process'
}

# Section Keywords for Detection
SECTION_KEYWORDS = {
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

# Vagueness Detection Patterns
VAGUE_QUANTITY_PATTERNS = [
    r'\b(?:a\s+few|few|some|several|many|various|multiple)\b',
    r'\b(?:approximately|roughly|about|around|~)\s*\d+',
    r'\b(?:up\s+to|at\s+least|minimum\s+of|maximum\s+of)\b',
    r'\b(?:as\s+needed|if\s+needed|when\s+required|if\s+required)\b',
    r'\b(?:etc\.?|and\s+so\s+on|among\s+others)\b',
    r'[#]+|\bTBD\b|\bTBA\b',
    r'\d+\s*[-–]\s*\d+(?!\s*(?:days|hours|minutes|seconds))',
]

VAGUE_DESCRIPTOR_PATTERNS = [
    r'\b(?:suitable|appropriate|reasonable|adequate|sufficient)\b',
    r'\b(?:high\s+quality|good\s+quality|professional)\b',
    r'\b(?:user-friendly|easy\s+to\s+use|intuitive)\b',
    r'\b(?:scalable|robust|efficient|optimal)\b',
    r'\b(?:comprehensive|complete|full|extensive)\b',
    r'\b(?:standard|typical|normal|regular|common)\b'
]

SCOPE_RISK_PATTERNS = [
    r'\b(?:may\s+include|might\s+include|could\s+include)\b',
    r'\b(?:additional\s+work|extra\s+work|further\s+work)\b',
    r'\b(?:as\s+per\s+client|according\s+to\s+client|client\s+requirements?)\b',
    r'\b(?:and\s+other|plus\s+other|including\s+but\s+not\s+limited\s+to)\b',
    r'\b(?:where\s+applicable|if\s+applicable|as\s+applicable)\b'
]

# High-Risk Scope Creep Patterns
HIGH_RISK_PATTERNS = [
    r'\b(?:as\s+per\s+client\s+requirements?|according\s+to\s+client\s+requirements?)\b',
    r'\b(?:additional\s+work\s+may\s+be\s+performed|extra\s+work\s+may\s+be\s+done)\b',
    r'\b(?:including\s+but\s+not\s+limited\s+to)\b',
    r'\b(?:and\s+any\s+other|plus\s+any\s+other|and\s+other\s+related)\b',
    r'\b(?:as\s+needed|when\s+needed|if\s+needed|where\s+needed)\b',
    r'\b(?:may\s+require\s+additional|might\s+need\s+extra)\b',
    r'\b(?:subject\s+to\s+change|may\s+be\s+modified)\b',
    r'\b(?:to\s+be\s+determined|tbd|to\s+be\s+decided)\b'
]

# Technology Terms for Capitalization Checking
TECH_TERMS = {
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
    'kubernetes': 'Kubernetes',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'jira': 'JIRA',
    'confluence': 'Confluence',
    'slack': 'Slack',
    'teams': 'Microsoft Teams',
    'azure': 'Azure',
    'gcp': 'GCP',
    'oauth': 'OAuth',
    'saml': 'SAML',
    'ldap': 'LDAP',
    'https': 'HTTPS',
    'http': 'HTTP',
    'ftp': 'FTP',
    'ssh': 'SSH',
    'ssl': 'SSL',
    'tls': 'TLS'
}

# Common Spelling Mistakes
COMMON_SPELLING_MISTAKES = {
    'recieve': 'receive',
    'occured': 'occurred',
    'seperate': 'separate',
    'definately': 'definitely',
    'accomodate': 'accommodate',
    'untill': 'until',
    'sucessful': 'successful',
    'neccessary': 'necessary',
    'acheive': 'achieve',
    'maintainance': 'maintenance',
    'persue': 'pursue',
    'occurence': 'occurrence',
    'recomend': 'recommend',
    'independant': 'independent',
    'developement': 'development',
    'enviroment': 'environment',
    'managment': 'management',
    'requirment': 'requirement',
    'completly': 'completely'
}

# Unprofessional Terms
UNPROFESSIONAL_TERMS = {
    'asap': 'as soon as possible',
    'fyi': 'for your information',
    'btw': 'by the way',
    'gonna': 'going to',
    'wanna': 'want to',
    'kinda': 'kind of',
    'sorta': 'sort of',
    'stuff': 'items/materials',
    'things': 'components/elements',
    'guys': 'team members',
    'awesome': 'excellent',
    'cool': 'suitable',
    'super': 'very',
    'tons of': 'many',
    'lots of': 'numerous'
}

# Risk Assessment Weights
RISK_WEIGHTS = {
    'High': 10,
    'Medium': 5,
    'Low': 2
}

# Quality Issue Severity Weights
QUALITY_SEVERITY_WEIGHTS = {
    'High': 5,
    'Medium': 3,
    'Low': 1
}

# Section Validation Templates
SECTION_TEMPLATES = {
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

# Mitigation Strategy Templates
MITIGATION_TEMPLATES = {
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

# Redline Suggestion Templates
REDLINE_TEMPLATES = {
    'few': 'Replace with specific number (e.g., "3-5 items")',
    'some': 'Specify exact quantity (e.g., "4 reports")',
    'several': 'Define exact count (e.g., "6-8 databases")',
    'various': 'List specific items (e.g., "MySQL, PostgreSQL, and MongoDB databases")',
    '#': 'Replace with actual number (e.g., "3 servers" instead of "# servers")',
    'as needed': 'Set clear limits (e.g., "up to 5 additional reports, if requested in writing")',
    'appropriate': 'Define specific criteria (e.g., "meeting SOC 2 Type II compliance standards")',
    'comprehensive': 'Define scope boundaries (e.g., "covering all 12 identified system modules")',
    'reasonable': 'Specify measurable standards (e.g., "within 2 business days")',
    'standard': 'Specify which standard (e.g., "following IEEE 802.11 wireless standards")',
    'additional work': 'Define exactly what additional work is included vs. billable',
    'client requirements': 'Reference specific, documented requirements',
    'may include': 'Either include in scope or explicitly exclude',
    'as applicable': 'Define specific conditions for applicability'
}

# UI Configuration
UI_COLORS = {
    'risk_high': '🔴',
    'risk_medium': '🟡', 
    'risk_low': '🟢',
    'check_pass': '✅',
    'check_fail': '❌',
    'warning': '⚠️',
    'info': 'ℹ️'
}

# Report Configuration
REPORT_SECTIONS = [
    'header',
    'executive_summary',
    'detailed_findings',
    'risk_analysis',
    'quality_assessment',
    'recommendations',
    'redline_suggestions',
    'appendix'
]

# API Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.3
GEMINI_MAX_TOKENS = 2048

# Text Processing Limits
MAX_TEXT_LENGTH = 50000  # Maximum characters to process
MAX_CONTEXT_LENGTH = 200  # Maximum context characters around vague items
MAX_BATCH_SIZE = 10  # Maximum items per AI analysis batch

# Error Messages
ERROR_MESSAGES = {
    'file_too_large': f'File size exceeds {MAX_FILE_SIZE_MB}MB limit',
    'unsupported_format': f'Unsupported file format. Please use: {", ".join(SUPPORTED_FILE_TYPES)}',
    'empty_file': 'File appears to be empty or unreadable',
    'parsing_failed': 'Failed to extract text from the document',
    'api_error': 'AI analysis service temporarily unavailable',
    'analysis_failed': 'Document analysis failed. Please try again.',
    'invalid_document': 'Document format is not recognized or corrupted'
}

# Success Messages
SUCCESS_MESSAGES = {
    'analysis_complete': 'Document analysis completed successfully!',
    'report_generated': 'Audit report generated successfully!',
    'file_uploaded': 'File uploaded and ready for analysis'
}
