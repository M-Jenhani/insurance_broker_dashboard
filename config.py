# Configuration File for Insurance Broker Dashboard

# Data Settings
DATA_PATH = "data/prospects.csv"
CLEANED_DATA_PATH = "data/cleaned_prospects.csv"
MODELS_PATH = "models/"

# Scoring Thresholds
HIGH_PRIORITY_THRESHOLD = 18
VERY_HIGH_PRIORITY_THRESHOLD = 20
MEDIUM_PRIORITY_THRESHOLD = 15

# ML Model Settings
CONVERSION_PROBABILITY_THRESHOLD = 0.7
MODEL_TEST_SIZE = 0.2
RANDOM_STATE = 42

# Business Rules
URGENT_DAYS_THRESHOLD = 7
SHORT_TERM_DAYS_THRESHOLD = 30
RECENT_LEADS_DAYS = 7

# Geographic Settings
URBAN_ZIPCODES = ['75', '77', '92', '93', '94', '95']  # Île-de-France

# Coverage Level Mapping
COVERAGE_LEVELS = {
    'ECO': 1,
    'MOYEN': 2,
    'ELEVE': 3,
    'MAXI': 4
}

# Regime Weights for Scoring
REGIME_WEIGHTS = {
    'Régime général': 0.5,
    'Alsace-Moselle': 0.0,
    'Régime TNS': 1.0,
    'Régime agricole': 0.5,
    'Hors sécu': 0.8,
    'Régime CFE': 0.5
}

# Email Settings
DEFAULT_ALERT_EMAIL = "contact@cabinet-vital.fr"
ESTIMATED_COMMISSION = 150  # euros per conversion

# Export Settings
EXPORT_PATH = "exports/"
DATE_FORMAT = "%Y%m%d"

# Dashboard Settings
DASHBOARD_TITLE = "🏥 Insurance Broker Dashboard - Lead Management System"
DASHBOARD_ICON = "🏥"
DASHBOARD_LAYOUT = "wide"

# Colors for Visualizations
COLOR_SCHEME = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17becf'
}

# Report Settings
REPORT_HEADER = """
# INSURANCE BROKER DASHBOARD REPORT
## Generated automatically
"""

# Reengagement Settings
REENGAGEMENT_PERIODS = {
    '3-6 mois': (3, 6),
    '6-12 mois': (6, 12),
    '12-24 mois': (12, 24),
    '>24 mois': (24, 999)
}

# Feature Names for ML
FEATURE_COLUMNS = [
    'age_at_submission',
    'spouse_age_at_submission',
    'num_children',
    'medical_care',
    'hospitalization',
    'optical',
    'dental',
    'social_security_regime_encoded',
    'days_to_effective',
    'source_score',
    'zip_score',
    'has_spouse'
]

# Segmentation Labels
DEMOGRAPHIC_SEGMENTS = [
    'Young Singles',
    'Young Families',
    'Middle-Aged Singles',
    'Middle-Aged Families',
    'Senior Couples',
    'Senior Singles'
]

COVERAGE_SEGMENTS = [
    'Economy',
    'Standard',
    'Premium',
    'Luxury'
]

SCORE_SEGMENTS = [
    'Low',
    'Medium',
    'High',
    'Very High'
]
