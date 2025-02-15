import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from streamlit_sortables import sort_items
from utils import calculate_loss_distribution, reorder_creditors, calculate_total_loss_with_absorption
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def format_currency(value):
    """Format number in millions with thousand separators using dots"""
    in_millions = value / 1000000
    if in_millions >= 1:
        formatted = "{:,.1f}M".format(in_millions).replace(",", ".")
    else:
        formatted = "{:,.0f}".format(value).replace(",", ".")
    return f"€{formatted}"

def render_bank_values():
    st.header("Bank Values")
    data = []
    bank_data = st.session_state.current_bank_data["Bank A"]  # Use single bank
    row = {}
    row["Bank"] = "Bank A"
    for k, v in bank_data.items():
        if k != "total_assets":
            row[k] = v
    data.append(row)

    df = pd.DataFrame(data)
    display_df = df.copy()
    numeric_cols = [col for col in df.columns if col != "Bank"]
    for col in numeric_cols:
        display_df[col] = df[col].apply(lambda x: format_currency(float(x)))

    st.dataframe(display_df, use_container_width=True)

def calculate_scenario_values(total_assets, scenario):
    """Calculate asset and liability values based on selected scenario"""
    if scenario == "FOLTF":
        liability_percentage = 0.20  # 20% of assets moved to liabilities
    elif scenario == "Resolution Valuation":
        liability_percentage = 0.30  # 30% of assets moved to liabilities
    elif scenario == "Liquidation Valuation":
        liability_percentage = 0.40  # 40% of assets moved to liabilities
    else:
        liability_percentage = 0.0  # Default case

    # Calculate values while maintaining total
    liability_value = total_assets * liability_percentage
    asset_value = total_assets - liability_value
    return asset_value, liability_value

def main():
    apply_styles()
    st.title("Banking Sector Loss Distribution Model")

    # Initialize session states
    if 'creditor_order' not in st.session_state:
        st.session_state.creditor_order = [c for c in DEFAULT_CREDITORS.keys() if c != "Asset Absorption"]
    if 'current_bank_data' not in st.session_state:
        st.session_state.current_bank_data = {"Bank A": DEFAULT_BANKS["Bank A"].copy()}
    if 'exempt_creditors' not in st.session_state:
        st.session_state.exempt_creditors = set()
    if 'graph_explanations' not in st.session_state:
        st.session_state.graph_explanations = {}
    if 'creditor_names' not in st.session_state:
        st.session_state.creditor_names = {c: c for c in DEFAULT_CREDITORS.keys()}

    tab1, tab2 = st.tabs(["Loss Distribution", "Bank Values"])

    with tab1:
        with st.sidebar:
            st.header("Configuration")

            # Scenario selection
            scenario = st.radio(
                "Select Scenario",
                options=["Default", "FOLTF", "Resolution Valuation", "Liquidation Valuation"],
                help="""
                FOLTF: Redistributes 20% of assets to liabilities
                Resolution Valuation: Redistributes 30% of assets to liabilities
                Liquidation Valuation: Redistributes 40% of assets to liabilities
                Default: No redistribution applied
                """
            )

            # Loss percentage slider - disabled for non-default scenarios
            if scenario == "Default":
                loss_percentage = st.slider(
                    "Loss Percentage of Total Assets",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0
                )
            else:
                # Display disabled slider with fixed value for non-default scenarios
                st.slider(
                    "Loss Percentage of Total Assets",
                    min_value=0.0,
                    max_value=100.0,
                    value=20.0,  # Fixed value for scenarios
                    step=1.0,
                    disabled=True,
                    help="Loss percentage is fixed in scenario mode"
                )
                loss_percentage = 20.0  # Use fixed value for scenarios

            # Creditor hierarchy section
            st.subheader("Creditor Hierarchy")
            with st.container():
                st.markdown("""
                    <div style='background-color: #f5f3ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                        Drag and drop creditors to reorder
                    </div>
                """, unsafe_allow_html=True)

                sorted_creditors = sort_items(
                    [st.session_state.creditor_names[c] for c in st.session_state.creditor_order]
                )

                # Update order if changed
                if sorted_creditors != [st.session_state.creditor_names[c] for c in st.session_state.creditor_order]:
                    name_to_key = {v: k for k, v in st.session_state.creditor_names.items()}
                    st.session_state.creditor_order = [name_to_key[name] for name in sorted_creditors]
                    st.rerun()

            # Display creditor values and exempt checkboxes
            bank = "Bank A"  # Use single bank
            st.subheader("Creditor Values")

            for creditor in st.session_state.creditor_order:
                # Editable creditor name
                new_name = st.text_input(
                    "Name",
                    value=st.session_state.creditor_names[creditor],
                    key=f"name_{creditor}",
                    label_visibility="collapsed"
                )
                st.session_state.creditor_names[creditor] = new_name

                # Value input
                value = st.number_input(
                    "Value (EUR)",
                    value=float(st.session_state.current_bank_data[bank][creditor]),
                    key=f"value_{creditor}_{bank}",
                    step=1000000.0,
                    format="%f",
                    label_visibility="collapsed"
                )
                st.markdown(f'<p class="formatted-value">{format_currency(value)}</p>', unsafe_allow_html=True)
                st.session_state.current_bank_data[bank][creditor] = value

                # Exempt checkbox
                is_exempt = st.checkbox(
                    "Exempt",
                    value=creditor in st.session_state.exempt_creditors,
                    key=f"exempt_{creditor}",
                    help="Exclude this creditor from loss absorption"
                )
                if is_exempt and creditor not in st.session_state.exempt_creditors:
                    st.session_state.exempt_creditors.add(creditor)
                elif not is_exempt and creditor in st.session_state.exempt_creditors:
                    st.session_state.exempt_creditors.remove(creditor)

                if creditor != st.session_state.creditor_order[-1]:
                    st.markdown('<hr class="creditor-divider">', unsafe_allow_html=True)

        # Main content area for Loss Distribution
        bank = "Bank A"  # Use single bank
        st.subheader(f"Loss Distribution Analysis")

        col1, col2 = st.columns([2, 1])

        with col1:
            total_assets = st.session_state.current_bank_data[bank]["total_assets"]
            total_loss = calculate_total_loss_with_absorption(total_assets, loss_percentage)

            # Calculate scenario-based values
            asset_value, liability_value = calculate_scenario_values(total_assets, scenario)

            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("", ""),
                column_widths=[0.4, 0.6],
                horizontal_spacing=0.1
            )

            # Update asset visualization based on scenario
            remaining_asset_value = max(0, asset_value - total_loss)
            loss_absorbed = min(total_loss, asset_value * 0.08)  # 8% of scenario assets
            remaining_loss = max(0, total_loss - loss_absorbed)

            fig.add_trace(
                go.Bar(
                    name="Remaining Assets",
                    x=[""],
                    y=[remaining_asset_value],
                    marker_color="#2ecc71",
                    text=format_currency(remaining_asset_value),
                    textposition='inside',
                ),
                row=1, col=1
            )

            if loss_absorbed > 0:
                fig.add_trace(
                    go.Bar(
                        name="8% Loss Absorption",
                        x=[""],
                        y=[loss_absorbed],
                        marker_color="#e74c3c",
                        text=format_currency(loss_absorbed),
                        textposition='inside',
                    ),
                    row=1, col=1
                )

            creditor_distribution = calculate_loss_distribution(
                remaining_loss,
                st.session_state.current_bank_data[bank],
                DEFAULT_CREDITORS,
                st.session_state.creditor_order,
                st.session_state.exempt_creditors
            )

            for creditor in st.session_state.creditor_order:
                if creditor in st.session_state.exempt_creditors:
                    continue

                loss_amount = creditor_distribution[creditor]
                if loss_amount > 0:
                    fig.add_trace(
                        go.Bar(
                            name=st.session_state.creditor_names[creditor],
                            x=[""],
                            y=[loss_amount],
                            marker_color=DEFAULT_CREDITORS[creditor]['color'],
                            text=format_currency(loss_amount),
                            textposition='inside',
                        ),
                        row=1, col=2
                    )

            fig.update_layout(
                height=600,
                showlegend=True,
                barmode='stack',
                title=f"Loss Distribution Analysis ({loss_percentage}% Loss)",
                legend_title="Components",
            )

            fig.update_xaxes(showticklabels=True)
            fig.update_yaxes(
                title_text="Amount (EUR)",
                tickformat=",.0f",
                tickprefix="",
                ticksuffix="M",
                tickvals=[i * 1000000 for i in range(0, int(total_assets/1000000) + 1, 100)],
                ticktext=[f"{i}M" for i in range(0, int(total_assets/1000000) + 1, 100)],
                col=1
            )
            fig.update_yaxes(
                title_text="",
                showticklabels=False,
                tickformat=",.0f",
                tickprefix="",
                ticksuffix="M",
                tickvals=[i * 1000000 for i in range(0, int(total_assets/1000000) + 1, 100)],
                ticktext=[f"{i}M" for i in range(0, int(total_assets/1000000) + 1, 100)],
                col=2
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Graph Explanation")
            if bank not in st.session_state.graph_explanations:
                st.session_state.graph_explanations[bank] = ""

            explanation = st.text_area(
                "Add your explanation here",
                value=st.session_state.graph_explanations[bank],
                height=300,
                key=f"explanation_{bank}",
                label_visibility="collapsed"
            )
            st.session_state.graph_explanations[bank] = explanation

            # Display scenario information
            st.markdown("### Scenario Details")
            if scenario != "Default":
                st.markdown(f"""
                **{scenario}**
                - Assets: {format_currency(asset_value)} ({int(asset_value/total_assets*100)}%)
                - Liabilities: {format_currency(liability_value)} ({int(liability_value/total_assets*100)}%)
                """)

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Loss", format_currency(total_loss))

        with col2:
            st.metric("Loss Absorbed by Assets", format_currency(loss_absorbed))

        with col3:
            st.metric("Remaining Loss", format_currency(remaining_loss))

        # Distribution percentages
        st.write("#### Distribution Percentages")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Asset Absorption")
            asset_percentage = (loss_absorbed / total_loss) * 100 if total_loss > 0 else 0
            st.progress(asset_percentage / 100)
            st.write(f"8% Threshold: {asset_percentage:.1f}%")

        with col2:
            st.write("Creditor Distribution")
            for creditor in st.session_state.creditor_order:
                if creditor in st.session_state.exempt_creditors:
                    continue
                loss_amount = creditor_distribution[creditor]
                percentage = (loss_amount / total_loss) * 100 if total_loss > 0 else 0
                st.progress(percentage / 100)
                display_name = st.session_state.creditor_names[creditor]
                st.write(f"{display_name}: {percentage:.1f}%")

    with tab2:
        render_bank_values()

if __name__ == "__main__":
    main()