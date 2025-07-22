"""
Main Streamlit dashboard for the OCR Receipt Processor.
This is a simple wrapper that imports the dashboard functionality.
"""

import streamlit as st
import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# Import the comprehensive dashboard
try:
    from dashboard import main as dashboard_main
    dashboard_main()
except ImportError as e:
    st.error(f"Could not import the dashboard module: {e}")
    st.info("Dashboard module not found.")
    
    # Fallback simple dashboard
    st.title("📄 OCR Receipt Processor Dashboard")
    st.markdown("Dashboard is being migrated to the new modular structure.")
    st.info("Please use the original ocr_dashboard.py for now.") 