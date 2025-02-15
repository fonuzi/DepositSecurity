import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        st.session_state.creditor_order = [c for c in DEFAULT_CREDITORS.keys() if c != "Asset Absorption"]
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
            st.info("Use the buttons to reorder creditors")

            # Display creditors with up/down buttons, value inputs, and exempt checkbox
            for idx, creditor in enumerate(st.session_state.creditor_order):
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])

                with col1:
                    st.write(f"### {idx + 1}. {creditor}")

                # Value input
                if len(selected_banks) > 0:
                    selected_bank = selected_banks[0]  # Use first selected bank for editing

                    # Value input
                    with col2:
                        st.session_state.current_bank_data[selected_bank][creditor] = st.number_input(
                            "Value (EUR)",
                            value=float(st.session_state.current_bank_data[selected_bank][creditor]),
                            key=f"value_{creditor}_{selected_bank}",
                            step=1000000.0,
                            format="%f",
                            label_visibility="collapsed"
                        )

                    # Up button
                    with col3:
                        if idx > 0:  # Can move up
                            if st.button("↑", key=f"up_{creditor}"):
                                st.session_state.creditor_order = reorder_creditors(
                                    st.session_state.creditor_order,
                                    creditor,
                                    idx - 1
                                )
                                st.rerun()

                    # Down button
                    with col4:
                        if idx < len(st.session_state.creditor_order) - 1:  # Can move down
                            if st.button("↓", key=f"down_{creditor}"):
                                st.session_state.creditor_order = reorder_creditors(
                                    st.session_state.creditor_order,
                                    creditor,
                                    idx + 1
                                )
                                st.rerun()

                    # Exempt checkbox
                    with col5:
                        is_exempt = st.checkbox(
                            "Exempt",
                            value=creditor in st.session_state.exempt_creditors,
                            key=f"exempt_{creditor}"
                        )
                        if is_exempt and creditor not in st.session_state.exempt_creditors:
                            st.session_state.exempt_creditors.add(creditor)
                        elif not is_exempt and creditor in st.session_state.exempt_creditors:
                            st.session_state.exempt_creditors.remove(creditor)

        # Main content area for Loss Distribution
        if not selected_banks:
            st.warning("Please select at least one bank to display.")
        else:
            # Calculate loss distribution for each selected bank
            all_loss_data = {}
            asset_absorption_data = {}
            for bank in selected_banks:
                total_loss = calculate_total_loss_with_absorption(
                    st.session_state.current_bank_data[bank]["total_assets"],
                    loss_percentage
                )
                # Calculate asset absorption (8% of total assets)
                asset_absorption = min(total_loss, st.session_state.current_bank_data[bank]["Asset Absorption"])
                asset_absorption_data[bank] = asset_absorption

                # Calculate remaining loss distribution
                remaining_loss = max(0, total_loss - asset_absorption)
                all_loss_data[bank] = calculate_loss_distribution(
                    remaining_loss,
                    st.session_state.current_bank_data[bank],
                    DEFAULT_CREDITORS,
                    st.session_state.creditor_order,
                    st.session_state.exempt_creditors
                )

            # Create subplot with two rows
            fig = make_subplots(
                rows=2, 
                cols=1,
                subplot_titles=("Asset Absorption", "Loss Distribution by Creditor"),
                row_heights=[0.3, 0.7],
                vertical_spacing=0.1
            )

            # Add asset absorption bars
            for bank in selected_banks:
                fig.add_trace(
                    go.Bar(
                        name="Asset Absorption",
                        x=[bank],
                        y=[asset_absorption_data[bank]],
                        marker_color=DEFAULT_CREDITORS["Asset Absorption"]["color"],
                        text=f'€{asset_absorption_data[bank]:,.0f}',
                        textposition='inside',
                        showlegend=False
                    ),
                    row=1, col=1
                )

            # Add creditor loss distribution bars
            for bank in selected_banks:
                loss_data = all_loss_data[bank]
                for creditor in st.session_state.creditor_order:
                    if creditor in st.session_state.exempt_creditors:
                        continue

                    loss_amount = loss_data[creditor]
                    fig.add_trace(
                        go.Bar(
                            name=creditor,
                            x=[bank],
                            y=[loss_amount],
                            marker_color=DEFAULT_CREDITORS[creditor]['color'],
                            text=f'€{loss_amount:,.0f}',
                            textposition='inside',
                        ),
                        row=2, col=1
                    )

            # Update layout
            fig.update_layout(
                height=800,
                title=f"Loss Distribution Analysis ({loss_percentage}% Loss)",
                showlegend=True,
                legend_title="Creditor Type",
                font=dict(size=12),
                barmode='stack'
            )

            # Update y-axis labels
            fig.update_yaxes(title_text="Amount (EUR)", row=1, col=1)
            fig.update_yaxes(title_text="Amount (EUR)", row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # Summary statistics for each selected bank
            st.subheader("Summary Statistics")

            for bank in selected_banks:
                st.write(f"### {bank}")
                total_loss = calculate_total_loss_with_absorption(
                    st.session_state.current_bank_data[bank]["total_assets"],
                    loss_percentage
                )

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric("Total Loss", f"€{total_loss:,.2f}")

                with col2:
                    st.metric("Asset Absorption", f"€{asset_absorption_data[bank]:,.2f}")

                with col3:
                    st.write("Loss Distribution (%)")
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
                        percentage = (all_loss_data[bank][creditor] / total_loss) * 100
                        st.progress(percentage / 100)
                        st.write(f"{creditor}: {percentage:.1f}%")

            # Export functionality
            if st.button("Export Data"):
                export_data = []
                for bank in selected_banks:
                    total_loss = calculate_total_loss_with_absorption(
                        st.session_state.current_bank_data[bank]["total_assets"],
                        loss_percentage
                    )

                    # Add asset absorption data
                    export_data.append({
                        'Bank': bank,
                        'Type': 'Asset Absorption',
                        'Amount': asset_absorption_data[bank],
                        'Percentage': (asset_absorption_data[bank] / total_loss) * 100
                    })

                    # Add creditor loss data
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
                        export_data.append({
                            'Bank': bank,
                            'Type': 'Creditor',
                            'Creditor': creditor,
                            'Amount': all_loss_data[bank][creditor],
                            'Percentage': (all_loss_data[bank][creditor] / total_loss) * 100
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