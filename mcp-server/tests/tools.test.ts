import { checkBlocker } from '../src/utils/blocker_logic';

describe('Blocker Logic', () => {
  it('should detect BLOCKER_FAIL', () => {
    const result = { result: 'BLOCKER_FAIL', explanation: 'Test fail' };
    const blocker = checkBlocker(result);
    expect(blocker).not.toBeNull();
    expect(blocker?.blocking).toBe(true);
  });

  it('should detect blocking: true', () => {
    const result = { blocking: true, explanation: 'Test blocking' };
    const blocker = checkBlocker(result);
    expect(blocker).not.toBeNull();
    expect(blocker?.blocking).toBe(true);
  });

  it('should return null for non-blocking results', () => {
    const result = { tier: 'MINIMAL', blocking: false };
    const blocker = checkBlocker(result);
    expect(blocker).toBeNull();
  });
});
