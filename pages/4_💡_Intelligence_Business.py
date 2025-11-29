"""
Business Intelligence Page - Intelligence Business et Recommandations
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from business_intelligence import BusinessIntelligence

st.set_page_config(page_title="Intelligence Business", page_icon="💡", layout="wide")

# Get data from session state, reload if missing
if 'df_full' not in st.session_state or st.session_state.get('df_full', pd.DataFrame()).empty:
    from utils.data_loader import load_data, load_models
    from components.filters import create_sidebar_filters
    
    df_full = load_data()
    if df_full is not None:
        st.session_state['df_full'] = df_full
        st.session_state['models'] = load_models()
        st.session_state['df_filtered'] = create_sidebar_filters(df_full)

df = st.session_state.get('df_full', pd.DataFrame())
models = st.session_state.get('models', None)

if df.empty:
    st.error("❌ Pas de données disponibles. Vérifiez que les fichiers de données existent.")
    st.stop()

st.header("💡 Intelligence Business")

bi = BusinessIntelligence(df)

# Key recommendations
st.subheader("🎯 Recommandations Stratégiques")

recommendations = bi.get_all_recommendations()

for _, rec in recommendations.iterrows():
    if rec['priority'] == 'High':
        st.error(f"**[PRIORITÉ HAUTE] {rec['category']}**")
    else:
        st.warning(f"**[PRIORITÉ MOYENNE] {rec['category']}**")
    
    st.write(f"➤ {rec['insight']}")
    st.markdown("---")

# Seasonal analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Tendances Saisonnières")
    seasonal = bi.analyze_seasonal_trends()
    
    monthly_dist = pd.DataFrame(list(seasonal['monthly_distribution'].items()),
                                columns=['Mois', 'Nombre'])
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                  'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    monthly_dist['Mois'] = monthly_dist['Mois'].apply(
        lambda x: month_names[int(float(x))-1] if pd.notna(x) and str(x).replace('.','').isdigit() else 'N/A'
    )
    
    fig = px.bar(monthly_dist, x='Mois', y='Nombre',
                title="Soumissions par mois (historique)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"💡 {seasonal['recommendation']}")

with col2:
    st.subheader("📍 Zones à Forte Demande")
    geographic = bi.identify_high_demand_areas()
    
    fig = px.bar(geographic['top_departments'].head(10),
                x=geographic['top_departments'].head(10).index,
                y='count',
                title="Top 10 départements")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"💡 {geographic['recommendation']}")

# Campaign performance
st.subheader("📊 Performance des Campagnes")

campaign_perf = bi.analyze_campaign_performance()

fig = px.scatter(campaign_perf['campaign_stats'].reset_index(),
                x='leads', y='avg_score', size='quality_index',
                hover_data=['source'],
                title="Qualité vs Quantité par source",
                labels={'leads': 'Nombre de leads', 'avg_score': 'Score moyen'})
st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 {campaign_perf['recommendation']}")

# Market segments
st.subheader("🎯 Opportunités de Marché")

segments = bi.identify_underserved_segments()

if segments['gaps']:
    gap_df = pd.DataFrame(segments['gaps']).T
    gap_df = gap_df.sort_values('gap', ascending=False)
    
    fig = px.bar(gap_df, y=gap_df.index, x='gap',
                orientation='h',
                title="Écart entre part de marché attendue et réelle (%)",
                labels={'gap': 'Écart (%)', 'index': 'Régime'})
    st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 {segments['recommendation']}")
