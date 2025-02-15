import streamlit as st

def apply_styles():
    """
    Apply custom CSS styles to the Streamlit app
    """
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #0066cc;
        }
        .stSelectbox {
            margin-bottom: 1rem;
        }
        .stNumberInput {
            margin-bottom: 1rem;
        }
        .st-emotion-cache-1y4p8pa {
            max-width: 100%;
        }
        .st-emotion-cache-16idsys p {
            font-size: 14px;
            margin-bottom: 0.5rem;
        }
        /* Creditor hierarchy styling */
        [data-testid="stSidebar"] .element-container:has(.streamlit-sortables) {
            background-color: #f5f3ff;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .streamlit-sortables > div {
            background-color: #4338ca !important;
            color: white !important;
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 6px !important;
            cursor: move !important;
            font-size: 14px !important;
            border: none !important;
        }
        /* Info message style */
        [data-testid="stSidebar"] .stAlert {
            background-color: #f5f3ff;
            color: #4338ca;
            border: none;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)