# Future Improvements

This document outlines planned and potential future improvements for the JIT Two-Stage Retrieval Agentic RAG solution, mapped to the FDE Assessment competencies.

## [OPERATIONAL EXCELLENCE]

### CI/CD & Deployment
- **Automated Progressive Delivery (Canary/Blue-Green)**: Implement automated traffic shifting in the production environment that only triggers after the ADK Evaluation quality gate has passed.
    - **Logic**: Following a successful build and staging evaluation, the pipeline automatically deploys a new version to production with 5-10% traffic (Canary).
    - **Quality Gate**: The system monitors real-time production metrics (error rates, latency) and compares them against the staging evaluation baseline. If performance remains stable, traffic is fully cut over (Blue-Green).
    - **Benefit**: Minimizes the blast radius of potential regressions and ensures that only "evaluated-and-verified" agent logic reaches the entire user base.

## [PERFORMANCE & COST OPTIMIZATION]

### Scalability & Elasticity
- **Multi-Region Regionalized RAG**: Implement a globally distributed architecture to minimize cross-region latency and ensure high availability for millions of users worldwide.
    - **Logic**: Deploy the Cloud Run backend and Vertex AI Search retrieval layers across multiple regions (e.g., `us-central1`, `europe-west1`, `asia-northeast1`).
    - **Routing**: Utilize a **Global Load Balancer** to automatically route user requests to the geographically nearest healthy region.
    - **Data Synchronization**: Implement global document replication where the ingestion pipeline synchronizes document updates across all regional Data Stores.
    - **Benefit**: Ensures that the entire "Retrieval -> Rerank -> Reason" loop occurs within the user's local region, minimizing speed-of-light delays and ensuring the <4s latency SLA is met globally while providing robust regional failover.

### AI Cost Management (Model Selection Trade-offs)
- **Dynamic Model Selection via Query Classifier**: Implement a "Query Classifier" step using the ADK that analyzes the incoming query's complexity and intent before routing it to the appropriate model tier.
    - **Logic**: The router classifies the task into tiers: "Ultra-Simple" (greetings, system status), "Standard" (grounded Q&A, summarization), or "Hard" (complex multi-document synthesis, reasoning).
    - **Routing**: 
        - **Ultra-Simple**: Routes to a specialized, fine-tuned **Small Language Model (SLM)** or a quantized local model to minimize cost for non-reasoning tasks.
        - **Standard**: Routes to a cost-effective tier like `gemini-2.0-flash-lite`.
        - **Hard**: Routes to a high-capacity model like `gemini-3.0-flash` or `gemini-2.5-pro`.
    - **Benefit**: Dramatically reduces the token budget for the "chatter" and simple interactions that make up a large percentage of high-volume traffic, while preserving high-fidelity capabilities for actual research and reasoning.

- **Summarization-based Context Compaction (Long-Term Memory)**: Implement an automated context window management strategy to maintain long-running multi-turn conversations without exponential token costs.
    - **Logic**: Every 5-10 turns, the system triggers a background "summarization" task that condenses the existing conversation history into a concise, semantically dense "State Summary."
    - **Context Management**: This summary replaces the raw message history in the next agentic reasoning turn, preserving essential context and user intent while discarding redundant tokens.
    - **Benefit**: Keeps the input token count stable even for 100+ turn conversations, providing massive cost savings for power users and preventing context window overflow.

## [SECURITY, PRIVACY, AND COMPLIANCE]

### Authentication & Authorization
- **Scalable Identity Management (Groups & Domain Access)**: Replace individual user-based access controls with scalable identity primitives for production-grade environments.
    - **Current Limitation**: The Infrastructure as Code (`infrastructure/modules/load_balancer/main.tf` L76-L89) currently grants IAP access only to a single user (`user:${var.user_email}`). While suitable for a rapid development phase, this does not scale to millions of users.
    - **Proposed Solution**: 
        - **Google Groups**: Grant the `roles/iap.httpsResourceAccessor` role to a centralized Google Group (e.g., `group:rag-users@example.com`) to manage access via group membership rather than individual IaC updates.
        - **Domain-Level Access**: For internal tools, grant access to an entire workspace domain (e.g., `domain:example.com`).
        - **External Identities**: Implement IAP External Identities for B2C/SaaS scenarios to handle millions of non-Google identities.
    - **Benefit**: Decouples identity management from infrastructure deployment, enabling seamless onboarding of millions of users without requiring Terraform changes.

### Network Security & Data Protection
- **Enterprise Network Isolation via VPC & VPC-SC**: Implement a custom Virtual Private Cloud (VPC) and VPC Service Controls to secure the application infrastructure and sensitive data.
    - **Logic**: Create a custom VPC network and connect Cloud Run to it using a **Serverless VPC Access Connector**. Implement **VPC Service Controls (VPC-SC)** to create a security perimeter around Vertex AI and Cloud Storage.
    - **Components**: Custom VPC network, Serverless VPC Access Connector, and optionally Cloud Memorystore for Redis (for low-latency caching).
    - **Benefit**: Prevents data exfiltration by ensuring that sensitive documents and model interactions remain within a trusted network perimeter. This is a critical requirement for production environments serving enterprise customers.
