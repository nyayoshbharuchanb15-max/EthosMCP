import crypto from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { Phase1InputSchema, Phase1OutputSchema } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function registerAuditContext(input: any) {
  const parsed = Phase1InputSchema.parse(input);

  const run_id = uuidv4();
  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const query_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  const payload = { run_id, ...parsed };

  try {
    const response = await axios.post(`${ORCHESTRATOR_URL}/audit/register`, payload, {
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' },
    });

    logger.info('Phase 1 completed', { run_id, orchestrator_status: response.status });

    const output = Phase1OutputSchema.parse({
      run_id,
      status: 'REGISTERED',
      phase: 1,
      timestamp: new Date().toISOString(),
      query_hash,
      next_phase: 2,
    });

    return {
      content: [{ type: 'text', text: JSON.stringify(output, null, 2) }],
    };
  } catch (error: any) {
    logger.error('Phase 1 orchestrator call failed', { run_id, error: error.message });
    throw new Error(`Failed to register audit context: ${error.message}`);
  }
}
