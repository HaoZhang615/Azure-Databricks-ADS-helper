# Industry Templates

Industry-specific starting configurations for common Foundry ADS scenarios. Use these to accelerate pattern selection and probing question focus areas for specific verticals.

## Financial Services

### Common Use Cases
- **Document AI**: Loan application processing, contract analysis, regulatory filing extraction
- **Risk Copilot**: Internal analyst tool for risk report summarisation and Q&A
- **Fraud detection assistant**: Agent that queries transaction data and generates explanations
- **Customer service bot**: Grounded on product knowledge base, escalation to human agent

### Architecture Starting Point
**Pattern 8 (Enterprise Landing Zone) + Pattern 1 (Baseline Chat)**

### Non-Negotiable Requirements
- Private endpoints for all PaaS services (Pattern 8 subnets)
- Customer-managed encryption keys (Key Vault Managed HSM)
- Data residency: DataZone deployment types for EU/US compliance
- Content Safety enabled at strict thresholds
- Audit logging to immutable storage (Azure Monitor + Log Analytics with export)
- No public endpoint on Foundry resource

### Key Questions
- "Are you subject to SR 11-7 model risk management guidelines?"
- "Does the AI output require explainability for regulatory audit?"
- "Is there a DORA (Digital Operational Resilience Act) compliance requirement for this workload?"
- "Does the model need to stay in EU datacenters?"

### Recommended Evaluation Metrics
- Groundedness (factual accuracy of document extraction)
- PII detection validation (no PII leakage in outputs)
- Response consistency (same question, same answer across runs)

---

## Healthcare and Life Sciences

### Common Use Cases
- **Clinical documentation AI**: Draft clinical notes, discharge summaries
- **Medical literature assistant**: RAG over clinical trials, drug information, protocols
- **Prior authorisation automation**: Agent that processes insurance forms against clinical guidelines
- **Patient engagement chatbot**: Symptom triage (with mandatory human escalation)

### Architecture Starting Point
**Pattern 8 (Enterprise Landing Zone) + Pattern 2 (Multi-Agent MAF) for automation use cases**

### Non-Negotiable Requirements
- HIPAA BAA with Microsoft required before processing PHI
- De-identify PHI before sending to model (pre-processing layer)
- Human-in-the-loop for all clinical output (agent cannot act without clinician approval)
- Audit trail for every AI-generated clinical suggestion
- Private endpoints; no PHI over public internet
- Content Safety configured for medical context (self-harm, medical advice thresholds)

### Key Questions
- "Is this processing Protected Health Information? If yes, HIPAA BAA must be in place before data enters Foundry."
- "Who validates AI-generated clinical content before it reaches a patient record?"
- "Is this system a medical device under FDA or EU MDR? AI-assisted clinical tools may require regulatory approval."

---

## Manufacturing and Industrial

### Common Use Cases
- **Maintenance copilot**: Agent answering equipment maintenance questions grounded on technical manuals
- **Quality inspection AI**: Batch inference processing defect images or sensor logs
- **Supply chain assistant**: Multi-agent workflow coordinating demand forecasting, inventory, and supplier data
- **Safety incident analysis**: Summarising incident reports and suggesting root cause analysis

### Architecture Starting Point
**Pattern 1 (Baseline Chat) for copilot use cases; Pattern 3 (Batch Inference) for overnight quality processing**

### Typical Constraints
- OT/IT network separation: AI platform lives in IT zone; must access OT data via DMZ or API gateway
- Long tail of older equipment with undocumented technical specs � knowledge base quality is critical
- Shift workers as primary users � simple, mobile-friendly UI is non-negotiable

### Key Questions
- "Are the technical manuals in a machine-readable format, or are they scanned PDFs that need OCR?"
- "Do workers need to use this on the factory floor on a mobile device?"
- "Is there OT network isolation that prevents direct connectivity to Azure?"

---

## Retail and E-Commerce

### Common Use Cases
- **Product recommendation and personalisation**: Agent with product catalogue tool + customer history tool
- **Customer service automation**: Multi-turn chat agent handling returns, order tracking, product questions
- **Content generation**: Batch inference generating product descriptions, SEO content
- **Demand forecasting assistant**: AI explaining anomalies in sales data to analysts

### Architecture Starting Point
**Pattern 1 (Baseline Chat) for customer service; Pattern 3 (GlobalBatch) for content generation at scale**

### Typical Constraints
- Peak traffic events (Black Friday, holiday) require PTU or APIM spillover routing (Pattern 4)
- Product catalogue changes daily � RAG index must refresh frequently (hourly or daily incremental)
- Customer-facing latency requirements are strict (sub-2s response expected)

### Key Questions
- "How many concurrent users at peak � for example, Black Friday?"
- "How frequently does your product catalogue change? We need to design the index refresh pipeline."
- "Is this customer-facing or internal? Customer-facing requires much stricter latency and Content Safety."

---

## Public Sector / Government

### Common Use Cases
- **Citizen services chatbot**: Grounded on government regulations and service documentation
- **Policy analysis AI**: Summarising and comparing policy documents for analysts
- **Case management assistant**: Agent surfacing relevant case precedents and regulations

### Architecture Starting Point
**Pattern 8 (Enterprise Landing Zone) is baseline; FedRAMP High may require Azure Government cloud**

### Non-Negotiable Requirements
- Data sovereignty: all data must stay in specified national boundary
- FedRAMP High or equivalent: review Azure Government cloud availability
- Accessibility: AI-generated responses must be accessible (WCAG 2.1 AA minimum)
- Audit trails for all AI-generated advice to citizens

### Key Questions
- "Is this subject to FedRAMP or a national equivalent compliance framework?"
- "Is Azure Government cloud required, or is commercial Azure with appropriate controls sufficient?"
- "Are there open records / FOIA requirements on AI-generated government communications?"

---

## Telecommunications

### Common Use Cases
- **Network operations copilot**: Agent answering NOC questions grounded on network documentation, runbooks, and topology data
- **Customer churn prediction assistant**: AI explaining churn risk factors to retention agents with recommended actions
- **Intelligent IVR / virtual agent**: Multi-turn voice agent handling billing inquiries, plan changes, and troubleshooting
- **Network anomaly summarisation**: Batch inference processing network telemetry logs and generating incident summaries

### Architecture Starting Point
**Pattern 1 (Baseline Chat) for copilot; Pattern 2 (Multi-Agent) for complex customer service automation**

### Typical Constraints
- Massive scale: millions of subscribers means token costs must be modelled carefully (Pattern 4 PTU Gateway is likely needed)
- Network data is often in proprietary formats — knowledge base ingestion pipeline needs custom parsing
- 24/7 operations: AI must be highly available; PTU with APIM spillover is strongly recommended

### Key Questions
- "How many concurrent customer interactions at peak? This drives PTU sizing and APIM rate limiting."
- "Is the network documentation structured (APIs, databases) or unstructured (PDFs, wikis)?"
- "Do you need real-time network event processing, or is batch summarisation sufficient?"
- "Is this customer-facing (IVR) or internal (NOC)? Customer-facing requires much stricter Content Safety and latency."

---

## Energy and Utilities

### Common Use Cases
- **Field technician copilot**: Agent answering equipment maintenance and safety questions grounded on technical manuals
- **Regulatory compliance assistant**: RAG over regulatory filings, safety standards, and audit reports
- **Outage analysis AI**: Batch inference processing outage reports and generating root cause summaries
- **Customer billing assistant**: Agent handling billing inquiries and usage explanations

### Architecture Starting Point
**Pattern 1 (Baseline Chat) for copilot; Pattern 8 (Enterprise Landing Zone) for regulated utilities**

### Typical Constraints
- Critical infrastructure: AI must not provide safety-critical advice without human validation
- Regulated environment: audit trails required for all AI-generated advice to regulators or customers
- OT/IT separation: field devices and SCADA systems are in isolated OT networks; AI lives in IT zone

### Key Questions
- "Is this a regulated utility? NERC CIP, NRC, or regional equivalents affect private endpoint and audit requirements."
- "Are the technical manuals and safety standards in machine-readable format, or do they require OCR/document intelligence?"
- "Is the AI providing safety-critical advice? If yes, human-in-the-loop is mandatory — no autonomous AI actions on safety."
- "Do field technicians need this on mobile devices in areas with limited connectivity? Consider Foundry Local for offline scenarios."

---

*Last updated: March 2026. Sources: Azure AI Foundry docs, Azure Architecture Center.*
