"""
Template for creating new dashboard pages
Copy this file and modify for your needs
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add paths if needed
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Optional imports from your modules
# from business_intelligence import BusinessIntelligence
# from components.metrics import display_kpi_row

# Page configuration
st.set_page_config(
    page_title="Your Page Title",
    page_icon="📈",  # Choose an emoji
    layout="wide"
)

# Get data from session state, reload if missing
if 'df_filtered' not in st.session_state or st.session_state.get('df_filtered', pd.DataFrame()).empty:
    from utils.data_loader import load_data, load_models
    from components.filters import create_sidebar_filters
    
    df_full_temp = load_data()
    if df_full_temp is not None:
        st.session_state['df_full'] = df_full_temp
        st.session_state['models'] = load_models()
        st.session_state['df_filtered'] = create_sidebar_filters(df_full_temp)

df = st.session_state.get('df_filtered', pd.DataFrame())
df_full = st.session_state.get('df_full', pd.DataFrame())
models = st.session_state.get('models')

# Check if data is available
if df.empty:
    st.error("❌ Pas de données disponibles. Vérifiez que les fichiers de données existent.")
    st.stop()

# Page header
st.header("📈 Your Page Title")

# Optional: Check if models are needed
# if models is None:
#     st.warning("⚠️ Modèles ML non disponibles")

# Your page content here
st.subheader("📊 Section 1")

# Example: Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Metric 1", f"{len(df):,}")

with col2:
    st.metric("Metric 2", f"{df['priority_score'].mean():.1f}")

with col3:
    st.metric("Metric 3", "Value")

with col4:
    st.metric("Metric 4", "Value")

st.markdown("---")

# Example: Display charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Chart 1")
    # Your chart code
    fig = px.bar(df['segment'].value_counts())
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Chart 2")
    # Your chart code
    fig = px.histogram(df, x='priority_score')
    st.plotly_chart(fig, use_container_width=True)

# Example: Data table
st.markdown("---")
st.subheader("📋 Data Table")
st.dataframe(df.head(20), use_container_width=True)

# Example: Export functionality
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Export Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Télécharger CSV",
            csv,
            "export.csv",
            "text/csv"
        )

with col2:
    st.info("💡 **Astuce**: Add helpful tips here")
