import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import calculate_loss_distribution, reorder_creditors
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def render_bank_management():
    st.header("Bank Management")

    # Add new bank
    st.subheader("Add New Bank")
    new_bank_name = st.text_input("Bank Name")

    if new_bank_name and new_bank_name not in st.session_state.current_bank_data:
        if st.button("Add Bank"):
            # Initialize with default values scaled to 50% of Bank A
            st.session_state.current_bank_data[new_bank_name] = {
                "total_assets": DEFAULT_BANKS["Bank A"]["total_assets"] * 0.5,
                **{creditor: DEFAULT_BANKS["Bank A"][creditor] * 0.5 
                   for creditor in DEFAULT_CREDITORS.keys()}
            }
            st.success(f"Added {new_bank_name}")
            st.rerun()

    # Remove existing bank
    st.subheader("Remove Bank")
    bank_to_remove = st.selectbox("Select Bank to Remove", 
                                options=[b for b in st.session_state.current_bank_data.keys()
                                       if b != "Bank A"])  # Prevent removing Bank A

    if bank_to_remove and st.button("Remove Bank"):
        del st.session_state.current_bank_data[bank_to_remove]
        st.success(f"Removed {bank_to_remove}")
        st.rerun()

def render_bank_values():
    st.header("Bank Values")

    # Create a DataFrame for better display
    data = []
    for bank_name, bank_data in st.session_state.current_bank_data.items():
        row = {"Bank": bank_name}
        row.update({k: v for k, v in bank_data.items() if k != "total_assets"})
        data.append(row)

    df = pd.DataFrame(data)

    # Display as table with formatting
    st.dataframe(
        df.style.format("{:,.2f}").set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f6')]},
            {'selector': 'td', 'props': [('text-align', 'right')]}
        ]),
        use_container_width=True
    )

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
    tab1, tab2, tab3 = st.tabs(["Loss Distribution", "Bank Values", "Bank Management"])

    with tab1:
        # Sidebar for controls
        with st.sidebar:
            st.header("Configuration")

            # Bank selection
            selected_bank = st.selectbox(
                "Select Bank",
                options=st.session_state.current_bank_data.keys(),
                key="bank_selector"
            )

            # Total loss input
            total_loss = st.number_input(
                "Total Loss (EUR)",
                min_value=0.0,
                value=st.session_state.current_bank_data[selected_bank]["total_assets"] * 0.1,
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

    with tab2:
        render_bank_values()

    with tab3:
        render_bank_management()

if __name__ == "__main__":
    main()