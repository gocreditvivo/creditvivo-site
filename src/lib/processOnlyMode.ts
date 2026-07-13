export const PROCESS_ONLY_FLAGS = {
  PROCESS_ONLY_MODE: true,
  LOCAL_EXPORT_MODE: false,
  PRODUCTION_SEND_MODE: false,
  SECURE_VAULT_WRITE: false,
  PAYMENTS_ENABLED: false,
  COMMERCIAL_LAUNCH_READY: false,
} as const;

export type RiskyAction =
  | 'real_upload'
  | 'local_export'
  | 'production_send'
  | 'secure_vault_write'
  | 'payment'
  | 'attorney_packet_share'
  | 'scanner_parse_real_data'
  | 'supabase_production_write';

export function isProcessOnlyMode() {
  return PROCESS_ONLY_FLAGS.PROCESS_ONLY_MODE;
}

export function getProcessOnlyBlock(action: RiskyAction) {
  return {
    ok: false,
    action,
    status: 'BLOCKED',
    reason: 'Credit Vivo TEST VERSION is process-only. No production action is enabled.',
    flags: PROCESS_ONLY_FLAGS,
  };
}

export function assertProcessOnlyBlocked(action: RiskyAction): never {
  throw new Error(`${action} blocked: Credit Vivo TEST VERSION is process-only.`);
}

export const REQUIRED_SAFETY_LABELS = [
  'Simulation only',
  'Draft only',
  'Not sent',
  'Approval required',
  'Admin review required',
  'Compliance blocked',
  'Secure vault required',
  'Production blocked',
  'Tim approval required',
] as const;
