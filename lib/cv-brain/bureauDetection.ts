import { BUREAU_MARKERS } from './rules';
import type { Bureau } from '@/types/credit';

export type BureauDetectionResult = {
  detectedBureaus: Bureau[];
  reportType: 'single_bureau' | 'merged_3_bureau' | 'partial' | 'unknown';
  confidenceScore: number;
  warnings: string[];
};

export function detectBureaus(rawText: string): BureauDetectionResult {
  const lower = rawText.toLowerCase();
  const detected = Object.entries(BUREAU_MARKERS)
    .filter(([, markers]) => markers.some((m) => lower.includes(m)))
    .map(([bureau]) => bureau as Bureau);

  const unique = Array.from(new Set(detected));
  const reportType = unique.length >= 3 ? 'merged_3_bureau' : unique.length === 1 ? 'single_bureau' : unique.length > 1 ? 'partial' : 'unknown';
  const confidenceScore = unique.length >= 3 ? 0.95 : unique.length === 1 ? 0.82 : unique.length > 1 ? 0.75 : 0.25;
  const warnings = unique.length === 0 ? ['Bureau could not be detected. Admin review required.'] : [];

  return { detectedBureaus: unique.length ? unique : ['Unknown'], reportType, confidenceScore, warnings };
}
