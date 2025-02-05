import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import calculate_loss_distribution, reorder_creditors
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def render_bank_values():
    st.header("Bank Management")

    # Add new bank
    col1, col2 = st.columns([3, 1])
    with col1:
        new_bank_name = st.text_input("New Bank Name")
    with col2:
        if st.button("Add Bank") and new_bank_name and new_bank_name not in st.session_state.current_bank_data:
            # Initialize with default values scaled to 50% of Bank A
            st.session_state.current_bank_data[new_bank_name] = {
                "total_assets": DEFAULT_BANKS["Bank A"]["total_assets"] * 0.5,
                **{creditor: DEFAULT_BANKS["Bank A"][creditor] * 0.5 
                   for creditor in DEFAULT_CREDITORS.keys()}
            }
            st.success(f"Added {new_bank_name}")
            st.rerun()

    # Remove bank
    col1, col2 = st.columns([3, 1])
    with col1:
        bank_to_remove = st.selectbox(
            "Select Bank to Remove",
            options=[b for b in st.session_state.current_bank_data.keys() if b != "Bank A"],
            key="remove_bank_selector"
        )
    with col2:
        if bank_to_remove and st.button("Remove Bank"):
            del st.session_state.current_bank_data[bank_to_remove]
            st.success(f"Removed {bank_to_remove}")
            st.rerun()

    # Display bank values
    st.header("Bank Values")

    # Create DataFrame for bank values display
    data = []
    for bank_name, bank_data in st.session_state.current_bank_data.items():
        row = {}
        row["Bank"] = bank_name
        for k, v in bank_data.items():
            if k != "total_assets":
                row[k] = v  # Keep as numeric value
        data.append(row)

    df = pd.DataFrame(data)
    display_df = df.copy()

    # Format all numeric columns
    numeric_cols = [col for col in df.columns if col != "Bank"]
    for col in numeric_cols:
        display_df[col] = df[col].apply(lambda x: "{:,.2f}".format(float(x)))

    st.dataframe(display_df, use_container_width=True)

def main():
    # Apply custom styles
    apply_styles()

    st.title("Banking Sector Loss Distribution Model")

    # Initialize session states
    if 'creditor_order' not in st.session_state:
        st.session_state.creditor_order = list(DEFAULT_CREDITORS.keys())
    if 'current_bank_data' not in st.session_state:
        st.session_state.current_bank_data = DEFAULT_BANKS.copy()

    # Create tabs
    tab1, tab2 = st.tabs(["Loss Distribution", "Bank Values"])

    with tab1:
        # Sidebar for controls
        with st.sidebar:
            st.header("Configuration")

            # Bank selection (multiple)
            selected_banks = st.multiselect(
                "Select Banks to Compare",
                options=list(st.session_state.current_bank_data.keys()),
                default=[list(st.session_state.current_bank_data.keys())[0]],
                key="bank_selector"
            )

            # Total loss input (percentage of total assets)
            loss_percentage = st.slider(
                "Loss Percentage of Total Assets",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=1.0
            )

            # Creditor hierarchy management
            st.subheader("Creditor Hierarchy")
            st.info("Use the buttons to reorder creditors and adjust values")

            # Display creditors with up/down buttons and value inputs
            for idx, creditor in enumerate(st.session_state.creditor_order):
                st.write(f"### {idx + 1}. {creditor}")

                # Display current selected bank's value
                if len(selected_banks) > 0:
                    selected_bank = selected_banks[0]  # Use first selected bank for editing
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

                    # Value input
                    with col1:
                        st.session_state.current_bank_data[selected_bank][creditor] = st.number_input(
                            "Value (EUR)",
                            value=float(st.session_state.current_bank_data[selected_bank][creditor]),
                            key=f"value_{creditor}_{selected_bank}",
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
                        if st.button("Reset", key=f"reset_{creditor}_{selected_bank}"):
                            st.session_state.current_bank_data[selected_bank][creditor] = DEFAULT_BANKS[selected_bank][creditor]
                            st.rerun()

        # Main content area for Loss Distribution
        if not selected_banks:
            st.warning("Please select at least one bank to display.")
        else:
            # Calculate loss distribution for each selected bank
            all_loss_data = {}
            for bank in selected_banks:
                total_loss = st.session_state.current_bank_data[bank]["total_assets"] * (loss_percentage / 100)
                all_loss_data[bank] = calculate_loss_distribution(
                    total_loss,
                    st.session_state.current_bank_data[bank],
                    DEFAULT_CREDITORS,
                    st.session_state.creditor_order
                )

            # Create stacked bar chart
            fig = go.Figure()

            # Add bars for each bank and creditor
            for bank in selected_banks:
                loss_data = all_loss_data[bank]
                bank_total = sum(loss_data.values())

                for creditor in st.session_state.creditor_order:
                    loss_amount = loss_data[creditor]
                    fig.add_trace(go.Bar(
                        name=creditor,
                        x=[bank],
                        y=[loss_amount],
                        marker_color=DEFAULT_CREDITORS[creditor]['color'],
                        text=f'€{loss_amount:,.0f}',
                        textposition='inside',
                    ))

            # Update layout
            fig.update_layout(
                barmode='stack',
                height=600,
                title=f"Loss Distribution by Creditor Hierarchy ({loss_percentage}% Loss)",
                yaxis_title="Loss Amount (EUR)",
                xaxis_title="Banks",
                showlegend=True,
                legend_title="Creditor Type",
                font=dict(size=12),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Summary statistics for each selected bank
            st.subheader("Summary Statistics")

            for bank in selected_banks:
                st.write(f"### {bank}")
                total_loss = st.session_state.current_bank_data[bank]["total_assets"] * (loss_percentage / 100)
                loss_data = all_loss_data[bank]

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Total Loss", f"€{total_loss:,.2f}")

                with col2:
                    for creditor in st.session_state.creditor_order:
                        percentage = (loss_data[creditor] / total_loss) * 100
                        st.progress(percentage / 100)
                        st.write(f"{creditor}: {percentage:.1f}%")

            # Export functionality
            if st.button("Export Data"):
                export_data = []
                for bank in selected_banks:
                    loss_data = all_loss_data[bank]
                    total_loss = st.session_state.current_bank_data[bank]["total_assets"] * (loss_percentage / 100)
                    for creditor in st.session_state.creditor_order:
                        export_data.append({
                            'Bank': bank,
                            'Creditor': creditor,
                            'Loss Amount': loss_data[creditor],
                            'Percentage': (loss_data[creditor] / total_loss) * 100
                        })

                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="loss_distribution.csv",
                    mime="text/csv"
                )

    with tab2:
        render_bank_values()

if __name__ == "__main__":
    main()