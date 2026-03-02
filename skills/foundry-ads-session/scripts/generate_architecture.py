#!/usr/bin/env python3
"""
Microsoft Foundry Architecture Diagram Generator (Mermaid)

Generates Mermaid flowchart syntax for architecture diagrams. Supports 8
Microsoft Foundry architecture patterns. Optionally renders to PNG via mermaid-cli.

Usage:
    python generate_architecture.py --list
    python generate_architecture.py --pattern baseline-chat
    python generate_architecture.py --pattern ptu-gateway --params '{"include_spillover": true}'
    python generate_architecture.py --pattern baseline-chat --render --filename contoso

Output: Mermaid code to stdout (or to .mmd file + PNG when using --render).
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
from typing import Any, Dict


# ---------------------------------------------------------------------------
# 1. Pattern Generators
# ---------------------------------------------------------------------------


def generate_baseline_chat(params: Dict[str, Any]) -> str:
    """Baseline Chat (RAG + Agent Service) - the recommended Foundry starting pattern."""
    name = params.get("name", "Foundry Baseline Chat")
    include_content_safety = params.get("include_content_safety", True)

    cs_node = ""
    cs_edge = ""
    if include_content_safety:
        cs_node = "    CS(Content Safety)"
        cs_edge = "  AGENT --> CS"

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph SRC["User Channels"]
            WEB[[Web App]]
            API[[API Clients]]
          end

          AGW([Application Gateway])

          subgraph FOUNDRY["Microsoft Foundry - AI Project"]
            AGENT[Agent Service]
            LLM[Model Deployment - GPT-4o]
            SRCH[(Azure AI Search - Vector Index)]
            {cs_node}
          end

          subgraph DATA["Grounding Data"]
            BLOB[(Blob Storage - Source Documents)]
            INGESTION[Indexing Pipeline]
          end

          subgraph OBS["Observability"]
            APPINS(Application Insights)
            KV(Key Vault)
          end

          WEB & API --> AGW --> AGENT
          AGENT --> LLM
          AGENT --> SRCH
          {cs_edge}
          BLOB --> INGESTION --> SRCH
          APPINS -.->|traces| AGENT
          KV -.->|secrets| AGENT
    """)


def generate_multi_agent(params: Dict[str, Any]) -> str:
    """Multi-Agent Orchestration - Semantic Kernel orchestrator routing to specialised sub-agents."""
    name = params.get("name", "Foundry Multi-Agent Orchestration")
    agent_count = int(params.get("agent_count", 3))
    include_langgraph = params.get("include_langgraph", False)

    orch_label = "LangGraph Orchestrator" if include_langgraph else "Semantic Kernel Orchestrator"

    NL = chr(10)
    labels = ["Research", "Writing", "Validation", "Summarisation", "Code"]
    agent_blocks = []
    agent_ids = []
    for i in range(agent_count):
        label = labels[i] if i < len(labels) else f"Specialist {i+1}"
        aid = f"AGT{i+1}"
        agent_ids.append(aid)
        agent_blocks.append(f"    {aid}[{label} Agent]")
    agent_nodes = NL.join(agent_blocks)
    agent_edges = " & ".join(agent_ids)

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          USER[[User Request]]

          subgraph ORCH["Orchestration Layer"]
            SK[{orch_label}]
            A2A[A2A Protocol Router]
          end

          subgraph AGENTS["Specialist Agents"]
{agent_nodes}
          end

          subgraph TOOLS["Shared Tools"]
            SRCH[(Azure AI Search)]
            CODE[Code Interpreter]
            FUNC[[Azure Functions - custom tools]]
          end

          subgraph MODEL["Model Deployments"]
            GPT4O[GPT-4o - reasoning]
            PHI4[Phi-4 - fast tasks]
          end

          subgraph OBS["Observability"]
            TRACE[Agent Tracing - Foundry Portal]
            APPINS(Application Insights)
          end

          USER --> SK --> A2A --> {agent_edges}
          {agent_edges} --> SRCH & CODE & FUNC
          {agent_edges} --> GPT4O & PHI4
          TRACE -.->|spans| A2A & {agent_edges}
          APPINS -.->|metrics| SK
    """)


def generate_batch_inference(params: Dict[str, Any]) -> str:
    """Batch Inference Pipeline - high-volume document processing with Foundry models."""
    name = params.get("name", "Foundry Batch Inference Pipeline")
    include_adf = params.get("include_adf", False)

    trigger_node = "    ADF[Azure Data Factory - trigger]" if include_adf else "    SCHED[Azure Container Apps Job - schedule]"
    trigger_id = "ADF" if include_adf else "SCHED"

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph INGEST["Input"]
            BLOB_IN[(Blob Storage - raw documents)]
            {trigger_node}
          end

          subgraph PROCESS["Batch Processing"]
            QUEUE[Azure Service Bus - job queue]
            WORKERS[Container Apps - worker pool]
            FDR[Foundry Model Deployment - GPT-4o mini]
          end

          subgraph OUTPUT["Output"]
            BLOB_OUT[(Blob Storage - results JSONL)]
            COSMOS[(Cosmos DB - metadata)]
          end

          subgraph OBS["Observability"]
            MON[Azure Monitor - throughput and cost]
            APPINS(Application Insights)
          end

          BLOB_IN --> {trigger_id} --> QUEUE --> WORKERS
          WORKERS --> FDR --> BLOB_OUT & COSMOS
          MON -.->|token usage and latency| WORKERS & FDR
          APPINS -.->|traces| WORKERS
    """)


def generate_ptu_gateway(params: Dict[str, Any]) -> str:
    """PTU Gateway with APIM - provisioned throughput management with spillover to PAYG."""
    name = params.get("name", "Foundry PTU Gateway")
    include_spillover = params.get("include_spillover", True)

    spillover_node = ""
    spillover_edge = ""
    if include_spillover:
        spillover_node = "    PAYG[PAYG Deployment - spillover capacity]"
        spillover_edge = "  POL -->|on 429 retry| PAYG"

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph CALLERS["API Callers"]
            APP1[[Application A]]
            APP2[[Application B]]
            APP3[[Application C]]
          end

          subgraph APIM["Azure API Management"]
            AGW([API Gateway])
            subgraph POL["Policies"]
              TKN[Token Rate Limiting]
              RATE[Request Rate Limiting]
              RETRY[Retry with Backoff]
              CB[Circuit Breaker]
            end
          end

          subgraph FDR["Foundry Model Deployments"]
            PTU[PTU Deployment - reserved capacity]
            {spillover_node}
          end

          subgraph OBS["Observability and Chargeback"]
            MON(Application Insights)
            KV(Key Vault)
            COST[Azure Monitor - Token Logs]
          end

          APP1 & APP2 & APP3 --> AGW --> POL
          POL --> TKN & RATE & RETRY & CB
          POL -->|primary| PTU
          {spillover_edge}
          TKN -.->|token usage logs| COST
          MON -.->|traces and latency| POL & PTU
          KV -.->|APIM subscription keys| POL
    """)


def generate_fine_tuning(params: Dict[str, Any]) -> str:
    """Fine-Tuning + Custom Deployment - domain-specific model adaptation with evaluation gate."""
    name = params.get("name", "Foundry Fine-Tuning Pipeline")
    base_model = params.get("base_model", "GPT-4o mini")

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph DATA["Training Data Pipeline"]
            SRC_DATA[[Source Documents]]
            CURATE[Curation and Formatting]
            BLOB_TRAIN[(Blob Storage - Training JSONL)]
          end

          subgraph FDR["Microsoft Foundry - AI Project"]
            FT_JOB[Fine-Tuning Job]
            BASE[Base Model - {base_model}]
            FT_MODEL[Fine-Tuned Model]
            subgraph EVALP["Evaluation Pipeline"]
              DEV_TIER[DeveloperTier Deployment - 24hr eval]
              EVAL_SDK[azure-ai-evaluation - Groundedness and Coherence]
              GATE{{Eval Pass?}}
            end
            PROD[Production Deployment - Standard or PTU]
          end

          subgraph CONSUME["Consumers"]
            APP[[Application]]
          end

          SRC_DATA --> CURATE --> BLOB_TRAIN
          BLOB_TRAIN --> FT_JOB
          BASE --> FT_JOB --> FT_MODEL
          FT_MODEL --> DEV_TIER --> EVAL_SDK --> GATE
          GATE -->|pass| PROD
          GATE -->|fail| FT_JOB
          PROD --> APP
    """)


def generate_multi_project(params: Dict[str, Any]) -> str:
    """Multi-Project Platform - multiple AI projects sharing central Foundry resources with RBAC isolation."""
    name = params.get("name", "Foundry Multi-Project Platform")
    team_count = int(params.get("team_count", 2))

    NL = chr(10)
    project_blocks: list = []
    connects: list = []
    srch_lines: list = []
    cosmos_lines: list = []
    rbac_lines: list = []
    agt_list: list = []
    for i in range(team_count):
        letter = chr(65 + i)
        idx = i + 1
        project_blocks.append(f"  subgraph PRJ{idx}['Project {letter} - Team {letter}']")
        project_blocks.append(f"    AGT{idx}[Agent Service {letter}]")
        project_blocks.append(f"    EVLR{idx}[Evaluation Runs {letter}]")
        project_blocks.append(f"    RBAC{idx}(Azure AI User - Team {letter})")
        project_blocks.append("  end")
        connects.append(f"  FND --> PRJ{idx}")
        srch_lines.append(f"  AGT{idx} --> SRCH")
        cosmos_lines.append(f"  AGT{idx} --> COSMOS")
        rbac_lines.append(f"  RBAC{idx} -.->|scoped to Project {letter}| PRJ{idx}")
        agt_list.append(f"AGT{idx}")
    project_nodes = NL.join(project_blocks)
    project_connects = NL.join(connects)
    agent_srch = NL.join(srch_lines)
    agent_cosmos = NL.join(cosmos_lines)
    rbac_edges = NL.join(rbac_lines)
    agent_gpt = " & ".join(agt_list)

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph PLATFORM["Central Platform Team"]
            FND[Microsoft Foundry Hub]
            SRCH[(Azure AI Search - Shared Index)]
            COSMOS[(Cosmos DB - Shared Conversation State)]
            POLICY(Azure Policy - Allowed Models and Regions)
            COST[Azure Monitor - Token Cost Alerts per Project]
          end

          {project_nodes}

          subgraph MODELS["Shared Model Deployments"]
            GPT4O[GPT-4o - Standard Deployment]
            PHI4[Phi-4 - Serverless API]
          end

          {project_connects}
          {agent_srch}
          {agent_cosmos}
          {rbac_edges}
          {agent_gpt} --> GPT4O & PHI4
          POLICY -.->|governs deployments| MODELS
          COST -.->|chargeback per project| PLATFORM
    """)


def generate_aoai_migration(params: Dict[str, Any]) -> str:
    """AOAI to Foundry Migration - phased migration path from Azure OpenAI Service to Microsoft Foundry."""
    name = params.get("name", "AOAI to Foundry Migration")

    return textwrap.dedent(f"""\n        %% {name}
        flowchart LR
          subgraph BEFORE["Before - Azure OpenAI Service"]
            AOAI_RES[azure.openai.com Resource]
            AOAI_DEP[Deployment - gpt-4o]
            AOAI_KEY(API Key Auth)
            AOAI_SDK[openai Python SDK]
          end

          subgraph MIGRATION["Migration Phases"]
            PH1[Phase 1 - Inventory Deployments and Usage]
            PH2[Phase 2 - Provision Foundry Hub and Project]
            PH3[Phase 3 - Recreate Deployments in Foundry]
            PH4[Phase 4 - Switch Auth to Managed Identity]
            PH5[Phase 5 - Update Endpoint and SDK]
            PH6[Phase 6 - Shadow Traffic Comparison]
            PH7[Phase 7 - Cutover and Decommission AOAI]
          end

          subgraph AFTER["After - Microsoft Foundry"]
            FND_RES[services.ai.azure.com Resource]
            PRJ[AI Project]
            FND_DEP[Deployment - gpt-4o in Foundry]
            AGENT_SVC[Agent Service and Tracing]
            EVAL_SVC[Evaluation and Safety]
            MI(Managed Identity Auth)
            NEW_SDK[azure-ai-projects SDK]
          end

          subgraph GUARD["Guardrails During Migration"]
            CS(Content Safety - parity check)
            MON[Azure Monitor - shadow comparison]
            KV(Key Vault - keys during transition)
          end

          AOAI_RES --> PH1 --> PH2 --> PH3 --> PH4 --> PH5 --> PH6 --> PH7 --> FND_RES
          FND_RES --> PRJ --> FND_DEP & AGENT_SVC & EVAL_SVC
          AOAI_KEY -.->|replace with| MI
          AOAI_SDK -.->|migrate to| NEW_SDK
          AOAI_DEP -.->|recreate as| FND_DEP
          MON -.->|shadow comparison| AOAI_RES & FND_RES
          KV -.->|holds keys during transition| AOAI_RES & FND_RES
          CS -.->|add Content Safety during migration| PRJ
    """)


def generate_enterprise_landing_zone(params: Dict[str, Any]) -> str:
    """Enterprise Landing Zone - network-secured Foundry deployment with private endpoints and hub-spoke networking."""
    name = params.get("name", "Foundry Enterprise Landing Zone")
    include_bastion = params.get("include_bastion", True)
    include_ddos = params.get("include_ddos", True)

    bastion_node = ""
    bastion_edge = ""
    if include_bastion:
        bastion_node = "    BASTION{{Azure Bastion}}"
        bastion_edge = "  BASTION --> JUMP"

    ddos_node = ""
    ddos_edge = ""
    if include_ddos:
        ddos_node = "    DDOS(DDoS Protection)"
        ddos_edge = "  DDOS -.->|protects| HUB_VNET"

    return textwrap.dedent(f"""\n        %% {name}
        flowchart TB
          subgraph HUB["Hub VNet"]
            FW{{{{Azure Firewall}}}}
            {bastion_node}
            JUMP[Jump Box VM]
            DNS[Private DNS Zones]
            {ddos_node}
          end

          subgraph SPOKE["AI Spoke VNet"]
            subgraph PE["Private Endpoints"]
              PE_FDR(PE - Foundry Resource)
              PE_SRCH(PE - AI Search)
              PE_BLOB(PE - Blob Storage)
              PE_KV(PE - Key Vault)
              PE_COSMOS(PE - Cosmos DB)
            end

            subgraph COMPUTE["AI Workloads"]
              ACA[Container Apps Environment]
              BUILD[Self-Hosted Build Agent]
            end
          end

          subgraph FDR_RES["Microsoft Foundry - Private"]
            HUB_RES[Foundry Hub - No Public Access]
            PRJ[AI Project]
            AGENT[Agent Service]
            LLM[Model Deployment - GPT-4o]
          end

          subgraph GOV["Governance"]
            POLICY(Azure Policy - deny public endpoints)
            MON[Azure Monitor - NSG Flow Logs]
            DEFENDER(Defender for Cloud)
          end

          FW --> PE_FDR & PE_SRCH & PE_BLOB & PE_KV & PE_COSMOS
          {bastion_edge}
          PE_FDR --> HUB_RES --> PRJ --> AGENT --> LLM
          ACA --> PE_FDR
          BUILD --> PE_FDR
          DNS -.->|resolves private| PE
          POLICY -.->|enforces| FDR_RES & SPOKE
          MON -.->|monitors| HUB & SPOKE
          DEFENDER -.->|scans| FDR_RES
          {ddos_edge}
    """)


# ---------------------------------------------------------------------------
# 2. Pattern Registry & CLI
# ---------------------------------------------------------------------------

PATTERNS = {
    "baseline-chat": {
        "fn": generate_baseline_chat,
        "desc": "Baseline Chat (RAG + Agent Service) with Application Gateway, AI Search, and Content Safety",
        "params": "name, include_content_safety (bool)",
    },
    "multi-agent": {
        "fn": generate_multi_agent,
        "desc": "Multi-Agent Orchestration with Semantic Kernel, A2A Protocol, and specialist sub-agents",
        "params": "name, agent_count (int, default 3), include_langgraph (bool)",
    },
    "batch-inference": {
        "fn": generate_batch_inference,
        "desc": "Batch Inference Pipeline with Container Apps worker pool and Foundry model deployment",
        "params": "name, include_adf (bool)",
    },
    "ptu-gateway": {
        "fn": generate_ptu_gateway,
        "desc": "PTU Gateway with APIM, token rate limiting, circuit breaker, and PAYG spillover",
        "params": "name, include_spillover (bool)",
    },
    "fine-tuning": {
        "fn": generate_fine_tuning,
        "desc": "Fine-Tuning Pipeline with evaluation gate, DeveloperTier deployment, and promotion",
        "params": 'name, base_model (str, default "GPT-4o mini")',
    },
    "multi-project": {
        "fn": generate_multi_project,
        "desc": "Multi-Project Platform (CoE) with shared Foundry Hub, per-team projects, and RBAC isolation",
        "params": "name, team_count (int, default 2)",
    },
    "aoai-migration": {
        "fn": generate_aoai_migration,
        "desc": "Azure OpenAI to Foundry Migration with phased cutover, shadow traffic, and identity migration",
        "params": "name",
    },
    "enterprise-landing-zone": {
        "fn": generate_enterprise_landing_zone,
        "desc": "Enterprise Landing Zone with hub-spoke networking, private endpoints, Firewall, and DDoS",
        "params": "name, include_bastion (bool), include_ddos (bool)",
    },
}


def list_patterns():
    print("\n=== Available Microsoft Foundry Architecture Patterns ===\n")
    for key, info in PATTERNS.items():
        print(f"  {key:30s}  {info['desc']}")
        print(f"  {'':30s}  Params: {info['params']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Microsoft Foundry architecture diagrams (Mermaid)."
    )
    parser.add_argument(
        "--list", action="store_true", help="List available patterns"
    )
    parser.add_argument(
        "--pattern",
        choices=list(PATTERNS.keys()),
        help="Architecture pattern to generate",
    )
    parser.add_argument(
        "--name", help="Diagram title (overrides default)"
    )
    parser.add_argument(
        "--filename", help="Output filename without extension (used with --render)"
    )
    parser.add_argument(
        "--params",
        help='JSON string of additional parameters, e.g. \'{"include_content_safety": true}\'',
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Write .mmd file and render PNG via mermaid-cli (npx required)",
    )
    parser.add_argument(
        "--output-dir",
        default="diagrams",
        help="Output directory for .mmd and .png files (default: diagrams)",
    )

    args = parser.parse_args()

    if args.list:
        list_patterns()
        return

    if not args.pattern:
        parser.error("--pattern is required (or use --list)")

    params: Dict[str, Any] = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"Error parsing --params JSON: {e}", file=sys.stderr)
            sys.exit(1)

    if args.name:
        params["name"] = args.name

    code = PATTERNS[args.pattern]["fn"](params)

    if args.render:
        filename = args.filename or args.pattern.replace("-", "_") + "_architecture"
        out_dir = args.output_dir
        os.makedirs(out_dir, exist_ok=True)

        mmd_path = os.path.join(out_dir, f"{filename}.mmd")
        png_path = os.path.join(out_dir, f"{filename}.png")

        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Mermaid written to: {mmd_path}", file=sys.stderr)

        cmd = [
            "npx", "-y", "@mermaid-js/mermaid-cli",
            "-i", mmd_path,
            "-o", png_path,
            "--scale", "3",
            "--backgroundColor", "white",
            "--width", "1600",
            "-q",
        ]
        print(f"Rendering PNG: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"mermaid-cli error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"PNG rendered to: {png_path}", file=sys.stderr)
    else:
        print(code)


if __name__ == "__main__":
    main()
