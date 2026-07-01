import http from 'node:http';
import crypto from 'node:crypto';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { logger } from '../index.js';
import { validateBearerToken } from '../auth/oauth.js';
import type { TokenClaims } from '../types/mcp.d.js';

const PORT = parseInt(process.env.MCP_PORT || '3000', 10);

// In-memory token bucket for rate limiting (100 req/min per org_id)
const rateBuckets = new Map<string, { tokens: number; lastRefill: number }>();
const RATE_LIMIT = 100;
const RATE_WINDOW_MS = 60_000;

function checkRateLimit(orgId: string): boolean {
  const now = Date.now();
  let bucket = rateBuckets.get(orgId);
  if (!bucket || now - bucket.lastRefill >= RATE_WINDOW_MS) {
    bucket = { tokens: RATE_LIMIT, lastRefill: now };
    rateBuckets.set(orgId, bucket);
  }
  if (bucket.tokens <= 0) return false;
  bucket.tokens -= 1;
  return true;
}

function getAuthHeader(req: http.IncomingMessage): string | null {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Bearer ')) return null;
  return auth.slice(7);
}

function sendSSE(res: http.ServerResponse, event: string, data: any) {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

async function handleRequest(
  req: http.IncomingMessage,
  res: http.ServerResponse,
  server: McpServer,
) {
  const requestId = crypto.randomUUID();
  res.setHeader('X-Request-ID', requestId);

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === 'GET' && req.url === '/sse') {
    // Validate auth for SSE
    const token = getAuthHeader(req);
    if (!token) {
      res.writeHead(401, { 'WWW-Authenticate': 'Bearer realm="ai-compliance-mcp", error="invalid_token"' });
      res.end(JSON.stringify({ error: 'Missing Authorization header' }));
      return;
    }
    try {
      await validateBearerToken(token);
    } catch (err: any) {
      res.writeHead(401, { 'WWW-Authenticate': 'Bearer realm="ai-compliance-mcp", error="invalid_token"' });
      res.end(JSON.stringify({ error: err.message }));
      return;
    }

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    });

    sendSSE(res, 'connected', { requestId, message: 'SSE connection established' });

    req.on('close', () => {
      logger.info('SSE client disconnected', { requestId });
    });
    return;
  }

  if (req.method === 'POST' && req.url === '/messages') {
    // Validate auth
    const token = getAuthHeader(req);
    if (!token) {
      res.writeHead(401, { 'WWW-Authenticate': 'Bearer realm="ai-compliance-mcp", error="invalid_token"' });
      res.end(JSON.stringify({ error: 'Missing Authorization header' }));
      return;
    }
    let tokenClaims: TokenClaims;
    try {
      tokenClaims = await validateBearerToken(token);
    } catch (err: any) {
      res.writeHead(401, { 'WWW-Authenticate': 'Bearer realm="ai-compliance-mcp", error="invalid_token"' });
      res.end(JSON.stringify({ error: err.message }));
      return;
    }

    // Rate limit
    if (!checkRateLimit(tokenClaims.org_id)) {
      res.writeHead(429, { 'Retry-After': '60' });
      res.end(JSON.stringify({ error: 'Rate limit exceeded. Try again in 60 seconds.' }));
      return;
    }

    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        // Parse and forward JSON-RPC to MCP SDK
        const message = JSON.parse(body);
        logger.info('Received message', { requestId, method: message.method });

        // For now, reflect back. The MCP SDK processes messages internally.
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          jsonrpc: '2.0',
          id: message.id,
          result: { status: 'received', phase: message.method },
        }));
      } catch (err: any) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON-RPC request' }));
      }
    });
    return;
  }

  // Health check
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy', transport: 'http', port: PORT }));
    return;
  }

  res.writeHead(404);
  res.end('Not found');
}

export async function startHttpTransport(server: McpServer): Promise<void> {
  const httpServer = http.createServer((req, res) =>
    handleRequest(req, res, server).catch((err) => {
      logger.error('HTTP handler error', { error: err.message });
      res.writeHead(500);
      res.end('Internal server error');
    }),
  );

  return new Promise((resolve) => {
    httpServer.listen(PORT, () => {
      logger.info(`MCP Server running on HTTP/SSE transport at port ${PORT}`);
      resolve();
    });
  });
}
