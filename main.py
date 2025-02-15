import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import calculate_loss_distribution, reorder_creditors, calculate_total_loss_with_absorption
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def render_bank_values():
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
    if 'exempt_creditors' not in st.session_state:
        st.session_state.exempt_creditors = set()

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

            # Exempt creditors section
            st.subheader("Exempt Creditors")
            st.info("Select creditors to exempt from loss distribution")

            # Create exempt checkboxes for all creditors except Asset Absorption
            for creditor in [c for c in st.session_state.creditor_order if not DEFAULT_CREDITORS.get(c, {}).get('system', False)]:
                is_exempt = st.checkbox(
                    f"Exempt {creditor}",
                    value=creditor in st.session_state.exempt_creditors,
                    key=f"exempt_{creditor}"
                )
                if is_exempt and creditor not in st.session_state.exempt_creditors:
                    st.session_state.exempt_creditors.add(creditor)
                elif not is_exempt and creditor in st.session_state.exempt_creditors:
                    st.session_state.exempt_creditors.remove(creditor)

            st.markdown("---")

            # Display creditors with up/down buttons and value inputs
            for idx, creditor in enumerate(st.session_state.creditor_order):
                st.write(f"### {idx + 1}. {creditor}")

                # Don't allow editing system creditors like Asset Absorption
                if DEFAULT_CREDITORS.get(creditor, {}).get('system', False):
                    st.info(f"Fixed at {DEFAULT_CREDITORS[creditor]['fixed_percentage']}% of total assets")
                    continue

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

                    # Up button (not for Asset Absorption)
                    with col2:
                        if idx > 1:  # Can move up (but not above Asset Absorption)
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
                total_loss = calculate_total_loss_with_absorption(
                    st.session_state.current_bank_data[bank]["total_assets"],
                    loss_percentage
                )
                all_loss_data[bank] = calculate_loss_distribution(
                    total_loss,
                    st.session_state.current_bank_data[bank],
                    DEFAULT_CREDITORS,
                    st.session_state.creditor_order,
                    st.session_state.exempt_creditors
                )

            # Create stacked bar chart
            fig = go.Figure()

            # Add bars for each bank and creditor
            for bank in selected_banks:
                loss_data = all_loss_data[bank]
                bank_total = sum(loss_data.values())

                for creditor in st.session_state.creditor_order:
                    if creditor in st.session_state.exempt_creditors:
                        continue

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
                total_loss = calculate_total_loss_with_absorption(
                    st.session_state.current_bank_data[bank]["total_assets"],
                    loss_percentage
                )
                loss_data = all_loss_data[bank]

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Total Loss", f"€{total_loss:,.2f}")

                with col2:
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
                        percentage = (loss_data[creditor] / total_loss) * 100
                        st.progress(percentage / 100)
                        st.write(f"{creditor}: {percentage:.1f}%")

            # Export functionality
            if st.button("Export Data"):
                export_data = []
                for bank in selected_banks:
                    loss_data = all_loss_data[bank]
                    total_loss = calculate_total_loss_with_absorption(
                        st.session_state.current_bank_data[bank]["total_assets"],
                        loss_percentage
                    )
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
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