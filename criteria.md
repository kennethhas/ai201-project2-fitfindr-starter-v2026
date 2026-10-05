# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 because search_listings uses keyword matching, so some reasonable phrasings may not match even when the loop works correctly.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because an empty search result is a clear condition. If search_listings returns [], the agent should always stop before suggest_outfit.


---

## 3. The selected item stays the same through the session

For 5 of 5 matching queries, the `id` stored in
`session["selected_item"]` matches the `id` of the listing passed to
`suggest_outfit`.

**Why this target:**
I chose 5 of 5 because passing the selected item through the session is
deterministic. If the IDs do not match, the agent used a different listing
than the one it selected, which means the state handoff is incorrect.
---

## 4. The fit card includes the important item details

For 5 of 5 successful runs, the fit card mentions the selected item's title,
its price, and its platform.

**Why this target:**
I chose 5 of 5 because the item, price, and platform are facts provided
directly to `create_fit_card`. Different wording is acceptable, but leaving
out one of these facts means the final response did not use all of the
important information it was given.
---

## 5. Search respects the maximum price

For 5 different queries that include a maximum price, every listing returned
by `search_listings` has a price less than or equal to the requested maximum.
At least one of the five queries must use a price ceiling that excludes an
otherwise matching listing.

**Why this target:**
I chose 5 of 5 because price filtering is deterministic. Returning even one
listing above the user's stated budget means the filter is incorrect. Requiring
at least one query to exclude an otherwise matching item also proves that the
price filter was actually exercised.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
