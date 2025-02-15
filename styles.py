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
            margin-bottom: 0.5rem;
        }
        .st-emotion-cache-1y4p8pa {
            max-width: 100%;
        }
        .st-emotion-cache-16idsys p {
            font-size: 14px;
            margin-bottom: 0.5rem;
        }
        /* Creditor hierarchy container */
        [data-testid="stSidebar"] .element-container:has(.streamlit-sortables) {
            background-color: #f5f3ff;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0; /* Changed from 1rem */
            width: 100%;
            box-sizing: border-box;
        }
        /* Fixed-width container for sortable items */
        .streamlit-sortables {
            width: 100%;
            box-sizing: border-box;
        }
        /* Individual sortable items */
        .streamlit-sortables > div {
            background-color: #4338ca !important;
            color: white !important;
            padding: 0.75rem 1rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 6px !important;
            cursor: move !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            border: none !important;
            width: 100% !important;
            box-sizing: border-box !important;
            display: block !important;
            text-align: left !important;
            transition: none !important;
        }
        /* Ensure sidebar maintains width */
        [data-testid="stSidebar"] {
            min-width: 320px;
            max-width: 320px;
        }
        /* Creditor values styling */
        .creditor-name {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #1f2937;
        }
        .formatted-value {
            font-size: 14px;
            color: #4b5563;
            margin-bottom: 0.25rem; /* Changed from 0.5rem */
            display: block;
        }
        /* Checkbox styling */
        .stCheckbox {
            margin-top: 0;
            margin-bottom: 0.5rem;
        }
        /* Fix checkbox alignment */
        .stCheckbox > div[data-testid="stMarkdownContainer"] {
            display: inline-block;
            margin-left: 0.5rem;
        }
        /* Force horizontal layout for checkbox and label */
        .stCheckbox > label {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }
        .stCheckbox > label > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Creditor divider line */
        .creditor-divider {
            border: 0;
            height: 1px;
            background-color: #e5e7eb;
            margin: 0.5rem 0; /* Changed from 1rem */
        }
        </style>
    """, unsafe_allow_html=True)