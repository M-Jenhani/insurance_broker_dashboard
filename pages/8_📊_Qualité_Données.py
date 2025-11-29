"""
Data Quality Page - Qualité des Données
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Qualité des Données", page_icon="📊", layout="wide")

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

st.header("📊 Qualité des Données")

# Data overview
st.subheader("📋 Vue d'ensemble")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", f"{len(df):,}")

with col2:
    missing_values = df.isnull().sum().sum()
    st.metric("Valeurs Manquantes", f"{missing_values:,}")

with col3:
    duplicate_rows = df.duplicated().sum()
    st.metric("Doublons", f"{duplicate_rows:,}")

with col4:
    completeness = (1 - missing_values / (len(df) * len(df.columns))) * 100
    st.metric("Complétude", f"{completeness:.1f}%")

st.markdown("---")

# Missing values analysis
st.subheader("🔍 Analyse des Valeurs Manquantes")

missing_by_column = df.isnull().sum()
missing_pct = (missing_by_column / len(df) * 100).sort_values(ascending=False)

if missing_pct.sum() > 0:
    missing_df = pd.DataFrame({
        'Colonne': missing_pct.index,
        'Valeurs Manquantes': missing_by_column.values,
        'Pourcentage': missing_pct.values
    })
    missing_df = missing_df[missing_df['Valeurs Manquantes'] > 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(missing_df, use_container_width=True)
    
    with col2:
        fig = px.bar(missing_df, x='Pourcentage', y='Colonne',
                    orientation='h',
                    title="Pourcentage de valeurs manquantes par colonne")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.success("✅ Aucune valeur manquante détectée!")

st.markdown("---")

# Data types
st.subheader("📊 Types de Données")

dtypes_df = pd.DataFrame({
    'Colonne': df.dtypes.index,
    'Type': df.dtypes.values.astype(str)
})

col1, col2 = st.columns(2)

with col1:
    st.dataframe(dtypes_df, use_container_width=True)

with col2:
    type_counts = dtypes_df['Type'].value_counts()
    fig = px.pie(values=type_counts.values, names=type_counts.index,
                title="Répartition des types de données")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Data profiling
st.subheader("📈 Profiling des Colonnes Numériques")

numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

if len(numeric_cols) > 0:
    selected_col = st.selectbox("Sélectionner une colonne", numeric_cols)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Moyenne", f"{df[selected_col].mean():.2f}")
        st.metric("Médiane", f"{df[selected_col].median():.2f}")
    
    with col2:
        st.metric("Min", f"{df[selected_col].min():.2f}")
        st.metric("Max", f"{df[selected_col].max():.2f}")
    
    with col3:
        st.metric("Std Dev", f"{df[selected_col].std():.2f}")
        st.metric("Valeurs Uniques", f"{df[selected_col].nunique():,}")
    
    # Distribution
    fig = px.histogram(df, x=selected_col, nbins=50,
                      title=f"Distribution de {selected_col}")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Data quality issues
st.subheader("⚠️ Problèmes de Qualité Détectés")

issues = []

# Check for duplicates
if duplicate_rows > 0:
    issues.append(f"🔴 {duplicate_rows} lignes dupliquées détectées")

# Check for missing email
if 'email' in df.columns:
    missing_email = df['email'].isnull().sum()
    if missing_email > 0:
        issues.append(f"🔴 {missing_email} prospects sans email")

# Check for missing phone
if 'phone_number' in df.columns:
    missing_phone = df['phone_number'].isnull().sum()
    if missing_phone > 0:
        issues.append(f"🟡 {missing_phone} prospects sans téléphone")

# Check for invalid ages
if 'age_at_submission' in df.columns:
    invalid_age = ((df['age_at_submission'] < 18) | (df['age_at_submission'] > 120)).sum()
    if invalid_age > 0:
        issues.append(f"🟡 {invalid_age} âges potentiellement invalides")

if len(issues) > 0:
    for issue in issues:
        st.warning(issue)
else:
    st.success("✅ Aucun problème de qualité majeur détecté!")

# Export data quality report
st.markdown("---")

if st.button("📥 Exporter Rapport de Qualité"):
    report = f"""
RAPPORT DE QUALITÉ DES DONNÉES
Généré le: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

=== VUE D'ENSEMBLE ===
Total de records: {len(df):,}
Colonnes: {len(df.columns)}
Valeurs manquantes: {missing_values:,}
Doublons: {duplicate_rows:,}
Complétude: {completeness:.1f}%

=== VALEURS MANQUANTES PAR COLONNE ===
{missing_by_column[missing_by_column > 0].to_string()}

=== TYPES DE DONNÉES ===
{df.dtypes.to_string()}

=== PROBLÈMES DÉTECTÉS ===
{chr(10).join(issues) if issues else 'Aucun problème majeur'}
"""
    
    st.download_button(
        "Télécharger le rapport",
        report,
        f"data_quality_report_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
        "text/plain"
    )
