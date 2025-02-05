# Default creditor types with their properties
DEFAULT_CREDITORS = {
    "Single Resolution Fund": {
        "color": "#1f77b4",
        "priority": 1
    },
    "Secured Creditors": {
        "color": "#ff7f0e",
        "priority": 2
    },
    "Depositors > €100k": {
        "color": "#2ca02c",
        "priority": 3
    },
    "Senior Unsecured Creditors": {
        "color": "#d62728",
        "priority": 4
    },
    "Subordinated Debt": {
        "color": "#9467bd",
        "priority": 5
    },
    "Shareholders": {
        "color": "#8c564b",
        "priority": 6
    }
}

# Sample bank data (in EUR)
DEFAULT_BANKS = {
    "Bank A": {
        "total_assets": 1000000000,
        "Single Resolution Fund": 50000000,
        "Secured Creditors": 300000000,
        "Depositors > €100k": 250000000,
        "Senior Unsecured Creditors": 200000000,
        "Subordinated Debt": 100000000,
        "Shareholders": 100000000
    },
    "Bank B": {
        "total_assets": 750000000,
        "Single Resolution Fund": 37500000,
        "Secured Creditors": 225000000,
        "Depositors > €100k": 187500000,
        "Senior Unsecured Creditors": 150000000,
        "Subordinated Debt": 75000000,
        "Shareholders": 75000000
    },
    "Bank C": {
        "total_assets": 500000000,
        "Single Resolution Fund": 25000000,
        "Secured Creditors": 150000000,
        "Depositors > €100k": 125000000,
        "Senior Unsecured Creditors": 100000000,
        "Subordinated Debt": 50000000,
        "Shareholders": 50000000
    }
}
