import { getRegulatorySummary } from './regulatory_citations';

export function formatExplanation(
  baseExplanation: string,
  regulatoryCitations: string[],
  phase: number
): string {
  const citationsText = regulatoryCitations
    .map(c => `${c}: ${getRegulatorySummary(c)}`)
    .join('\n');

  return `${baseExplanation}\n\nRegulatory Basis (Phase ${phase}):\n${citationsText}`;
}
