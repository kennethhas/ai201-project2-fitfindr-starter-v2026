# FitFindr capstone: understand and finish

## What the project demonstrates

The original application searches a mock clothing dataset through MCP, then
calls Gemini for an outfit suggestion and a fit card. Shape A adds an
operational layer: a reproducible run path and records of real behavior.

The later measured improvement is a separate step. First commit your criteria,
collect baseline evidence, diagnose a result, change one thing, and rerun the
same test set. Logging alone is not a completed before-and-after improvement.

## What the new code does

| File | What you should be able to explain |
|---|---|
| `serve.py` | Receives HTTP requests and calls the existing agent. Flask hooks start a timer and write the resulting record. The lock permits one agent run at a time. |
| `observability.py` | Writes JSON Lines through Python logging, rotates the file, and redacts credential fields and the configured key. It does not detect all personal information. |
| `summarize_usage.py` | Reads ten eligible uncached successful requests and calculates observed average usage and a one-query-per-person daily projection. |
| `test_observability.py` | Uses a stubbed agent to check the logging plumbing. These checks are not evidence about live Gemini quality or latency. |
| `capture_capstone.py` | Sends actual HTTP requests, saves each response immediately, and copies the matching structured log using the request ID. It assigns no acceptance verdicts. |

## Evidence collection order

1. Review the extension and the proposed test inputs in `capture_capstone.py`.
2. Write your five capstone criteria with your own targets and reasons. At
   least three concern the extension and one concerns failure. The previously
   supplied AI draft is not evidence of independent authorship.
3. Preserve the old Unit 3–4 criteria in a separately named Markdown file, then
   put your capstone criteria in `criteria.md`. Commit before acceptance runs.
4. Import and review the collector, then commit any modifications to it.
5. In terminal A, activate `.venv`, set `$env:AI201_CACHE='0'`, and run
   `python serve.py`. Keep this terminal running.
6. In terminal B, activate `.venv`, set `$env:AI201_CACHE='0'`, and run
   `python capture_capstone.py --label before`.
7. Read the real responses and logs. Produce one row per criterion with three
   trial columns, a target, and MET or MISSED. A target must hold in all three
   trials to be MET. Save the baseline before editing application code.
8. Diagnose every miss by file/function and mechanism. Select one improvement
   based on the diagnosis. Commit it, restart the server, and run the collector
   with `--label after`. Reevaluate all five criteria.
9. Finish the nine README sections. Paste at least ten actual structured records
   plus failure evidence, both result tables, cost arithmetic, limitations, and
   two specific AI-assistance moments. Verify startup from a fresh checkout.
10. Review the final diff and Git history, merge the completed work into the
    submitted repository's default branch, push, verify GitHub, and submit the
    same repository URL. Do not publish `.env` or other secrets.

The collector's proposed inputs are ten matching queries plus three invalid
queries per trial. Across three trials that is 39 requests and normally up to
60 initial model calls per phase, plus any provider retries. It reuses requests
as evidence for multiple criteria; it does not pretend they are independent
datasets. The before and after phases use the same inputs and criteria digest.
Review whether this design actually measures your final criteria before use.

The collector must run on the machine hosting the server because it reads its
local log. In a VS Code remote session, both terminals can run on that machine.
It preserves partial evidence if interrupted and refuses to overwrite it. Ask
for help with a partial run rather than deleting inconvenient results.

## What the numbers mean

- `duration_ms`: server request time, excluding network transit, application
  startup, and the final log write.
- `client_elapsed_seconds`: HTTP round-trip time seen by the collector.
- `queue_ms`: waiting to acquire the agent lock in this process.
- `agent_ms`: time inside the agent, including MCP startup, provider latency,
  pacing, and retries. This is not CPU time.
- `model_calls`: adapter counter difference while this request holds the lock.
- `reported_tokens`: adapter-reported prompt and output tokens. Missing usage
  metadata can make this incomplete; it is not a verified billing statement.
- `request_id`: identifier connecting one HTTP response to its record.

Cost arithmetic, after measurement: sum the reported tokens for ten selected
runs and divide by ten. For 100 people making one identical-pattern query per
day, multiply that measured average by 100. State the cache setting, sample,
failures excluded, and missing billing categories. Do not invent a dollar cost.

## Explain it later

Use this sequence, filling in numbers only from your own evidence:

- What the original FitFindr did.
- What you added and why it was a bounded extension.
- What standards you chose and why.
- What the actual tests revealed, including misses.
- Which function caused a problem and how.
- What one change you made and what happened in the retest.
- What remains unverified or broken and the next thing you would investigate.

A successful environment check proves imports, data, and a small Gemini call.
It does not prove the complete agent or new HTTP path. A passed health check
proves only the server is awake. A passed mock test proves only the behavior
covered by the stubbed test. Keep these claims separate from acceptance results.

Render is optional. Local-with-logs has the same credit under the supplied Unit
9 brief. Spend no more than 45 minutes troubleshooting hosting before using
the documented local route.
