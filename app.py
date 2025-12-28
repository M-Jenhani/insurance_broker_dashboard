"""
Streamlit Dashboard for Insurance Broker Lead Management
Main Entry Point - Inspired by real-world brokerage experience

Run with: streamlit run app.py
"""
import streamlit as st
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.data_loader import load_data, load_models
from utils.styling import load_custom_css
from components.filters import create_sidebar_filters

# Page configuration
st.set_page_config(
    page_title="Insurance Broker Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Header
st.markdown('<h1 class="main-header">🏥 Insurance Broker Dashboard - Lead Management System</h1>', unsafe_allow_html=True)
st.markdown('#### <span style="color: #f97316;">🔒 Démo avec données synthétiques uniquement</span>',unsafe_allow_html=True)
st.warning("Cette démonstration repose **exclusivement sur des données synthétiques générées** pour l’occasion — **aucune donnée réelle**", icon="🔒")


# Load data
df = load_data()
if df is None:
    st.stop()

models = load_models()

# Store in session state for pages to access
st.session_state['df_full'] = df
st.session_state['models'] = models

# Sidebar navigation
st.sidebar.title("📋 Navigation")
st.sidebar.info("👈 Utilisez le menu de navigation ci-dessus pour accéder aux différentes pages")

# Apply filters
df_filtered = create_sidebar_filters(df)
st.session_state['df_filtered'] = df_filtered

# Main page content
st.success(f"✅ {len(df_filtered):,} prospects **synthétiques** chargés ({len(df_filtered)/len(df)*100:.1f}% du total)")

st.markdown("""
## 👋 Welcome to the Insurance Broker Dashboard

Utilisez le menu de gauche pour naviguer entre les pages:

- **📊 Vue d'ensemble** - Métriques clés et visualisations
- **🎯 Segmentation & Insights** - Analyse ML des segments
- **📈 Classement Prioritaire** - Leads à contacter en priorité
- **💡 Intelligence Business** - Recommandations stratégiques
- **📍 Analyse Géographique** - Cartographie des prospects
- **📞 Suivi Conversions** - Tracking des performances
- **⚙️ Automatisation** - Génération d'emails et rapports
- **📊 Qualité des Données** - Audit et nettoyage
- **⚙️ Paramètres** - Configuration du système

### 🚀 Démarrage Rapide

1. Utilisez les **filtres** dans la barre latérale
2. Naviguez vers **🎯 Classement Prioritaire** pour voir les leads à contacter
3. Consultez **💡 Intelligence Business** pour les recommandations stratégiques

### 📈 Statistiques Rapides
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    high_priority = len(df_filtered[df_filtered['priority_score'] >= 18])
    st.metric("🔥 Haute Priorité", f"{high_priority:,}", f"{high_priority/len(df_filtered)*100:.1f}%")

with col2:
    avg_score = df_filtered['priority_score'].mean()
    st.metric("⭐ Score Moyen", f"{avg_score:.1f}")

with col3:
    if 'segment' in df_filtered.columns:
        n_segments = df_filtered['segment'].nunique()
        st.metric("🎯 Segments", n_segments)
    else:
        st.metric("📊 Sources", df_filtered['source'].nunique())

with col4:
    if models:
        st.metric("🤖 Modèles ML", "✅ Chargés")
    else:
        st.metric("🤖 Modèles ML", "⚠️ Non disponibles")

st.markdown("---")
st.info("💡 **Astuce**: Exécutez `python src/ml_models.py` pour entraîner les modèles ML et obtenir des insights avancés.")
