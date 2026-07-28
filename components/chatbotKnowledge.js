export const REQUIRED_DISCLAIMER =
  'Results vary. Credit Vivo does not guarantee removals, approvals, credit score increases, or timelines.';

export const SAFE_ATTORNEY_WORDING =
  'Attorney review may be available for eligible unresolved credit-reporting issues through a separate compliant arrangement.';

export const officialSources = {
  croa: 'https://www.ftc.gov/legal-library/browse/statutes/credit-repair-organizations-act',
  disputeCfpb: 'https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/',
  disputeFtc: 'https://consumer.ftc.gov/articles/disputing-errors-your-credit-reports-0',
  debtValidation: 'https://www.consumerfinance.gov/ask-cfpb/what-information-does-a-debt-collector-have-to-give-me-about-the-debt-en-331/',
  debtValidationRule: 'https://www.consumerfinance.gov/rules-policy/regulations/1006/34',
  cfpbComplaint: 'https://www.consumerfinance.gov/complaint/',
  creditReports: 'https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/'
};

export const creditVivoBrain = {
  identity:
    'Credit Vivo is a credit report review and credit readiness portal. The safe mechanism is review, organize, document, dispute possible reporting errors, track responses, educate, and escalate eligible unresolved issues for human review.',
  promise:
    'Credit Vivo helps customers understand possible inaccurate, incomplete, outdated, duplicate, unverifiable, mixed-file, fraud-related, or reporting-error items. It does not guarantee removals, approvals, score increases, or timelines.',
  customerPath: [
    'Upload report or create a test preview',
    'Review customer-friendly findings',
    'Confirm facts and supporting documents',
    'Prepare dispute-ready items for human review',
    'Track bureau/furnisher responses',
    'Plan the next round only when evidence supports it',
    'Use monthly updates and credit-building tasks while disputes run'
  ],
  staffRules: [
    'Never send a dispute letter without customer review and authorization.',
    'Never assert identity theft, fraud, payment, balance, or account facts the customer has not confirmed.',
    'Never put SSNs, full DOBs, IDs, bureau credentials, credit report PDFs, or payment data into chat.',
    'Keep forensic/Metro 2 details internal; customers get plain-English explanations.',
    'Route legal, attorney, complaint, refund, cancellation, and sensitive-data questions to staff review.'
  ],
  escalationTriggers: [
    'possible identity theft or mixed-file issue',
    'repeat wrong reporting after prior disputes',
    'debt collector cannot provide basic validation information',
    'bureau or furnisher response conflicts with documents',
    'customer asks for legal advice, lawsuit evaluation, or attorney action',
    'customer reports threats, harassment, or possible FDCPA/FCRA issue'
  ]
};

export const demoCustomerAccounts = [
  {
    accountId: 'CV-DEMO-1001',
    customerName: 'Test Customer',
    aliases: ['test customer', 'test', 'demo customer'],
    status: 'Manual review queued',
    plan: 'Launch preview',
    assignedSpecialist: 'Credit Vivo Support',
    activeReviewItems: 6,
    documentsNeeded: ['Government ID', 'Proof of address'],
    latestUpdate: 'Initial issue review completed',
    lastActivity: 'Today 9:12 AM',
    nextStep: 'Upload ID and proof of address before dispute drafts are finalized.'
  },
  {
    accountId: 'CV-DEMO-1002',
    customerName: 'Maria Lopez',
    aliases: ['maria lopez', 'maria'],
    status: 'Documents needed',
    plan: 'Credit review preview',
    assignedSpecialist: 'Credit Vivo Support',
    activeReviewItems: 4,
    documentsNeeded: ['Proof of address', 'Collector letter'],
    latestUpdate: 'Collection validation review started',
    lastActivity: 'Yesterday 3:40 PM',
    nextStep: 'Upload the collector letter and current proof of address in the secure vault.'
  },
  {
    accountId: 'CV-DEMO-1003',
    customerName: 'Jayden Smith',
    aliases: ['jayden smith', 'jayden'],
    status: 'Response tracking',
    plan: 'Monthly update preview',
    assignedSpecialist: 'Credit Vivo Support',
    activeReviewItems: 3,
    documentsNeeded: ['Bureau response letter'],
    latestUpdate: 'Waiting for bureau response window',
    lastActivity: 'Monday 11:20 AM',
    nextStep: 'Upload any bureau response letter before staff prepares the next review.'
  }
];

const accountLookupWords = [
  'account',
  'acct',
  'case',
  'customer',
  'client',
  'lookup',
  'look up',
  'name',
  'status',
  'progress'
];

const intentSynonyms = {
  upload: ['send report', 'add report', 'credit karma pdf', 'identityiq', 'smartcredit', 'myscoreiq', 'file report'],
  process: ['how long', 'what now', 'start', 'begin', 'signed up', 'new client', 'joined', 'onboard'],
  dispute: ['fix error', 'wrong item', 'not mine', 'bureau error', 'incorrect', 'investigate', 'reinvestigate'],
  collections: ['collector calling', 'collection agency', 'debt buyer', 'validate debt', 'midland', 'portfolio recovery', 'jefferson capital'],
  identity: ['id theft', 'fraud alert', 'mixed file', 'wrong address', 'wrong name', 'someone opened', 'stolen identity'],
  pricing: ['membership', 'billing', 'charge', 'charged', 'subscription', 'cancel plan', 'refund'],
  attorney: ['lawyer', 'sue', 'lawsuit', 'court', 'rights violated', 'attorney'],
  score: ['points', 'fico', 'vantage', 'credit score', 'mortgage', 'auto loan', 'approval'],
  complaint: ['cfpb', 'bbb', 'complain', 'ignored me', 'no answer', 'escalation'],
  staff: ['agent', 'human', 'specialist', 'support', 'representative', 'case worker'],
  account_status: ['where am i', 'case status', 'my status', 'customer file', 'client file', 'account lookup']
};

export const chatbotQuickReplies = [
  'Look up my case status',
  'What should I upload next?',
  'Explain this in simple words',
  'What needs staff review?',
  'What can Credit Vivo do safely?'
];

export const creditVivoKnowledge = [
  {
    id: 'upload',
    title: 'Uploading a credit report',
    keywords: ['upload', 'report', 'pdf', 'scan', 'file', 'bureau'],
    answer:
      'You can start at /scan and upload one 3-bureau report or separate Experian, Equifax, and TransUnion reports. Use the secure upload flow only for your own report. Do not send passwords, full Social Security numbers, unrelated IDs, or unrelated sensitive documents through chat.',
    nextStep: 'Go to /scan and use a sample or your own report only when the secure portal is ready.',
    sources: []
  },
  {
    id: 'process',
    title: 'Credit Vivo process',
    keywords: ['process', 'how it works', 'next', 'after upload', 'what happens'],
    answer:
      `${creditVivoBrain.identity} After upload, Credit Vivo organizes the report, looks for possible inaccurate, incomplete, outdated, duplicate, or unverifiable items, prepares customer-friendly findings, and tracks next steps. A human review should happen before any dispute package is sent.`,
    nextStep: 'Open /findings after upload to review the plain-English findings.',
    sources: []
  },
  {
    id: 'dispute',
    title: 'Dispute basics',
    keywords: ['dispute', 'bureau', 'furnisher', 'experian', 'equifax', 'transunion'],
    answer:
      'A dispute is a request for a credit bureau or furnisher to investigate information that may be inaccurate, incomplete, outdated, duplicate, unverifiable, or tied to identity issues. Customers can dispute directly with credit bureaus and furnishers at no cost. A good dispute should identify the item, state the facts, explain why the information is disputed, and include supporting documents when available.',
    nextStep: 'Review each finding and confirm documents before any dispute draft is finalized.',
    sources: [officialSources.disputeCfpb, officialSources.disputeFtc, officialSources.creditReports]
  },
  {
    id: 'collections',
    title: 'Collections and validation',
    keywords: ['collection', 'collector', 'debt', 'validation', 'fdcpa'],
    answer:
      'For collection accounts, the safer workflow is to review ownership, balance, dates, original creditor information, and whether the item is reporting consistently. Debt collectors generally must provide validation information about the debt, including who the creditor is, the amount, and how to dispute it. If a collector contacts you, keep the letter/message and avoid unsupported claims.',
    nextStep: 'Upload collector letters or bureau responses in the portal when secure storage is connected.',
    sources: [officialSources.debtValidation, officialSources.debtValidationRule]
  },
  {
    id: 'identity',
    title: 'Identity and fraud workflow',
    keywords: ['identity', 'fraud', 'theft', 'stolen', 'id', 'passport', 'license'],
    answer:
      'Identity-related issues may require extra documents such as proof of identity, proof of address, or an FTC identity theft report. Credit Vivo should not create identity-theft claims unless the customer confirms the facts and provides supporting documents. Mixed-file, fraud, old address, name variation, and employer-data issues should be reviewed carefully before any account disputes.',
    nextStep: 'If identity theft may be involved, route the case to staff review before any letters are prepared.',
    sources: [officialSources.disputeCfpb]
  },
  {
    id: 'pricing',
    title: 'Pricing and payments',
    keywords: ['price', 'pricing', 'cost', 'pay', 'payment', 'stripe', 'refund', 'cancel'],
    answer:
      'Credit Vivo pricing should be clear about what is included and what may be separate, such as postage, certified mail, credit monitoring, report access, identity verification, attorney review, or third-party costs. Credit repair marketing and contracts must avoid misleading claims and must respect cancellation and fee rules. Payment checkout is still marked as launch preview until vendors are connected.',
    nextStep: 'Open /pricing and review the written plan before paying for any service.',
    sources: [officialSources.croa]
  },
  {
    id: 'attorney',
    title: 'Attorney escalation',
    keywords: ['attorney', 'lawyer', 'lawsuit', 'sue', 'legal', 'court'],
    answer:
      `${SAFE_ATTORNEY_WORDING} The chatbot cannot decide that you have a lawsuit or give legal advice. It can help identify when staff should review whether escalation may be appropriate.`,
    nextStep: 'Route unresolved, documented, high-impact issues to staff or attorney-review hold.',
    sources: []
  },
  {
    id: 'score',
    title: 'Scores and results',
    keywords: ['score', 'increase', 'boost', 'delete', 'remove', 'approval', 'mortgage', 'car'],
    answer:
      'Credit report changes and score movement depend on the facts, bureau data, scoring model, balances, payment history, new accounts, timing, and lender criteria. Credit Vivo can help organize possible issues and next steps, but results are not guaranteed.',
    nextStep: 'Use the dashboard and monthly update pages to track progress without assuming a specific score result.',
    sources: [officialSources.croa]
  },
  {
    id: 'complaint',
    title: 'CFPB or regulator complaint routing',
    keywords: ['cfpb', 'complaint', 'regulator', 'ignored', 'no response', 'bureau ignored', 'escalate'],
    answer:
      'A CFPB complaint may be appropriate only after the customer has a real issue and supporting details. The customer should first keep documents, dates, dispute copies, responses, and communication records. Credit Vivo should not file complaints automatically or exaggerate facts. Staff should review the timeline and documents before any complaint help.',
    nextStep: 'Route complaint questions to staff review and collect the timeline, documents, and prior responses.',
    sources: [officialSources.cfpbComplaint, officialSources.creditReports]
  },
  {
    id: 'staff',
    title: 'Staff next-action workflow',
    keywords: ['staff', 'specialist', 'review', 'what should we do', 'next action', 'workflow'],
    answer:
      `Credit Vivo staff should follow this order: ${creditVivoBrain.customerPath.join(' -> ')}. Staff should keep forensic details internal, show the customer plain-English explanations, and only move items forward when the facts and documents support the next step.`,
    nextStep: 'Use dashboard, findings, vault, messages, and monthly update pages to keep the customer informed.',
    sources: []
  },
  {
    id: 'account_status',
    title: 'Customer account status lookup',
    keywords: ['account', 'acct', 'customer', 'client', 'case', 'lookup', 'look up', 'status', 'name'],
    answer:
      'Credit Vivo can give a basic default account status when a customer name or account ID matches a safe demo record. The chatbot should only show non-sensitive status fields, such as case stage, documents needed, latest update, and next step. Real customer lookup must require secure login and staff authorization before showing private account data.',
    nextStep: 'Ask for a demo customer name or account ID, such as CV-DEMO-1001, Maria Lopez, or Jayden Smith.',
    sources: []
  }
];

export const defaultChatQa = creditVivoKnowledge.map((item) => ({
  id: item.id,
  question: item.keywords[1]
    ? `What should I know about ${item.title.toLowerCase()}?`
    : item.title,
  answer: item.answer,
  nextStep: item.nextStep,
  sources: item.sources || []
}));

export const blockedPatterns = [
  {
    id: 'guarantee',
    pattern: /\b(guarantee|guaranteed|100%|for sure|promise)\b/i,
    reason: 'Guarantees about credit repair, approvals, deletions, or score increases are not allowed.'
  },
  {
    id: 'delete_anything',
    pattern: /\b(delete|remove|erase)\b.*\b(anything|accurate|all|everything|guaranteed)\b/i,
    reason: 'The chatbot cannot claim accurate information can be removed or that any item will be deleted.'
  },
  {
    id: 'fake_dispute',
    pattern: /\b(fake|lie|make up|false|not mine even though|dispute accurate)\b/i,
    reason: 'Credit Vivo cannot help create false disputes or unsupported identity-theft claims.'
  },
  {
    id: 'cpn',
    pattern: /\b(cpn|credit privacy number|new credit identity|tradeline fraud)\b/i,
    reason: 'The chatbot cannot help with CPNs, synthetic identities, or identity misuse.'
  },
  {
    id: 'legal_advice',
    pattern: /\b(do i have a lawsuit|can i sue|will i win|legal advice|court strategy)\b/i,
    reason: 'Legal questions require qualified attorney review.'
  },
  {
    id: 'sensitive_data',
    pattern: /\b\d{3}-?\d{2}-?\d{4}\b|\b\d{1,2}\/\d{1,2}\/(?:19|20)\d{2}\b|\b(?:passport|driver'?s?\s*license|state id)\s*[:#]?\s*[A-Z0-9-]{4,}\b/i,
    reason: 'Do not send full SSNs, full DOBs, IDs, or private document numbers in chat.'
  }
];

export function findKnowledge(question) {
  const lower = String(question || '').toLowerCase();
  const scored = creditVivoKnowledge
    .map((item) => ({
      item,
      score:
        item.keywords.reduce((count, keyword) => count + (lower.includes(keyword) ? 2 : 0), 0) +
        (intentSynonyms[item.id] || []).reduce((count, phrase) => count + (lower.includes(phrase) ? 3 : 0), 0)
    }))
    .sort((a, b) => b.score - a.score);

  return scored[0]?.score > 0 ? scored[0].item : creditVivoKnowledge[1];
}

export function getConversationStyle(question) {
  const lower = String(question || '').toLowerCase();
  const vague =
    lower.length < 24 ||
    /\b(help|confused|what now|next|status|idk|don't know|dont know|explain)\b/i.test(lower);
  const worried = /\b(scared|worried|urgent|angry|mad|stressed|panic|problem|wrong|ignored)\b/i.test(lower);
  const simple = /\b(simple|plain english|explain|break it down|what does this mean)\b/i.test(lower);

  return { vague, worried, simple };
}

export function getSuggestedReplies(topicId, status = 'ok') {
  if (status === 'blocked') {
    return ['Contact staff', 'What can Credit Vivo do safely?', 'Why was this blocked?'];
  }

  if (status === 'not_found') {
    return ['Look up status for CV-DEMO-1001', 'Look up customer Maria Lopez', 'What is Jayden Smith account status?'];
  }

  const suggestions = {
    upload: ['What documents do I need?', 'What happens after upload?', 'Open /scan'],
    process: ['What is my next step?', 'What needs staff review?', 'Look up my case status'],
    dispute: ['What makes a strong dispute?', 'What documents support this?', 'What should staff review?'],
    collections: ['What is debt validation?', 'What collector documents help?', 'Should this go to staff?'],
    identity: ['What identity documents help?', 'When is fraud staff review needed?', 'What should I not send in chat?'],
    pricing: ['What is included?', 'Why no guarantees?', 'What is still launch preview?'],
    attorney: ['When does staff escalate?', 'What can the chatbot say?', 'What documents matter?'],
    score: ['Why do scores vary?', 'What can I do monthly?', 'What affects score movement?'],
    complaint: ['What documents support a complaint?', 'When should staff review?', 'What happened before escalation?'],
    staff: ['What is the customer path?', 'What should staff avoid?', 'What is next action?'],
    account_status: ['What should I upload next?', 'Show latest update', 'What needs staff review?']
  };

  return suggestions[topicId] || chatbotQuickReplies;
}

function normalizeLookup(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function findCustomerAccount(question) {
  const normalized = normalizeLookup(question);
  const wantsLookup = accountLookupWords.some((word) => normalized.includes(word));
  const accountIdMatch = String(question || '').match(/\bCV-[A-Z0-9-]+\b/i);

  if (!wantsLookup && !accountIdMatch) {
    return null;
  }

  const accountId = accountIdMatch?.[0]?.toUpperCase();
  const account = demoCustomerAccounts.find((item) => {
    if (accountId && item.accountId.toUpperCase() === accountId) return true;
    return item.aliases.some((alias) => normalized.includes(alias));
  });

  if (!account) {
    return {
      matched: false,
      topic: 'Customer account status lookup',
      answer:
        'I can look up default demo accounts by customer name or account ID, but I did not find a matching demo record. For real customers, use secure portal login or staff verification before showing account status.',
      nextStep: 'Try CV-DEMO-1001, Maria Lopez, Jayden Smith, or route the real customer to secure login.',
      sources: []
    };
  }

  return {
    matched: true,
    topic: 'Customer account status lookup',
    account,
    answer:
      `Account ${account.accountId} is for ${account.customerName}.\n\n` +
      `Status: ${account.status}\n` +
      `Plan: ${account.plan}\n` +
      `Assigned team: ${account.assignedSpecialist}\n` +
      `Active review items: ${account.activeReviewItems}\n` +
      `Documents needed: ${account.documentsNeeded.length ? account.documentsNeeded.join(', ') : 'None listed'}\n` +
      `Latest update: ${account.latestUpdate}\n` +
      `Last activity: ${account.lastActivity}`,
    nextStep: account.nextStep,
    sources: []
  };
}

export function getBrainSummary() {
  return {
    identity: creditVivoBrain.identity,
    promise: creditVivoBrain.promise,
    customerPath: creditVivoBrain.customerPath,
    staffRules: creditVivoBrain.staffRules,
    escalationTriggers: creditVivoBrain.escalationTriggers,
    defaultChatQa,
    quickReplies: chatbotQuickReplies,
    demoCustomerAccounts: demoCustomerAccounts.map((account) => ({
      accountId: account.accountId,
      customerName: account.customerName,
      status: account.status,
      nextStep: account.nextStep
    })),
    officialSources
  };
}

export function checkChatCompliance(text) {
  const hits = blockedPatterns.filter((rule) => rule.pattern.test(String(text || '')));
  const safeHits = hits.map((hit) => ({
    id: hit.id,
    reason: hit.reason,
  }));
  return {
    blocked: hits.some((hit) => hit.id !== 'legal_advice'),
    needsStaffReview: hits.length > 0,
    hits: safeHits
  };
}
