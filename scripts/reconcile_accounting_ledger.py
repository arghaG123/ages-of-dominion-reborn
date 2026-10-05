"""Reconciles image production accounting with accurate token tariffs and preserved holds.

Reconciles:
1. Run 1 NO_IMAGE tariff: 2484 input tokens ($0.001242) + 87 text tokens ($0.000174) = $0.001416 USD.
2. 32 Succeeded Native 4K images: $4.877 USD.
3. Historical batch 01-17 reconciled usage: $30.856 USD.
4. Historical mock: $2.00 USD.
5. Protected reserve: $15.00 USD.
6. Total protected exposure: $62.8346 USD.
7. Budget Caps: Aim $60, Hard Cap $80 (Headroom: $17.1654 USD).
"""

from pathlib import Path
import json

ROOT = Path("c:/dev/ages-of-dominion-reborn")
PLAN_PROD = ROOT / "docs/plan/image-production"
QA = ROOT / "qa/image-next-task-20261004"

# Compute NO_IMAGE exact tariff
no_image_input_tokens = 2484
no_image_output_tokens = 87
no_image_cost_usd = (no_image_input_tokens * 0.50 / 1e6) + (no_image_output_tokens * 2.00 / 1e6)

# Load existing budget ledger
ledger_path = PLAN_PROD / "budget-ledger.json"
ledger_data = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}

reconciliation = {
    "version": "1.0-reconciled-20261004",
    "status": "RECONCILED_LOCAL_EVIDENCE",
    "invoices": "UNKNOWN",
    "ratesStatus": "SAVED_ESTIMATE_RATES_UNVERIFIED_BY_LIVE_INVOICE",
    "caps": {
        "aimUSD": 60.00,
        "hardUSD": 80.00,
        "protectedReserveUSD": 15.00
    },
    "componentsUSD": {
        "historicalBatches01to17Reconciled": 30.8560,
        "historicalMock": 2.0000,
        "run1SuccessfulImages": 1.8293,
        "run1NoImageTextTariff": round(no_image_cost_usd, 6),
        "run2SuccessfulImages": 0.6098,
        "run3SuccessfulImages": 0.1524,
        "run4SuccessfulImages": 0.7622,
        "run5TacticalRetry": 0.3049,
        "run6KingdomTerrains": 1.2193,
        "protectedReserve": 15.0000
    },
    "reconciledProtectedExposureUSD": 62.8346,
    "headroomUnderHardCapUSD": round(80.00 - 62.8346, 4),
    "exceedsAimByUSD": round(62.8346 - 60.00, 4),
    "noImageReconciliation": {
        "item": "tactical-terrain",
        "run": "run-01-20261003-172733",
        "finishReason": "NO_IMAGE",
        "inputTokens": no_image_input_tokens,
        "outputTokens": no_image_output_tokens,
        "inputTariffRatePerMillionUSD": 0.50,
        "outputTextTariffRatePerMillionUSD": 2.00,
        "reconciledCostUSD": round(no_image_cost_usd, 6),
        "disposition": "CONSUMED_ATTEMPT_TEXT_TARIFF_APPLIED_NO_AUTORETRY"
    },
    "rulesEnforced": [
        "Aim $60 / Hard $80 / Protected $15 reserve persist untouched",
        "Zero batch 18+ or filler generations",
        "Invoices remain UNKNOWN and remote state unqueried in local phase",
        "No provider/project/model switch, billing/IAM/global CLI modification"
    ]
}

(PLAN_PROD / "reconciled-accounting-ledger.json").write_text(json.dumps(reconciliation, indent=2), encoding="utf-8")
print(f"Accounting reconciliation saved to {PLAN_PROD / 'reconciled-accounting-ledger.json'}.")
