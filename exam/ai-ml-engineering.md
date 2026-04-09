# AI Assessment: AI/ML Engineering

This assessment probes the candidate's expertise in designing, implementing, and optimizing production-grade GenAI solutions using the Agentic RAG pattern.

## Agentic & Multi-Agent Systems

**Q1: In your implementation, you chose a unified RAG agent instead of a multi-agent orchestration pattern (e.g., a "Router" agent followed by specialized "Retriever" and "Writer" agents). What were the primary trade-offs you considered regarding latency, reasoning complexity, and state management for a system scaling to millions of users?**

**A1:** A unified agent reduces the overhead of inter-agent communication and state synchronization, which is critical for minimizing latency in high-scale systems. In a multi-agent setup, each handoff introduces additional token usage and potential reasoning drift. However, a unified agent requires a more sophisticated prompt (as seen in `app/agent.py`) to manage the two-stage retrieval workflow autonomously. For millions of users, the unified approach is more cost-effective and easier to trace, while specialized agents would only be justified if the sub-tasks (e.g., complex tool-use or domain-specific reasoning) became too complex for a single context window to handle reliably.

**Q2: Your `root_agent` uses a sequential tool-calling pattern (Retrieve -> Rerank -> Respond). How does the Google ADK handle the "planning" phase of this agent, and how would you optimize the tool-calling loop if the agent needed to retrieve from multiple heterogeneous data sources simultaneously?**

**A2:** The Google ADK's `Runner` executes the agent's logic by iteratively calling the model and executing tools. Currently, the agent is instructed via the system prompt to call `stage_1_retrieval` first. To optimize for multiple sources, I would implement a "Parallel Retriever" tool or use the ADK's ability to suggest multiple tool calls in a single turn. This allows the model to initiate multiple retrieval requests in parallel, reducing the overall wall-clock time compared to sequential calls, which is essential for maintaining a <4s latency SLA.

**Q2.1: You mentioned the ADK executes tools "until a final response is generated." Can you explain the underlying mechanism for this loop? How does the agent (and the ADK Runner) determine that no further tool calls are needed and that the current output is indeed the final grounded response?**

**A2.1:** This is governed by a **multi-turn reasoning loop** (often called a ReAct loop). The mechanism works as follows:
1. **Model Turn**: The `Runner` sends the conversation history and the current prompt to the model.
2. **Action Detection**: The model responds with either a `call` (requesting a tool execution) or `content` (plain text).
3. **Execution**: If the model provides a `call`, the `Runner` executes the tool locally, appends the result to the history, and immediately triggers another **Model Turn**.
4. **Finality Check**: The `Runner` identifies a "final response" when the model returns a text response **without** any accompanying tool calls. In the context of Gemini, this is signalled when the response's `finish_reason` is `STOP` and the parts contain text rather than `function_call` objects. 
5. **Safety Bounds**: To prevent infinite loops (e.g., if the agent keeps calling a tool that returns errors), the ADK `Runner` has a configurable `max_iterations` limit. If reached, the Runner terminates the loop and returns an error or a partial response.

**Q2.2: How do you ensure the agent doesn't prematurely provide a "final response" before it has finished reranking the documents?**

**A2.2:** This is primarily controlled via **System Instructions** and **Few-Shot Prompting** in `app/agent.py`. The prompt explicitly defines the "Operational Workflow" as a strict sequence. By instructing the agent that it *must* pass results to `rerank_documents` *if* documents are found, we increase the probability that the model's internal "planning" state won't transition to a final answer until that tool result is present in its context window. Additionally, by using a model with strong reasoning capabilities like `gemini-2.5-pro`, the agent is better at following these multi-step logical dependencies without "skipping" steps.

**Q3: How do you handle "reasoning drift" where the agent might interpret retrieved snippets in a way that contradicts the original user intent?**

**A3:** This is mitigated by the combination of the system instruction in `app/agent.py` and the two-stage retrieval process. The system instruction strictly enforces grounding ("NEVER hypothesize," "Only use information provided"). Furthermore, the `rerank_documents` tool (Stage 2) uses a Cross-Encoder model (`semantic-ranker-52b`) which provides a deeper semantic understanding than the initial vector search. By only providing the agent with high-scoring, reranked snippets, we reduce the "noise" in the context window, thereby minimizing the chance of reasoning drift or hallucinations.

---

## Retrieval & Data Engineering (RAG)

**Q4: You implemented a Two-Stage Retrieval architecture. Why is the second stage (reranking) necessary if Vertex AI Search already provides high-quality vector search results?**

**A4:** Stage 1 (Vertex AI Search) is optimized for high-speed recall across millions of documents using Bi-Encoders. While fast, Bi-Encoders can miss subtle semantic nuances. Stage 2 (Vertex AI Ranking API) uses a Cross-Encoder, which is significantly more computationally expensive but far more accurate as it processes the query and document simultaneously. This two-stage approach allows us to maintain "hyperscale" performance (searching millions of docs in Stage 1) while achieving "expert-level" precision (reranking the top ~20-50 candidates in Stage 2) for the final grounded response.

**Q5: In `app/reranker.py`, you log reranking errors to BigQuery. How would you use this data to improve the retrieval pipeline's performance or cost efficiency over time?**

**A5:** The `reranker_errors` table in BigQuery serves as an observability hook for the ranking service. By analyzing these errors alongside the user feedback (`feedback` table), we can identify queries where the reranker failed to produce high-scoring matches. If we consistently see low scores for certain topics, it suggests a gap in the "Stage 1" retrieval (recall issue) or a need to fine-tune the embedding model. From a cost perspective, we can analyze the distribution of `rerank_score` to determine if we can reduce the number of documents sent to Stage 2 (`top_k`) without sacrificing grounding quality.

**Q6: How does your RAG pipeline handle document updates or "stale" information in a production environment with millions of documents?**

**A6:** The design spec (`docs/DESIGN_SPEC.md`) outlines an ETL pipeline triggered by GCS events. When a document is updated in GCS, an Eventarc trigger invokes a Cloud Function that re-parses and re-indexes the document in Vertex AI Search. For millions of documents, this event-driven approach ensures "near real-time" index freshness without the need for expensive daily full-reindexes. Additionally, we use metadata tagging (e.g., `last_updated_timestamp`) which the agent can use to prioritize newer information if conflicts arise.

---

## Model Selection & Tuning

**Q7: Your implementation allows switching between Vertex AI and AI Studio via `USE_VERTEX_AI`. Why would a Senior Engineer choose Vertex AI for a "production grade" solution despite the potentially simpler API of AI Studio?**

**A7:** Vertex AI is the choice for production because it offers enterprise-grade features that AI Studio lacks: 1) **Regionalization**: We can pin models and data to specific regions (e.g., `us-central1`) for compliance and latency. 2) **SLA & Quota Management**: Vertex AI provides robust SLAs and dedicated quota management. 3) **Security**: It integrates natively with IAM, VPC-SC, and IAP, which is critical for the RBAC implementation. AI Studio is excellent for rapid prototyping, but Vertex AI provides the stability and security required for millions of users.

**Q8: You recently downgraded the production model from `gemini-2.5-pro` to `gemini-2.0-flash-lite`. What were the primary drivers for this change, and what specific performance-to-cost metrics did you evaluate to justify this "lite" model for a system targeting millions of users?**

**A8:** The primary drivers were **latency** and **unit economics at scale**. While `gemini-2.5-pro` offers superior reasoning, its higher cost-per-token and higher latency (TTFT) become bottlenecks when serving millions of users. `gemini-2.0-flash-lite` provides a "sweet spot" for RAG tasks where the heavy lifting (retrieval and reranking) is handled by specialized tools. We evaluated: 1) **Token Throughput**: Flash-lite handles significantly higher RPS within the same quota limits. 2) **Latency SLA**: It ensures we stay under the <2s TTFT requirement. 3) **Retrieval Accuracy**: We confirmed that for grounded generation based on provided context, the reasoning gap between Pro and Flash-lite was negligible, while the cost reduction was >10x.

**Q14: How do you decide between using `gemini-2.0-flash` vs. `gemini-2.0-flash-lite`? When is the "lite" version insufficient?**

**A14:** `flash-lite` is ideal for high-volume, low-latency tasks like simple summarization, basic tool extraction, and grounded Q&A. However, it may be insufficient for: 1) **Complex Multi-step Planning**: If the agent needs to orchestrate more than 3-4 dependent tool calls. 2) **Large-scale JSON Extraction**: When extracting 50+ fields with strict schema constraints. 3) **Nuanced Sentiment/Legal Analysis**: Where subtle linguistic differences change the outcome. In these cases, the standard `flash` or `pro` models are preferred.

**Q15: With Gemini's 1M+ context window, why continue using a RAG architecture instead of simply stuffing all documents into the context?**

**A15:** While "Long Context" is powerful, RAG remains superior for millions of documents for three reasons: 1) **Cost**: Sending 1M tokens on every user query is prohibitively expensive. 2) **Latency**: Processing a full context window takes significantly longer than a targeted RAG turn. 3) **Precision**: LLMs can still suffer from "Lost in the Middle" or attention dilution when the context is too large. RAG acts as a pre-filter, ensuring the model only pays attention to the most relevant information, which improves both grounding quality and performance.

**Q16: Your agent uses Tool Calling to interact with the RAG pipeline. Why choose Tool Calling over prompting the model to output a specific JSON format?**

**A16:** Tool Calling (Function Calling) is more robust for production because: 1) **Strict Typing**: The model is forced to adhere to a schema defined in the tool's signature, reducing parsing errors. 2) **Model Optimization**: Gemini is explicitly trained to recognize when a tool call is needed, leading to higher reliability than generic "output JSON" prompts. 3) **Clean State Management**: The ADK handles the injection of tool results back into the conversation history, maintaining a clear separation between "thinking," "acting," and "responding."

---

## LLM Ops and Evaluation

**Q9: Your evaluation suite (`eval/`) uses `hallucinations_v1` with a 0.9 threshold. How did you design the "Golden Test Set" to ensure it adequately covers the "long tail" of user queries?**

**A9:** The test set in `eval/eval_cases.json` is categorized by industry verticals (Finance, SaaS, Legal) and includes specific "negative" test cases (e.g., `fin_02_rbac_violation`, `fin_03_hallucination_check`). A high-quality golden set must include: 1) **Adversarial queries** designed to trigger hallucinations. 2) **Edge cases** where documents contain conflicting info. 3) **Security probes** to test RBAC. By using `gemini-2.5-pro` as an "LLM-as-a-judge," we get a more nuanced evaluation than simple keyword matching, which is essential for assessing semantic grounding.

**Q9.1: How do you validate the "LLM-as-a-Judge" itself? (The "Meta-Evaluation" Problem)**

**A9.1:** To ensure the judge (Gemini 2.5 Pro) is reliable, we perform **Meta-Evaluation** by comparing its scores against human-annotated labels on a small subset of the golden set. We calculate the **Alignment Score** (e.g., Cohen's Kappa or simple accuracy) between the LLM judge and human experts. If the alignment drops below 85%, we refine the evaluation prompt (the "Rubric") to provide more explicit criteria and few-shot examples of "good" vs. "bad" responses.

**Q9.2: In your CI/CD pipeline, how do you handle "flaky" evaluations where the same prompt might pass or fail across different runs due to model non-determinism?**

**A9.2:** We address non-determinism by: 1) **Setting `temperature=0`** for both the agent and the judge during eval. 2) **N-of-M Voting**: Running the evaluation multiple times (e.g., 3 runs) and taking the majority or average score. 3) **Semantic Versioning for Prompts**: Treating the evaluation rubric as code and versioning it alongside the application logic, ensuring that a "pass" today means the same as a "pass" tomorrow.

**Q9.3: How do you balance "Component-Level" evaluation (retrieval vs. generation) vs. "End-to-End" (E2E) evaluation?**

**A9.3:** E2E evaluation tells us if the user is happy, but component-level evaluation tells us *why* they aren't. We use **RAGAS-style metrics**:
*   **Faithfulness (Generation)**: Is the answer derived *only* from the retrieved context?
*   **Answer Relevance (Generation)**: Does the answer actually address the user's query?
*   **Context Precision (Retrieval)**: Are the relevant documents ranked highly?
*   **Context Recall (Retrieval)**: Did we retrieve all necessary documents?
By measuring these independently, we can pinpoint if a failure is due to a weak retriever (Stage 1), a poor reranker (Stage 2), or a hallucinating generator (Agent).

**Q10: If the `tool_trajectory_avg_score` falls below 1.0, what is the most likely failure point in your agent's logic?**

**A10:** A score below 1.0 indicates that the agent failed to follow the prescribed tool-calling sequence or, more likely, failed to pass the correct parameters. In this RAG implementation, the most critical parameter is the `user_email` for RBAC filtering. If the agent forgets to extract the email from the `[USER IDENTITY: ...]` context and pass it to `stage_1_retrieval`, the trajectory score will drop. This is a "hard fail" because it represents a potential security breach (retrieving data without a filter).

**Q11: How do you implement "Online Evaluation" (Production Monitoring) vs. "Offline Evaluation" (Pre-deployment)?**

**A11:** **Offline Evaluation** (in `eval/`) uses the Golden Set to prevent regressions before deployment. **Online Evaluation** uses production logs in BigQuery. We implement "Shadow Logging" where a smaller, cheaper model (like Gemini Flash) asynchronously evaluates a percentage of production traffic using the same `hallucinations_v1` rubric. This allows us to detect "Data Drift" (new user query patterns) that our Golden Set might have missed.

**Q12: Your system logs user feedback to BigQuery. How do you close the "Data Flywheel" loop to improve model performance?**

**A12:** Negative feedback (e.g., a "thumbs down") triggers an automated workflow: 1) The interaction is flagged for human review. 2) If the error is confirmed, the query-response pair is added to the **Negative Test Set** in `eval_cases.json`. 3) This updated test set is then used for **Fine-tuning** (if using a smaller model) or to refine the **System Instructions** in `app/agent.py`. This ensures the system continuously learns from its mistakes.

**Q13: How do you handle "LLM Bias" when using a model as a judge for your evaluations?**

**A13:** LLM judges often exhibit **Position Bias** (preferring the first response) or **Verbosity Bias** (preferring longer responses). We mitigate this by: 1) **Swapping Positions**: Running the judge on pairs of responses in both A-B and B-A order. 2) **Strict Rubrics**: Forcing the judge to provide a structured reasoning (Chain-of-Thought) before outputting a final score. 3) **Length Normalization**: Penalizing the judge if it correlates high scores too strongly with response length.
