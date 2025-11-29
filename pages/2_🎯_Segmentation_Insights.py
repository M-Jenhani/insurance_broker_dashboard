"""
Segmentation & Insights Page - Analyse ML des segments
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

st.set_page_config(page_title="Segmentation Insights", page_icon="🎯", layout="wide")

# Get data from session state, reload if missing
if 'df_filtered' not in st.session_state or st.session_state.get('df_filtered', pd.DataFrame()).empty:
    from utils.data_loader import load_data, load_models
    from components.filters import create_sidebar_filters
    
    df_full = load_data()
    if df_full is not None:
        st.session_state['df_full'] = df_full
        st.session_state['models'] = load_models()
        st.session_state['df_filtered'] = create_sidebar_filters(df_full)

df = st.session_state.get('df_filtered', pd.DataFrame())
models = st.session_state.get('models', None)

if df.empty:
    st.error("❌ Pas de données disponibles. Vérifiez que les fichiers de données existent.")
    st.stop()

st.header("📊 Segmentation & Insights ML")

if models is None:
    st.error("❌ Modèles ML non disponibles. Veuillez d'abord entraîner les modèles avec `python src/ml_models.py`")
    st.stop()

segmentation = models['segmentation']
anomaly_detector = models['anomaly_detector']
feature_analyzer = models['feature_analyzer']

# Check if data has segments
if 'segment' not in df.columns:
    st.warning("⚠️ Données non segmentées. Rechargez les données traitées.")
    st.stop()

# Overview metrics
st.subheader("📊 Vue d'ensemble")
col1, col2, col3, col4 = st.columns(4)

with col1:
    n_segments = df['segment'].nunique()
    st.metric("Segments Identifiés", n_segments)

with col2:
    anomalies = len(df[df['is_anomaly'] == True]) if 'is_anomaly' in df.columns else 0
    st.metric("Prospects Atypiques", f"{anomalies:,}", f"{anomalies/len(df)*100:.1f}%")

with col3:
    avg_score = df['priority_score'].mean()
    st.metric("Score Moyen", f"{avg_score:.1f}")

with col4:
    if 'adjusted_score' in df.columns:
        avg_adjusted = df['adjusted_score'].mean()
        st.metric("Score Ajusté Moyen", f"{avg_adjusted:.1f}")
    else:
        st.metric("Score Ajusté", "N/A")

st.markdown("---")

# Segment profiles
st.subheader("👥 Profils des Segments")

segment_stats = df.groupby('segment').agg({
    'id': 'count',
    'priority_score': 'mean',
    'age_at_submission': 'mean',
    'num_children': 'mean'
}).reset_index()

segment_stats.columns = ['Segment', 'Nombre', 'Score Moyen', 'Âge Moyen', 'Enfants Moy.']
segment_stats = segment_stats.sort_values('Score Moyen', ascending=False)

# Add segment names from model
if hasattr(segmentation, 'segment_profiles'):
    segment_names = {i: profile.get('name', f'Segment {i}') 
                    for i, profile in segmentation.segment_profiles.items()}
    segment_stats['Nom'] = segment_stats['Segment'].map(segment_names)
    segment_stats = segment_stats[['Segment', 'Nom', 'Nombre', 'Score Moyen', 'Âge Moyen', 'Enfants Moy.']]

st.dataframe(segment_stats, use_container_width=True)

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribution des segments")
    segment_counts = df['segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Nombre']
    
    # Add names if available
    if hasattr(segmentation, 'segment_profiles'):
        segment_counts['Nom'] = segment_counts['Segment'].map(segment_names)
        fig = px.pie(segment_counts, values='Nombre', names='Nom',
                    title="Répartition des prospects par segment")
    else:
        fig = px.pie(segment_counts, values='Nombre', names='Segment',
                    title="Répartition des prospects par segment")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⭐ Score moyen par segment")
    fig = px.bar(segment_stats, x='Segment', y='Score Moyen',
                title="Performance des segments",
                color='Score Moyen', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

# Feature importance
st.markdown("---")
st.subheader("📊 Importance des Variables")

if hasattr(feature_analyzer, 'feature_importance') and feature_analyzer.feature_importance is not None:
    importance_df = feature_analyzer.feature_importance.copy()
    importance_df = importance_df.rename(columns={
        'feature': 'Variable',
        'correlation': 'Importance'
    })
    
    fig = px.bar(importance_df.head(15), x='Importance', y='Variable',
                title="Top 15 variables les plus influentes sur le score",
                orientation='h', color='Importance', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Ces variables ont la plus forte corrélation avec le score de priorité.")

# Export
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Exporter les segments"):
        csv = df[['id', 'first_name', 'last_name', 'segment', 'priority_score']].to_csv(index=False)
        st.download_button("Télécharger CSV", csv, "segments.csv", "text/csv")

with col2:
    st.info("💡 **Astuce**: Utilisez ces segments pour personnaliser vos campagnes marketing")
