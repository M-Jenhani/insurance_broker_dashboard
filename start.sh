#!/bin/bash
# Render start script for Streamlit

pip install -r Requirements.txt
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
