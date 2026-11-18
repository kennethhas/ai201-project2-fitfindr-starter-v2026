# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

Milestone 1 notes:

- Confirmed the starter runs.
- Reviewed listing fields including title, size, and price.
- Reviewed six full listing records.

## What This Does

FitFindr is a three-tool agent that helps a user find a secondhand clothing item
based on a description, size, and maximum price. It searches the available
listings, selects the best matching item, and uses the user's wardrobe to
suggest an outfit. It then creates a short fit card that includes the selected
item, price, platform, and overall styling idea.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the listings data for items that match the user's description, and optionally filters by size and maximum price.
- **Inputs:** `description` (`str`), `size` (`str | None`), `max_price` (`float | None`)
- **Returns:** A list of matching listing dictionaries, ordered with the best match first. Each dictionary can include fields such as `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

- **What it does:** Takes the selected listing and the user's wardrobe and generates one or two outfit suggestions.
- **Inputs:** `new_item` (`dict`), `wardrobe` (`dict`)
- **Returns:** A non-empty string containing outfit suggestions based on the selected item and the user's wardrobe.
- **When it has nothing:** If the wardrobe is empty, it returns general styling advice instead of failing or returning an empty string.

### `create_fit_card`

- **What it does:** Creates a short post-style caption using the selected item and the outfit suggestion.
- **Inputs:** `outfit` (`str`), `new_item` (`dict`)
- **Returns:** A two-to-four sentence caption that mentions the item, its price, its platform, and the overall vibe.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns a descriptive message instead of raising an error.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a helpful
message in the session and stop. Otherwise, take the first result, save it as
the selected item, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions extract the size and maximum
price from the user's query. The remaining text is used as the item description.

**What moves through the session:** The parsed query is stored first, followed
by the search results. The first result is saved as `selected_item`.
`suggest_outfit` reads that selected item from the session and its result is
stored as `outfit_suggestion`. `create_fit_card` then reads the outfit
suggestion and selected item, and the final result is stored as `fit_card`.

---

## Sample Run

**One full query**

```text
$ python agent.py

=== A query the data can match ===
parsed: {'description': 'looking for a vintage graphic tee', 'size': None, 'max_price': 30.0}
found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
state: selected lst_002 → suggest_outfit received lst_002
outfit: Pair the Y2K Baby Tee — Butterfly Print with the baggy straight-leg
jeans, dark wash to lean into authentic 2000s proportions. Layer the slightly
cropped vintage black denim jacket over top for structure, and finish the look
with chunky white sneakers and the black crossbody bag for an effortless
everyday streetwear vibe.

Alternatively, for a softer look that blends the tee's butterfly print and
pastel colors with your earth tones, tuck the baby tee into the wide-leg khaki
trousers. Accentuate the waist with the brown leather belt, and wear the chunky
white sneakers to keep the outfit casual, balanced, and comfortable.

fit card: Channel major 2000s energy with this super cute Y2K Baby Tee
featuring a dreamy butterfly print in pink and purple. It's giving the ultimate
effortless streetwear vibe, and it's up for grabs on depop for just $18.00!

```

**The three tools, tested one at a time**

```text
$ python -c "from tools import search_listings; r=search_listings('graphic tee', max_price=30); print([(x['id'], x['title'], x['price']) for x in r])"

[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0),
 ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0),
 ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0),
 ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0),
 ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0),
 ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0)]

```

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Outfit One: Pair the vintage Levi's 501 jeans with the white ribbed tank top, layered under the vintage black denim jacket. Complete the look with the chunky white sneakers and the black crossbody bag for a classic, effortless streetwear vibe.

Outfit Two: Style the vintage Levi's 501 jeans with the oversized grey crewneck sweatshirt for a relaxed, cozy silhouette. Add the brown leather belt to define the waist and finish the outfit with the black combat boots and black crossbody bag for an easy, everyday look.
```

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Scored these vintage Levi's 501 jeans in a timeless medium wash and they are the ultimate closet staple. Just style them with crisp white sneakers for an effortless streetwear look that never misses. Grab this classic denim piece now on depop for just $38.00 before someone else does!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ I asked AI to help me review my `search_listings` logic.
- _What came back:_ It pointed out that my keyword check used substring
  matching (`word in searchable_text`), so "hat" matched "that" in the Polo
  listing and "red" matched "structured" in the Denim Jacket. It also noted I
  kept filler words like "a" and "for", which appear in almost every listing.
- _What I changed:_ I kept my structure but switched to whole-word matching
  with a stopword list, and changed `if size is not None:` to `if size:` so an
  empty size string doesn't filter out every listing. My size matching was
  already whole-token, so `L` doesn't match `XL`; I kept that as-is.

**Moment 2**

- *What I asked for:*I asked AI to help me review my `agent.py`
- _What came back:_ It said my structure was excellent — I used a `while True`
  loop with a `step` variable, while its version ran the steps in a straight
  line. But it found a bug in my size regex: the letters-only pattern was
  checked first, so "size US 8.5" was cut down to just "US", which would match
  every US shoe size. It also pointed out that I never recorded what
  `suggest_outfit` actually received, so I had no way to check my state
  criterion (criterion 3).
- _What I changed:_ I kept my loop structure. I moved the `US` pattern first
and defined the size regex once as `SIZE_PATTERN` so the find and remove
steps can't drift apart. I added `session["outfit_input"]` and a `state:`
line in `_show` that prints both IDs. I also made the empty-search message
use the user's actual price and size.
<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion                                            | Target              | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict     |
| ---------------------------------------------------- | ------------------- | ----- | ----- | ----- | ----- | ----- | ----------- |
| 1. Matching query completes all three tools          | 4 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)   |
| 2. Empty query stops before suggest_outfit           | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)   |
| 3. Selected item ID matches outfit input ID          | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)\* |
| 4. Fit card includes item title, price, and platform | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)   |
| 5. Search respects maximum price                     | 5 different queries | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)   |

\*Criterion 3: supported by the same-dictionary handoff in agent.py; direct ID assertions would strengthen per-run evidence.

Criterion 5: each column represents one distinct price-limit query; the full evaluation repeated each scenario five times.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
Criterion 1 — Matching query
Query: vintage graphic tee under $30
[2] search_listings (via MCP)
    → 10 match(es)
[3] select_item
    out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
[5] create_fit_card
    out: Channel major 2000s energy with this dreamy butterfly print baby tee...

```

```
Criterion 2 — Impossible query
Query: designer ballgown size XXS under $5
[2] search_listings (via MCP)
out: [] (empty)
→ 0 match(es)
[3] branch
→ Search returned no results. Stopping before suggest_outfit.
```

````
### Criterion 3 — Selected item stays consistent

Produced by: `run_eval.py::main` and `agent.py::run_agent`

Actual trace:

```text
[3] select_item
    out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
    in: Y2K Baby Tee — Butterfly Print ($18.0, depop)
````

Relevant code from `agent.py::run_agent`:

```python
item = session["selected_item"]
session["outfit_input"] = item

session["outfit_suggestion"] = suggest_outfit(
    item,
    session["wardrobe"],
)
```

The same item dictionary is used for both values, so the item ID is preserved. The trace displays the item title rather than its ID.

```

```

    Criterion 4 — Fit card

Selected item:
Y2K Baby Tee — Butterfly Print ($18.0, depop)

Actual fit card:
Obsessed with this white, pink, and purple Y2K Butterfly
Print baby tee for giving off the ultimate effortless,
everyday throwback vibe! It’s up on my depop right now
for $18.00 and works with everything from baggy jeans
to khaki trousers. Grab it before it's gone!

```

```

Criterion 5 — Price filtering verification
vintage jeans: PASS | 10 results | budget $30
graphic tee: PASS | 3 results | budget $20
denim jacket: PASS | 5 results | budget $40
leather bomber: PASS | 3 results | budget $60
suede boots: PASS | 1 results | budget $50

Boundary verification:
Under $40: $42 denim jacket excluded
Under $50: $42 denim jacket included

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

```

**_Verdicts and Diagnoses_**

| #   | Criterion                                         | Target              | Verdict   | How I decided                                                                                                                                                                                                                             |
| --- | ------------------------------------------------- | ------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Matching query completes all three tools          | 4/5                 | MET (5/5) | All five runs completed search_listings, suggest_outfit, and create_fit_card.                                                                                                                                                             |
| 2   | Empty query stops before suggest_outfit           | 5/5                 | MET (5/5) | All five runs returned zero results and stopped before suggest_outfit, with a helpful message.                                                                                                                                            |
| 3   | Selected item ID remains consistent               | 5/5                 | MET (5/5) | All five traces showed the same item being selected and passed to suggest_outfit. The code passes the same dictionary, so the ID is preserved. The logs show item names rather than IDs.uses the same item dictionary, preserving its ID. |
| 4   | Fit card mentions item title, price, and platform | 5/5                 | MET (5/5) | All five fit cards identified the Y2K butterfly-print baby tee, included $18.00, and mentioned depop. I counted recognizable product names as mentions.                                                                                   |
| 5   | Search respects maximum price                     | 5 different queries | MET (5/5) | All five searches returned items within the price limit. A $42 jacket was excluded at $40 and included at $50.                                                                                                                            |

### Diagnoses

All five criteria met their original targets. However, testing showed a problem that my criteria did not measure.

**Problem:** When I searched for "leather bomber under $60", FitFindr selected Platform Mary Janes shoes costing $55 instead of returning a leather bomber jacket.

**Where it happened:** The search_listings tool.

**Why it happened:** The keyword search matches individual words and can return unrelated clothing that shares part of the description. It does not consistently require the requested product type to match.

**Pattern:** My agent follows the three-tool workflow, keeps the selected item consistent, and respects price limits, but sometimes returns the wrong type of clothing.

**Were my targets too easy?** Yes. Criterion 1 had a target of 4 out of 5 successful runs. Since the three-tool workflow should complete consistently when a matching item is available, I think this target was too low. My original criteria also did not directly measure whether search results matched the requested clothing type.

**What I would tighten:** would raise Criterion 1's target from 4/5 to 5/5 successful runs. I would also add a future search-relevance criterion requiring the selected item to match the requested clothing type in at least 4 of 5 different searches.

I would keep my original criteria and targets unchanged for this evaluation.

## I kept my five original criteria unchanged because they are measurable and were written before testing.

```

```

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
in: vintage graphic tee under $30
out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
in: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ 10 match(es)
[3] select_item
out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
in: Y2K Baby Tee — Butterfly Print ($18.0, depop)
out: Pair the Y2K Baby Tee — Butterfly Print with the baggy straight-leg jeans, dark wash to lean into authentic 20…
[5] create_fit_card
in: Y2K Baby Tee — Butterfly Print ($18.0, depop)
out: Channel major 2000s energy with this super cute Y2K Baby Tee featuring a dreamy butterfly print in pink and pu…

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit: Pair the Y2K Baby Tee — Butterfly Print with the baggy straight-leg jeans, dark wash to lean into authentic 2000s proportions. Layer the slightly cropped vintage black denim jacket over top for structure, and finish the look with chunky white sneakers and the black crossbody bag for an effortless everyday streetwear vibe.

Alternatively, for a softer look that blends the tee's butterfly print and pastel colors with your earth tones, tuck the baby tee into the wide-leg khaki trousers. Accentuate the waist with the brown leather belt, and wear the chunky white sneakers to keep the outfit casual, balanced, and comfortable.

Fit card: Channel major 2000s energy with this super cute Y2K Baby Tee featuring a dreamy butterfly print in pink and purple. It's giving the ultimate effortless streetwear vibe, and it's up for grabs on depop for just $18.00!

**Empty search**

python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
in: designer ballgown size XXS under $5
out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
in: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
out: [] (empty)
→ 0 match(es)
[3] branch
→ Search returned no results. Stopping before suggest_outfit.

I couldn't find a matching item. Try: raise your $5 price limit; try a size other than XXS; use broader words like 'tee' or 'jacket'.

0 model calls this session

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I moved the search_listings tool from a direct Python function call to an MCP call using mcp_client.call_tool(). I registered the tool in mcp_server.py with a description and typed parameters.

After making the change, I tested the agent using a vintage graphic tee search. The search returned 10 matching items, and the agent successfully generated an outfit suggestion and fit card. The agent continued working as expected after the MCP change.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

I improved the search_listings function in tools.py. Before the change, an item only needed to match one keyword from the user's description to appear in the results.

I changed the matching condition from if score == 0 to if score < len(query_words). Now a listing must match every meaningful keyword in the search description.

I kept the existing size and maximum-price filters unchanged.

Which failure it was meant to fix:

During my baseline evaluation, searching for "leather bomber under $60" returned Platform Mary Janes shoes, a leather belt, and a shoulder bag. The search tool accepted partially matching items that were not the requested clothing type.

My goal was to reduce irrelevant search results without breaking the agent's existing workflow.

**Which failure it was meant to fix:**

### Run Log — After

ran python run_eval.py --label after using the same scenarios as the before evaluation, with five tries per scenario and caching disabled.

Evidence file: results/run_2026-10-12_0024_after.md

Produced by: run_eval.py::main, agent.py::run_agent, and tools.py::search_listings through MCP.

| Criterion                                            | Target              | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict   |
| ---------------------------------------------------- | ------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| 1. Matching query completes all three tools          | 4 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 2. Empty query stops before suggest_outfit           | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 3. Selected item ID remains consistent               | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 4. Fit card mentions item title, price, and platform | 5 of 5              | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 5. Search respects maximum price                     | 5 different queries | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |

Criterion 3 was evaluated using the same dictionary handoff as before. The trace displays item names rather than IDs.

For Criterion 5, all five different queries remained within budget. The denim jacket query returned no results under $40, while the empty-wardrobe diagnostic found the matching $42 denim jacket under $50.

**_Before and After Comparison_**

| Test query                    | Before              | After     |
| ----------------------------- | ------------------- | --------- |
| Leather bomber under $60      | 3 unrelated results | 0 results |
| Vintage graphic tee under $30 | 10 results          | 3 results |
| Denim jacket under $40        | 5 results           | 0 results |
| Vintage jeans under $30       | 10 results          | 1 result  |
| Suede boots under $50         | 1 result            | 1 result  |

**_Real Output — After_**

From agent.py::run_agent, recorded by run_eval.py::main:

Query: leather bomber under $60

[1] parse_query
in: leather bomber under $60
out: {'description': 'leather bomber', 'size': None, 'max_price': 60.0}

[2] search_listings (via MCP)
in: {'description': 'leather bomber', 'size': None, 'max_price': 60.0}
out: [] (empty)
→ 0 match(es)

[3] branch
→ Search returned no results. Stopping before suggest_outfit.

Actual response:

I couldn't find a matching item. Try: raise your $60 price limit; use broader words like 'tee' or 'jacket'.

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

---

## What's Still Broken

All five of my original acceptance criteria were MET after testing, so there are no missed criteria that still need fixing.

However, FitFindr still has some limitations.

**1. Search is too strict.**

I changed `search_listings` to require every meaningful keyword to match. This fixed the leather bomber problem, but it could reject good items that use different words or descriptions.

**2. Search does not fully understand clothing categories.**

FitFindr uses keyword matching rather than understanding what type of clothing the user actually wants. It may still struggle with synonyms or descriptions that mean the same thing.

**3. My testing could be more detailed.**

My five criteria passed, but they did not directly measure search relevance. Also, my evaluation traces showed selected item names instead of explicitly recording their IDs.

**Why I stopped here:**

I focused on fixing one specific problem for Milestone 5. After the improvement, the leather bomber search returned no unrelated items, and the original five criteria still passed. I stopped because the required improvement and before-and-after evaluation were complete.

**What I would improve next:**

I would add better clothing-category matching, test more search queries, and record item IDs directly in the trace to make future evaluations more accurate.

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

```

```

## Capstone

**What This Extends**

This builds on my Unit 3–4 FitFindr agent. The agent itself (`agent.py::run_agent`,
`search_listings` over MCP, `suggest_outfit`, `create_fit_card`) did not change.
What I added is a layer around the `/ask` route in `serve.py` so I can see what
it is doing:

- a structured log file (`logs/requests.jsonl`) with one JSON line per request
  and a request ID that also comes back in the `X-Request-ID` header
- timing for each request (`duration_ms`, `queue_ms`, `agent_ms`), a model
  call count, and the token counts the adapter reports
- `summarize_usage.py` to get the ten-run average and the 100-people-a-day number
- `capture_capstone.py` and `evaluate_capstone.py`, which run my test batch
  against the live server and score it against `criteria.md`
- one fix: the `/ask` route now rejects a non-text query with HTTP 400 instead
  of crashing

**The Shape**

Shape A, deploy and instrument. I used the local-with-logs route.

Out of scope: hosting on Render (RUNNING.md describes it but I did not do it),
any new user interface, any change to how search or outfits work, retries when
Gemini is down, and running more than one worker. The only change to how the
app behaves is the validation fix I picked after the baseline.

**Running It**

Local with logs. RUNNING.md has the full steps: Python 3.11–3.13 (I used 3.12),
`pip install -r requirements.txt`, a Gemini key in `.env`, no local model files
because the app calls Gemini remotely. Then:

```powershell
$env:AI201_CACHE='0'; python serve.py
```

and `POST /ask` with `{"query": "..."}` to `http://127.0.0.1:5000`.

<!-- TODO: after you do the clean clone, replace this comment with something like:
I verified this from a fresh `git clone` of the `capstone/observability` branch
on 2026-11-18. Setup, `python test.py`, starting the server, and one /ask
request all worked following RUNNING.md as written. -->

The run records in `results/capstone_before/` and `results/capstone_after/`
are the evidence it ran outside the editor. They are 78 real HTTP requests
against the server started with the command above, written by
`capture_capstone.py::main`.

**Instrumentation**

Every request appends one JSON line to `logs/requests.jsonl`. The logger in
`serve.py` writes it after the handler returns. Fields: `timestamp`,
`request_id`, `method`, `path`, `input`, `output` (the session on success, or
the error), `status_code`, `outcome` (`success`, `error`, or `rejected`),
`duration_ms`, `queue_ms` (time waiting on the one-at-a-time lock), `agent_ms`,
`model_calls`, `reported_tokens`, `cache_enabled`, `model`. The file rotates
at about 5 MB and keeps two backups. Credential-looking fields get redacted.

Ten real log entries, pasted as text. I did not edit them.

Rejected requests after the fix (HTTP 400, zero model calls):

```json
{"timestamp": "2026-11-18T18:28:30.917571+00:00", "request_id": "6865460e34bd4c0eaf55b01b3e2a8db7", "method": "POST", "path": "/ask", "input": {"query": 123}, "output": {"error": "The 'query' field must be non-empty text, e.g. {\"query\": \"vintage graphic tee under $30\"}"}, "status_code": 400, "outcome": "rejected", "duration_ms": 0.153, "queue_ms": null, "agent_ms": null, "model_calls": 0, "reported_tokens": {"prompt": 0, "output": 0, "total": 0}, "cache_enabled": false, "model": "gemini-3.5-flash-lite"}
{"timestamp": "2026-11-18T18:32:11.879160+00:00", "request_id": "2e3668c4294d4b07864a53a57b1585e2", "method": "POST", "path": "/ask", "input": {"query": 123}, "output": {"error": "The 'query' field must be non-empty text, e.g. {\"query\": \"vintage graphic tee under $30\"}"}, "status_code": 400, "outcome": "rejected", "duration_ms": 0.178, "queue_ms": null, "agent_ms": null, "model_calls": 0, "reported_tokens": {"prompt": 0, "output": 0, "total": 0}, "cache_enabled": false, "model": "gemini-3.5-flash-lite"}
{"timestamp": "2026-11-18T18:35:34.823043+00:00", "request_id": "f1639ef8d74945f481f0f51241a0a415", "method": "POST", "path": "/ask", "input": {"query": 123}, "output": {"error": "The 'query' field must be non-empty text, e.g. {\"query\": \"vintage graphic tee under $30\"}"}, "status_code": 400, "outcome": "rejected", "duration_ms": 0.168, "queue_ms": null, "agent_ms": null, "model_calls": 0, "reported_tokens": {"prompt": 0, "output": 0, "total": 0}, "cache_enabled": false, "model": "gemini-3.5-flash-lite"}
```

The two failures from the baseline that I diagnose below:

```json
{"timestamp": "2026-11-18T18:12:05.998161+00:00", "request_id": "42ca22a5f5bd45ee9fdf9e8746bfa113", "method": "POST", "path": "/ask", "input": {"query": 123}, "output": {"http_status": 500, "message": "500 INTERNAL SERVER ERROR"}, "status_code": 500, "outcome": "error", "duration_ms": 2.344, "queue_ms": null, "agent_ms": null, "model_calls": 0, "reported_tokens": {"prompt": 0, "output": 0, "total": 0}, "cache_enabled": false, "model": "gemini-3.5-flash-lite"}
{"timestamp": "2026-11-18T18:17:36.961834+00:00", "request_id": "e149643f116b40cfb1468410f40c407b", "method": "POST", "path": "/ask", "input": {"query": "cardigan under $40"}, "output": {"error": "ModelUnavailable: Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}"}, "status_code": 500, "outcome": "error", "duration_ms": 6983.84, "queue_ms": 0.001, "agent_ms": 6983.186, "model_calls": 2, "reported_tokens": {"prompt": 412, "output": 104, "total": 516}, "cache_enabled": false, "model": "gemini-3.5-flash-lite"}
```

The slow one from the baseline (HTTP 200 but 36.4 seconds):

```json
{
  "timestamp": "2026-11-18T18:18:48.093959+00:00",
  "request_id": "4fa02f41b93844a986621e9935c1d811",
  "method": "POST",
  "path": "/ask",
  "input": { "query": "boots under $50" },
  "output": {
    "error": null,
    "fit_card": "Found these gorgeous tan suede Chelsea boots and I am obsessed with the vintage earth-tone vibe! They're up on my poshmark for $44.00, perfect for styling with everything from baggy dark denim to relaxed khaki trousers. Grab them before I change my mind and keep them for myself!",
    "outfit_input": {
      "brand": null,
      "category": "shoes",
      "colors": ["tan", "camel"],
      "condition": "fair",
      "description": "Tan suede Chelsea boots with elastic side panels. Stacked heel. Some scuffing on the toe — can be brushed out with suede cleaner.",
      "id": "lst_028",
      "platform": "poshmark",
      "price": 44.0,
      "size": "US 8.5",
      "style_tags": ["vintage", "classic", "western", "earth tones"],
      "title": "Suede Chelsea Boots — Tan"
    },
    "outfit_suggestion": "Outfit 1: Pair the tan suede Chelsea boots with the baggy straight-leg jeans in dark wash and the white ribbed tank top. Add the vintage black denim jacket for an effortless, classic look that bridges vintage and streetwear aesthetics. Complete the outfit with the black crossbody bag.\n\nOutfit 2: Combine the tan suede Chelsea boots with the wide-leg khaki trousers and the white ribbed tank top for a cohesive earth-tone palette. Cinch the waist with the brown leather belt to tie the browns and tans together, and layer the oversized grey crewneck sweatshirt on top for a relaxed, minimal silhouette.",
    "parsed": { "description": "boots", "max_price": 50.0, "size": null },
    "query": "boots under $50",
    "search_results": [
      {
        "brand": null,
        "category": "shoes",
        "colors": ["tan", "camel"],
        "condition": "fair",
        "description": "Tan suede Chelsea boots with elastic side panels. Stacked heel. Some scuffing on the toe — can be brushed out with suede cleaner.",
        "id": "lst_028",
        "platform": "poshmark",
        "price": 44.0,
        "size": "US 8.5",
        "style_tags": ["vintage", "classic", "western", "earth tones"],
        "title": "Suede Chelsea Boots — Tan"
      }
    ],
    "selected_item": {
      "brand": null,
      "category": "shoes",
      "colors": ["tan", "camel"],
      "condition": "fair",
      "description": "Tan suede Chelsea boots with elastic side panels. Stacked heel. Some scuffing on the toe — can be brushed out with suede cleaner.",
      "id": "lst_028",
      "platform": "poshmark",
      "price": 44.0,
      "size": "US 8.5",
      "style_tags": ["vintage", "classic", "western", "earth tones"],
      "title": "Suede Chelsea Boots — Tan"
    },
    "wardrobe": {
      "items": [
        {
          "category": "bottoms",
          "colors": ["dark blue", "indigo"],
          "id": "w_001",
          "name": "Baggy straight-leg jeans, dark wash",
          "notes": "High-waisted, sits above the hip",
          "style_tags": ["denim", "streetwear", "baggy"]
        },
        {
          "category": "bottoms",
          "colors": ["khaki", "tan"],
          "id": "w_002",
          "name": "Wide-leg khaki trousers",
          "notes": null,
          "style_tags": ["earth tones", "minimal", "wide-leg"]
        },
        {
          "category": "tops",
          "colors": ["white"],
          "id": "w_003",
          "name": "White ribbed tank top",
          "notes": "Goes with everything",
          "style_tags": ["basics", "minimal", "fitted"]
        },
        {
          "category": "tops",
          "colors": ["grey", "charcoal"],
          "id": "w_004",
          "name": "Oversized grey crewneck sweatshirt",
          "notes": "Really oversized — drops below the hip",
          "style_tags": ["oversized", "basics", "cozy"]
        },
        {
          "category": "tops",
          "colors": ["black"],
          "id": "w_005",
          "name": "Black cropped zip hoodie",
          "notes": null,
          "style_tags": ["athletic", "streetwear", "cropped"]
        },
        {
          "category": "outerwear",
          "colors": ["black"],
          "id": "w_006",
          "name": "Vintage black denim jacket",
          "notes": "Slightly cropped",
          "style_tags": ["denim", "vintage", "classic"]
        },
        {
          "category": "shoes",
          "colors": ["white"],
          "id": "w_007",
          "name": "Chunky white sneakers",
          "notes": null,
          "style_tags": ["sneakers", "chunky", "streetwear"]
        },
        {
          "category": "shoes",
          "colors": ["black"],
          "id": "w_008",
          "name": "Black combat boots",
          "notes": "Lace-up, mid-ankle height",
          "style_tags": ["boots", "grunge", "classic"]
        },
        {
          "category": "accessories",
          "colors": ["brown"],
          "id": "w_009",
          "name": "Brown leather belt",
          "notes": null,
          "style_tags": ["classic", "earth tones", "accessories"]
        },
        {
          "category": "accessories",
          "colors": ["black"],
          "id": "w_010",
          "name": "Black crossbody bag",
          "notes": null,
          "style_tags": ["minimal", "accessories", "everyday"]
        }
      ]
    }
  },
  "status_code": 200,
  "outcome": "success",
  "duration_ms": 36428.797,
  "queue_ms": 0.001,
  "agent_ms": 36428.107,
  "model_calls": 2,
  "reported_tokens": { "prompt": 703, "output": 183, "total": 886 },
  "cache_enabled": false,
  "model": "gemini-3.5-flash-lite"
}
```

Four normal successful requests from the after run:

```json
<!-- TODO: paste four lines with "status_code": 200 here.
     Run:  Get-Content logs\requests.jsonl -Tail 13   and copy any four 200s. -->
```

That is ten entries, with three rejections and two errors, so the failure
path is shown with real records.

**What It Costs**

`evaluate_capstone.py` measured this over the first ten successful uncached
`/ask` runs of the after phase (request IDs are in
`results/capstone_after/report.md`). `python summarize_usage.py logs/requests.jsonl`
gives the same thing. Tokens are what the adapter reports for prompt plus
output on `gemini-3.5-flash-lite`. Time is wall clock at the server handler, so
it includes MCP startup and waiting on Gemini.

|                          | Ten-run total | Per run |
| ------------------------ | ------------: | ------: |
| Tokens (prompt + output) |         8,718 |   871.8 |
| Seconds                  |        113.51 |   11.35 |

For 100 people making one query each per day:

```text
871.8 tokens × 100 = 87,180 tokens/day
11.35 s     × 100 = 1,135 s/day, about 19 minutes of request time
```

The baseline phase came out at 868.0 tokens and 10.61 s per run (86,800
tokens/day), so the fix did not change usage. This is a token count, not
dollars. To turn it into dollars I would need Gemini's current price for this
model, which I did not pin down. Failed runs are left out of the average, so
the real number is a bit higher. One of 30 valid requests failed in the
baseline and zero of 30 after.

**Run Log and Verdicts**

My criteria are in [`criteria.md`](criteria.md), committed as `10c8ba1` before
I collected any results. Each trial is the same batch: ten valid queries plus
three invalid payloads. A criterion is MET only if it hits the target in all
three trials. `capture_capstone.py::main` sent the requests and saved each
response with its matching log line to `results/capstone_<phase>/responses.jsonl`,
and `evaluate_capstone.py::main` scored them into these tables.

Before (commit `1664aaf`, 39 requests):

| Criterion                     | Target per trial  | Run 1 | Run 2 | Run 3 | Verdict |
| ----------------------------- | ----------------- | ----- | ----- | ----- | ------- |
| 1. Complete request records   | 13/13             | 13/13 | 13/13 | 13/13 | MET     |
| 2. HTTP response time         | 10/10 within 30 s | 10/10 | 10/10 | 8/10  | MISSED  |
| 3. Recorded model usage       | 10/10             | 10/10 | 10/10 | 9/10  | MISSED  |
| 4. Invalid input rejection    | 3/3               | 2/3   | 2/3   | 2/3   | MISSED  |
| 5. Preserve original behavior | 10/10             | 10/10 | 10/10 | 9/10  | MISSED  |

After (commit `fa4ce3a`, 39 requests):

| Criterion                     | Target per trial  | Run 1 | Run 2 | Run 3 | Verdict |
| ----------------------------- | ----------------- | ----- | ----- | ----- | ------- |
| 1. Complete request records   | 13/13             | 13/13 | 13/13 | 13/13 | MET     |
| 2. HTTP response time         | 10/10 within 30 s | 10/10 | 10/10 | 10/10 | MET     |
| 3. Recorded model usage       | 10/10             | 10/10 | 10/10 | 10/10 | MET     |
| 4. Invalid input rejection    | 3/3               | 3/3   | 3/3   | 3/3   | MET     |
| 5. Preserve original behavior | 10/10             | 10/10 | 10/10 | 10/10 | MET     |

How I decided each baseline verdict:

- **C1 MET.** All 39 responses had an `X-Request-ID` that matched exactly one
  log line with every field, including the three 500s. In `responses.jsonl`
  every entry has `matching_logs` of length 1.
- **C2 MISSED.** Trial 3 was 8/10. `valid_5` came back 500, and `valid_9` came
  back 200 but took 36.43 s. The other 28 valid requests were all 200 under
  30 s. The slowest one that passed was 22.59 s.
- **C3 MISSED.** Trial 3 was 9/10. `valid_5` failed, so its usage (2 calls,
  516 tokens) was logged but does not count as a pass.
- **C4 MISSED.** 2/3 in every trial. `{}` and `{"query":"   "}` got a 400 with
  a JSON `error` and zero model calls every time. `{"query":123}` got a 500
  with Flask's HTML error page and no JSON every time.
- **C5 MISSED.** Trial 3 was 9/10. `valid_5` was a 500 so there was no
  `selected_item` or `fit_card`. The other 29 all had a `selected_item` that
  was in `search_results`, priced at or under the ceiling, with a non-empty
  `outfit_suggestion` and `fit_card`.

I did not revise any criteria. `criteria.md` is the same file in commit
`10c8ba1`, in `results/capstone_before/criteria_snapshot.md`, and in
`results/capstone_after/criteria_snapshot.md`. I ran `git diff HEAD -- criteria.md`
before each capture and it was empty.

Real output under each criterion (file and function that produced it):

- C1: any log line above. Even the 500 for `42ca22a5…` has a timestamp,
  input, output, status, outcome and duration. File `logs/requests.jsonl`,
  written by the logger in `serve.py`.
- C2: `valid_9` trial 3, `"duration_ms": 36428.797`, `"status_code": 200`.
  `capture_capstone.py::main` measured it at the client as
  `client_elapsed_seconds: 36.431`.
- C3: `valid_9` trial 3, `"model_calls": 2, "reported_tokens": {"prompt": 703,
"output": 183, "total": 886}`, a pass. `valid_5` trial 3,
  `"outcome": "error"` with 516 tokens, a miss.
- C4: before, `{"query": 123}` gave `"status_code": 500` and the body was
  `non_json_body: "<!doctype html>…500 Internal Server Error…"`. After, it gave
  `"status_code": 400, "outcome": "rejected", "model_calls": 0` and
  `{"error": "The 'query' field must be non-empty text, …"}`. This is the
  `/ask` route in `serve.py`.
- C5: `valid_9` trial 3, `selected_item.id` is `lst_028`, which is the only
  item in `search_results`, price 44.0 under the 50 ceiling, `fit_card` and
  `outfit_suggestion` both non-empty. Produced by `agent.py::run_agent`.

**Diagnoses**

The seven miss lines in the baseline report are really three different things.

_Miss A: `{"query": 123}` returned 500 in all three trials (C4)._

Where: the `/ask` handler in `serve.py`, before the agent runs.

Why: the handler checked that `query` was there and that it was not blank, but
it never checked the type. An integer passed both checks and then hit code
that expects a string (the query parsing in `run_agent` uses string methods
and regexes), which raised. Nothing caught it, so Flask sent its default HTML
500 page with no JSON `error` field. The log line proves the agent never ran:
`model_calls: 0`, `agent_ms: null`, `duration_ms: 2.3`. This one is
deterministic, 3 out of 3, and it is the one I fixed.

_Miss B: `valid_5` ("cardigan under $40"), trial 3, returned 500 after 7 s
(C2, C3, C5)._

Where: the Gemini call in `generate.py`, reached from `suggest_outfit` or
`create_fit_card` inside `run_agent`.

Why: Gemini returned `503 UNAVAILABLE` with the message "high demand."
`generate.py` raised `ModelUnavailable`, `run_agent` does not catch that, so
it went up to `serve.py` which turned it into a 500 JSON error. The log shows
`model_calls: 2` and 516 tokens before it died, so the request had already
spent model calls and then threw them away. There is no retry on a 503
anywhere in the path, so a temporary outage on Google's side becomes a hard
failure for the user. The same query passed in trials 1 and 2 and in all three
after trials, which fits an outside cause and not a bug in the query. My fix
did not touch this.

_Miss C: `valid_9` ("boots under $50"), trial 3, returned 200 but took 36.4 s
(C2)._

Where: inside the agent waiting on the model. `agent_ms: 36428` and
`queue_ms: 0.001`, so it was not waiting on the request lock.

Why: the token count (886) is normal, so it was not a long output. It was wait
time. This request ran at 18:18:48, about 70 seconds after the 503 in Miss B at
18:17:36, so Gemini was already having problems in that window. `generate.py`
also paces itself against the per-minute limit after a lot of calls in a row.
My log only records total `agent_ms`, not time per model call, so I cannot
tell from this evidence how much was Gemini being slow and how much was the
pacing wait. That is a gap in my instrumentation, not just a slow request.
The same query took 13.2 s and 14.5 s in the other baseline trials and
14.3 / 14.1 / 8.8 s after.

**The Improvement**

What I changed (commit `fa4ce3a`): in the `/ask` handler in `serve.py`, the
query now has to be a `str` with some non-whitespace in it, and that check runs
before the lock and before the agent. If it fails, the route returns 400 with
`{"error": "The 'query' field must be non-empty text, e.g. …"}` and logs the
request as `outcome: "rejected"` with `model_calls: 0`.

Why this one: Miss A was the only failure that was deterministic, fully inside
code I control, and fixable with one change. Misses B and C are on Gemini's
side and would need retries and better timing, which is real work but not a
clean before-and-after in one unit.

Did it help, and how I know: yes. C4 went from 2/3 in every trial to 3/3 in
every trial. The three numeric-query requests in the after run each got a 400
in under 0.2 ms with zero model calls (log lines above). The other four
criteria also read MET after, but I am not claiming the fix did that. Those
misses were one 503 and one slow response from Gemini, and they just did not
happen again in the after run (0 of 30 valid requests failed, versus 1 of 30
before). The after run shows the fix did not break anything. It does not show
the Gemini problems are solved.

What it cost elsewhere: nothing I can measure. The check adds about 0.15 ms to
a rejected request and no model calls. Mean latency went from 10.61 s to
11.35 s and mean tokens from 868.0 to 871.8 between phases, but individual
requests ranged from 2.7 s to 23.0 s in the after run, so that difference is
noise from Gemini, and the check runs before any of that work starts anyway.

Was a target too easy: yes, Criterion 2. All 30 valid after requests passed at
30 s, but four requests across both phases landed between 20 and 23 s (22.50,
21.50, 22.59 before, 23.01 after). A 20-second target would have missed in
both phases, and that would be a better test of whether two serial model calls
is acceptable for an interactive request. Next time I would set C2 to 10/10
within 20 s and expect it to miss until the Gemini wait is dealt with.

**What's Still Broken**

All five criteria read MET after the change, but two of the baseline failures
were not fixed, they just did not come back:

1. _Gemini 503 turning into a user-facing 500 (Miss B)._ What I would do:
   catch `ModelUnavailable` in `generate.py`, retry once or twice with a short
   wait, and if it still fails return a 503 JSON error that says to try again
   instead of a 500. Why I stopped: the brief asks for one measured
   improvement, and a retry is hard to measure honestly because the failure
   is random. Three trials cannot show whether the retry helped.
2. _The 36-second request (Miss C)._ What I would do: log the time for each
model call separately so I can tell Gemini latency from rate-limit pacing,
then decide whether the agent needs a timeout. Why I stopped: without the
per-call timing I would be guessing at the cause, and adding it after the
baseline would have changed what the after run was measuring.
<!-- TODO: if you have NOT done the clean clone, keep item 3. If you have, delete it. -->
3. _Clean-checkout check._ I have not yet run RUNNING.md from a fresh clone.

What I would do first: the per-call timing. It is the smallest change, it
makes both remaining misses diagnosable instead of guessed, and it would have
let me set a 20-second target I could defend instead of the 30-second one I
had to call too easy.

**How I Used AI**

AI helped with reading the repo, the logging and timing code, the draft of the
criteria, the capture and evaluate scripts, and working through the diagnoses
and this write-up. I chose to go with the AI-drafted criteria and say so here.
They are not independently authored, so the brief's independent-authorship
requirement may not be met. Every number, verdict, and pasted log line above
is from real runs on my machine. Nothing was made up or edited.

- _Moment 1:_ I asked for a deploy-and-instrument extension to my existing
  repo. AI gave me request logging, timing, usage summary, and some engineering
  checks as a patch. I imported it and ran the checks locally. They use a
  stubbed agent, so I did not count them as acceptance evidence.
- _Moment 2:_ I asked AI to draft criteria. It proposed five areas and numeric
  targets. Before any run I had the batch spelled out as ten valid plus three
  invalid requests per trial and committed the file on its own (`10c8ba1`) so
  the results would be scored against a frozen standard.

- _Moment 3:_ After the baseline I gave AI the saved responses and log lines
  for the three failures and asked what the mechanism was. It called the
  numeric-query 500 a missing type check in my handler, deterministic and
  mine to fix, and the other two Gemini-side. I picked the validation fix
  because it was the only one with a clean before-and-after. When AI summed up
  the after run as "all criteria passed," I kept the distinction that only C4
  was fixed and the others just did not recur.
