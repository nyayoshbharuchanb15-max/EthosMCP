import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import winston from 'winston';
import { registerTools } from './server.js';
import { startStdioTransport } from './transport/stdio.js';
import { startHttpTransport } from './transport/sse.js';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
  ),
  defaultMeta: { service: 'ai-compliance-mcp-server' },
  transports: [
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'production'
        ? winston.format.json()
        : winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
  ],
});

const server = new McpServer({
  name: 'ai-compliance-mcp-server',
  version: '1.0.0',
  description: '9-phase AI compliance audit pipeline — risk classification, bias assessment, adversarial testing, and W3C VC 2.0 certificate issuance',
});

registerTools(server);

async function main() {
  const transport = process.env.MCP_TRANSPORT || 'stdio';

  if (transport === 'http') {
    await startHttpTransport(server);
  } else if (transport === 'stdio' || process.argv.includes('--stdio')) {
    await startStdioTransport(server);
  } else if (process.argv.includes('--http')) {
    await startHttpTransport(server);
  } else {
    await startStdioTransport(server);
  }

  // Health check tool
  server.tool(
    'health_check',
    {},
    async () => ({
      content: [{ type: 'text', text: JSON.stringify({
        status: 'healthy',
        version: '1.0.0',
        transport: process.env.MCP_TRANSPORT || 'stdio',
        timestamp: new Date().toISOString(),
      }) }],
    }),
  );

  logger.info('AI Compliance MCP Server started', {
    transport: process.env.MCP_TRANSPORT || 'stdio',
    orchestrator: process.env.ORCHESTRATOR_URL || 'http://localhost:8080',
  });
}

main().catch((error) => {
  logger.error('Fatal startup error', { error: error.message, stack: error.stack });
  process.exit(1);
});
