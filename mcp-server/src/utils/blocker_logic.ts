export interface BlockerResult {
  blocking: boolean;
  result: string;
  explanation: string;
}

export function checkBlocker(result: any): BlockerResult | null {
  if (result.blocking === true || result.result === 'BLOCKER_FAIL') {
    return {
      blocking: true,
      result: 'BLOCKER_FAIL',
      explanation: result.explanation || 'A critical regulatory blocker was encountered, halting the audit pipeline.'
    };
  }
  return null;
}
