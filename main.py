import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import calculate_loss_distribution, reorder_creditors
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def main():
    # Apply custom styles
    apply_styles()
    
    st.title("Banking Sector Loss Distribution Model")
    st.subheader("Creditor Hierarchy Analysis Tool")

    # Sidebar for controls
    with st.sidebar:
        st.header("Configuration")
        
        # Bank selection
        selected_bank = st.selectbox(
            "Select Bank",
            options=DEFAULT_BANKS.keys(),
            key="bank_selector"
        )

        # Total loss input
        total_loss = st.number_input(
            "Total Loss (EUR)",
            min_value=0.0,
            value=DEFAULT_BANKS[selected_bank]["total_assets"] * 0.1,
            step=1000000.0,
            format="%f"
        )

        # Creditor hierarchy management
        st.subheader("Creditor Hierarchy")
        st.info("Drag and drop to reorder creditors")
        
        creditor_order = st.session_state.get('creditor_order', list(DEFAULT_CREDITORS.keys()))
        new_order = st.multiselect(
            "Adjust Creditor Order",
            options=creditor_order,
            default=creditor_order,
            key="creditor_order"
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Calculate loss distribution
        loss_data = calculate_loss_distribution(
            total_loss,
            DEFAULT_BANKS[selected_bank],
            DEFAULT_CREDITORS,
            new_order
        )

        # Create stacked bar chart
        fig = go.Figure()
        
        # Add bars for each creditor
        y_position = 0
        for creditor in new_order:
            loss_amount = loss_data[creditor]
            fig.add_trace(go.Bar(
                name=creditor,
                y=[loss_amount],
                x=['Loss Distribution'],
                marker_color=DEFAULT_CREDITORS[creditor]['color'],
                text=f'€{loss_amount:,.0f}',
                textposition='inside',
            ))
            y_position += loss_amount

        # Update layout
        fig.update_layout(
            barmode='stack',
            height=600,
            title="Loss Distribution by Creditor Hierarchy",
            yaxis_title="Loss Amount (EUR)",
            showlegend=True,
            legend_title="Creditor Type",
            font=dict(size=12),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Summary statistics
        st.subheader("Summary Statistics")
        
        # Display total loss
        st.metric("Total Loss", f"€{total_loss:,.2f}")
        
        # Display loss percentages
        st.write("Loss Distribution (%)")
        for creditor in new_order:
            percentage = (loss_data[creditor] / total_loss) * 100
            st.progress(percentage / 100)
            st.write(f"{creditor}: {percentage:.1f}%")

    # Export functionality
    if st.button("Export Data"):
        df = pd.DataFrame({
            'Creditor': new_order,
            'Loss Amount': [loss_data[creditor] for creditor in new_order],
            'Percentage': [(loss_data[creditor] / total_loss) * 100 for creditor in new_order]
        })
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="loss_distribution.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
