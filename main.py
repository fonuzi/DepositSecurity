import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import calculate_loss_distribution, reorder_creditors, calculate_total_loss_with_absorption
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def format_currency(value):
    """Format number as currency with thousand separators"""
    return f"€{value:,.2f}"

def render_bank_values():
    st.header("Bank Values")

    # Create DataFrame for bank values display
    data = []
    for bank_name, bank_data in st.session_state.current_bank_data.items():
        row = {}
        row["Bank"] = bank_name
        for k, v in bank_data.items():
            if k != "total_assets":
                row[k] = v
        data.append(row)

    df = pd.DataFrame(data)
    display_df = df.copy()

    # Format all numeric columns
    numeric_cols = [col for col in df.columns if col != "Bank"]
    for col in numeric_cols:
        display_df[col] = df[col].apply(lambda x: format_currency(float(x)))

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

            # Bank selection
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
            st.info("Click and select creditors to reorder")

            # Create a reorderable list using selectbox for each position
            creditor_positions = {}
            available_creditors = list(st.session_state.creditor_order)

            for position in range(len(available_creditors)):
                current_creditor = st.session_state.creditor_order[position]
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Allow selection of creditor for this position
                    selected = st.selectbox(
                        f"Position {position + 1}",
                        options=available_creditors,
                        index=available_creditors.index(current_creditor),
                        key=f"pos_{position}"
                    )
                    creditor_positions[position] = selected

                    # Remove selected creditor from available options
                    if selected in available_creditors:
                        available_creditors.remove(selected)

                with col2:
                    # Exempt checkbox
                    is_exempt = st.checkbox(
                        "Exempt",
                        value=current_creditor in st.session_state.exempt_creditors,
                        key=f"exempt_{current_creditor}"
                    )
                    if is_exempt and current_creditor not in st.session_state.exempt_creditors:
                        st.session_state.exempt_creditors.add(current_creditor)
                    elif not is_exempt and current_creditor in st.session_state.exempt_creditors:
                        st.session_state.exempt_creditors.remove(current_creditor)

            # Update creditor order based on selections
            st.session_state.creditor_order = [creditor_positions[i] for i in range(len(creditor_positions))]

            # Display bank values for editing
            if len(selected_banks) > 0:
                selected_bank = selected_banks[0]
                st.subheader("Bank Values")
                for creditor in st.session_state.creditor_order:
                    value = st.number_input(
                        f"{creditor} Value (EUR)",
                        value=float(st.session_state.current_bank_data[selected_bank][creditor]),
                        key=f"value_{creditor}_{selected_bank}",
                        step=1000000.0,
                        format="%f"
                    )
                    st.session_state.current_bank_data[selected_bank][creditor] = value

        # Main content area for Loss Distribution
        if not selected_banks:
            st.warning("Please select at least one bank to display.")
        else:
            # Calculate loss distribution for each selected bank
            loss_data = {}
            for bank in selected_banks:
                total_assets = st.session_state.current_bank_data[bank]["total_assets"]
                total_loss = calculate_total_loss_with_absorption(total_assets, loss_percentage)

                # Calculate asset absorption amount (8% threshold)
                asset_absorption = min(total_loss, total_assets * 0.08)
                remaining_loss = max(0, total_loss - asset_absorption)

                # Calculate distribution for remaining loss
                creditor_distribution = calculate_loss_distribution(
                    remaining_loss,
                    st.session_state.current_bank_data[bank],
                    DEFAULT_CREDITORS,
                    st.session_state.creditor_order,
                    st.session_state.exempt_creditors
                )

                loss_data[bank] = {
                    "asset_absorption": asset_absorption,
                    "creditor_distribution": creditor_distribution
                }

            # Create visualization
            fig = go.Figure()

            # Add combined bars for each bank
            for bank in selected_banks:
                bank_data = loss_data[bank]

                # Add asset absorption bar
                fig.add_trace(go.Bar(
                    name="Asset Absorption",
                    x=[bank],
                    y=[bank_data["asset_absorption"]],
                    marker_color=DEFAULT_CREDITORS["Asset Absorption"]["color"],
                    text=format_currency(bank_data["asset_absorption"]),
                    textposition='inside',
                ))

                # Add creditor bars
                y_position = bank_data["asset_absorption"]
                for creditor in st.session_state.creditor_order:
                    if creditor in st.session_state.exempt_creditors:
                        continue

                    loss_amount = bank_data["creditor_distribution"][creditor]
                    if loss_amount > 0:
                        fig.add_trace(go.Bar(
                            name=creditor,
                            x=[bank],
                            y=[loss_amount],
                            marker_color=DEFAULT_CREDITORS[creditor]['color'],
                            text=format_currency(loss_amount),
                            textposition='inside',
                        ))
                        y_position += loss_amount

            # Update layout
            fig.update_layout(
                barmode='stack',
                height=600,
                title=f"Loss Distribution Analysis ({loss_percentage}% Loss)",
                yaxis_title="Amount (EUR)",
                showlegend=True,
                legend_title="Creditor Type",
                font=dict(size=12),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Summary statistics
            st.subheader("Summary Statistics")

            for bank in selected_banks:
                st.write(f"### {bank}")
                bank_data = loss_data[bank]
                total_loss = bank_data["asset_absorption"] + sum(bank_data["creditor_distribution"].values())

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric("Total Loss", format_currency(total_loss))

                with col2:
                    st.metric("Asset Absorption", format_currency(bank_data["asset_absorption"]))

                with col3:
                    st.write("Loss Distribution (%)")
                    # Show asset absorption percentage
                    percentage = (bank_data["asset_absorption"] / total_loss) * 100
                    st.progress(percentage / 100)
                    st.write(f"Asset Absorption: {percentage:.1f}%")

                    # Show creditor percentages
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
                        loss_amount = bank_data["creditor_distribution"][creditor]
                        percentage = (loss_amount / total_loss) * 100
                        st.progress(percentage / 100)
                        st.write(f"{creditor}: {percentage:.1f}%")

            # Export functionality
            if st.button("Export Data"):
                export_data = []
                for bank in selected_banks:
                    bank_data = loss_data[bank]
                    total_loss = bank_data["asset_absorption"] + sum(bank_data["creditor_distribution"].values())

                    # Add asset absorption data
                    export_data.append({
                        'Bank': bank,
                        'Type': 'Asset Absorption',
                        'Amount': bank_data["asset_absorption"],
                        'Percentage': (bank_data["asset_absorption"] / total_loss) * 100
                    })

                    # Add creditor distribution data
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue
                        loss_amount = bank_data["creditor_distribution"][creditor]
                        export_data.append({
                            'Bank': bank,
                            'Type': 'Creditor',
                            'Creditor': creditor,
                            'Amount': loss_amount,
                            'Percentage': (loss_amount / total_loss) * 100
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