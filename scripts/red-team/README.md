# Red Team: Security Simulation Scripts

This directory contains scripts designed to proactively "attack" the RAG system to verify security boundaries, RBAC isolation, and data leakage prevention.

## `simulate_security_breach.py`

This script performs an automated security audit by simulating various user personas (attacker, legitimate user, cross-role user) and asserting that the agent only returns authorized information.

### What the script exercises:
1.  **Public Isolation**: Attempts to query sensitive acquisition (`internal`) and financial (`finance`) data using a random personal email. It asserts that the agent **does not** leak specific keywords like valuation prices or risk amounts.
2.  **Cross-Role Isolation**: Verifies that a user with one role (e.g., `finance`) cannot access data from another privileged role they don't possess (e.g., `admin`).
3.  **Positive Verification**: Confirms that legitimate access still works correctly for authorized users (e.g., `admin@bank.com`), ensuring security doesn't break functionality.
4.  **Keyword Detection**: Uses a "known-secrets" matching strategy to detect if specific sensitive values from the `knowledge-base/` documents appear in the agent's response for unauthorized users.

### Prerequisites:
- **Python 3.11+**
- **Requests Library**: `pip install requests`
- **Target URL**: The service must be reachable (either via local port 8080 or the public Load Balancer).

### How to Run:

**Against Local Dev:**
```bash
python3 scripts/red-team/simulate_security_breach.py --url http://localhost:8080 --verbose
```

**Against Staging:**
```bash
# Note: Ensure you are authenticated or the LB allows your IP
python3 scripts/red-team/simulate_security_breach.py --url https://rag-stage.example.com
```

### When to Run:
- **Before Production Promotion**: As a final "go/no-go" security check.
- **After RBAC Code Changes**: To ensure `app/roles.py` or metadata mapping logic hasn't regressed.
- **When adding new Golden Data**: To verify the new documents are correctly protected.

### Exit Codes:
- `0`: All security boundaries are secure.
- `1`: **Potential Data Leakage detected!** One or more tests failed to restrict access.
