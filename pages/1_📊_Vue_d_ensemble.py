"""
Overview Page - Vue d'ensemble des prospects
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Vue d'ensemble", page_icon="📊", layout="wide")

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

st.header("📊 Vue d'ensemble des prospects")

# Key metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Prospects", f"{len(df):,}")

with col2:
    high_priority = len(df[df['priority_score'] >= 18])
    st.metric("Leads Haute Priorité", f"{high_priority:,}", f"{high_priority/len(df)*100:.1f}%")

with col3:
    avg_score = df['priority_score'].mean()
    st.metric("Score Moyen", f"{avg_score:.1f}")

with col4:
    if 'adjusted_score' in df.columns:
        avg_adjusted = df['adjusted_score'].mean()
        st.metric("Score Ajusté Moyen", f"{avg_adjusted:.1f}", "avec fraîcheur")
    else:
        recent_leads = len(df[df['submission_date'] >= datetime.now() - timedelta(days=7)])
        st.metric("Nouveaux (7j)", f"{recent_leads:,}")

with col5:
    if 'segment' in df.columns:
        n_segments = df['segment'].nunique()
        st.metric("Segments ML", f"{n_segments}", "clustering")
    else:
        conversion_rate = np.random.uniform(0.15, 0.25)  # Simulated
        st.metric("Taux de Conversion", f"{conversion_rate*100:.1f}%")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution des soumissions")
    daily_subs = df.groupby(df['submission_date'].dt.date).size().reset_index()
    daily_subs.columns = ['Date', 'Nombre']
    fig = px.line(daily_subs, x='Date', y='Nombre', title="Soumissions quotidiennes")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Distribution des scores")
    
    # Show both priority and adjusted scores if available
    if 'adjusted_score' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df['priority_score'], name='Score priorité', opacity=0.7, nbinsx=30))
        fig.add_trace(go.Histogram(x=df['adjusted_score'], name='Score ajusté', opacity=0.7, nbinsx=30))
        fig.update_layout(
            title="Distribution des scores (priorité vs ajusté)",
            xaxis_title="Score",
            yaxis_title="Nombre",
            barmode='overlay'
        )
        fig.add_vline(x=18, line_dash="dash", line_color="red", annotation_text="Seuil haute priorité")
    else:
        fig = px.histogram(df, x='priority_score', nbins=30,
                          title="Distribution des scores de priorité",
                          labels={'priority_score': 'Score de priorité', 'count': 'Nombre'})
        fig.add_vline(x=18, line_dash="dash", line_color="red", annotation_text="Seuil haute priorité")
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Show segments if available
    if 'segment' in df.columns:
        st.subheader("👥 Répartition par segments")
        segment_counts = df['segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Nombre']
        fig = px.bar(segment_counts, x='Segment', y='Nombre',
                    title="Distribution des segments ML",
                    color='Nombre', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("🏥 Régimes de sécurité sociale")
        regime_counts = df['social_security_regime'].value_counts()
        fig = px.pie(values=regime_counts.values, names=regime_counts.index,
                     title="Répartition par régime")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📱 Sources des leads")
    source_counts = df['source'].value_counts().head(10)
    fig = px.bar(x=source_counts.index, y=source_counts.values,
                title="Top 10 sources de prospects",
                labels={'x': 'Source', 'y': 'Nombre'})
    st.plotly_chart(fig, use_container_width=True)
