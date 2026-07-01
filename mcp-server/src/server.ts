import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { logger } from './index.js';
import { getJsonSchema } from './types/schemas.js';
import { registerAuditContext } from './tools/phase1_register.js';
import { scopeRegulatoryBaseline } from './tools/phase2_scope.js';
import { classifyAiRisk } from './tools/phase3_risk.js';
import { assessPrivacyCompliance } from './tools/phase4_privacy.js';
import { runBiasAssessment } from './tools/phase5_bias.js';
import { runSecurityTests } from './tools/phase6_security.js';
import { generateExplainabilityReport } from './tools/phase7_explain.js';
import { issueComplianceCertificate } from './tools/phase8_certify.js';
import { monitorModelDrift } from './tools/phase9_monitor.js';

export function registerTools(server: McpServer) {
  server.tool(
    'register_audit_context',
    'Phase 1: Register an AI system for compliance auditing',
    getJsonSchema(1) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'register_audit_context' });
      return registerAuditContext(args);
    },
  );

  server.tool(
    'scope_regulatory_baseline',
    'Phase 2: Determine applicable regulatory frameworks',
    getJsonSchema(2) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'scope_regulatory_baseline' });
      return scopeRegulatoryBaseline(args);
    },
  );

  server.tool(
    'classify_ai_risk',
    'Phase 3: Classify AI system risk tier per EU AI Act Art. 5-6',
    getJsonSchema(3) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'classify_ai_risk' });
      return classifyAiRisk(args);
    },
  );

  server.tool(
    'assess_privacy_compliance',
    'Phase 4: GDPR Art. 35 DPIA and Art. 25 Privacy by Design assessment',
    getJsonSchema(4) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'assess_privacy_compliance' });
      return assessPrivacyCompliance(args);
    },
  );

  server.tool(
    'run_bias_assessment',
    'Phase 5: Multi-dimensional bias scan using Fairlearn and AIF360',
    getJsonSchema(5) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'run_bias_assessment' });
      return runBiasAssessment(args);
    },
  );

  server.tool(
    'run_security_tests',
    'Phase 6: Adversarial robustness testing via ART, input validation',
    getJsonSchema(6) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'run_security_tests' });
      return runSecurityTests(args);
    },
  );

  server.tool(
    'generate_explainability_report',
    'Phase 7: SHAP/LIME feature importance and compliance report',
    getJsonSchema(7) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'generate_explainability_report' });
      return generateExplainabilityReport(args);
    },
  );

  server.tool(
    'issue_compliance_certificate',
    'Phase 8: Issue W3C VC 2.0 with EdDSA signing and Merkle anchoring',
    getJsonSchema(8) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'issue_compliance_certificate' });
      return issueComplianceCertificate(args);
    },
  );

  server.tool(
    'monitor_model_drift',
    'Phase 9: Continuous drift detection and reaudit triggering',
    getJsonSchema(9) as Record<string, z.ZodTypeAny>,
    async (args, extra) => {
      logger.info('Tool invoked', { tool: 'monitor_model_drift' });
      return monitorModelDrift(args);
    },
  );
}
