---
name: foundry-ads-session
description: Conduct Microsoft Foundry (Microsoft Foundry) Architecture Design Sessions (ADS). Orchestrate a structured multi-turn conversation to gather solution requirements across any AI/ML use case (enterprise chat, agentic workflows, multi-agent orchestration, RAG, fine-tuning, batch inference, real-time scoring, etc.), then generate a Foundry-centric architecture diagram. Use when the user wants to (1) design a Microsoft Foundry solution, (2) run an architecture design session for an AI/ML platform, (3) scope a Foundry migration or greenfield AI project, (4) gather requirements for an enterprise AI platform, or (5) generate a Microsoft Foundry architecture diagram from requirements.
license: MIT
compatibility: Works with Claude Code, GitHub Copilot, VS Code, Cursor, and any Agent Skills compatible tool. PNG export requires Node.js (npx @mermaid-js/mermaid-cli). Fallback is Mermaid in Markdown preview.
metadata:
  author: community
  version: "1.0"
  domain: Microsoft Foundry (Microsoft Foundry)
---

# Microsoft Foundry ADS Session

This skill provides **domain-specific knowledge for Microsoft Foundry (Microsoft Foundry)** to be used within an Architecture Design Session. The ADS methodology (persona, pacing, session structure, decision narration, trade-off framework, self-critique) is defined in the runtime system prompt. This skill supplies the Foundry-specific questions, patterns, components, and references that the methodology operates on.

## Domain: Microsoft Foundry

This skill covers the Microsoft Foundry unified AI platform including:

- **Resource Model**: Foundry resource (`Microsoft.CognitiveServices/account` kind=`AIServices`) + project subresource; Classic Hub (`Microsoft.MachineLearningServices/workspaces` kind=`Hub`) + Project (legacy, still supported as Foundry Classic)
- **SDK / API**: `azure-ai-projects` v1.0.0 (GA Jul 2025, Foundry Classic) and v2.0.0b4+ (Preview Feb 2026, new Foundry portal); `azure-ai-inference`, `azure-ai-evaluation`, `azure-ai-agents`; OpenAI-compatible client via `get_openai_client()`
- **Agent Service**: Multi-agent framework (MAF), hosted agents (LangGraph, custom frameworks), standard vs basic agent setup; Foundry MCP Server (`mcp.ai.azure.com`)
- **Model Deployment**: GlobalStandard, GlobalProvisionedManaged, GlobalBatch, DataZoneStandard, DataZoneProvisionedManaged, DataZoneBatch, Standard, ProvisionedManaged, DeveloperTier; MaaS (serverless) vs MaaP (managed online endpoint)
- **Networking**: Public, Private Link (`privatelink.cognitiveservices.azure.com`), Managed VNet with outbound rules; agent subnet injection (RFC-1918 /24)
- **Identity & Security**: Managed Identity (system/user-assigned), Entra ID, `DefaultAzureCredential`; RBAC roles (Azure AI User, Azure AI Project Manager, Contributor); CMK encryption; Content Safety; Key Vault
- **Observability**: Azure Monitor, Application Insights, OpenTelemetry tracing via `azure-ai-projects`; token usage metrics, latency, evaluation scores
- **Enterprise Patterns**: Landing zone integration, hub-spoke networking, multi-region design, dev/test/prod, governance, cost management, chargeback

## Phase-Specific Foundry Questions

### Phase 1: Context Discovery

Ask about:
- Business problem or opportunity driving this initiative
- Industry and regulatory context
- Greenfield project vs. migration from existing system (Azure OpenAI standalone, AzureML workspaces, on-prem LLM, Databricks MLflow)
- Primary AI use case: enterprise chat, RAG grounding, agentic workflows, batch inference, fine-tuning, real-time scoring, or multi-agent orchestration
- Key stakeholders: AI engineers, data scientists, app developers, security/infra teams
- Timeline, budget constraints, and success criteria
- Expected user base and request volume (tokens per minute / requests per minute)
- Microsoft licensing context (Azure subscription tier, EA agreement, PAYG)

Adapt: If user mentions migration, read [references/migration-patterns.md](references/migration-patterns.md). If user names a specific industry, read [references/industry-templates.md](references/industry-templates.md) for starter context.

### Phase 2: Current Landscape

Ask about:
- Existing AI/ML workloads and platforms (Azure OpenAI Service, AzureML, Databricks, HuggingFace, on-prem GPU clusters)
- Data sources for grounding/RAG (databases, SharePoint, Blob Storage, Azure AI Search existing indexes)
- Current model preferences or constraints (GPT-4o, o1, o3-mini, Phi-4, third-party OSS via MaaS)
- Agent tooling already in use (LangChain, Semantic Kernel, custom REST tools, MCP servers)
- Existing observability stack (Application Insights, Datadog, custom logging)
- CI/CD and MLOps maturity (manual deployments vs. automated pipelines)

See [references/probing-questions.md](references/probing-questions.md) for deep-dive question banks when the user answers are vague or incomplete.

### Phase 3: Security & Networking

Ask about:
- Network topology: public endpoints (default), Private Link, Managed VNet with outbound rules
- Private endpoint DNS: customer-managed private DNS zones vs. Azure Private DNS Zones
- Identity model: Managed Identity (system or user-assigned) vs. API key authentication
- RBAC requirements: who gets Azure AI User, Azure AI Project Manager, Contributor/Owner roles
- Data exfiltration controls: Managed VNet egress rules, approved outbound endpoints
- Regulatory compliance: HIPAA, SOC2, GDPR, FedRAMP, financial services regulations
- Encryption: Microsoft-managed keys (default) vs. Customer-Managed Keys (CMK) via Key Vault
- Content Safety requirements: prompt injection filtering, harmful content detection, groundedness
- Agent standard setup requirements: customer-owned Cosmos DB, Storage, AI Search in customer VNet

### Phase 4: Operational Requirements

Ask about:
- HA/DR requirements and RPO/RTO targets
- Zone redundancy: Cosmos DB (ZRS/GZRS), Blob Storage (ZRS/GZRS), AI Search (3+ replicas)
- Multi-region design: custom APIM/AGW gateway layer required (no native multi-region)
- Capacity model: pay-per-token GlobalStandard vs. reserved PTUs ProvisionedManaged vs. GlobalBatch 24hr async
- Token throughput planning: PTU sizing, spillover configuration, APIM rate limiting policies
- Environment strategy: separate Foundry projects per dev/test/prod vs. shared project with deployment promotion
- Monitoring: Azure Monitor metrics, Application Insights traces, OpenTelemetry integration
- Cost allocation: tagging strategy (tenantId, costCenter, application, environment, owner), Cost Management exports
- Operating model: who owns fine-tuned models, who approves new deployments, who triages latency incidents

Use [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) for domain-specific failure scenarios to raise proactively during this phase.

## Readiness Gate

After each phase, internally track information completeness using [references/readiness-checklist.md](references/readiness-checklist.md).

### Decision Logic

```
IF all must-have items are gathered:
    -> Proceed to diagram generation
IF some should-have items are missing:
    -> State assumptions explicitly, ask user to confirm or correct
IF must-have items are missing:
    -> Ask targeted follow-up questions (max 2 additional turns)
IF user says "just generate something" or expresses impatience:
    -> Generate with sensible defaults, document all assumptions
```

Always tell the user what you know and what you are assuming before generating.

## Foundry Diagram Components

When generating diagrams, use these Foundry-specific node shapes (extends the generic style guide from the architecture-diagramming skill):

| Component Type | Shape | Mermaid Syntax | Example |
|----------------|-------|----------------|---------|
| **AI Foundry Resource / Project** | Rectangle | `[Name]` | `[Foundry Resource]`, `[AI Project]` |
| **Model Deployment / Endpoint** | Rectangle | `[Name]` | `[GPT-4o GlobalStandard]` |
| **Storage (Blob, Cosmos DB, AI Search)** | Cylinder | `[(Name)]` | `[(AI Search Index)]`, `[(Cosmos DB)]` |
| **Security (Entra ID, Key Vault, Content Safety)** | Rounded | `(Name)` | `(Entra ID)`, `(Key Vault)` |
| **Networking (Private Endpoint, APIM, App Gateway)** | Hexagon/Stadium | `{{Name}}` / `([Name])` | `{{Private Endpoint}}`, `([APIM])` |
| **External / On-Prem / Third-Party Systems** | Double-bordered | `[[Name]]` | `[[On-Prem Data Source]]` |
| **Applications (App Service, Container Apps)** | Rectangle | `[Name]` | `[Container App]` |

### Pattern Selection

Match gathered requirements to a Foundry architecture pattern. Read [references/foundry-patterns.md](references/foundry-patterns.md) for the pattern catalog.

Common patterns:

| Use Case | Pattern |
|----------|---------|
| Enterprise chat with RAG grounding | Baseline Chat (RAG + Agent Service standard setup) |
| Multi-step agentic workflows | Multi-Agent Orchestration (MAF) |
| Large-scale async bulk processing | Batch Inference (GlobalBatch deployment) |
| High-throughput real-time scoring with SLA | PTU Gateway (ProvisionedManaged + APIM) |
| Domain-specific custom model | Fine-Tuning + Custom Deployment pipeline |
| Multi-team AI platform with isolation | Multi-Project Platform (Hub + Projects) |
| Moving from Azure OpenAI standalone | Azure OpenAI -> Foundry Migration |
| Full enterprise governance + private networking | Enterprise Landing Zone |

### Generating the Diagram

Generate a Mermaid `flowchart` diagram based on the gathered requirements. Use the pattern templates in [references/foundry-patterns.md](references/foundry-patterns.md) as a starting point, then customise based on the specific requirements gathered.

Follow the architecture-diagramming skill's style guide for general Mermaid conventions (arrow styles, subgraph naming, layout direction). Apply the Foundry-specific node shapes listed above.

For rendering, Architecture Recap format, and iteration workflow, defer to the architecture-diagramming skill.

## Optional: Workload Profiling

These questions are **not a mandatory phase** � the customer may or may not raise workload-specific topics during the session. Have this content ready to deploy when the conversation naturally moves toward workloads, but do not force it as a separate phase.

If the customer discusses workloads, ask about:
- Inference workloads: expected TPM, peak RPM, latency SLA (P50/P99), synchronous vs. async
- Agent workloads: number of agents, tool call frequency, max conversation turns, state persistence requirements
- RAG pipeline: document corpus size, update frequency, chunking strategy, hybrid search (semantic + keyword)
- Batch workloads: record count, acceptable turnaround time (hours vs. days), cost sensitivity
- Fine-tuning: training data size, base model selection, evaluation pass criteria, re-training frequency
- Evaluation: groundedness, coherence, safety thresholds; automated vs. human-in-the-loop review
- Multi-model routing: model fallback chains, model comparison A/B testing, cost vs. quality routing

If a workload area warrants deeper exploration, offer a Technical Deep-Dive using [references/technical-deep-dives.md](references/technical-deep-dives.md).

## Foundry Expertise

You know Microsoft Foundry inside-out: the difference between GlobalStandard pay-per-token and ProvisionedManaged reserved PTUs, when Agent standard setup costs are justified, why managed VNet egress rules beat open public networking, and how the new Foundry resource model (AIServices kind) differs from the classic Hub/Project model. Connect technical decisions to business outcomes: "ProvisionedManaged" is not just a deployment type - it is the latency guarantee that makes real-time customer-facing AI viable at scale. "Agent standard setup" is not just extra Cosmos DB overhead - it is the isolation boundary that satisfies enterprise compliance requirements. Translate tech into value.

## Reference Files

| File | Load When |
|------|-----------|
| [references/conversation-framework.md](references/conversation-framework.md) | Understanding full phase detail, signal detection, and transition logic |
| [references/foundry-patterns.md](references/foundry-patterns.md) | Selecting architecture pattern before diagram generation |
| [references/readiness-checklist.md](references/readiness-checklist.md) | Evaluating if enough information has been gathered |
| [references/industry-templates.md](references/industry-templates.md) | User mentions a specific industry vertical |
| [references/migration-patterns.md](references/migration-patterns.md) | User is migrating from an existing platform |
| [references/probing-questions.md](references/probing-questions.md) | User gives vague answers and needs deeper probing |
| [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) | Trade-off analysis or failure mode walkthrough needed |
| [references/technical-deep-dives.md](references/technical-deep-dives.md) | User accepts a technical deep-dive on a workload topic |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate_architecture.py](scripts/generate_architecture.py) | Generate Mermaid diagram code for a given Foundry architecture pattern |
