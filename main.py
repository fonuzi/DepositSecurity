import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from streamlit_sortables import sort_items
from utils import calculate_loss_distribution, reorder_creditors, calculate_total_loss_with_absorption
from styles import apply_styles
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS

def format_currency(value):
    """Format number with thousand separators using dots and currency symbol"""
    whole_part = int(value)
    formatted = "{:,.0f}".format(whole_part).replace(",", ".")
    return f"€{formatted}"

def format_number(value):
    """Format number with thousand separators using dots, without currency symbol"""
    whole_part = int(value)
    return "{:,.0f}".format(whole_part).replace(",", ".")

def parse_formatted_number(formatted_str):
    """Convert formatted number string back to float"""
    try:
        return float(formatted_str.replace(".", ""))
    except (ValueError, AttributeError):
        return 0.0

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
        display_df[col] = df[col].apply(lambda x: format_currency(float(x)))

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
    if 'graph_explanations' not in st.session_state:
        st.session_state.graph_explanations = {}

    # Create tabs
    tab1, tab2 = st.tabs(["Loss Distribution", "Bank Values"])

    with tab1:
        with st.sidebar:
            st.header("Configuration")

            # Bank selection
            selected_bank = st.selectbox(
                "Select Bank",
                options=list(st.session_state.current_bank_data.keys()),
                key="bank_selector"
            )

            # Creditor hierarchy management
            st.subheader("Creditor Hierarchy")
            st.info("Drag and drop creditors to reorder")

            # Create sortable list for creditors
            sorted_creditors = sort_items(st.session_state.creditor_order)

            if sorted_creditors != st.session_state.creditor_order:
                st.session_state.creditor_order = sorted_creditors
                st.rerun()

            # Display creditor values and exempt checkboxes
            if selected_bank:
                st.subheader("Creditor Values")

                for creditor in st.session_state.creditor_order:
                    col1, col2 = st.columns([2, 3])

                    with col1:
                        st.write(creditor)

                    with col2:
                        current_value = float(st.session_state.current_bank_data[selected_bank][creditor])

                        # Number input with dots format and spinners
                        new_value = st.number_input(
                            "Value (EUR)",
                            min_value=0.0,
                            value=current_value,
                            step=1000000.0,
                            format="%.0f",
                            key=f"value_{creditor}_{selected_bank}",
                            label_visibility="collapsed"
                        )

                        # Update the displayed value with proper formatting
                        st.markdown(f"<p style='font-size: 1rem; margin-top: -1rem;'>{format_number(new_value)}</p>", unsafe_allow_html=True)

                        # Update state if value changed
                        if new_value != current_value:
                            st.session_state.current_bank_data[selected_bank][creditor] = new_value
                            st.rerun()

                    # Checkbox for exempt status
                    is_exempt = st.checkbox(
                        "Exempt",
                        value=creditor in st.session_state.exempt_creditors,
                        key=f"exempt_{creditor}"
                    )
                    if is_exempt and creditor not in st.session_state.exempt_creditors:
                        st.session_state.exempt_creditors.add(creditor)
                    elif not is_exempt and creditor in st.session_state.exempt_creditors:
                        st.session_state.exempt_creditors.remove(creditor)

                    # Add horizontal line after each creditor
                    st.markdown("---")

        # Main content area for Loss Distribution
        if not selected_bank:
            st.warning("Please select at least one bank to display.")
        else:
            # Calculate loss distribution for each selected bank
            selected_banks = [selected_bank] #Using selected bank from selectbox
            for bank in selected_banks:
                st.subheader(f"{bank} Loss Distribution")

                # Create columns for graph and explanation
                col1, col2 = st.columns([2, 1])

                with col1:
                    total_assets = st.session_state.current_bank_data[bank]["total_assets"]
                    total_loss = calculate_total_loss_with_absorption(total_assets, 10.0) #Using default value for loss percentage

                    # Create figure with two subplots side by side
                    fig = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=("Assets", "Liabilities"),
                        column_widths=[0.4, 0.6],
                        horizontal_spacing=0.1
                    )

                    # Asset bar
                    threshold_8_percent = total_assets * 0.08
                    remaining_asset_value = max(0, total_assets - total_loss)
                    loss_absorbed = min(total_loss, threshold_8_percent)
                    remaining_loss = max(0, total_loss - loss_absorbed)

                    # Add asset bar components
                    fig.add_trace(
                        go.Bar(
                            name="Remaining Assets",
                            x=["Total Assets"],
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
                                x=["Total Assets"],
                                y=[loss_absorbed],
                                marker_color="#e74c3c",
                                text=format_currency(loss_absorbed),
                                textposition='inside',
                            ),
                            row=1, col=1
                        )

                    # Calculate creditor distribution
                    creditor_distribution = calculate_loss_distribution(
                        remaining_loss,
                        st.session_state.current_bank_data[bank],
                        DEFAULT_CREDITORS,
                        st.session_state.creditor_order,
                        st.session_state.exempt_creditors
                    )

                    # Add creditor bars
                    for creditor in st.session_state.creditor_order:
                        if creditor in st.session_state.exempt_creditors:
                            continue

                        loss_amount = creditor_distribution[creditor]
                        if loss_amount > 0:
                            fig.add_trace(
                                go.Bar(
                                    name=creditor,
                                    x=["Loss Distribution"],
                                    y=[loss_amount],
                                    marker_color=DEFAULT_CREDITORS[creditor]['color'],
                                    text=format_currency(loss_amount),
                                    textposition='inside',
                                ),
                                row=1, col=2
                            )

                    # Update layout
                    fig.update_layout(
                        height=600,
                        showlegend=True,
                        barmode='stack',
                        title=f"Loss Distribution Analysis (10% Loss)", #Using default value
                        legend_title="Components",
                    )

                    # Update axes
                    fig.update_xaxes(showticklabels=True)
                    fig.update_yaxes(title_text="Amount (EUR)")

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("### Graph Explanation")
                    # Add text area for explanation
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

                # Summary statistics below the graph and explanation
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Loss", format_currency(total_loss))

                with col2:
                    st.metric("Loss Absorbed by Assets", format_currency(loss_absorbed))

                with col3:
                    st.metric("Remaining Loss", format_currency(remaining_loss))

                # Detailed percentages
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
                        st.write(f"{creditor}: {percentage:.1f}%")

    with tab2:
        render_bank_values()

if __name__ == "__main__":
    main()