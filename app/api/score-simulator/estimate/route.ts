import { NextResponse } from "next/server";
import type { CreditIssue, ParsedTradeline } from "@/types/credit";
import type { ScannerNegativeAccount, ScoreProfile } from "@/types/score-simulator";
import {
  buildScoreSummary,
  estimateAllImpacts,
  estimateScenario,
  scannerTradelinesToSimulatorAccounts,
} from "@/lib/score-impact-engine";

export const runtime = "nodejs";

type RequestBody = {
  profile?: ScoreProfile;
  accounts?: ScannerNegativeAccount[];
  tradelines?: ParsedTradeline[];
  issues?: CreditIssue[];
  selectedAccountIds?: string[];
};

const fallbackProfile: ScoreProfile = {
  startingScore: 552,
  currentScore: 579,
  goalScore: 680,
  scoreSource: "UserEntered",
};

function normalizeProfile(profile?: ScoreProfile): ScoreProfile {
  return {
    startingScore: Number(profile?.startingScore || fallbackProfile.startingScore),
    currentScore: Number(profile?.currentScore || fallbackProfile.currentScore),
    goalScore: Number(profile?.goalScore || fallbackProfile.goalScore),
    scoreSource: profile?.scoreSource || fallbackProfile.scoreSource,
    goalReason: profile?.goalReason,
  };
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as RequestBody;
    const profile = normalizeProfile(body.profile);
    const accounts =
      body.accounts && body.accounts.length > 0
        ? body.accounts
        : scannerTradelinesToSimulatorAccounts(body.tradelines || [], body.issues || []);

    const impacts = estimateAllImpacts(accounts, profile);
    const selectedAccountIds = body.selectedAccountIds?.length
      ? body.selectedAccountIds
      : impacts.slice(0, 3).map((impact) => impact.accountId);

    return NextResponse.json({
      ok: true,
      profile,
      accounts,
      impacts,
      summary: buildScoreSummary(profile, accounts),
      scenario: estimateScenario("Selected scanner findings", selectedAccountIds, accounts, profile),
      compliance: {
        estimatedOnly: true,
        exactFicoFormulaClaimed: false,
        guaranteedScoreIncrease: false,
        guaranteedDeletion: false,
        guaranteedApproval: false,
        legalAdviceProvided: false,
        customerApprovalRequired: true,
        adminReviewRequired: true,
        complianceReviewRequired: true,
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "Score simulator estimate failed.",
      },
      { status: 400 },
    );
  }
}
