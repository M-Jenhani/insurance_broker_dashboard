"""
Data loading utilities for the dashboard
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from ml_models import ProspectSegmentation, AnomalyDetector, FeatureAnalyzer


@st.cache_data
def load_data():
    """Load cleaned prospect data"""
    try:
        # Try to load processed data with segments first
        df = pd.read_csv('data/processed_prospects.csv')
        df['submission_date'] = pd.to_datetime(df['submission_date'])
        df['effective_date'] = pd.to_datetime(df['effective_date'])
        return df
    except FileNotFoundError:
        try:
            # Fall back to cleaned data without segments
            df = pd.read_csv('data/cleaned_prospects.csv')
            df['submission_date'] = pd.to_datetime(df['submission_date'])
            df['effective_date'] = pd.to_datetime(df['effective_date'])
            st.warning("⚠️ Données chargées sans informations de segments. Exécutez `python src/ml_models.py` pour générer les segments.")
            return df
        except FileNotFoundError:
            st.error("❌ Fichier de données non trouvé. Veuillez d'abord générer les données.")
            return None


@st.cache_resource
def load_models():
    """Load ML models"""
    try:
        segmentation = ProspectSegmentation()
        anomaly_detector = AnomalyDetector()
        feature_analyzer = FeatureAnalyzer()
        
        segmentation.load_model('models/segmentation_model.pkl')
        anomaly_detector.load_model('models/anomaly_detector.pkl')
        feature_analyzer.load_model('models/feature_analyzer.pkl')
        
        return {
            'segmentation': segmentation,
            'anomaly_detector': anomaly_detector,
            'feature_analyzer': feature_analyzer
        }
    except Exception as e:
        st.warning(f"⚠️ Modèles ML non trouvés: {e}. Certaines fonctionnalités seront limitées.")
        return None
