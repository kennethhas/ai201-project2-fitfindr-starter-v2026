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

- *What I asked for:* I asked AI to help me review my `search_listings` logic.
- *What came back:* It pointed out that my keyword check used substring
  matching (`word in searchable_text`), so "hat" matched "that" in the Polo
  listing and "red" matched "structured" in the Denim Jacket. It also noted I
  kept filler words like "a" and "for", which appear in almost every listing.
- *What I changed:* I kept my structure but switched to whole-word matching
  with a stopword list, and changed `if size is not None:` to `if size:` so an
  empty size string doesn't filter out every listing. My size matching was
  already whole-token, so `L` doesn't match `XL`; I kept that as-is.

**Moment 2**

- *What I asked for:*I asked AI to help me review my `agent.py` 
- *What came back:* It said my structure was excellent  — I used a `while True`
  loop with a `step` variable, while its version ran the steps in a straight
  line. But it found a bug in my size regex: the letters-only pattern was
  checked first, so "size US 8.5" was cut down to just "US", which would match
  every US shoe size. It also pointed out that I never recorded what
  `suggest_outfit` actually received, so I had no way to check my state
  criterion (criterion 3).
- *What I changed:* I kept my loop structure. I moved the `US` pattern first
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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

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
