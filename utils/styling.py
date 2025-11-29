"""
Styling utilities
"""
import streamlit as st


def load_custom_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .high-priority {
            background-color: #ffebee;
            border-left-color: #d32f2f;
        }
        .success-card {
            background-color: #e8f5e9;
            border-left-color: #4caf50;
        }
    </style>
    """, unsafe_allow_html=True)
