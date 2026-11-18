# Unit 9 Capstone — FitFindr acceptance criteria

## Authorship and timing

These criteria and their initial targets and rationales were drafted by AI.
Kenneth chose to proceed with this AI-assisted test plan and disclose that
assistance. They are not represented as independently authored criteria.
The Unit 9 brief asks for independent authorship; this disclosure does not
establish compliance with that requirement.

This standard is committed before capstone acceptance results. The earlier
Unit 3–4 criteria are preserved in `criteria-unit3-4.md`. Mock instrumentation
checks are separate engineering checks, not these acceptance trials.

## Test conditions

Use the existing local HTTP server with `AI201_CACHE=0`, a valid Gemini key,
and no other active clients. The server process is started before measurement;
its startup is excluded. MCP process startup, model-client initialization,
provider waits, pacing within the request, and retries are included. Measure
latency at the HTTP client. The collector pauses ten seconds after each valid
request; that deliberate pause is outside the next request's latency.

Each of three trials uses the same ten valid queries plus three invalid inputs
in `capture_capstone.py`. The valid queries and their price ceilings are:

| Query | Price ceiling |
|---|---:|
| graphic tee under $30 | 30 |
| jeans under $40 | 40 |
| flannel shirt under $30 | 30 |
| track jacket under $50 | 50 |
| cardigan under $40 | 40 |
| leather belt under $20 | 20 |
| graphic hoodie under $30 | 30 |
| sneakers under $50 | 50 |
| boots under $50 | 50 |
| shoulder bag under $40 | 40 |

Invalid payloads: `{}`, `{"query":"   "}`, and `{"query":123}`.
The same requests may supply evidence for more than one criterion. Each target
must hold in all three trials to receive MET. Incomplete collections are not
complete evaluations and receive no final verdict. Repeat the entire set
unchanged after the selected improvement.

## 1. Complete request records — extension

For all 13 `/ask` requests in each trial, exactly one structured log record
must match the response's request ID. It must contain an offset-aware timestamp,
the submitted input, the JSON output or an HTTP error summary, a finite
nonnegative duration, the matching HTTP status, and the outcome. Successes and
unsuccessful requests must both be represented.

**Target:** 13/13 per trial, for all three trials.

**Reason for the proposed target:** Logging is the purpose of the operational
extension. A missing failure record removes the evidence needed to diagnose
that request. The draft previously mentioned ten requests; before any acceptance
results, the sample was specified as ten valid plus three invalid requests so
failure coverage is explicit. No missing or duplicate records are acceptable
in this bounded test. This does not claim every possible production failure
will be logged, including a process that is forcibly terminated.

## 2. HTTP response time — extension

Each of the ten valid queries must return HTTP 200, no session error, and a
nonempty string `fit_card` within 30.0 seconds measured by the collector from
sending the HTTP request through reading its complete response body. Use the
warm server and uncached conditions defined above.

**Target:** 10/10 within 30.0 seconds per trial, for all three trials.

**Reason for the proposed target:** Thirty seconds is an AI-proposed usability
budget for one complete search-and-generation request, not a measured capability
or a course requirement. A slower response exceeds that chosen waiting budget.
A much tighter budget may require changes beyond this operational extension;
a looser one would tolerate a longer wait. The target stays fixed if missed.

## 3. Recorded model usage — extension

Each of the ten valid requests must complete successfully and have exactly one
matching log with caching disabled, a positive integer model-call count, positive
integer reported prompt and output token counts, and a reported total equal to
their sum. Missing usage must not be interpreted as a free request.

**Target:** 10/10 per trial, for all three trials.

**Reason for the proposed target:** Per-request measurements are needed to
calculate the sample's average usage. Missing counts can understate the
projection. The target concerns availability and internal consistency of the
adapter's reported prompt/output counts, not independent billing accuracy or
all possible token billing categories. Failed or unmeasured requests do not
count as passes.

## 4. Invalid input rejection — failure behavior

Each of the three invalid payloads must return HTTP 400 and a JSON object with
a nonempty string `error`. Its matching log must show zero model calls.

**Target:** 3/3 per trial, for all three trials.

**Reason for the proposed target:** Missing, blank, and numeric queries can be
identified before calling Gemini. Each caller should receive a correctable
input error, and none of these cases should consume a model call. An HTTP 500
or a non-JSON error is a miss. The scope is these three cases, not every
malformed payload or nested wardrobe structure.

## 5. Preserve the original agent's basic behavior — regression

For each valid query, the HTTP response must be 200 with no session error.
`selected_item` must identify an item in `search_results`, its numeric price
must be at or below that query's price ceiling, and `outfit_suggestion` and
`fit_card` must both be nonempty strings.

**Target:** 10/10 per trial, for all three trials.

**Reason for the proposed target:** The new operational layer should preserve
the original successful flow and the selected item's budget constraint. These
queries are intentionally supported by the bundled dataset. This check does
not establish the subjective quality of outfits, semantic relevance of every
result, or the factual accuracy of every generated sentence.
