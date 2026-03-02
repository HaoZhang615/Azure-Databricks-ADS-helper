# Probing Questions

Load this file when the user gives vague or incomplete answers during the ADS conversation. Use the relevant section to dig deeper with progressive follow-up questions.

## AI Workload Type

**Context**: User says "we need AI" or "we want to use GPT" without specifying the workload shape.

**Progressive Questions**:
1. "Is this primarily a chat or Q&A interface for internal users, or is it automated processing in the background?"
2. "Does the AI need to take actions — call APIs, query databases, run code — or just answer questions?"
3. "Is this a single-turn interaction, or does the AI maintain context across a multi-turn conversation?"
4. "Do you need to process large batches of documents overnight, or respond to users in real time?"
5. "Is there a need for multiple specialised agents — one for research, one for data, one for writing — or a single general-purpose agent?"
6. "Do you already have agent code in LangGraph, AutoGen, or Semantic Kernel that you want to bring in?"

**Red Flags**:
- "We want AI on our data" without specifying who uses it or how. Push for a concrete user scenario.
- "We need an agent" when a simple RAG chat would suffice. Agents add orchestration complexity.
- "We want to automate everything." Identify the single highest-value workflow to start.

---

## Model Selection

**Context**: User says "we need GPT-4" or "the latest model" without considering cost or capability fit.

**Progressive Questions**:
1. "What tasks will the model perform: summarisation, classification, code generation, reasoning, multilingual?"
2. "What languages does the content use? If non-English is primary, test model quality on that language."
3. "Is cost per query a constraint? GPT-4o mini is 15x cheaper than GPT-4o for many tasks."
4. "Do you have data sovereignty requirements that prevent data leaving specific Azure regions?"
5. "Have you considered Phi-4 for lower-cost on-premises scenarios or edge deployment?"
6. "Do you need multimodal capabilities — processing images, audio, or documents with mixed content?"

**Red Flags**:
- "We need the most powerful model." Capability overkill drives unnecessary cost. Right-size to the task.
- "We will use GPT-4o for everything including simple classification." GPT-4o mini handles classification at a fraction of the cost.
- No awareness of Phi-4 for small/open model scenarios. Surface it as a cost-efficient alternative.

---

## RAG and Knowledge Sources

**Context**: User says "we want to ground AI on our data" without specifying the knowledge base.

**Progressive Questions**:
1. "What documents or data will the AI be grounded on — internal policies, product manuals, customer data, code documentation?"
2. "Where does this content live today: SharePoint, Confluence, blob storage, databases, PDFs on file shares?"
3. "How frequently does the knowledge base change? Daily, weekly, or is it relatively static?"
4. "Approximately how many documents or pages are in scope? This affects AI Search index sizing."
5. "Are there documents the AI should never have access to — confidential HR files, M&A documents?"
6. "Do different user groups need different document visibility? Row-level security in AI Search handles this."
7. "Is semantic (meaning-based) search sufficient, or do you need keyword precision for regulatory queries?"

**Red Flags**:
- "All our data" without scoping. Large unscoped corpora degrade retrieval quality and increase cost.
- No document access control plan. If different users should see different documents, this is a day-one design decision.
- "We will index everything and let the AI decide." Noise in the index degrades answer quality.

---

## Deployment Type and Throughput

**Context**: User assumes pay-per-token is fine, or conversely insists on PTU without understanding the cost.

**Progressive Questions**:
1. "What is the expected peak requests per minute? And the expected daily total requests?"
2. "What latency is acceptable for users? Under 1 second, under 3 seconds, or can they wait 10+ seconds?"
3. "Is there a hard SLA requirement — for example, 99.9% availability with defined p95 latency?"
4. "Will traffic be consistent throughout the day or bursty — for example, everyone using it during business hours only?"
5. "Are you processing records overnight in bulk? GlobalBatch costs 50% less than Standard for async workloads."
6. "Does the organisation operate across multiple geographies? DataZone types ensure data stays in EU or US."

**Red Flags**:
- No throughput estimate at all. Cannot size PTU without a baseline — ask for order of magnitude.
- "We will use PTU because it is better." PTU is cost-effective only above ~65% utilisation. Below that, pay-per-token wins.
- "We need real-time and cheap." Real-time + cheap are in tension. Surface the trade-off explicitly.

---

## Security and Networking

**Context**: User says "standard security" or has not thought about network topology.

**Progressive Questions**:
1. "Does your organisation have an Azure landing zone or hub-spoke VNet topology already deployed?"
2. "Can the AI application call out to public internet endpoints, or does all traffic need to stay on-VNet?"
3. "Does Foundry need to reach on-premises data sources? If so, we need VPN/ExpressRoute and private endpoints."
4. "Is customer-managed encryption (CMK) required, or is Microsoft-managed encryption acceptable?"
5. "For agent subnet injection, we need a dedicated /24 subnet. Do you have that available in your VNet?"
6. "Is there a security review or Azure Policy set that all resources must pass?"

**Red Flags**:
- "No special security" from regulated industries. Explicitly confirm this with the security team, not just the developer.
- User has no /24 available for agent subnet injection. This is a hard requirement for Agent Service standard setup.
- "We will add private endpoints later." Network architecture is a day-one decision — retrofitting is expensive.

---

## Agent Design

**Context**: User wants agents but has not designed the agent workflow.

**Progressive Questions**:
1. "What tools should the agent have: web search, code execution, database queries, API calls to internal systems?"
2. "Who triggers the agent: a human user in chat, a scheduled job, or an event from another system?"
3. "How long can an agent run? Short tasks complete in seconds; complex workflows may take minutes."
4. "Does the agent need to hand off to a human if it cannot complete a task? What is the escalation path?"
5. "Should agent conversations be saved across sessions, or start fresh each time?"
6. "Do you have compliance requirements around agent decision logging or audit trails?"

**Red Flags**:
- "The agent should do everything." Scope creep in agent design leads to unreliable, hard-to-debug workflows.
- No human-in-the-loop consideration for high-stakes actions. Agents that take irreversible actions need approval gates.
- "We do not need to log what the agent did." Agent audit trails are often a compliance requirement.

---

## Evaluation and Quality

**Context**: User has not considered how they will know if the AI is working correctly.

**Progressive Questions**:
1. "How will you know if the AI gives a wrong or misleading answer? Who is responsible for catching errors?"
2. "Do you have a golden dataset of questions and expected answers to evaluate the model against?"
3. "What quality metrics matter most: factual accuracy, tone, completeness, latency, or format compliance?"
4. "Will you run evaluations in your CI/CD pipeline before deploying model updates?"
5. "Do you need human evaluation alongside automated metrics?"
6. "Is there a performance regression risk when upgrading to a new model version?"

**Red Flags**:
- "We will just test it manually." Manual testing does not scale. Push for azure-ai-evaluation integration.
- No evaluation dataset prepared. Evaluation without a benchmark is not evaluation.
- "We will deploy and fix issues as they come up." AI quality failures in production erode user trust rapidly.

---

## Cost and Budget

**Context**: User avoids discussing cost or assumes AI is inexpensive.

**Progressive Questions**:
1. "Do you have a monthly AI budget allocated, or does this design need to support a business case?"
2. "How many tokens per day do you expect to process — prompt tokens plus completion tokens?"
3. "Have you modelled the cost difference between GlobalStandard and ProvisionedManaged for your expected volume?"
4. "Is there a requirement to allocate AI costs back to individual teams or projects?"
5. "Are you aware that GlobalBatch costs 50% less than Standard for overnight processing?"

**Red Flags**:
- No token volume estimate. Cannot evaluate PTU vs pay-per-token without a baseline.
- "GPT-4o for everything." High-volume tasks using GPT-4o mini would cost 15x less with equivalent quality for many use cases.
- "We need PTU to control costs." PTU is only cheaper than pay-per-token above ~65% sustained utilisation.

---

## Failure Modes and Resilience

**Context**: User has not considered what happens when the AI service is unavailable or produces bad output.

**Progressive Questions**:
1. "What happens if the Foundry endpoint is unavailable for 5 minutes? Is there a fallback or graceful degradation?"
2. "What happens when the model produces a hallucinated or incorrect answer? How does the application handle it?"
3. "If you hit your token rate limit mid-day, which workloads get priority?"
4. "How do you detect when answer quality degrades over time — drift in evaluation scores, user feedback signals?"
5. "For agentic workflows: if a tool call fails, does the agent retry, skip, or abort the task?"

**Red Flags**:
- "The Azure SLA is sufficient." Endpoint availability does not guarantee answer quality — both need monitoring.
- No token rate limit contingency. PTU exhaustion or TPM throttling on GlobalStandard can silently degrade applications.
- Agent with no error handling. Tool failures that bubble up as unhandled exceptions break the entire agent run.
