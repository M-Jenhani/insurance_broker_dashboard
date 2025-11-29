"""
Priority Ranking Page - Leads à Contacter en Priorité
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from business_intelligence import EmailGenerator

st.set_page_config(page_title="Classement Prioritaire", page_icon="🎯", layout="wide")

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

st.header("🎯 Leads à Contacter en Priorité")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    priority_threshold = st.selectbox(
        "Niveau de priorité",
        ["Tous", "Très élevé (>20)", "Élevé (18-20)", "Moyen (15-18)", "Faible (<15)"]
    )

with col2:
    urgency_filter = st.selectbox(
        "Urgence (date d'effet)",
        ["Tous", "Immédiat (<7 jours)", "Court terme (7-30 jours)", "Moyen terme (>30 jours)"]
    )

with col3:
    family_filter = st.selectbox(
        "Situation familiale",
        ["Tous", "Avec enfants", "Avec conjoint", "Seul(e)"]
    )

# Apply filters
df_priority = df.copy()

if priority_threshold != "Tous":
    if "Très élevé" in priority_threshold:
        df_priority = df_priority[df_priority['priority_score'] > 20]
    elif "Élevé" in priority_threshold:
        df_priority = df_priority[(df_priority['priority_score'] >= 18) & (df_priority['priority_score'] <= 20)]
    elif "Moyen" in priority_threshold:
        df_priority = df_priority[(df_priority['priority_score'] >= 15) & (df_priority['priority_score'] < 18)]
    else:
        df_priority = df_priority[df_priority['priority_score'] < 15]

if urgency_filter != "Tous":
    if "Immédiat" in urgency_filter:
        df_priority = df_priority[df_priority['days_to_effective'] < 7]
    elif "Court terme" in urgency_filter:
        df_priority = df_priority[(df_priority['days_to_effective'] >= 7) & (df_priority['days_to_effective'] <= 30)]
    else:
        df_priority = df_priority[df_priority['days_to_effective'] > 30]

if family_filter != "Tous":
    if "enfants" in family_filter:
        df_priority = df_priority[df_priority['num_children'] > 0]
    elif "conjoint" in family_filter:
        df_priority = df_priority[df_priority['spouse_age_at_submission'] != -999]
    else:
        df_priority = df_priority[(df_priority['num_children'] == 0) & (df_priority['spouse_age_at_submission'] == -999)]

# Sort by adjusted score (time-decayed) if available, otherwise use priority_score
if 'adjusted_score' in df_priority.columns and df_priority['adjusted_score'].notna().any():
    df_priority = df_priority.sort_values('adjusted_score', ascending=False)
else:
    df_priority = df_priority.sort_values('priority_score', ascending=False)

st.info(f"📋 {len(df_priority)} prospects correspondent à vos critères")

# Top leads cards
st.subheader("🔥 Top 10 Leads à Contacter Aujourd'hui")

for idx, row in df_priority.head(10).iterrows():
    # Build title with score and freshness indicator
    title = f"⭐ {row['title']} {row['first_name']} {row['last_name']} - Score: {row['priority_score']:.1f}"
    
    # Add freshness indicator if available
    if 'days_since_submission' in row and pd.notna(row['days_since_submission']):
        days_old = int(row['days_since_submission'])
        if days_old <= 7:
            title += " 🟢 (Nouveau)"
        elif days_old <= 30:
            title += " 🟡 (Récent)"
        else:
            title += f" 🔴 ({days_old}j)"
    
    # Add adjusted score if available
    if 'adjusted_score' in row and pd.notna(row['adjusted_score']):
        title += f" | Ajusté: {row['adjusted_score']:.1f}"
    
    with st.expander(title):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📞 Contact:**")
            st.write(f"Téléphone: {row['phone_number']}")
            st.write(f"Email: {row['email']}")
            st.write(f"Ville: {row['city']} ({row['zip_code']})")
            
            # Show contact quality if available
            if 'contact_quality_score' in row and pd.notna(row['contact_quality_score']):
                quality = row['contact_quality_score']
                quality_label = "Excellent" if quality >= 1.5 else "Bon" if quality >= 1 else "Moyen"
                st.write(f"Qualité contact: {quality_label} ({quality:.1f}/2)")
        
        with col2:
            st.write("**👨‍👩‍👧‍👦 Profil:**")
            st.write(f"Âge: {row['age_at_submission']} ans")
            st.write(f"Conjoint: {'Oui' if row['spouse_age_at_submission'] != -999 else 'Non'}")
            st.write(f"Enfants: {row['num_children']}")
            st.write(f"Régime: {row['social_security_regime']}")
            
            # Show segment if available
            if 'segment' in row and pd.notna(row['segment']):
                st.write(f"Segment ML: {row['segment']}")
        
        with col3:
            st.write("**💼 Besoins:**")
            coverage_map = {1: 'ECO', 2: 'MOYEN', 3: 'ÉLEVÉ', 4: 'MAXI'}
            st.write(f"Soins médicaux: {coverage_map[row['medical_care']]}")
            st.write(f"Hospitalisation: {coverage_map[row['hospitalization']]}")
            st.write(f"Optique: {coverage_map[row['optical']]}")
            st.write(f"Dentaire: {coverage_map[row['dental']]}")
            
            # Show anomaly flag if available
            if 'is_anomaly' in row and row['is_anomaly']:
                st.warning("🚨 Prospect atypique - Vérifier le profil")
        
        # Generate personalized email
        if st.button(f"📧 Générer email personnalisé", key=f"email_{idx}"):
            email = EmailGenerator.generate_personalized_advice(row)
            st.text_area("Email généré:", email, height=400, key=f"email_text_{idx}")

# Export functionality
st.markdown("---")
st.subheader("📥 Export")

col1, col2 = st.columns(2)

with col1:
    csv = df_priority.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Télécharger en CSV",
        csv,
        f"leads_prioritaires_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv"
    )

with col2:
    # Generate email alert
    if st.button("📧 Générer alerte email"):
        email = EmailGenerator.generate_high_priority_alert(df_priority.head(10))
        st.text_area("Email d'alerte:", email, height=400, key="alert_email")
