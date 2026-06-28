import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as dotenv from "dotenv";
import { classify_ai_risk } from "./tools/classify_ai_risk";
import { audit_supply_chain } from "./tools/audit_supply_chain";
import { verify_human_oversight } from "./tools/verify_human_oversight";
import { run_bias_assessment } from "./tools/run_bias_assessment";
import { generate_dpia } from "./tools/generate_dpia";
import { run_adversarial_tests } from "./tools/run_adversarial_tests";
import { score_audit_weighted } from "./tools/score_audit_weighted";
import { generate_audit_certificate } from "./tools/generate_audit_certificate";
import { monitor_model_drift } from "./tools/monitor_model_drift";
import { checkBlocker } from "./utils/blocker_logic";

dotenv.config();

const server = new McpServer({
  name: "ai-governance-mcp",
  version: "1.0.0",
});

/**
 * Middleware to check for BLOCKER_FAIL and halt the pipeline.
 */
async function withBlockerCheck<T>(toolName: string, execution: () => Promise<T>): Promise<T | any> {
  console.log(`[${new Date().toISOString()}] Invoking tool: ${toolName}`);
  const result = await execution();
  const blocker = checkBlocker(result);
  if (blocker) {
    console.error(`[${new Date().toISOString()}] BLOCKER_FAIL detected in ${toolName}. Halting pipeline.`);
    return blocker;
  }
  return result;
}

// 1. classify_ai_risk
server.tool(
  "classify_ai_risk",
  {
    system_name: z.string(),
    use_case: z.string(),
    deployment_context: z.string(),
    processes_biometric_data: z.boolean(),
    used_in_critical_infra: z.boolean(),
    affects_access_to_services: z.boolean(),
    autonomous_decision: z.boolean(),
  },
  async (args) => {
    const result = await withBlockerCheck("classify_ai_risk", () => classify_ai_risk(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 2. audit_supply_chain
server.tool(
  "audit_supply_chain",
  {
    model_id: z.string(),
    data_sources: z.array(z.string()),
    third_party_components: z.array(z.string()),
  },
  async (args) => {
    const result = await withBlockerCheck("audit_supply_chain", () => audit_supply_chain(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 3. verify_human_oversight
server.tool(
  "verify_human_oversight",
  {
    architecture_description: z.string(),
    has_kill_switch: z.boolean(),
    override_mechanism: z.boolean(),
    monitoring_capability: z.boolean(),
    automation_bias_mitigations: z.boolean(),
  },
  async (args) => {
    const result = await withBlockerCheck("verify_human_oversight", () => verify_human_oversight(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 4. run_bias_assessment
server.tool(
  "run_bias_assessment",
  {
    model_endpoint: z.string(),
    test_dataset_ref: z.string(),
    protected_classes: z.array(z.string()),
    intersectional: z.boolean(),
  },
  async (args) => {
    const result = await withBlockerCheck("run_bias_assessment", () => run_bias_assessment(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 5. generate_dpia
server.tool(
  "generate_dpia",
  {
    processing_activity: z.string(),
    data_categories: z.array(z.string()),
    data_subjects: z.array(z.string()),
    recipients: z.array(z.string()),
    storage_location: z.string(),
    transfer_mechanisms: z.array(z.string()),
  },
  async (args) => {
    const result = await withBlockerCheck("generate_dpia", () => generate_dpia(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 6. run_adversarial_tests
server.tool(
  "run_adversarial_tests",
  {
    model_endpoint: z.string(),
    test_suites: z.array(z.string()),
    threat_model: z.string(),
  },
  async (args) => {
    const result = await withBlockerCheck("run_adversarial_tests", () => run_adversarial_tests(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 7. score_audit_weighted
server.tool(
  "score_audit_weighted",
  {
    audit_session_id: z.string(),
    phase_results: z.array(z.any()),
  },
  async (args) => {
    const result = await withBlockerCheck("score_audit_weighted", () => score_audit_weighted(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 8. generate_audit_certificate
server.tool(
  "generate_audit_certificate",
  {
    audit_session_id: z.string(),
    weighted_audit_score: z.any(),
    blocker_fail_detected: z.boolean(),
  },
  async (args) => {
    const result = await withBlockerCheck("generate_audit_certificate", () => generate_audit_certificate(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// 9. monitor_model_drift
server.tool(
  "monitor_model_drift",
  {
    model_id: z.string(),
    production_data_stream: z.string(),
    baseline_data_ref: z.string(),
    monitoring_thresholds: z.record(z.number()),
  },
  async (args) => {
    const result = await withBlockerCheck("monitor_model_drift", () => monitor_model_drift(args));
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// Health Check
server.tool(
  "health_check",
  {},
  async () => {
    return { content: [{ type: "text", text: JSON.stringify({ status: "healthy", timestamp: new Date().toISOString() }) }] };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("AI Governance MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
