import type { TokenClaims } from '../types/mcp.d.js';

export const SCOPE_PHASE_MAP: Record<string, number[]> = {
  'audit:context:write': [1],
  'audit:scope:read': [2],
  'audit:risk:execute': [3],
  'audit:privacy:execute': [4],
  'audit:bias:execute': [5],
  'audit:security:execute': [6],
  'audit:explain:execute': [7],
  'audit:certify:issue': [8],
  'audit:monitor:read': [9],
  'audit:admin': [1, 2, 3, 4, 5, 6, 7, 8, 9],
};

export const SCOPE_PHASE_NAME: Record<string, string> = {
  'audit:context:write': 'Register Audit Context',
  'audit:scope:read': 'Scope Regulatory Baseline',
  'audit:risk:execute': 'Classify AI Risk',
  'audit:privacy:execute': 'Assess Privacy Compliance',
  'audit:bias:execute': 'Run Bias Assessment',
  'audit:security:execute': 'Run Security Tests',
  'audit:explain:execute': 'Generate Explainability Report',
  'audit:certify:issue': 'Issue Compliance Certificate',
  'audit:monitor:read': 'Monitor Model Drift',
  'audit:admin': 'Admin (all phases)',
};

export function requireScope(token: TokenClaims, requiredScope: string): void {
  const hasAdmin = token.scope.includes('audit:admin');
  const hasExact = token.scope.includes(requiredScope);

  if (!hasAdmin && !hasExact) {
    throw {
      code: -32001,
      message: `Insufficient scope: requires "${requiredScope}"`,
    };
  }
}

export function getPhaseScopes(phase: number): string[] {
  return Object.entries(SCOPE_PHASE_MAP)
    .filter(([_, phases]) => phases.includes(phase))
    .map(([scope]) => scope);
}
