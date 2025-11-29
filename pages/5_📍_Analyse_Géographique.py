"""
Geographic Analysis Page - Analyse Géographique
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse Géographique", page_icon="📍", layout="wide")

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

if df.empty:
    st.error("❌ Pas de données disponibles. Vérifiez que les fichiers de données existent.")
    st.stop()

st.header("📍 Analyse Géographique")

# Department analysis
df['department'] = df['zip_code'].astype(str).str[:2]

dept_stats = df.groupby('department').agg({
    'id': 'count',
    'priority_score': 'mean'
}).reset_index()
dept_stats.columns = ['Département', 'Nombre', 'Score Moyen']
dept_stats = dept_stats.sort_values('Nombre', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Top 15 Départements par Volume")
    fig = px.bar(dept_stats.head(15), x='Département', y='Nombre',
                title="Départements avec le plus de prospects")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⭐ Top 15 Départements par Qualité")
    top_quality = dept_stats.nlargest(15, 'Score Moyen')
    fig = px.bar(top_quality, x='Département', y='Score Moyen',
                title="Départements avec les scores les plus élevés",
                color='Score Moyen', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

# City analysis
st.subheader("🏙️ Analyse par ville")

city_stats = df.groupby('city').agg({
    'id': 'count',
    'priority_score': 'mean'
}).reset_index()
city_stats.columns = ['Ville', 'Nombre', 'Score Moyen']
city_stats = city_stats[city_stats['Nombre'] >= 5]  # Filter small cities
city_stats = city_stats.sort_values('Nombre', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.write("**Top 20 villes par volume:**")
    st.dataframe(city_stats.head(20), use_container_width=True)

with col2:
    st.write("**Opportunités (volume élevé + score élevé):**")
    opportunity = city_stats[
        (city_stats['Nombre'] >= city_stats['Nombre'].quantile(0.75)) &
        (city_stats['Score Moyen'] >= city_stats['Score Moyen'].quantile(0.75))
    ]
    st.dataframe(opportunity, use_container_width=True)

# Urban vs Rural
st.subheader("🏙️ Urbain vs Rural")

urban_depts = ['75', '77', '92', '93', '94', '95']
df['area_type'] = df['department'].astype(str).apply(lambda x: 'Île-de-France' if x in urban_depts else 'Autres régions')

area_comparison = df.groupby('area_type').agg({
    'id': 'count',
    'priority_score': 'mean',
    'age_at_submission': 'mean'
}).reset_index()

col1, col2, col3 = st.columns(3)

with col1:
    fig = px.pie(area_comparison, values='id', names='area_type',
                title="Répartition géographique")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(area_comparison, x='area_type', y='priority_score',
                title="Score moyen par zone")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = px.bar(area_comparison, x='area_type', y='age_at_submission',
                title="Âge moyen par zone")
    st.plotly_chart(fig, use_container_width=True)
