import { describe, it, expect } from 'vitest';
import { translations } from '../src/lib/i18n';

describe('Frontend i18n & Utility Tests', () => {
  it('should have complete English and Tamil translations for key portal strings', () => {
    expect(translations.en.portalTitle).toContain('Tamil Nadu');
    expect(translations.ta.portalTitle).toContain('தமிழ்நாடு');
    expect(translations.en.submitComplaint).toBe('Submit Grievance');
    expect(translations.ta.submitComplaint).toBe('மனு தாக்கல் செய்க');
  });
});
