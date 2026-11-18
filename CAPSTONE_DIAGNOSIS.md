# Baseline diagnosis and selected improvement

Recorded 2026-11-18 from Kenneth's pasted collector and evaluator output.
The actual evidence is in `results/capstone_before/` on his computer; those
files were not available to the assistant when this diagnosis was drafted.
Tested baseline commit: `1664aafcd6d2ca0aa90d1251b44441c83f6120ec`.

## Observed baseline

| Criterion | Trial 1 | Trial 2 | Trial 3 | Verdict |
| --- | --- | --- | --- | --- |
| Complete request records | 13/13 | 13/13 | 13/13 | MET |
| Completed responses within 30 seconds | 10/10 | 10/10 | 8/10 | MISSED |
| Successful requests with reported usage | 10/10 | 10/10 | 9/10 | MISSED |
| Invalid input rejection | 2/3 | 2/3 | 2/3 | MISSED |
| Preserve original behavior | 10/10 | 10/10 | 9/10 | MISSED |

All 39 requests had one matching log. Across the 30 valid-query requests,
29 returned HTTP 200 and one returned HTTP 500. All three numeric-query
requests returned HTTP 500 instead of the required JSON error with HTTP 400.
Missing and blank queries returned HTTP 400 in all three trials.

## Diagnosed mechanism: numeric input

Stage: HTTP input validation in `serve.ask`, before the agent or Gemini.
The original expression `(payload.get("query") or "").strip()` assumes that
a truthy query value is a string. For `{"query": 123}`, it calls `123.strip()`.
Integers have no `strip` method, so Python raises `AttributeError` and Flask
returns HTTP 500. The baseline logs report zero model calls for these cases.

An isolated Flask test using the unchanged application code reproduced
`AttributeError: 'int' object has no attribute 'strip'`. This is separate
engineering evidence, not an extra live acceptance trial.

Selected change: require a JSON object containing a nonblank string query
before string operations or agent work. Return a clear JSON error with HTTP
400 for invalid values. Do not convert arbitrary input to text. Preserve the
existing response path for valid strings and the existing logging hooks.

Expected effect: the numeric-query cases should change from HTTP 500 to
HTTP 400, retain a matching rejection log, and continue making zero model
calls. Whether criterion 4 is met must be established by the full after run.

## Other misses: diagnosis remains incomplete

- Trial 3 `valid_5`, request `e149643f116b40cfb1468410f40c407b`,
  returned HTTP 500 in 7.011 seconds after two reported model calls. It
  failed criteria 2, 3, and 5 because they require a completed successful
  response. The summary alone does not establish that usage was missing
  or that a selected item's budget was wrong. Inspect the saved response
  error and the function that produced it before identifying the cause.
- Trial 3 `valid_9`, request `4fa02f41b93844a986621e9935c1d811`,
  returned HTTP 200 in 36.431 seconds, exceeding the 30-second target.
  Two reported model calls do not explain their duration. Inspect
  `queue_ms`, `agent_ms`, and the response; the current instrumentation
  does not separately time every MCP operation or each provider call.
  Do not label this a provider, retry, or pacing problem without evidence.

The input-validation change is not expected to fix either valid-query miss.
Variation in later model responses or latency must not be attributed to it.
Keep the five criteria and test inputs unchanged for the after evaluation.

## Baseline usage, not a dollar-cost claim

The first ten eligible successful uncached requests totaled 106.133406
server-measured seconds and 8,680 reported prompt-plus-output tokens.
Mean per query: 106.133406 / 10 = 10.6133406 seconds and 8,680 / 10 =
868 reported tokens. At 100 people making one uncached query each per day:
100 * 868 = 86,800 reported tokens and 100 * 10.6133406 = 1,061.33406
aggregate request-seconds. This is neither CPU time nor a dollar bill;
failed-request usage and other billing categories are excluded.

## Evidence sequence

Commit the saved baseline evidence before importing the improvement.
Run the isolated engineering checks, restart the server so it loads the
change, and collect all 39 after requests with caching disabled. Evaluate
the same criteria and compare results without overwriting the baseline.

On Kenneth's Windows environment, `python -X utf8` allowed the collector's
Git/file text comparison to pass; `git diff HEAD -- criteria.md` was empty.
Continue using that flag for collection and evaluation. This execution
workaround does not change the criteria or the measured application.

AI assistance: the assistant drafted this diagnosis from the reported
baseline and code inspection, reproduced the input-validation failure,
and prepared the proposed fix and isolated regression check. Live after
results are pending.
