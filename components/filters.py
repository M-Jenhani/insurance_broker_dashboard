"""
Sidebar filters component
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def create_sidebar_filters(df):
    """Create sidebar filters and return filtered dataframe"""
    st.sidebar.header("🎯 Filtres")
    
    # Date range
    st.sidebar.subheader("📅 Période")
    date_range = st.sidebar.date_input(
        "Période",
        value=(df['submission_date'].min(), df['submission_date'].max()),
        key="date_range"
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[
            (df['submission_date'].dt.date >= start_date) &
            (df['submission_date'].dt.date <= end_date)
        ]
    else:
        df_filtered = df
    
    # Priority score
    st.sidebar.subheader("⭐ Score de Priorité")
    min_score = st.sidebar.slider(
        "Score minimum",
        min_value=int(df['priority_score'].min()),
        max_value=int(df['priority_score'].max()),
        value=int(df['priority_score'].min()),
        key="min_score"
    )
    df_filtered = df_filtered[df_filtered['priority_score'] >= min_score]
    
    # Source
    if 'source' in df.columns:
        st.sidebar.subheader("📍 Source")
        sources = ['Tous'] + list(df['source'].unique())
        selected_source = st.sidebar.selectbox("Source", sources, key="source")
        if selected_source != 'Tous':
            df_filtered = df_filtered[df_filtered['source'] == selected_source]
    
    # Segment filter (if available)
    if 'segment' in df.columns:
        st.sidebar.subheader("🎯 Segment")
        segments = ['Tous'] + sorted(df['segment'].unique().tolist())
        selected_segment = st.sidebar.selectbox("Segment", segments, key="segment")
        if selected_segment != 'Tous':
            df_filtered = df_filtered[df_filtered['segment'] == selected_segment]
    
    # Contact quality
    if 'contact_quality' in df.columns:
        st.sidebar.subheader("📞 Qualité Contact")
        qualities = ['Tous'] + sorted(df['contact_quality'].unique().tolist())
        selected_quality = st.sidebar.selectbox("Qualité", qualities, key="quality")
        if selected_quality != 'Tous':
            df_filtered = df_filtered[df_filtered['contact_quality'] == selected_quality]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.metric("📊 Prospects filtrés", len(df_filtered))
    st.sidebar.metric("📈 % du total", f"{len(df_filtered)/len(df)*100:.1f}%")
    
    return df_filtered
