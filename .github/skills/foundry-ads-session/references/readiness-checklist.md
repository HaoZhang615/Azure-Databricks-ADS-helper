# Readiness Checklist - Microsoft Foundry ADS

Evaluate information completeness before generating the architecture diagram.

## Readiness Score Calculation

```
Score = (must_have_gathered / must_have_total) * 60
      + (should_have_gathered / should_have_total) * 30
      + (nice_to_have_gathered / nice_to_have_total) * 10

Ready to generate:     All must-haves gathered AND score >= 75
Generate with caveats: All must-haves gathered AND score >= 50
Not ready:             Any must-have missing
```

## Must-Have Items

Cannot generate a diagram without these.

| Item | Why It Matters | Default If Forced | Probing Question |
|------|---------------|-------------------|------------------|
| **Primary AI use case** | Determines architecture pattern | None - must have | What AI capability are you building? |
| **Deployment model** | Feature set differs: new Foundry Projects has Foundry IQ; Hub-based has Prompt Flow | Assume new Foundry Projects unless Prompt Flow mentioned | Are you starting fresh, or do you have existing Azure AI Foundry resources? Do you use Prompt Flow today? |
| **Model selection** | Determines endpoint type, pricing, availability | GPT-4o GlobalStandard PAYG | Which model - GPT-4o, o3, or another? OpenAI only, or open-source like Llama or Phi? |
| **Network posture** | Determines private endpoints and VNet requirements | Public endpoints | Does your security team require all traffic on a private network? |
| **Agent setup type (agents only)** | Standard = customer-owned Cosmos DB + Storage + AI Search. Basic = Microsoft-managed. | Basic Agent Setup | Does conversation history need to be stored in your own subscription for compliance? |
| **Success metrics / KPIs** | Without this, no definition of done | None - must have | What does success look like? Latency SLA, response quality, cost per query? |

## Should-Have Items

Generate with stated assumptions if missing after 1 follow-up.

| Item | Why It Matters | Default Assumption | Probing Question |
|------|---------------|-------------------|------------------|
| **Knowledge sources (RAG)** | Determines AI Search indexing strategy, chunking, update frequency | Single Azure Blob Storage corpus | What knowledge sources will your AI access? SharePoint, Blob, SQL, APIs? |
| **Capacity: PAYG vs PTU** | PTU ~40-60% savings requires pre-commitment | GlobalStandard PAYG | Do you have a projected query volume? Sustained load may justify PTU. |
| **Authentication approach** | Affects Managed Identity config, Entra ID integration | Managed Identity + Entra ID | How will your app authenticate to Foundry - Managed Identity, service principal, or API key? |
| **Evaluation and safety** | Determines content filters and evaluation strategy | Default content filter | How will you measure AI response quality? Topics the model must never discuss? |
| **Integration points** | Determines APIM, Logic Apps, or direct SDK | Direct SDK calls | What systems call your AI - web app, backend service, automated workflow? |
| **Compliance requirements** | Affects encryption, audit, CMK | No specific compliance | HIPAA, SOC2, GDPR, FedRAMP? |
| **At least one trade-off decision** | Validates alternatives were considered | None - must discuss | Which design trade-off felt most significant? |
| **One failure-mode walkthrough** | Validates resilience thinking | Assume no resilience planning | What happens when your AI endpoint returns a 429 during peak load? |
| **Operating model** | Who owns, monitors, pays | Central platform team | Who will own this in production? |

## Nice-to-Have Items

Use sensible defaults without asking.

| Item | Default Assumption | Override Signal |
|------|--------------------|------------------|
| Foundry IQ vs custom RAG | Custom RAG | User wants managed RAG with no retrieval code - Foundry IQ if on new Foundry Projects |
| Multi-agent vs single-agent | Single agent with tools | Complex workflows with handoffs - Multi-Agent Framework |
| Fine-tuning vs RAG vs prompting | RAG first | Narrow domain, under 10K quality examples, latency requirements |
| APIM gateway | No gateway (direct SDK) | Rate limiting, multi-model routing, multiple consumer teams |
| Monitoring tools | Azure Monitor + AI Foundry tracing | Datadog, Grafana, custom dashboards |
| CI/CD for prompts/agents | Manual deployment initially | MLOps maturity - add GitHub Actions pipeline |
| PTU spillover | No spillover config | User buying PTU - configure GlobalStandard spillover to avoid hard 429s |
| Content safety | Default Azure AI Content Safety filters | Consumer-facing or high-risk domain - custom blocklists + evaluation |
| Prompt caching | Not configured | Repeated prefix patterns (RAG system prompts) and cost sensitivity |
| Batch vs real-time | Real-time inference | Document processing, report generation, overnight jobs |
| Regional deployment | Single region | Geo-redundancy, data residency, or global users - multi-region with Traffic Manager |
| SDK version | azure-ai-projects 2.0.0b4 for new Foundry Projects; 1.0.0 GA for Hub-based | User on Hub-based - use GA SDK |
| AzureML dependency | Not applicable | ML training workloads - AzureML SDK v1 EOL June 30 2026, migrate to v2 |

## Pre-Generation Summary Template

Before generating the diagram, confirm requirements with the user:

```
## Architecture Requirements Summary

Use Case: [AI capability being built]
Pattern: [selected pattern from foundry-patterns.md]
Deployment Model: [New Foundry Projects / Hub-based]
Industry: [if applicable]

AI Capability:
- Model: [GPT-4o GlobalStandard PAYG / PTU ProvisionedManaged]
- Agent Setup: [Basic / Standard - if applicable]
- Capacity: [PAYG / PTU at X TPM]

Knowledge and Data (RAG):
- Sources: [Azure Blob, SharePoint, SQL Database]
- Search: [Azure AI Search - Basic / Standard / Storage Optimized]
- Update frequency: [real-time / daily / weekly]

Integration:
- Consumers: [web app / API / workflow]
- Gateway: [APIM / direct SDK]
- Auth: [Managed Identity / service principal]

Security and Networking:
- Network: [public / private / VNet]
- Compliance: [frameworks]
- Encryption: [Microsoft-managed / CMK]

Assumptions Made:
- [Assumption 1]: [reason]
- [Assumption 2]: [reason]

Does this accurately capture your requirements? Anything to add or correct?
```
