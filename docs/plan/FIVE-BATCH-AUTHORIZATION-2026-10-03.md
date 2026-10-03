# Owner authorization: next five batches — 3 October 2026

Direct owner instruction: **"We need to submit next 5 batches."** The batch executor is now authorized to prepare, submit, monitor and collect production09–13, exactly30 useful requests each,150 maximum. No separate repeated submission-approval question is needed. Previous planner draft-only/no09+ text is superseded for those five batches. Batch14+, provider fallback, quota/billing retries, extra failed-position replacements and publishing remain outside this authorization. This chat stays planner/verifier only; no jobs are submitted or delegated here.

The owner supplied the executor's report: eleven terminal jobs in the supplied project, zero active/unknown,08 already collected and terminal lock records. This is **executor-reported live evidence**, not a fresh provider query by this planner. Locally read09 draft/readiness/deferral and gap files confirm the authorization deferral; they were not changed here. The executor must record the new direct authorization and refresh lock/readiness before a paid action.

Use [the execution prompt](BATCHES-09-13-EXECUTION-PROMPT-2026-10-03.txt). It preserves the supplied project/model/account, single-active/unknown semantics and full scope. Submission sequence remains09 terminal -> submit10 before collect09, then11 before collect10,12 before collect11,13 before collect12; collect13 at terminal without buying14. Prepare ahead; no concurrent submissions.

## Budget arithmetic and a reconciliation route

Unreconciled commitments are48USD original production reservations +2USD mock reservation +15USD reserve =65USD. New6USD holds for five jobs add30USD, producing95USD, above80USD. A single09 readiness result of71USD is insufficient proof for five.09 and10 can fit the current holds at71/77USD respectively;11 would reach83USD. Target60 and hard80 remain unchanged.

Read-only local collection metadata inspection found240 usage records across01–08:

| Batch | Input tokens | Candidate output tokens | Reported total tokens |
|---|---:|---:|---:|
| 01 | 69,669 | 33,600 | 103,269 |
| 02 | 38,320 | 34,147 | 72,467 |
| 03 | 73,707 | 33,600 | 107,307 |
| 04 | 74,165 | 33,600 | 107,765 |
| 05 | 74,772 | 33,600 | 108,372 |
| 06 | 74,738 | 33,600 | 108,338 |
| 07 | 75,101 | 34,524 | 109,625 |
| 08 | 74,971 | 33,600 | 108,571 |
| Total | **555,443** | **270,271** | **825,714** |

All reported totals equal input plus candidate output; no thinking tokens are reported. This is collection metadata, not independently re-audited billing or proof of absence of other chargeable operations. The executor must bind/check these records against complete raw/provider usage before reconciliation.

Current official global pricing lists Flash Image input0.50USD/1M, text/reasoning3USD/1M and image60USD/1M at standard rates; Flex/Batch lists0.25/1.50/30 respectively. [Google pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing). Metadata ON_DEMAND versus a batch endpoint does not settle the invoice tariff; use a defensible higher-rate bound when uncertain.

Illustration: pricing **all**270,271 candidate tokens at the higher standard image rate and input at the standard input rate gives16.4939815USD for the eight known jobs' reported token usage. This deliberately overprices any text candidate tokens, but excludes missing/unreported usage, tax, storage/operations and other jobs. It is **not a verified final bill, automatic release authority or all-project total**.

For future30-request jobs, assuming input<=12,000/request and ALL billable output<=4,096/request are genuinely enforced, standard-rate token ceiling is7.5528USD/job, versus3.7764USD at batch rates. Use8USD rounded holds if standard-rate ambiguity remains rather than a6USD hold that cannot cover that bound. The executor must verify the output cap covers billed image plus reasoning/text and add any uncovered component; do not simply assume enforcement from a manifest field.

Illustrative bounded scenario: reconciled known token exposure16.494 + five8USD future holds40 + mock2 + reserve15 =73.494USD. Only6.506USD remains outside that reserve before80; other scoped jobs/unknown charges must be reconciled and uncertainties covered. This demonstrates a route worth investigating, **not a guarantee that five jobs fit**. Actual bills remain null when unavailable, and the60USD target still matters.

The executor may distinguish immutable original reservation history from current evidence-backed liability in its budget schema/validator. Original reservedUSD records remain; reconciliation records contain original/reconciled exposure, complete usage/source hashes, tariff source/date, limitations, invoice status, overhead provision and validator revision. Unknown/incomplete exposure retains the conservative hold. A terminal state alone or a favourable output-only estimate never releases money. The cap guard must use reconciled exposure only when its evidence is current and adequate, otherwise fall back to conservative reservation; include actual higher invoices when available and avoid double-counting one liability.

This necessary budget-accounting repair is authorized within the executor's batch scope. It does not authorize lowering the cap/reserve, erasing holds or weakening checks. Tests must reject missing/stale reconciliation, understated costs, unknown submissions and over-cap totals. If evidence cannot establish affordability, submit only batches that safely fit and report the real cost blocker; no renewed authorization question for09–13 is needed.

## Files and ownership

Planner writes here are this authorization report/prompt and current status pointers. Provider ledgers, locks,09 readiness/deferral, drafts/guides and executable scripts remain untouched for the batch AI. Recovery/game ownership remains unchanged. No live calls, paid submissions, collection, builds, device work, cleanup, uploads or messages to the executor occurred here. The owner manually supplies the prompt.
