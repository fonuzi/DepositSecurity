import streamlit as st
import plotly.graph_objects as go
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def format_currency(value):
    """Format number in millions with thousand separators"""
    in_millions = value / 1000000
    if in_millions >= 1:
        formatted = "{:,.1f}M".format(in_millions).replace(",", ".")
    else:
        formatted = "{:,.0f}".format(value).replace(",", ".")
    return f"€{formatted}"

def main():
    st.set_page_config(
        page_title="Banking Sector Loss Distribution Model",
        layout="wide"
    )
    
    st.title("Banking Sector Loss Distribution Model")
    
    # Get bank data
    bank_data = DEFAULT_BANKS["Bank A"]
    total_assets = bank_data["total_assets"]
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for each creditor
    for creditor, value in bank_data.items():
        if creditor != "total_assets":
            fig.add_trace(go.Bar(
                name=creditor,
                x=['Bank A'],
                y=[value],
                marker_color=DEFAULT_CREDITORS[creditor]['color'] if creditor in DEFAULT_CREDITORS else '#333',
                text=format_currency(value),
                textposition='inside',
            ))
    
    # Update layout
    fig.update_layout(
        barmode='stack',
        height=600,
        title="Bank Value Distribution",
        yaxis_title="Amount (EUR)",
        showlegend=True,
        legend_title="Creditor Type",
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Display bank values in a table
    st.subheader("Bank Values")
    for creditor, value in bank_data.items():
        if creditor != "total_assets":
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(creditor)
            with col2:
                st.write(format_currency(value))

if __name__ == "__main__":
    main()
