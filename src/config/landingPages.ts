/**
 * Landing Page Variant Configuration
 *
 * Controls which homepage variant is served. Supports:
 * - Config-based switching (set activeVariant below)
 * - Route-based switching (e.g. /lp/animated, /lp/classic)
 * - A/B testing (set abTest.enabled and the split)
 *
 * To add a new variant:
 * 1. Create a component in src/pages/landing/
 * 2. Import it in App.tsx
 * 3. Add it to the variants array below
 */

export type VariantId = 'classic' | 'animated' | 'dovly';

export interface LandingVariant {
  id: VariantId;
  name: string;
  description: string;
  component: string; // component path for reference
}

export const variants: LandingVariant[] = [
  {
    id: 'classic',
    name: 'Classic',
    description: 'Current minimal homepage with glassmorphism hero',
    component: 'src/pages/Home.tsx',
  },
  {
    id: 'animated',
    name: 'Animated (Dovly-style)',
    description: 'Full motion design with scroll reveals, animated counters, floating dashboard, progress bars, and scan-line effects',
    component: 'src/pages/landing/HomeAnimated.tsx',
  },
];

/**
 * Active variant for the default homepage (/).
 * Change this to switch the default landing page.
 */
export const activeVariant: VariantId = 'animated';

/**
 * A/B test configuration.
 * When enabled, visitors are randomly assigned a variant
 * based on the configured weights. The assignment is stored
 * in localStorage so the same user sees the same variant
 * on repeat visits.
 */
export const abTest = {
  enabled: false,
  // Weights must sum to 100
  weights: {
    classic: 0,
    animated: 100,
  } as Record<VariantId, number>,
  storageKey: 'cv_lp_variant',
};

/**
 * Campaign landing page configuration.
 * Each campaign targets a specific audience/use case.
 */
export interface CampaignPage {
  slug: string;
  title: string;
  description: string;
  audience: string;
  route: string;
}

export const campaignPages: CampaignPage[] = [
  {
    slug: 'auto-loan-denial',
    title: 'Auto Loan Denial',
    description: 'Credit issues blocking auto loan approval',
    audience: 'Consumers denied auto financing',
    route: '/auto-loan-denial',
  },
  {
    slug: 'mortgage-readiness',
    title: 'Mortgage Readiness',
    description: 'Prepare credit profile for mortgage application',
    audience: 'Prospective homebuyers',
    route: '/mortgage-readiness',
  },
  {
    slug: 'apartment-denial',
    title: 'Apartment Denial',
    description: 'Credit issues blocking rental application',
    audience: 'Renters denied housing',
    route: '/apartment-denial',
  },
  {
    slug: 'collection-not-mine',
    title: 'Collection Not Mine',
    description: 'Dispute collections that dont belong to you',
    audience: 'Consumers with erroneous collections',
    route: '/collection-not-mine',
  },
];

/**
 * Get the assigned variant for a visitor.
 * Uses localStorage for sticky assignment.
 */
export function getAssignedVariant(): VariantId {
  if (typeof window === 'undefined') return activeVariant;

  // Check for URL override first (?variant=classic)
  const params = new URLSearchParams(window.location.search);
  const override = params.get('variant') as VariantId | null;
  if (override && variants.some((v) => v.id === override)) {
    return override;
  }

  // If A/B testing is disabled, use the active variant
  if (!abTest.enabled) return activeVariant;

  // Check localStorage for sticky assignment
  try {
    const stored = localStorage.getItem(abTest.storageKey) as VariantId | null;
    if (stored && variants.some((v) => v.id === stored)) {
      return stored;
    }
  } catch {
    // localStorage not available
  }

  // Random assignment based on weights
  const random = Math.random() * 100;
  let cumulative = 0;
  for (const variant of variants) {
    cumulative += abTest.weights[variant.id] ?? 0;
    if (random <= cumulative) {
      try {
        localStorage.setItem(abTest.storageKey, variant.id);
      } catch {
        // localStorage not available
      }
      return variant.id;
    }
  }

  return activeVariant;
}
