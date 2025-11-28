import streamlit as st
import pandas as pd
import plotly.express as px

# Load cleaned data
df = pd.read_csv('data/cleaned_prospects.csv')
password = st.text_input("Password", type="password")

if password != "": 
    st.error("Access Denied")
    st.stop()

#Sidebat navigation 
st.sidebar.title("Insurance Dashboard")
page = st.sidebar.radio("page", ["Home", "Trends", "Priority Leads", "Re-Engagement"])

#Sidebar filters
regimes = st.sidebar.multiselect("Regime", df['social_security_regime'].unique(), default=df['social_security_regime'].unique())
villes = st.sidebar.multiselect("Ville", df['city'].unique(), default=df['city'].unique())
coverage_levels = st.sidebar.multiselect("Coverage Level", [1, 2, 3, 4], default=[1, 2, 3, 4])
filtered_df = df[df['social_security_regime'].isin(regimes) & 
                df['city'].isin(villes) & 
                df['medical_care'].isin(coverage_levels)]

st.title("Insurance Prospect Dashboard")

if page == "Home":
    st.write(f"Total Prospects: {len(filtered_df)}")
    fig = px.histogram(filtered_df, x='current_age', nbins=20, title='Current Age Distribution')
    st.plotly_chart(fig)

if page == "Trends":
    fig = px.pie(filtered_df, names='social_security_regime', title='Régime Distribution')
    st.plotly_chart(fig)
    fig = px.histogram(filtered_df, x='medical_care', color='dental', title='Medical vs. Dental Coverage Levels')
    st.plotly_chart(fig)

