# AI Evaluation: Golden Test Set

This directory contains the evaluation logic used to validate the quality, precision, and security of the JIT Two-Stage Retrieval Agent.

## Evaluation Strategy
Unlike unit tests that check for code crashes, these **AI Evaluations** use a "model-as-a-judge" (gemini-2.5-pro) to verify that the agent's reasoning is correct, grounded in the retrieved documents, and adheres to security boundaries.

### Core Metrics
- **`tool_trajectory_avg_score`**: Ensures the agent calls the `stage_1_retrieval` tool with the correct query and, crucially, the user's authenticated email for RBAC filtering.
- **`final_response_match_v2`**: Uses semantic matching to verify that the agent's answer is accurate, even if the phrasing differs from the "golden" answer.
- **`hallucinations_v1`**: A high-sensitivity check to ensure the agent only speaks based on retrieved context and does not make up information.

## Test Case Breakdown (10 Cases)

### 1. Finance Use Cases
- **`fin_01_market_analysis`**: Tests broad retrieval and synthesis of market risks.
- **`fin_02_rbac_violation`**: Verifies that a low-tier user cannot retrieve confidential M&A strategy documents.
- **`fin_03_hallucination_check`**: Confirms the agent correctly denies a false claim (e.g., Bitcoin hitting $1M in 2023) if not found in the docs.

### 2. SaaS Support Use Cases
- **`saas_01_error_resolution`**: Tests technical precision in resolving common infrastructure errors (GKE 503).
- **`saas_02_internal_docs`**: Validates that internal-only post-mortems are correctly retrieved by authorized SREs.
- **`saas_03_multi_turn`**: A complex test of conversation state, ensuring the agent maintains context across multiple questions about IAM permissions.

### 3. Legal Tech Use Cases
- **`legal_01_clause_search`**: Tests the ability to locate specific legal clauses (e.g., "Change of Control") in a massive document.
- **`legal_02_ethical_wall`**: A critical security test ensuring a lawyer from Firm A cannot retrieve documents belonging to Case B.

### 4. General Safety & Quality
- **`gen_01_no_info`**: Verifies that the agent gracefully handles "out-of-domain" questions (e.g., secret recipes) by stating it doesn't know.
- **`gen_02_citations`**: Ensures that every response includes clear, formatted citations to the source material.

## How to Run the Evaluation

From the root directory:
```bash
make eval
```

Or directly via the ADK CLI:
```bash
adk eval app eval/eval_cases.json --config_file_path=eval/eval_config.json --print_detailed_results
```

## Interpreting Results
- **Pass**: All metrics meet the thresholds defined in `eval_config.json`.
- **Fail**: Check the `detailed_results`. Look for "hallucination detected" or "tool trajectory mismatch." If the trajectory fails, the agent likely forgot to pass the `user_email` to the retrieval tool.
