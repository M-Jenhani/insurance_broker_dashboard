"""
Reusable metric card components
"""
import streamlit as st


def metric_card(title, value, delta=None, delta_color="normal", help_text=None):
    """Display a metric card"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def display_kpi_row(metrics_dict):
    """
    Display a row of KPI metrics
    
    Args:
        metrics_dict: Dict with format {"Title": {"value": val, "delta": delta, "help": help_text}}
    """
    cols = st.columns(len(metrics_dict))
    
    for col, (title, data) in zip(cols, metrics_dict.items()):
        with col:
            metric_card(
                title=title,
                value=data.get('value'),
                delta=data.get('delta'),
                delta_color=data.get('delta_color', 'normal'),
                help_text=data.get('help')
            )
