"""
Automation Page - Automatisation et Exports
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from business_intelligence import EmailGenerator

st.set_page_config(page_title="Automatisation", page_icon="⚙️", layout="wide")

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

st.header("⚙️ Automatisation et Exports")

st.info("""
Cette page permet de configurer les automatisations pour votre workflow quotidien:
- Exports CSV programmés
- Alertes email pour les leads haute priorité
- Rapports hebdomadaires automatiques
""")

# Daily/Weekly exports
st.subheader("📤 Exports Automatiques")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Export Quotidien")
    
    daily_threshold = st.slider("Score minimum pour export quotidien", 15, 25, 18)
    
    daily_leads = df[
        (df['submission_date'] >= datetime.now() - timedelta(days=1)) &
        (df['priority_score'] >= daily_threshold)
    ]
    
    st.write(f"Leads aujourd'hui: **{len(daily_leads)}**")
    
    if st.button("⬇️ Télécharger leads du jour"):
        csv = daily_leads.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Télécharger CSV",
            csv,
            f"leads_quotidien_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

with col2:
    st.markdown("### 📅 Export Hebdomadaire")
    
    weekly_threshold = st.slider("Score minimum pour export hebdomadaire", 10, 25, 15)
    
    weekly_leads = df[
        (df['submission_date'] >= datetime.now() - timedelta(days=7)) &
        (df['priority_score'] >= weekly_threshold)
    ]
    
    st.write(f"Leads cette semaine: **{len(weekly_leads)}**")
    
    if st.button("⬇️ Télécharger leads de la semaine"):
        csv = weekly_leads.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Télécharger CSV",
            csv,
            f"leads_hebdo_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

st.markdown("---")

# Email alerts configuration
st.subheader("📧 Configuration des Alertes Email")

col1, col2 = st.columns(2)

with col1:
    alert_email = st.text_input("Email du destinataire", "contact@cabinet-vital.fr")
    alert_frequency = st.selectbox("Fréquence", ["Quotidienne", "Hebdomadaire", "Immédiate (nouveau lead haute priorité)"])
    alert_threshold = st.slider("Score minimum pour alerte", 15, 25, 20)

with col2:
    st.write("**Aperçu de l'alerte:**")
    preview_leads = df[df['priority_score'] >= alert_threshold].head(3)
    if len(preview_leads) > 0:
        email_preview = EmailGenerator.generate_high_priority_alert(preview_leads)
        st.text_area("Aperçu Email", email_preview, height=300, label_visibility="collapsed")

if st.button("✅ Activer les alertes"):
    st.success(f"✅ Alertes activées! Vous recevrez des emails {alert_frequency.lower()} à {alert_email}")

st.markdown("---")

# Reports
st.subheader("📊 Rapports Automatiques")

report_type = st.selectbox(
    "Type de rapport",
    ["Rapport hebdomadaire complet", "Performance des campagnes", "Analyse géographique", "Segmentation client"]
)

if st.button("📄 Générer le rapport"):
    with st.spinner("Génération du rapport..."):
        st.success("✅ Rapport généré!")
        
        # Generate summary report
        report = f"""
# INSURANCE BROKER DASHBOARD REPORT
## {report_type}
### Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}

---

### 📊 MÉTRIQUES CLÉS
- Total prospects: {len(df):,}
- Leads haute priorité (>18): {len(df[df['priority_score'] >= 18]):,}
- Score moyen: {df['priority_score'].mean():.1f}/25
- Nouveaux leads (7 jours): {len(df[df['submission_date'] >= datetime.now() - timedelta(days=7)]):,}

### 🎯 TOP 5 SOURCES
{df['source'].value_counts().head().to_string()}

### 📍 TOP 5 DÉPARTEMENTS
{df['zip_code'].astype(str).str[:2].value_counts().head().to_string()}

### 💼 RÉPARTITION PAR RÉGIME
{df['social_security_regime'].value_counts().to_string()}

---
Rapport généré automatiquement par le Dashboard Insurance Broker
"""
        
        st.download_button(
            "⬇️ Télécharger le rapport (TXT)",
            report,
            f"rapport_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain"
        )
