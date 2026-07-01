import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';
import type { TokenClaims } from '../types/mcp.d.js';

const JWKS_CACHE_TTL_MS = 5 * 60 * 1000;
let jwksCache: { jwks: ReturnType<typeof createRemoteJWKSet>; fetchedAt: number } | null = null;

function getJWKS() {
  const uri = process.env.OAUTH_JWKS_URI;
  if (!uri) {
    throw new Error('OAUTH_JWKS_URI environment variable is required for HTTP transport');
  }
  if (jwksCache && Date.now() - jwksCache.fetchedAt < JWKS_CACHE_TTL_MS) {
    return jwksCache.jwks;
  }
  const jwks = createRemoteJWKSet(new URL(uri));
  jwksCache = { jwks, fetchedAt: Date.now() };
  return jwks;
}

export async function validateBearerToken(token: string): Promise<TokenClaims> {
  const jwks = getJWKS();
  const expectedIssuer = process.env.OAUTH_ISSUER;
  const expectedAudience = process.env.OAUTH_AUDIENCE || 'ai-compliance-mcp';

  try {
    const { payload } = await jwtVerify(token, jwks, {
      issuer: expectedIssuer,
      audience: expectedAudience,
      algorithms: ['RS256', 'ES256', 'EdDSA'],
    });

    const scope = extractScope(payload);
    const claims: TokenClaims = {
      sub: payload.sub || 'unknown',
      scope,
      org_id: (payload as any).org_id || (payload as any).organization_id || 'unknown',
      exp: payload.exp || 0,
      iss: payload.iss || '',
      aud: expectedAudience,
    };

    return claims;
  } catch (err: any) {
    const msg = err.code === 'ERR_JWT_EXPIRED' ? 'Token expired' : `Unauthorized: ${err.message}`;
    throw { code: -32001, message: msg };
  }
}

function extractScope(payload: JWTPayload): string[] {
  const raw = payload.scope;
  if (typeof raw === 'string') return raw.split(/\s+/);
  if (Array.isArray(raw)) return raw.map(String);
  return [];
}
