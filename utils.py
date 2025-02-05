def calculate_loss_distribution(total_loss, bank_data, creditors, creditor_order):
    """
    Calculate loss distribution based on creditor hierarchy
    """
    remaining_loss = total_loss
    distribution = {creditor: 0 for creditor in creditor_order}
    
    for creditor in creditor_order:
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
    """
    order = current_order.copy()
    current_position = order.index(creditor_to_move)
    order.pop(current_position)
    order.insert(new_position, creditor_to_move)
    return order
