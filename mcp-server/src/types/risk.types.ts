import { ExplainableResult } from './regulatory.types';

export type RiskTier = 'PROHIBITED' | 'HIGH' | 'LIMITED' | 'MINIMAL';

export interface RiskTierResult extends ExplainableResult {
  tier: RiskTier;
  blocking: boolean;
  annex_iii_domain?: string;
}
