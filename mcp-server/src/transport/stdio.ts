import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { logger } from '../index.js';

export async function startStdioTransport(server: McpServer): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  logger.info('MCP Server running on stdio transport');

  process.on('SIGINT', async () => {
    logger.info('Shutting down stdio transport');
    await server.close();
    process.exit(0);
  });
}
