import type { McpError } from '@modelcontextprotocol/sdk/types.js';

declare module '@modelcontextprotocol/sdk/types.js' {
  export enum ErrorCode {
    InvalidParams = -32602,
    MethodNotFound = -32601,
    InternalError = -32603,
    Unauthorized = -32001,
    RateLimited = -32029,
  }
}

export interface TokenClaims {
  sub: string;
  scope: string[];
  org_id: string;
  exp: number;
  iss: string;
  aud: string;
}

export interface Finding {
  finding_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'BLOCKER';
  regulation: string;
  article: string;
  description: string;
  remediation: string;
}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      MCP_TRANSPORT?: string;
      MCP_PORT?: string;
      ORCHESTRATOR_URL?: string;
      OAUTH_JWKS_URI?: string;
      OAUTH_ISSUER?: string;
      OAUTH_AUDIENCE?: string;
    }
  }
}
