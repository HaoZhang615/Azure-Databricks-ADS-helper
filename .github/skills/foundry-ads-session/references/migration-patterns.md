# Migration Patterns

Detailed migration playbooks for organisations moving to Microsoft Foundry from existing platforms. Reference alongside Pattern 7 (Azure OpenAI to Foundry Migration) in foundry-patterns.md.

## Migration 1: Azure OpenAI Service to Microsoft Foundry

### Why Migrate
- Agent Service, evaluation SDK, multi-model access available only in Foundry
- Unified project-based governance and RBAC
- AzureML SDK v1 EOL: June 30 2026 � immediate migration priority
- Access to Phi-4, fine-tuning, and future model releases via Foundry portal

### Compatibility: Zero Code Change Path
Foundry exposes an OpenAI-compatible endpoint at:


Existing openai Python SDK code needs only two changes:
1. Update  to the new Foundry URL
2. Replace API key with  (Managed Identity)

All , , and  paths continue to work.

### Migration Phases

| Phase | Action | Risk | Validation |
|-------|--------|------|------------|
| 1 | Create Foundry resource + project alongside existing Azure OpenAI resource | Low � additive | Confirm portal access and project creation |
| 2 | Point canary app instance at Foundry compatibility endpoint | Low � shadow traffic | Compare output quality between old and new endpoint |
| 3 | Replace API key auth with Managed Identity | Medium � auth change | Test all app environments; ensure MI has Cognitive Services User role |
| 4 | Enable Content Safety in Foundry project | Low � additive | Test content filtering thresholds; tune if blocking legitimate queries |
| 5 | Migrate custom agent/orchestration logic to Agent Service | High � code change | Full integration test of agent workflows |
| 6 | Add azure-ai-evaluation to CI/CD | Low � additive | Baseline evaluation scores before code changes |
| 7 | Cut all traffic to Foundry; decommission Azure OpenAI resource | Medium � traffic switch | Monitor error rates for 48 hours post-cutover |

### RBAC Changes Required
- Remove API key dependency: disable API key access on Foundry resource (enforce Entra ID only)
- App managed identity needs:  on the Foundry resource
- Developers need:  on the AI Project
- Platform admins need:  on the Foundry resource

---

## Migration 2: LangChain / LangGraph Self-Hosted to Agent Service

### Why Migrate
- Self-hosted LangGraph requires maintaining agent state store, retry logic, and observability separately
- Agent Service provides managed state (Cosmos DB + Blob), built-in retry, and Application Insights integration
- Foundry Agent Service supports LangGraph as a hosted agent framework natively (as of 2025)

### Migration Approach
- LangGraph graphs can be deployed as hosted agents in Foundry Agent Service
- Replace self-managed Redis or Postgres state store with Agent Service standard setup (Cosmos DB)
- Replace custom retry with Agent Service built-in retry and max_iterations limit
- Surface LangGraph traces to Application Insights via opentelemetry integration

| Step | Self-Hosted (Before) | Agent Service (After) |
|------|---------------------|------------------------|
| State storage | Redis / Postgres (self-managed) | Cosmos DB + Blob (Agent Service standard setup) |
| Retry logic | Custom in application code | Agent Service built-in; configure max_iterations |
| Observability | Custom logging + Grafana | Application Insights native integration |
| Agent definition | Python class / YAML graph | Foundry agent object with tools, system prompt, model |
| Hosting | AKS / Container Apps self-managed | Foundry Agent Service managed runtime |

---

## Migration 3: Azure Cognitive Search Standalone to AI Search in Foundry

### Why Migrate
- AI Search is now the recommended RAG retrieval backend for Foundry Agent Service
- Native integration: agent can call AI Search as a built-in tool without custom connector code
- Semantic ranking, hybrid search (BM25 + vector), and integrated vectorisation available

### Migration Steps
1. Add AI Search as a connection in the Foundry AI Project
2. Create index with same schema as existing Cognitive Search index
3. Re-index documents from source (Blob Storage, SharePoint, or custom connector)
4. Enable semantic ranking on the new index
5. Replace custom retrieval code with Agent Service built-in AI Search tool
6. Run retrieval quality evaluation (compare old vs new recall@10)
7. Decommission standalone Cognitive Search resource

**Note**: Existing Cognitive Search indexes cannot be directly migrated � documents must be re-indexed. Plan for index rebuild time based on document volume.

---

## Migration 4: AzureML SDK v1 to azure-ai-projects

### Why Migrate (URGENT)
AzureML SDK v1 (, ) reaches End of Life on **June 30, 2026**. Security patches and bug fixes stop on that date.

### SDK Mapping

| AzureML SDK v1 | azure-ai-projects v1.x | Notes |
|----------------|------------------------|-------|
| MLClient | AIProjectClient | New client, same credential pattern |
| workspace.get_connection() | project.connections.get() | Connection management |
| AzureOpenAI via v1 workspace | project.inference.get_azure_openai_client() | Inference client factory |
| Job submission | Not directly equivalent | Use Agent Service for agentic workloads |
| Model registry | Foundry model catalog | Browse and deploy from Foundry portal |
| Compute clusters | Not in Foundry scope | Use Azure ML v2 for custom compute |

### Migration Timeline Recommendation
- **By April 2026**: Inventory all code using azureml-core or azureml-sdk
- **By May 2026**: Complete migration and testing in dev/staging
- **By June 2026**: Cut over to azure-ai-projects in production
- **After June 30 2026**: AzureML SDK v1 no longer receives security patches

---

## Migration 5: On-Premises AI/ML Platform to Foundry

### Common Sources
- On-premises GPU servers running PyTorch training jobs
- Self-hosted open-source models (Llama, Mistral) via Hugging Face
- Custom inference servers (Triton, TorchServe, vLLM)

### Migration Considerations

| Concern | On-Premises | Foundry Approach |
|---------|-------------|------------------|
| Model hosting | Self-managed GPU servers | Foundry model deployments (managed) |
| Open model access | Self-hosted Hugging Face models | Foundry model catalog: Phi-4, Llama, Mistral available |
| Data sovereignty | Local datacenter | Foundry private endpoint + VNet; single-region deployments |
| Inference cost | Capital expense (GPU hardware) | Operational expense (pay-per-token or PTU) |
| Fine-tuning | Custom training pipeline | Foundry fine-tuning jobs (limited to supported base models) |
| Latency | Local network | Azure region latency (typically 20-100ms for cloud) |

**When NOT to migrate to Foundry**: Custom model architectures (non-OpenAI, non-Foundry catalog models) still require Azure ML v2 or custom container deployment.

---

## Cross-Cutting Considerations

These apply to all migration paths above.

### Identity and Access
- All Foundry resources should use Microsoft Entra ID (Managed Identity) — disable API key access in production.
- Map existing RBAC roles to Foundry resource-level roles: Cognitive Services User (inference), Cognitive Services Contributor (manage deployments), Azure AI Developer (project-level).
- If migrating from API key-based auth: update all application code to use `DefaultAzureCredential` or `ManagedIdentityCredential`.
- Service principals need explicit role assignments on the Foundry resource and AI Project.

### Networking
- Production workloads should use private endpoints for the Foundry resource (`privatelink.cognitiveservices.azure.com`), AI Search, Cosmos DB, and Blob Storage.
- Agent Service standard setup requires a dedicated `/24` subnet for agent egress — plan VNet address space accordingly.
- DNS Private Resolver in the hub VNet is the recommended approach for private endpoint DNS resolution across spokes and on-premises.
- If the source platform used public endpoints: the migration to private endpoints is a separate workstream — do not combine with the application migration.

### DevOps and CI/CD
- Foundry does not have native Git integration like Fabric. Use `azure-ai-projects` SDK in CI/CD pipelines to deploy agent definitions, model deployments, and AI Search indexes programmatically.
- Implement `azure-ai-evaluation` as a quality gate in CI/CD: block deployment if groundedness, coherence, or relevance scores regress below baseline.
- Pin model versions in production deployments. Subscribe to Azure model deprecation announcements. Budget 2-4 weeks for re-validation when base models update.
- Use infrastructure-as-code (Bicep or Terraform) for all Foundry resources, private endpoints, and networking. Never provision manually in portal.

### Cost Management
- Model the token cost early: estimate prompt tokens + completion tokens per request × requests per day × 30 days. Compare GlobalStandard vs PTU pricing.
- PTU crossover point: PTU becomes cheaper when sustained utilisation exceeds ~65% of reserved capacity.
- Set Azure Cost Management alerts at 50%, 80%, and 100% of monthly AI budget.
- If migrating from a platform with different pricing (per-request, per-hour): build a cost comparison model before committing to Foundry deployment type.
- Agent Service token consumption includes tool call tokens — multi-tool agents consume significantly more tokens than simple chat. Model this explicitly.

---

*Last updated: March 2026. Sources: Azure AI Foundry docs, Azure Architecture Center, Azure Well-Architected Framework.*
