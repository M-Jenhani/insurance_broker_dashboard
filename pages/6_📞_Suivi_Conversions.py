"""
Conversion Tracking Page - Suivi des Conversions
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

st.set_page_config(page_title="Suivi Conversions", page_icon="📞", layout="wide")

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

st.header("📞 Suivi des Conversions")

# Import conversion tracker
try:
    from conversion_tracker import ConversionTracker
    tracker = ConversionTracker()
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📝 Logger un contact", "📊 Statistiques", "🎯 Analyse par score"])
    
    with tab1:
        st.subheader("Enregistrer un nouveau contact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Prospect selection
            st.write("**Sélectionner le prospect:**")
            prospect_id = st.selectbox(
                "ID Prospect",
                options=df.sort_values('priority_score', ascending=False)['id'].head(100).tolist(),
                format_func=lambda x: f"{x} - {df[df['id']==x]['first_name'].values[0]} {df[df['id']==x]['last_name'].values[0]} (Score: {df[df['id']==x]['priority_score'].values[0]:.1f})"
            )
            
            # Show prospect details
            if prospect_id:
                prospect = df[df['id'] == prospect_id].iloc[0]
                st.info(f"""
                **Prospect sélectionné:**
                - Nom: {prospect['first_name']} {prospect['last_name']}
                - Âge: {prospect['age_at_submission']} ans
                - Score priorité: {prospect['priority_score']:.1f}
                - Email: {prospect['email']}
                - Téléphone: {prospect['phone_number']}
                """)
                
                # Show contact history if exists
                history = tracker.get_contact_history(prospect_id)
                if len(history) > 0:
                    st.warning(f"⚠️ Ce prospect a déjà été contacté {len(history)} fois")
                    with st.expander("Voir l'historique"):
                        st.dataframe(history[['contact_date', 'contacted_by', 'status', 'converted']])
        
        with col2:
            st.write("**Détails du contact:**")
            
            contacted_by = st.text_input("Contacté par", value="Agent")
            contact_method = st.selectbox("Méthode de contact", ["Phone", "Email", "SMS", "Meeting"])
            notes = st.text_area("Notes", placeholder="Commentaires sur le contact...")
            
            col_a, col_b = st.columns(2)
            with col_a:
                status = st.selectbox("Statut", ["Contacted", "Interested", "Not Interested", "No Answer", "Follow-up Scheduled"])
            with col_b:
                is_conversion = st.checkbox("✅ Conversion réussie?")
            
            if is_conversion:
                contract_value = st.number_input("Valeur du contrat (€)", min_value=0.0, value=500.0, step=50.0)
            else:
                contract_value = 0.0
        
        if st.button("💾 Enregistrer le contact", type="primary"):
            if prospect_id:
                prospect = df[df['id'] == prospect_id].iloc[0]
                
                # Log the contact
                success = tracker.log_contact(
                    prospect_id=prospect_id,
                    contacted_by=contacted_by,
                    contact_method=contact_method,
                    status=status if not is_conversion else "Converted",
                    priority_score=prospect['priority_score'],
                    adjusted_score=prospect.get('adjusted_score', prospect['priority_score']),
                    segment=prospect.get('segment', 'Unknown'),
                    notes=notes
                )
                
                # If conversion, log it
                if is_conversion and success:
                    tracker.log_conversion(
                        prospect_id=prospect_id,
                        contract_value=contract_value,
                        notes=notes
                    )
                    st.success(f"✅ Conversion enregistrée avec succès! Valeur: {contract_value}€")
                elif success:
                    st.success("✅ Contact enregistré avec succès!")
                else:
                    st.error("❌ Erreur lors de l'enregistrement")
                
                # Force refresh
                st.rerun()
    
    with tab2:
        st.subheader("📊 Statistiques Globales")
        
        # Get statistics
        stats = tracker.get_conversion_stats()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Contacts", stats['total_contacts'])
        with col2:
            st.metric("Conversions", stats['total_conversions'])
        with col3:
            st.metric("Taux de Conversion", f"{stats['conversion_rate']:.1f}%")
        with col4:
            st.metric("Revenu Total", f"{stats['total_revenue']:,.0f}€")
        
        if stats['total_contacts'] > 0:
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Conversions par Segment")
                segment_analysis = tracker.analyze_by_segment()
                if segment_analysis is not None and len(segment_analysis) > 0:
                    st.dataframe(
                        segment_analysis.style.format({
                            'Conversion Rate': '{:.1f}%',
                            'Total Revenue': '{:,.0f}€',
                            'Avg Contract Value': '{:,.0f}€'
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("Aucune donnée de segment disponible")
            
            with col2:
                st.subheader("📅 Contacts Récents (7 jours)")
                recent = tracker.get_recent_contacts(days=7)
                if len(recent) > 0:
                    st.metric("Contacts cette semaine", len(recent))
                    conversions_week = recent['converted'].sum()
                    st.metric("Conversions cette semaine", int(conversions_week))
                else:
                    st.info("Aucun contact récent")
            
            # Chart: Conversion rate by segment
            if segment_analysis is not None and len(segment_analysis) > 0:
                st.markdown("---")
                st.subheader("📈 Taux de Conversion par Segment")
                fig = px.bar(
                    segment_analysis,
                    x='Segment',
                    y='Conversion Rate',
                    text='Conversion Rate',
                    color='Conversion Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Aucun contact enregistré pour le moment. Utilisez l'onglet 'Logger un contact' pour commencer.")
    
    with tab3:
        st.subheader("🎯 Analyse de l'Efficacité des Scores")
        
        stats = tracker.get_conversion_stats()
        
        if stats['total_contacts'] > 0:
            effectiveness = tracker.analyze_score_effectiveness()
            
            if effectiveness is not None and len(effectiveness) > 0:
                st.write("**Analyse: Les prospects avec des scores élevés convertissent-ils mieux?**")
                
                # Display table
                st.dataframe(
                    effectiveness.style.format({
                        'Conversion Rate': '{:.1f}%'
                    }),
                    use_container_width=True
                )
                
                # Chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Contacts',
                    x=effectiveness['Score Range'],
                    y=effectiveness['Total Contacts'],
                    marker_color='lightblue',
                    yaxis='y'
                ))
                
                fig.add_trace(go.Scatter(
                    name='Taux de Conversion',
                    x=effectiveness['Score Range'],
                    y=effectiveness['Conversion Rate'],
                    marker_color='red',
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(width=3)
                ))
                
                fig.update_layout(
                    title='Efficacité des Scores de Priorité',
                    xaxis=dict(title='Plage de Score'),
                    yaxis=dict(title='Nombre de Contacts', side='left'),
                    yaxis2=dict(title='Taux de Conversion (%)', side='right', overlaying='y'),
                    legend=dict(x=0.7, y=1.1, orientation='h'),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Insights
                if len(effectiveness) > 1:
                    best_range = effectiveness.loc[effectiveness['Conversion Rate'].idxmax(), 'Score Range']
                    best_rate = effectiveness['Conversion Rate'].max()
                    
                    st.success(f"💡 **Insight**: Les prospects dans la plage '{best_range}' ont le meilleur taux de conversion ({best_rate:.1f}%)")
            else:
                st.info("Pas assez de données avec scores pour l'analyse")
        else:
            st.info("📊 Aucune donnée disponible pour l'analyse. Commencez par enregistrer des contacts.")

except ImportError as e:
    st.error(f"⚠️ Module de suivi des conversions non disponible: {e}")
    st.info("""
    Le module conversion_tracker.py existe mais n'a pas pu être importé.
    Vérifiez que le fichier src/conversion_tracker.py est présent.
    """)
