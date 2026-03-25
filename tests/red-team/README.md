# Red Team: Security & Resilience Testing

This directory contains specialized tests for "Red Teaming" and "Chaos Engineering" simulations to ensure production-grade security.

## RBAC Isolation Tests (`tests/red-team/test_rbac_isolation.py`)

These tests act as an automated security gate to ensure that users can never retrieve documents outside of their authorized scope.

### Test Scenarios:
1. **Public Isolation**: Verifies that users with unknown or personal emails can only retrieve documents tagged as `public`.
2. **Role Elevation Prevention**: Verifies that users cannot spoof roles (e.g., `finance`, `admin`) by providing malicious email strings.
3. **Anonymous Defaulting**: Ensures that missing identity headers default to the most restrictive access level.
4. **Admin Access**: Verifies that authorized admins correctly receive their full scope of permissions.

### Running the tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/red-team/
```

## Upcoming Tests (See todo.md)
- **Fault Injection**: Synthetic latency and failure injection for tool calls.
- **DR Drills**: Automated validation of Data Store rebuild RTO.
