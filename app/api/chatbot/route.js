import {
  checkChatCompliance,
  findCustomerAccount,
  findKnowledge,
  getConversationStyle,
  getSuggestedReplies,
  getBrainSummary,
  REQUIRED_DISCLAIMER,
} from "../../../components/chatbotKnowledge";

const MAX_MESSAGE_LENGTH = 1200;

function cleanMessage(value) {
  return String(value || "")
    .replace(/[<>]/g, "")
    .trim()
    .slice(0, MAX_MESSAGE_LENGTH);
}

function safeFallbackAnswer(question) {
  const topic = findKnowledge(question);
  const brain = getBrainSummary();
  const style = getConversationStyle(question);
  const opening = style.worried
    ? "I hear you. Let's slow it down and handle this one step at a time."
    : style.simple
      ? "Plain-English version:"
      : style.vague
        ? "I can help. Based on what you wrote, this is the safest next step:"
        : "Here is the Credit Vivo-safe answer:";

  return {
    id: topic.id,
    topic: topic.title,
    answer: `${opening}\n\n${topic.answer}\n\n${REQUIRED_DISCLAIMER}`,
    nextStep: topic.nextStep,
    sources: topic.sources || [],
    suggestions: getSuggestedReplies(topic.id),
    escalationTriggers: brain.escalationTriggers,
  };
}

export async function POST(request) {
  const body = await request.json().catch(() => ({}));
  const message = cleanMessage(body.message);

  if (!message) {
    return Response.json(
      {
        status: "error",
        answer: "Please type a Credit Vivo question first.",
        sources: [],
        suggestions: getSuggestedReplies("process"),
        guard: { blocked: false, needsStaffReview: false, hits: [] },
      },
      { status: 400 }
    );
  }

  const guard = checkChatCompliance(message);

  if (guard.blocked) {
    return Response.json({
      status: "blocked",
      answer:
        "I cannot help with that request. Credit Vivo can only support truthful, document-based review of possible inaccurate, incomplete, outdated, duplicate, unverifiable, or identity-related credit report information. Please avoid sending SSNs, full DOBs, ID numbers, credit report files, or payment data in chat.",
      nextStep: "Use the secure portal or contact Credit Vivo staff for human review.",
      sources: [],
      suggestions: getSuggestedReplies("process", "blocked"),
      guard,
    });
  }

  const accountLookup = findCustomerAccount(message);
  if (accountLookup) {
    return Response.json({
      status: accountLookup.matched ? "ok" : "not_found",
      answer: `${accountLookup.matched ? "I found a safe demo account match." : "I could not safely match that to a demo account."}\n\n${accountLookup.answer}\n\n${REQUIRED_DISCLAIMER}`,
      topic: accountLookup.topic,
      nextStep: accountLookup.nextStep,
      sources: accountLookup.sources,
      suggestions: getSuggestedReplies("account_status", accountLookup.matched ? "ok" : "not_found"),
      account: accountLookup.account
        ? {
            accountId: accountLookup.account.accountId,
            customerName: accountLookup.account.customerName,
            status: accountLookup.account.status,
            activeReviewItems: accountLookup.account.activeReviewItems,
            documentsNeeded: accountLookup.account.documentsNeeded,
            latestUpdate: accountLookup.account.latestUpdate,
            lastActivity: accountLookup.account.lastActivity,
          }
        : null,
      guard,
    });
  }

  const result = safeFallbackAnswer(message);
  const needsLegalReview = guard.hits.some((hit) => hit.id === "legal_advice");

  return Response.json({
    status: needsLegalReview ? "staff_review" : "ok",
    answer: needsLegalReview
      ? `This may need staff or attorney review. I can give general process information, but not legal advice.\n\n${result.answer}`
      : result.answer,
    topic: result.topic,
    nextStep: needsLegalReview ? "Route this conversation to staff review before taking action." : result.nextStep,
    sources: result.sources,
    suggestions: needsLegalReview ? getSuggestedReplies("attorney") : result.suggestions,
    escalationTriggers: needsLegalReview ? result.escalationTriggers : [],
    guard,
  });
}

export async function GET() {
  const brain = getBrainSummary();

  return Response.json({
    status: "ok",
    defaultQa: brain.defaultChatQa,
    demoCustomerAccounts: brain.demoCustomerAccounts,
    quickReplies: brain.quickReplies,
    staffRules: brain.staffRules,
    escalationTriggers: brain.escalationTriggers,
  });
}
