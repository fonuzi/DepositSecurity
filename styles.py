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
        /* Ensure sidebar maintains width */
        [data-testid="stSidebar"] {
            min-width: 320px;
            max-width: 320px;
        }
        /* Creditor name */
        .creditor-name {
            font-size: 14px;
            font-weight: 500;
            color: #262730;
            margin-bottom: 0.5rem;
        }
        /* Number input styling */
        div[data-testid="stNumberInput"] {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
        }
        div[data-testid="stNumberInput"] input {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            text-align: right;
            font-size: 14px;
        }
        div[data-testid="stNumberInput"] button {
            width: 28px;
            height: 28px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            font-size: 16px;
            color: #374151;
        }
        /* Formatted value */
        .formatted-value {
            font-size: 14px;
            color: #6b7280;
            margin-top: 0.25rem;
            margin-bottom: 0.5rem;
        }
        /* Exempt container */
        .exempt-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.25rem 0;
        }
        /* Checkbox styling */
        .stCheckbox {
            margin: 0;
        }
        .stCheckbox label {
            font-size: 14px;
            color: #374151;
        }
        .stCheckbox > div[data-testid="stMarkdownContainer"] {
            display: inline-block;
            margin-left: 0.5rem;
        }
        /* Info icon */
        .info-icon {
            color: #6b7280;
            cursor: help;
            font-size: 14px;
            margin-left: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)