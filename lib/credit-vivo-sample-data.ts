export const sampleFindings = {
  scoreGoal: "Better credit readiness",
  negativeItemsFound: 9,
  possibleErrors: 6,
  disputeDraftsReady: 5,
  positiveAccountsKept: 5,
  nextStep: "Review your dispute drafts",
};

export const sampleNegativeAccounts = [
  {
    name: "Caine & Weiner / Progressive",
    type: "Collection / paid collection review",
    bureaus: "Experian, Equifax, TransUnion",
    why: "Balance/status appears different across bureaus.",
    nextStep: "Verify current balance, paid/settled status, and original creditor.",
    priority: "High",
  },
  {
    name: "Capital One",
    type: "Charge-off review",
    bureaus: "Experian, Equifax, TransUnion",
    why: "Charge-off is reporting across all three bureaus.",
    nextStep: "Verify balance, charge-off amount, DOFD, payment history, and removal timeline.",
    priority: "High",
  },
  {
    name: "Credit One Bank — 12/27/2022",
    type: "Late-payment review",
    bureaus: "Experian, Equifax, TransUnion",
    why: "One or more bureaus show a 30-day late history while account is currently open/current.",
    nextStep: "Verify the late-payment support before any dispute draft is approved.",
    priority: "Medium",
  },
  {
    name: "Jefferson Capital / Verizon Wireless",
    type: "Debt buyer collection review",
    bureaus: "Experian, Equifax, TransUnion",
    why: "Collection appears across bureaus with reporting details to verify.",
    nextStep: "Verify original creditor, chain of title, balance, DOFD, and collection authority.",
    priority: "High",
  },
  {
    name: "LVNV / Resurgent / Capital One Platinum",
    type: "Debt buyer collection review",
    bureaus: "Experian, Equifax, TransUnion",
    why: "Collection reporting should be checked for balance, ownership, and dates.",
    nextStep: "Verify original creditor, itemization, and reporting timeline.",
    priority: "High",
  },
];

export const samplePositiveAccounts = [
  "Credit One Bank — 03/09/2026",
  "Ford Motor Credit",
  "Northwest Federal Credit",
  "JPMCB Card",
  "Macys/Citibank",
];

export const progressSteps = [
  { label: "Report uploaded", status: "complete" },
  { label: "AI review complete", status: "complete" },
  { label: "Drafts ready", status: "current" },
  { label: "Customer approved", status: "pending" },
  { label: "Mailed / submitted", status: "pending" },
  { label: "Waiting for response", status: "pending" },
  { label: "Response received", status: "pending" },
  { label: "Next step", status: "pending" },
];
