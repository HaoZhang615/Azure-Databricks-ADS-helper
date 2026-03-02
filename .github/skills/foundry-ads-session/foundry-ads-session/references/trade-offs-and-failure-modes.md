# Trade-offs and Failure Modes

Use this file to surface architectural trade-offs and known failure patterns during the ADS conversation. Do not volunteer all of these at once � introduce the relevant ones as design decisions arise.

## Trade-off 1: PTU vs Pay-Per-Token

| Dimension | ProvisionedManaged (PTU) | GlobalStandard (Pay-per-token) |
|-----------|--------------------------|--------------------------------|
| Cost model | Reserved capacity (hourly) | Per-token billed |
| Cost efficiency | Lower per-token above ~65% utilisation | Cheaper below ~65% utilisation |
| Latency predictability | High � no throttling under PTU limit | Variable � throttled at quota limit |
| Quota exhaustion | Hard cap at PTU limit (circuit to spillover) | Soft limit � 429 retry |
| Commitment | Monthly or annual reservation | No commitment |
| Best for | Production SLA, sustained high load | Dev/test, variable or unpredictable load |

**Crossover point**: PTU becomes cheaper than GlobalStandard when sustained token throughput exceeds approximately 65% of the reserved PTU capacity. Below that, pay-per-token wins. Use the Azure capacity calculator to model this.

**Recommendation**: Start with GlobalStandard. Add APIM spillover (Pattern 4) when you need SLA. Convert to PTU when traffic volume is proven and sustained.

---

## Trade-off 2: Agent Service Standard vs Basic Setup

| Dimension | Standard Setup | Basic Setup |
|-----------|---------------|-------------|
| State storage | Customer-owned Cosmos DB + Blob | Microsoft-managed |
| Data control | Full control, export anytime | Microsoft manages, limited export |
| Networking | Customer VNet compatible | Public only |
| Setup complexity | Higher � provision Cosmos DB, Blob, VNet | Minimal |
| Cost | Cosmos DB + Blob + egress charges | Included in Agent Service |
| Compliance | Meets CMK, private endpoint requirements | Does not meet strict isolation requirements |

**Recommendation**: Start with basic setup for prototyping. Migrate to standard setup before production if data residency, compliance, or private networking is required.

---

## Trade-off 3: Single Project vs Multi-Project Platform

| Dimension | Single Project | Multi-Project (Pattern 6) |
|-----------|---------------|---------------------------|
| Setup effort | Minimal | Significant (governance, tagging, RBAC) |
| Team isolation | None � shared RBAC scope | Per-project RBAC boundary |
| Cost chargeback | Not granular | Per-project tag-based chargeback |
| Resource sharing | N/A � all shared | Explicit: models shared, agent state isolated |
| Operations | Simple | Central platform team needed |
| When to use | Single team, single use case | 3+ teams, multi-domain AI platform |

**Recommendation**: Single project unless you have 3+ teams requiring isolation or explicit cost chargeback.

---

## Trade-off 4: Fine-Tuning vs Prompt Engineering vs RAG

| Approach | Cost | Maintenance | Best For |
|----------|------|-------------|----------|
| Prompt engineering | Lowest | Low | General tasks, quick iteration |
| RAG | Medium | Medium (index refresh) | Factual grounding, knowledge currency |
| Fine-tuning | Highest | High (retrain on model updates) | Consistent format, domain-specific style |

**Decision tree**:
1. Can prompt engineering solve it? -> Use prompt engineering first.
2. Does the AI need current factual knowledge? -> Add RAG.
3. Does the output have a required format or proprietary terminology that RAG + prompting cannot enforce? -> Consider fine-tuning.
4. Fine-tuning should be the last resort, not the first choice.

---

## Trade-off 5: MCP Hosted vs Custom MCP Server vs Inline Tools

| Approach | Effort | Flexibility | Governance |
|----------|--------|-------------|------------|
| Hosted MCP (mcp.ai.azure.com) | Minimal | Microsoft-curated tools | Microsoft-managed |
| Inline REST tools (in agent definition) | Low | Full custom | Self-managed |
| Custom MCP server (Azure Container App) | High | Unlimited | Self-managed |

**Recommendation**: Use hosted MCP for standard tools (Microsoft Learn, Bing, Azure). Use inline REST tools for 1-3 internal APIs. Build a custom MCP server only when sharing 4+ tools across multiple agents.

---

## Trade-off 6: New Foundry Portal vs Classic Portal

| Dimension | New Portal (ai.azure.com) | Classic Portal (ai.azure.com/classic) |
|-----------|---------------------------|---------------------------------------|
| Resource types | Foundry resources + Projects only | All: Hub-based, Project-based V1/V2, Azure OpenAI |
| UX | Streamlined, opinionated | Full-featured, complex |
| Agent Service | Full support | Limited |
| Prompt Flow | Basic (deprecated path) | Full Prompt Flow authoring |
| Model fine-tuning | Supported | Supported |
| Hub management | Not visible | Full hub management |
| Best for | New projects on Foundry resource | Managing legacy Hub-based resources |

**Recommendation**: Use new portal for all new projects. Switch to classic only when managing Hub-based legacy resources that are not yet migrated.

---

## Trade-off 7: Single Agent vs Multi-Agent Orchestration

| Dimension | Single Agent | Multi-Agent (Pattern 2) |
|-----------|-------------|-------------------------|
| Complexity | Low — one agent, one prompt | High — coordinator + specialists, routing logic |
| Debugging | Straightforward — single trace | Complex — trace spans multiple agents |
| Latency | Lower — no inter-agent routing | Higher — coordinator adds a hop per specialist |
| Capability | Limited by single system prompt | Unlimited — each agent is a specialist |
| Cost | Lower — fewer total tokens | Higher — coordinator + specialist tokens |
| When to use | Single domain, <10 tools | Multiple domains, >10 tools, distinct expertise areas |

**Decision tree**:
1. Can one agent with 5-10 tools handle all use cases? -> Single agent.
2. Do you need domain isolation (e.g. finance agent cannot call HR tools)? -> Multi-agent.
3. Are you building a platform where teams contribute their own agents? -> Multi-agent with MAF.

---

## Trade-off 8: Managed Compute vs Container Deployment for Agents

| Dimension | Agent Service (Managed) | Azure Container Apps (Self-hosted) |
|-----------|------------------------|------------------------------------|
| Ops effort | Minimal — Microsoft-managed | Full — you manage scaling, health, updates |
| Customisation | Agent Service API constraints | Unlimited — any framework (LangGraph, AutoGen, SK) |
| Networking | Standard: public; Standard setup: VNet | Full VNet integration |
| State management | Built-in thread/run persistence | You implement state store |
| Cost | Included in Foundry pricing | Container Apps + Foundry API calls |
| Best for | Standard chat/agent patterns | Custom orchestration, non-standard frameworks |

**Recommendation**: Start with Agent Service. Move to Container Apps only when Agent Service constraints block your architecture (custom framework, custom scaling, GPU sidecar).

---

## Trade-off 9: Content Safety — Strict vs Permissive Configuration

| Dimension | Strict (Low thresholds) | Permissive (High thresholds) |
|-----------|------------------------|------------------------------|
| False positive rate | High — blocks legitimate content | Low |
| Risk exposure | Low — catches most harmful content | Higher — some harmful content may pass |
| User experience | Frustrating if users hit filters frequently | Smooth — fewer interruptions |
| Compliance | Meets most regulatory requirements | May not meet strict content policies |
| Best for | Healthcare, government, customer-facing | Internal developer tools, creative applications |

**Recommendation**: Start strict. Monitor false positive rates for 2 weeks. Loosen category thresholds individually based on data, not assumptions. Always keep self-harm and violence at strictest level.

---

## Trade-off 10: AI Search vs Cosmos DB Vector Search for RAG

| Dimension | Azure AI Search | Cosmos DB (NoSQL + Vector) |
|-----------|----------------|---------------------------|
| Query capability | Full-text + vector + hybrid + semantic ranking | Vector similarity + NoSQL filter |
| Document processing | Built-in skillsets (chunking, embedding, OCR) | You implement chunking + embedding pipeline |
| Security filtering | Row-level security via security filters | Partition-based isolation |
| Ops complexity | Managed PaaS, minimal ops | Managed PaaS, but indexing pipeline is custom |
| Cost model | Per-unit (SU) pricing, index size-based | RU/s + storage, throughput-based |
| Best for | Document-heavy RAG, enterprise search | Transactional data + vector, multi-model DB |

**Recommendation**: AI Search for document-centric RAG (PDFs, policies, manuals). Cosmos DB vector when the data is already in Cosmos DB for transactional purposes and you want to add semantic search without a separate service.

---

# Failure Modes

Use these to test resilience thinking during the ADS conversation. When a customer proposes an architecture, ask: "What happens when [failure mode]?" If they cannot answer, walk through the scenario together.

---

### 1. Token Rate Limit Exhaustion (429 Throttling)

**Scenario**: Application hits the TPM (tokens per minute) or RPM (requests per minute) quota on a GlobalStandard deployment; all subsequent requests receive HTTP 429 responses until the rate window resets.

**Detection**: Application logs show HTTP 429 responses with `Retry-After` header. Azure Monitor metrics show `Throttled Requests` spike. End users experience timeouts or error messages. APIM analytics (if Pattern 4) show 429 pass-through.

**Blast Radius**: All applications sharing the same deployment. If no spillover is configured, the entire AI capability is unavailable for the throttle duration. Agentic workflows mid-execution may fail irrecoverably if retry logic is absent.

**Containment**:
1. If APIM Gateway (Pattern 4) is deployed: circuit-break to GlobalStandard spillover automatically.
2. If no gateway: implement exponential backoff with jitter in the application SDK.
3. Prioritise workloads: queue low-priority batch requests, serve interactive users first.

**Recovery**:
1. Rate window resets within 10-60 seconds depending on the quota tier.
2. If sustained overload: increase TPM quota in the deployment (self-service up to regional limit).
3. If at regional limit: add a second deployment in another region behind APIM.

**Prevention**: Implement APIM AI Gateway (Pattern 4) with PTU primary and GlobalStandard spillover. Set APIM rate-limit policies per consumer app. Monitor TPM/RPM usage at 80% threshold — alert before hitting the limit. Size PTU capacity for peak sustained load, not average.

---

### 2. RAG Hallucination — Grounded Answer Cites Wrong Source

**Scenario**: The AI returns a confident, well-structured answer that cites retrieved documents, but the answer contradicts the actual document content or synthesises information across documents incorrectly.

**Detection**: User reports incorrect information. Evaluation pipeline shows groundedness score drop below threshold. Manual spot-check of citations reveals mismatches between answer text and source content. A/B test against golden dataset shows regression.

**Blast Radius**: User trust erosion — once users see one wrong answer, they distrust all answers. In regulated industries (healthcare, finance), a hallucinated answer may trigger compliance incidents.

**Containment**:
1. Enable source citation display in the application so users can verify.
2. Add a disclaimer: "AI-generated — verify critical information against source documents."
3. For high-stakes use cases: require human review before the answer is surfaced.

**Recovery**:
1. Run azure-ai-evaluation groundedness evaluator on recent outputs to quantify the problem.
2. Check AI Search index quality: are chunks too large, too small, or missing key context?
3. Check system prompt: does it instruct the model to only use retrieved content?
4. Check retrieval: is hybrid search (keyword + vector) enabled? Keyword-only often misses semantic matches; vector-only misses exact terms.

**Prevention**: Implement azure-ai-evaluation in CI/CD with groundedness >= 4.0/5 gate. Use hybrid search (keyword + vector + semantic ranker) in AI Search. Chunk documents at 512-1024 tokens with 10-15% overlap. Include document title and section header in each chunk for context. Set system prompt to explicitly say: "Only answer based on the retrieved documents. If the documents do not contain the answer, say so."

---

### 3. Agent Tool Loop — Agent Calls Same Tool Repeatedly

**Scenario**: Agent enters an infinite loop calling the same tool repeatedly, consuming tokens without making progress. The agent run burns through budget and eventually times out.

**Detection**: Agent run duration exceeds expected maximum. Token consumption spikes for a single run. Tool call logs show the same tool called 5+ times with identical or near-identical parameters. Run eventually fails with timeout or token limit error.

**Blast Radius**: Single user's agent run. But if the agent is on a shared PTU deployment, the loop consumes capacity that degrades other users. Cost impact can be significant for long-running loops on pay-per-token.

**Containment**:
1. Set `max_turns` on Agent Service runs (default is unlimited — always set a limit).
2. Monitor per-run token consumption and kill runs exceeding a threshold.
3. Implement tool-call deduplication: if the agent calls the same tool with the same parameters twice, return a canned response instead of re-executing.

**Recovery**:
1. Cancel the stuck agent run via SDK: `agent_client.runs.cancel(run_id)`.
2. Review the tool call trace to identify why the agent looped (usually: tool returned an error the agent could not interpret, or tool output did not satisfy the agent's goal).
3. Fix the tool implementation to return clearer error messages or a structured "no result" response.

**Prevention**: Always set `max_turns` (recommend 10-15 for complex workflows, 5 for simple Q&A). Implement per-run token budgets. Add tool-level retry limits. Design tools to return structured errors: `{"status": "error", "message": "...", "suggestion": "try X instead"}`. Test agent workflows with adversarial inputs that are designed to trigger loops.

---

### 4. Content Safety False Positives — Legitimate Content Blocked

**Scenario**: Content Safety filters block legitimate business content (medical terminology, legal language, security research terms) causing the AI to refuse valid requests.

**Detection**: Users report "I can't ask about [legitimate topic]." Application logs show Content Safety filter triggers on categories that should be allowed. Evaluation pipeline shows increased refusal rate on valid test cases.

**Blast Radius**: All users of the application. In domain-specific applications (healthcare, legal, cybersecurity), false positives can render the AI useless for its primary purpose.

**Containment**:
1. Identify which Content Safety category is triggering (hate, sexual, violence, self-harm).
2. Review the specific input that was blocked — is it genuinely a false positive?
3. Temporarily adjust the threshold for that category from Low to Medium.

**Recovery**:
1. Adjust Content Safety configuration: raise severity threshold for the specific category causing false positives.
2. Use custom blocklists to be more precise instead of broad category thresholds.
3. For domain-specific needs: request a Content Safety exception via Azure support (available for healthcare and security research scenarios).

**Prevention**: Test Content Safety configuration with domain-specific test cases before go-live. Include medical, legal, or security terminology in your evaluation dataset. Start with default thresholds, then tune per-category based on false positive data — not assumptions. Document the business justification for any threshold changes. Review monthly as Content Safety models are updated.

---

### 5. Cost Runaway — Unexpected Token Consumption Spike

**Scenario**: A new feature deployment, prompt change, or traffic increase causes token consumption to spike 5-10× above budget; monthly AI bill is unexpectedly large.

**Detection**: Azure Cost Management alerts trigger on daily spend exceeding threshold. APIM token logging (Pattern 4) shows per-app consumption spike. Azure Monitor metrics show TPM increase without corresponding user traffic increase (indicates prompt bloat or retry storms).

**Blast Radius**: Organisation's AI budget. If PTU, no cost increase but performance degrades for other workloads. If pay-per-token, direct financial impact. May trigger emergency budget review and freeze new AI development.

**Containment**:
1. Identify the source: which app, which endpoint, which deployment?
2. If a single app: apply APIM rate-limit policy to cap that app's consumption.
3. If prompt change: roll back to previous prompt version.
4. If retry storm: fix the application's retry logic (exponential backoff, not immediate retry).

**Recovery**:
1. Analyse token consumption by app, deployment, and time window to find the root cause.
2. If prompt bloat: optimise system prompt and few-shot examples (shorter prompts = fewer tokens).
3. If traffic spike: right-size deployment (PTU if sustained, GlobalStandard if bursty).
4. Implement per-app token budgets in APIM.

**Prevention**: Set Azure Cost Management alerts at 50%, 80%, 100% of monthly budget. Implement per-app rate limits in APIM. Log token consumption per request (prompt tokens + completion tokens). Review prompt token efficiency monthly — shorter system prompts save significant cost at scale. Use GPT-4o mini for tasks that don't need GPT-4o capability.

---

### 6. Fine-Tune Regression — Updated Base Model Breaks Fine-Tuned Model

**Scenario**: A new base model version is released (e.g. GPT-4o-2024-08 → GPT-4o-2025-01); the fine-tuned model based on the old version is deprecated, and re-fine-tuning on the new version produces different (possibly worse) outputs.

**Detection**: Evaluation pipeline shows quality metrics regression after re-fine-tuning. Output format or style changes noticeably. Domain-specific terminology handling degrades. Users report "the AI changed" without any application code changes.

**Blast Radius**: All applications consuming the fine-tuned model deployment. If the old model version is deprecated with a hard deadline, the regression is forced.

**Containment**:
1. Deploy the re-fine-tuned model to a DeveloperTier deployment first — never directly to production.
2. Run the full evaluation suite against the new fine-tuned model before any traffic shift.
3. If regression: keep the old model version running until the evaluation gate passes.

**Recovery**:
1. Augment training data: add examples that cover the regressed scenarios.
2. Adjust hyperparameters: reduce learning rate, increase epochs if underfitting.
3. If the new base model is fundamentally different: re-curate the training dataset for the new model's behaviour.
4. Consider switching to prompt engineering + RAG if fine-tuning maintenance cost exceeds value.

**Prevention**: Pin base model versions in production. Subscribe to Azure model deprecation announcements. Maintain a golden evaluation dataset that covers all critical scenarios. Run evaluation automatically on every fine-tuning job before deployment. Budget 2-4 weeks for re-fine-tuning when model versions change.

---

### 7. Private Endpoint DNS Resolution Failure

**Scenario**: Foundry resource private endpoint is configured, but DNS resolution returns the public IP instead of the private IP; traffic is blocked by the "deny public access" policy or routes through the internet instead of the VNet.

**Detection**: Application receives connection timeout or "access denied" when calling Foundry API. `nslookup <foundry-resource>.cognitiveservices.azure.com` returns a public IP instead of a 10.x.x.x private IP. Azure Firewall logs show no traffic (traffic never reaches the private endpoint). Application works from a VM in the same VNet but fails from on-premises or another spoke.

**Blast Radius**: All applications that need to reach the Foundry resource from the affected network location. If DNS is misconfigured at the hub level, all spokes are affected.

**Containment**:
1. Verify DNS resolution from the failing client: `nslookup <resource>.cognitiveservices.azure.com`.
2. If public IP returned: the DNS Private Zone is not linked to the client's VNet or the DNS forwarder is not configured.
3. Temporarily allow public access on the Foundry resource to restore service while DNS is fixed.

**Recovery**:
1. Ensure the private DNS zone (`privatelink.cognitiveservices.azure.com`) is created and contains the A record for the resource.
2. Link the private DNS zone to the VNet where the client resides.
3. If using hub DNS: ensure DNS Private Resolver or custom DNS server forwards `privatelink.*` zones correctly.
4. For on-premises clients: configure conditional DNS forwarders to point `privatelink.cognitiveservices.azure.com` to the Azure DNS Private Resolver inbound endpoint.

**Prevention**: Use Azure DNS Private Resolver in the hub VNet — it handles all private DNS zone resolution for peered spokes and on-premises clients. Automate private DNS zone creation and VNet linking via Bicep/Terraform. Test DNS resolution from every network segment (hub, spoke, on-prem) during deployment, not after. Include DNS validation in the deployment pipeline as a post-provisioning check.

---

*Last updated: March 2026. Sources: Microsoft Foundry docs, Azure Architecture Center, Azure Well-Architected Framework.*
