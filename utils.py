def calculate_loss_distribution(total_loss, bank_data, creditors, creditor_order, exempt_creditors=None):
    """
    Calculate loss distribution based on creditor hierarchy, considering asset absorption and exemptions
    """
    if exempt_creditors is None:
        exempt_creditors = set()

    remaining_loss = total_loss
    distribution = {creditor: 0 for creditor in creditor_order}

    # First handle Asset Absorption
    if "Asset Absorption" in creditor_order:
        absorption_capacity = bank_data["Asset Absorption"]
        loss_absorbed = min(remaining_loss, absorption_capacity)
        distribution["Asset Absorption"] = loss_absorbed
        remaining_loss -= loss_absorbed

        if remaining_loss <= 0:
            return distribution

    # Then distribute remaining losses among non-exempt creditors
    available_creditors = [c for c in creditor_order 
                         if c not in exempt_creditors and c != "Asset Absorption"]

    for creditor in available_creditors:
        # Get maximum absorption capacity for this creditor
        capacity = bank_data[creditor] if creditor in bank_data else 0

        # Calculate loss to be absorbed by this creditor
        loss_absorbed = min(remaining_loss, capacity)
        distribution[creditor] = loss_absorbed

        # Update remaining loss
        remaining_loss -= loss_absorbed
        if remaining_loss <= 0:
            break

    return distribution

def reorder_creditors(current_order, creditor_to_move, new_position):
    """
    Reorder creditors list by moving a creditor to a new position
    Asset Absorption always stays at the top
    """
    order = current_order.copy()

    # Don't allow moving Asset Absorption
    if creditor_to_move == "Asset Absorption":
        return order

    current_position = order.index(creditor_to_move)
    order.pop(current_position)

    # Ensure we don't insert before Asset Absorption
    if "Asset Absorption" in order and new_position == 0:
        new_position = 1

    order.insert(new_position, creditor_to_move)
    return order

def calculate_total_loss_with_absorption(total_assets, loss_percentage):
    """
    Calculate total loss considering the 8% asset absorption threshold
    """
    return total_assets * (loss_percentage / 100)