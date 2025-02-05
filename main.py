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

    # Initialize session state for creditor order if not exists
    if 'creditor_order' not in st.session_state:
        st.session_state.creditor_order = list(DEFAULT_CREDITORS.keys())

    # Initialize bank data in session state if not exists
    if 'current_bank_data' not in st.session_state:
        st.session_state.current_bank_data = DEFAULT_BANKS.copy()

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
        st.info("Use the buttons to reorder creditors and adjust values")

        # Display creditors with up/down buttons and value inputs
        for idx, creditor in enumerate(st.session_state.creditor_order):
            st.write(f"### {idx + 1}. {creditor}")

            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

            # Value input
            with col1:
                st.session_state.current_bank_data[selected_bank][creditor] = st.number_input(
                    "Value (EUR)",
                    value=float(DEFAULT_BANKS[selected_bank][creditor]),
                    key=f"value_{creditor}",
                    step=1000000.0,
                    format="%f",
                    label_visibility="collapsed"
                )

            # Up button
            with col2:
                if idx > 0:  # Can move up
                    if st.button("↑", key=f"up_{creditor}"):
                        st.session_state.creditor_order = reorder_creditors(
                            st.session_state.creditor_order,
                            creditor,
                            idx - 1
                        )
                        st.rerun()

            # Down button
            with col3:
                if idx < len(st.session_state.creditor_order) - 1:  # Can move down
                    if st.button("↓", key=f"down_{creditor}"):
                        st.session_state.creditor_order = reorder_creditors(
                            st.session_state.creditor_order,
                            creditor,
                            idx + 1
                        )
                        st.rerun()

            # Reset value button
            with col4:
                if st.button("Reset", key=f"reset_{creditor}"):
                    st.session_state.current_bank_data[selected_bank][creditor] = DEFAULT_BANKS[selected_bank][creditor]
                    st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Calculate loss distribution
        loss_data = calculate_loss_distribution(
            total_loss,
            st.session_state.current_bank_data[selected_bank],
            DEFAULT_CREDITORS,
            st.session_state.creditor_order
        )

        # Create stacked bar chart
        fig = go.Figure()

        # Add bars for each creditor
        y_position = 0
        for creditor in st.session_state.creditor_order:
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
        for creditor in st.session_state.creditor_order:
            percentage = (loss_data[creditor] / total_loss) * 100
            st.progress(percentage / 100)
            st.write(f"{creditor}: {percentage:.1f}%")

    # Export functionality
    if st.button("Export Data"):
        df = pd.DataFrame({
            'Creditor': st.session_state.creditor_order,
            'Loss Amount': [loss_data[creditor] for creditor in st.session_state.creditor_order],
            'Percentage': [(loss_data[creditor] / total_loss) * 100 for creditor in st.session_state.creditor_order]
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