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
            margin: 1rem 0;
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
        /* Info message above sortable items */
        [data-testid="stSidebar"] .stAlert {
            background-color: #f5f3ff;
            color: #4338ca;
            border: none;
            padding: 1rem;
            margin-bottom: 1rem;
            width: 100%;
            box-sizing: border-box;
        }
        /* Ensure sidebar maintains width */
        [data-testid="stSidebar"] {
            min-width: 320px;
            max-width: 320px;
        }
        /* Creditor values styling */
        .creditor-value-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .creditor-value-container h3 {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #1f2937;
        }
        .creditor-value-container .number-input {
            width: 100%;
            margin-bottom: 0.25rem;
        }
        .creditor-value-container .formatted-value {
            font-size: 14px;
            color: #4b5563;
            margin-bottom: 0.5rem;
        }
        .creditor-value-container .exempt-checkbox {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)