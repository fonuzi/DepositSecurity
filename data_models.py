# Default creditor types with their properties
DEFAULT_CREDITORS = {
    "Asset Absorption": {
        "color": "#17becf",
        "priority": 1,
        "fixed_percentage": 8.0,  # 8% of total assets
        "system": True  # Flag to identify system-managed creditors
    },
    "Single Resolution Fund": {
        "color": "#1f77b4",
        "priority": 2
    },
    "Secured Creditors": {
        "color": "#ff7f0e",
        "priority": 3
    },
    "Depositors > €100k": {
        "color": "#2ca02c",
        "priority": 4
    },
    "Senior Unsecured Creditors": {
        "color": "#d62728",
        "priority": 5
    },
    "Subordinated Debt": {
        "color": "#9467bd",
        "priority": 6
    },
    "Shareholders": {
        "color": "#8c564b",
        "priority": 7
    }
}

# Sample bank data (in EUR)
DEFAULT_BANKS = {
    "Bank A": {
        "total_assets": 1000000000,
        "Asset Absorption": 80000000,  # 8% of total assets
        "Single Resolution Fund": 50000000,
        "Secured Creditors": 300000000,
        "Depositors > €100k": 250000000,
        "Senior Unsecured Creditors": 200000000,
        "Subordinated Debt": 100000000,
        "Shareholders": 100000000
    },
    "Bank B": {
        "total_assets": 750000000,
        "Asset Absorption": 60000000,  # 8% of total assets
        "Single Resolution Fund": 37500000,
        "Secured Creditors": 225000000,
        "Depositors > €100k": 187500000,
        "Senior Unsecured Creditors": 150000000,
        "Subordinated Debt": 75000000,
        "Shareholders": 75000000
    },
    "Bank C": {
        "total_assets": 500000000,
        "Asset Absorption": 40000000,  # 8% of total assets
        "Single Resolution Fund": 25000000,
        "Secured Creditors": 150000000,
        "Depositors > €100k": 125000000,
        "Senior Unsecured Creditors": 100000000,
        "Subordinated Debt": 50000000,
        "Shareholders": 50000000
    }
}