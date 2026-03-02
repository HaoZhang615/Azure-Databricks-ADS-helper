# Conversation Framework - Microsoft Foundry ADS

Foundry-specific signal detection, adaptive behaviors, phase execution details, and transition logic for the ADS session. The generic ADS methodology (persona, pacing, decision narration, trade-off framework) is defined in the runtime system prompt - this file provides the Foundry-specific content that methodology operates on.

## Table of Contents
- [Signal Detection](#signal-detection)
- [Phase 1: Context Discovery](#phase-1-context-discovery)
- [Phase 2: Current Landscape](#phase-2-current-landscape)
- [Phase 3: Security and Networking](#phase-3-security-and-networking)
- [Phase 4: Operational Requirements](#phase-4-operational-requirements)
- [Phase 5: Future State Diagram Generation](#phase-5-future-state-diagram-generation)
- [Phase 6: Iteration](#phase-6-iteration)
- [Optional: Workload Profiling](#optional-workload-profiling)

## Signal Detection

Detect these keywords early and adapt the interview path accordingly.

| User Signal | Adaptive Behavior |
|-------------|-------------------|
| "agent", "agentic", "AutoGen", "LangChain", "Semantic Kernel" | Probe agent tool definitions, multi-agent topology, state persistence. Steer toward MAF patterns. |
| "RAG", "grounding", "chat over my documents" | Ask about document corpus, AI Search existing indexes, hybrid search needs. Steer toward Baseline Chat pattern. |
| "Azure OpenAI", "AOAI" | Likely migration candidate. Ask about current endpoint usage, API key vs managed identity, deployment names. Load migration-patterns.md. |
| "AzureML", "Machine Learning workspace" | Classic Hub candidate or migration. Probe SDK version (v1 EOL Jun 2026). Load migration-patterns.md. |
| "fine-tun", "custom model", "domain-specific" | Steer toward Fine-Tuning pattern. Ask about training data size, base model, eval criteria. |
| "batch", "overnight processing", "bulk inference" | Steer toward GlobalBatch pattern. Ask about record volume, acceptable turnaround, cost sensitivity. |
| "compliance", "HIPAA", "SOC2", "GDPR", "FedRAMP" | Expand Phase 3 to 3+ turns. Private Link mandatory. Agent standard setup required. |
| "PTU", "provisioned", "throughput units" | Steer toward PTU Gateway pattern. Probe TPM, RPM, spillover strategy. |
| "multi-team", "platform team", "CoE", "center of excellence" | Steer toward Multi-Project Platform pattern. Probe project isolation, RBAC model, shared resources. |
| "IoT", "sensors", "telemetry", "devices" | Ask about real-time inference needs, edge vs cloud, batch vs streaming. |
| "cost", "budget", "cheap", "FinOps" | Note cost sensitivity. Probe GlobalStandard vs GlobalBatch vs PTU. Expand Phase 4 capacity discussion. |
| "MCP", "model context protocol", "tool use" | Probe Foundry MCP Server vs custom REST tools. Note mcp.ai.azure.com endpoint. |
| "evaluation", "hallucination", "accuracy" | Surface azure-ai-evaluation SDK. Probe groundedness, coherence, safety thresholds. |

---

## Phase 1: Context Discovery

**Purpose**: Establish the business problem, primary AI use case, and organisational context.

**Entry condition**: Conversation starts.

**Exit condition**: Use case identified, greenfield vs migration known, stakeholder context clear, scale intent understood.

### Core Questions

1. "What business problem or opportunity is driving this project?"
   - Vague answer: "Can you give me a specific example of what you want AI to do that it cannot do today?"
2. "Is this a new AI platform or are you migrating from an existing system?"
   - If migration: "What are you migrating from - Azure OpenAI standalone, AzureML workspaces, on-prem LLM, or custom inference code?"
3. "What is the primary AI use case - enterprise chat, RAG over documents, autonomous agents, batch processing, fine-tuning a custom model, or real-time inference?"
4. "What industry are you in, and are there specific regulatory requirements?"
5. "Who are the key stakeholders? AI engineers, data scientists, application developers, security and infrastructure teams?"
6. "Do you have a target go-live date or business milestone driving the timeline?"
7. "What does success look like? Response latency targets, cost per query, hallucination rate, user satisfaction score?"

### Transition

Bridge into current landscape: "That gives me a solid picture of what is driving this. Next I need to understand your existing AI estate and data landscape - what you are working with today."

### Anti-patterns

- Do NOT jump to model selection in Phase 1. Use case first, then model.
- Do NOT assume Foundry familiarity - ask about existing Azure AI experience.
- Do NOT open with questions. Start with a brief orientation then ask your first question.

---

## Phase 2: Current Landscape

**Purpose**: Map the existing AI/data platform, models in use, tooling investments, and data sources for grounding.

**Entry condition**: Business problem and use case are understood.

**Exit condition**: Existing platform named, data sources for grounding mapped, model preferences established, tooling context understood. After this phase, optionally generate a Current State diagram.

### Core Questions

1. "What AI or ML platforms are you using today - Azure OpenAI, AzureML, Databricks MLflow, HuggingFace, or something else?"
2. "What models are you targeting? GPT-4o, o1, o3-mini, Phi-4, or open-source models via serverless endpoints?"
3. "What data do you need to ground the AI on? SharePoint, Blob Storage, databases, existing Azure AI Search indexes?"
4. "Have you built any agent code or LLM integrations already - LangChain, Semantic Kernel, OpenAI SDK, custom REST?"
5. "What is your observability stack today - Application Insights, Datadog, custom logging?"
6. "What does your CI/CD maturity look like for AI workloads - manual deployments, scripts, or automated pipelines?"

### Red Flags to Surface

- **AzureML SDK v1 usage**: EOL June 30, 2026. Must plan migration to azure-ai-projects or AzureML SDK v2.
- **API key authentication in production**: Not recommended. Push toward Managed Identity and DefaultAzureCredential.
- **No evaluation framework**: Surface azure-ai-evaluation as a production must-have.
- **Monolithic single-agent design for complex workflows**: Suggest MAF multi-agent architecture early.

### Transition

Bridge into security: "Good - I have a solid picture of your current environment. Before I start sketching the target architecture, I need to understand your security and networking posture - those decisions cascade across everything."

---

## Phase 3: Security and Networking

**Purpose**: Determine network isolation model and identity/access requirements.

**Exit condition**: Network model selected, identity model confirmed, compliance scope clear, agent setup tier decided.

### Core Questions

1. Does your organisation require private networking, or are public endpoints acceptable?
2. How do you manage identities - Managed Identity, service principals, or API keys?
3. What compliance frameworks apply - HIPAA, SOC2, GDPR, FedRAMP, PCI-DSS?
4. Do you require customer-managed encryption keys?
5. Do your agents need to call internal APIs inside your corporate network? (Agent subnet injection - RFC-1918 /24 required)
6. Do you need Content Safety filtering for prompt injection and harmful content?

### Decision Tree: Network Model

Compliance requirement exists? YES -> Private Link required. NO -> Customer-facing production? YES -> Private Link recommended. NO -> Public OK for dev/PoC.

### Decision Tree: Agent Setup Tier

Using Agent Service? NO -> Skip. YES -> Data isolation between runs required? YES -> Standard setup (customer-owned Cosmos DB, Storage, AI Search). NO -> Basic setup.

---

## Phase 4: Operational Requirements

**Purpose**: Capacity model, reliability, cost, and operating model.

### Core Questions

1. What are your latency requirements? Sub-second P99 critical, or a few seconds acceptable?
2. What throughput - tokens per minute, requests per minute at peak?
3. Do you need zone redundancy? RPO/RTO targets?
4. How many environments - dev, test, production? Separate Foundry projects per environment?
5. Who owns the AI platform day-to-day?
6. Do you need cost chargeback per team? APIM token logging and tagging strategy?

### Capacity Decision Tree

Guaranteed low latency + consistent throughput -> ProvisionedManaged PTUs + GlobalStandard spillover.
Variable load, cost-optimise -> GlobalStandard pay-per-token.
Async, non-real-time, cost-critical -> GlobalBatch.

---

## Phase 5: Future State Diagram Generation

**Purpose**: Synthesise requirements into a concrete future state architecture diagram.

### Architecture Recap Format

| Component | Role in This Architecture | Why This Was Chosen |
|-----------|---------------------------|---------------------|
| GPT-4o GlobalStandard deployment | Primary inference endpoint | PAYG token billing - no PTU commitment yet |
| AI Search (hybrid semantic + BM25) | Document retrieval for RAG | SharePoint corpus with mixed terminology |
| Cosmos DB (agent state) | Conversation history + agent run state | Standard setup required for compliance isolation |

Rules: every node in the diagram must appear. The Why column must reference something the user said.

---

## Phase 6: Iteration

1. Invite feedback: What jumps out? Anything missing?
2. Explain architectural implication before each change.
3. Regenerate the Mermaid diagram with updates.
4. Stay opinionated: You could do that, but here is what I would recommend instead.

---

## Optional: Workload Profiling

Deploy when conversation naturally moves to workload specifics. Not a mandatory phase.

### Core Questions

1. Inference patterns - synchronous real-time, async batch, or mixed?
2. Agents - how many simultaneous runs, tool calls per run, max conversation length?
3. RAG - corpus size, update frequency, hybrid search needed?
4. Batch - record volume, acceptable turnaround window?
5. Fine-tuning - dataset size, base model, retraining frequency?
6. Evaluation criteria - groundedness, coherence, safety, latency, cost per query?

Use references/technical-deep-dives.md for deeper workload exploration.
