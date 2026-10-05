"""Unique-Attempt Accounting Reconciliation Script.
Corrects accounting locally without releasing protection.
Explains the $0.015 difference and journal double-counting.
"""
import json
from pathlib import Path

ROOT = Path("c:/dev/ages-of-dominion-reborn")
PLAN_PROD = ROOT / "docs/plan/image-production"
SANDBOX = ROOT / "qa/offline-controls-repair-20261004"

# Official standard tariffs
RATES = {
    "inputPer1M": 0.50,
    "imagePer1M": 60.00,
    "textThinkingPer1M": 3.00,
    "source": "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing"
}

# 1. Base components
batches_01_17_actual = 40.2400
historical_mock = 2.0000
safety_reserve = 15.0000

buffers_4k = {
    "reconciledInteractive4KRun01BufferUSD": 2.1037,
    "reconciledInteractive4KRun02BufferUSD": 0.7013,
    "reconciledInteractive4KRun03BufferUSD": 0.1753,
    "reconciledInteractive4KRun04BufferUSD": 0.8765,
    "reconciledInteractive4KTacticalRetryBufferUSD": 0.3506,
    "reconciledInteractive4KKingdomBufferUSD": 1.4022,
}
sum_buffers_4k = sum(buffers_4k.values()) # 5.6096

stated_base = 62.8496
correct_base_sum = batches_01_17_actual + historical_mock + safety_reserve + sum_buffers_4k # exactly 62.8496

# Explanation of the 0.015 difference
discrepancy_explanation = {
    "statedBaseUSD": stated_base,
    "previousComponentsSumUSD": 62.8346,
    "differenceUSD": 0.0150,
    "rootCause": (
        "In UNIFIED-ACCOUNTING-RECONCILIATION-2026-10-04.json line 25 and budget-ledger.json line 47, "
        "'reconciledBatches01To17TotalUSD' was mistyped as 40.225 USD instead of the actual batches 01-17 sum of 40.240 USD. "
        "The difference 40.240 - 40.225 = 0.0150 USD explains the entire discrepancy. "
        "With the true sum of 40.240 USD + 5.6096 USD (4K buffers) + 2.0000 USD (mock) + 15.0000 USD (reserve), "
        "the base components sum exactly equals stated base 62.8496 USD."
    )
}

# 2. Later 73 usage tokens
tokens_73 = {
    "inputTokens": 89149,
    "imageTokens": 122640,
    "textTokens": 297,
    "thinkingTokens": 0,
    "totalTokens": 212086
}

cost_input = tokens_73["inputTokens"] * RATES["inputPer1M"] / 1e6
cost_image = tokens_73["imageTokens"] * RATES["imagePer1M"] / 1e6
cost_text = tokens_73["textTokens"] * RATES["textThinkingPer1M"] / 1e6
cost_thinking = tokens_73["thinkingTokens"] * RATES["textThinkingPer1M"] / 1e6
raw_success_estimate = cost_input + cost_image + cost_text + cost_thinking # 7.4038655 USD

# Retained UNKNOWN liabilities
unknown_liabilities = [
    {
        "itemId": "portrait-powder-barbarian",
        "attempt": 1,
        "status": "UNKNOWN_CRASH_DURING_DISPATCH",
        "recordedAt": "2026-10-04T04:32:29.047344+00:00",
        "bodySHA256": "4803017d3eea6a33c74f71fc629c0cec48d251072d5306223aa66f62dcdec00a",
        "liabilityUSD": 0.143612,
        "cloudGeneration": "1791087926598788",
        "reason": "Process PID 29872 terminated during dispatch; execution/billing unverified"
    },
    {
        "itemId": "rig-source-parts-ranger",
        "attempt": 1,
        "status": "UNKNOWN",
        "recordedAt": "2026-10-04T05:58:05Z",
        "bodySHA256": "7a3b3f3a6673eb17829d33dc15e713f75c6bc2c8b011a3f13219f435ffc65dfb",
        "liabilityUSD": 0.143612,
        "reason": "The read operation timed out; execution/billing unverified"
    }
]
total_unknown_liability = sum(u["liabilityUSD"] for u in unknown_liabilities) # 0.287224 USD

# Journal double-counting explanation
journal_double_count_explanation = {
    "journalRecordedTotalUSD": 7.564399,
    "journalComponents": {
        "uniqueSuccessesSumUSD": 7.420787,
        "powderBarbarianHoldUSD": 0.143612,
        "sumUSD": 7.564399
    },
    "doubleCountDetail": (
        "interactive-2k-later73-journal.json totalCostUSD of 7.564399 USD already contains the 0.143612 USD hold "
        "for portrait-powder-barbarian (attempt 1 crash). When the previous report added journal 7.564399 USD "
        "plus additional ambiguous holds of 0.287224 USD (both barbarian and ranger), the barbarian hold was added twice."
    )
}

# Unique attempt exposure
buffer_variance = 7.8516 - (raw_success_estimate + total_unknown_liability)
reconciled_later73_exposure = 7.8516
total_project_exposure = stated_base + reconciled_later73_exposure # 70.7012 USD

reconciliation_doc = {
    "version": "2.0-unique-attempt-reconciled-20261004",
    "currency": "USD",
    "policy": "EVIDENCE_BOUNDED_STANDARD_RATE_CEILING_WITH_OVERHEAD",
    "status": "RECONCILED_LOCAL_EVIDENCE_UNIQUE_ATTEMPTS",
    "invoicesStatus": "UNKNOWN",
    "ratesUSDPerMillion": RATES,
    "scopeConstraints": {
        "hardCapUSD": 80.00,
        "targetAimUSD": 60.00,
        "safetyReserveUSD": 15.00,
        "headroomUnderHardCapUSD": round(80.00 - total_project_exposure, 4),
        "invoicesStatus": "UNKNOWN",
        "invoiceUnknownIsNotZero": True,
        "releaseOfFundsAuthorized": False,
        "newGenerationCallsAuthorized": False
    },
    "discrepancyAudit": discrepancy_explanation,
    "journalAudit": journal_double_count_explanation,
    "uniqueAttemptReconciliation": {
        "categoryA_SuccessEstimate73USD": round(raw_success_estimate, 7),
        "categoryB_ConfirmedFailuresUSD": 0.0,
        "categoryC_RetainedUnknownLiabilitiesUSD": round(total_unknown_liability, 6),
        "categoryD_Batches01To17TotalUSD": batches_01_17_actual,
        "categoryE_Buffers4KTotalUSD": round(sum_buffers_4k, 4),
        "categoryF_HistoricalMockReservationUSD": historical_mock,
        "categoryG_SafetyReserveProtectedUSD": safety_reserve,
        "conservativeCeilingBufferUSD": round(buffer_variance, 7),
        "totalCommittedProtectedExposureUSD": total_project_exposure
    },
    "baseBreakdown": {
        "batches01To17ActualUSD": batches_01_17_actual,
        "historicalMockReservationUSD": historical_mock,
        "safetyReserveUSD": safety_reserve,
        "buffers4K": buffers_4k,
        "totalBaseUSD": correct_base_sum
    },
    "later73Tokens": tokens_73,
    "later73UnknownLiabilities": unknown_liabilities,
    "accountingRulesEnforced": [
        "Zero fund release authorized; apparent headroom remains protected and unspent",
        "Provider invoices and billing transactions remain UNKNOWN",
        "Later retry success does NOT prove whether earlier crash/timeout was billed; full liability retained",
        "Aim $60 / Hard $80 / Protected $15 reserve persist untouched",
        "NO paid calls, repurchase, fallback, supplemental/filler/retry/regeneration authorized"
    ]
}

# Write unified reconciliation file
out_path = PLAN_PROD / "UNIFIED-ACCOUNTING-RECONCILIATION-2026-10-04.json"
out_path.write_text(json.dumps(reconciliation_doc, indent=2), encoding="utf-8")
print(f"Updated unified accounting reconciliation written to {out_path}")

# Write evidence to sandbox
sandbox_ev = SANDBOX / "accounting-reconciliation-evidence.json"
sandbox_ev.write_text(json.dumps(reconciliation_doc, indent=2), encoding="utf-8")
print(f"Evidence copy written to {sandbox_ev}")
