"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
 
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable
 

# ── query patterns ────────────────────────────────────────────────────────────
 
# Defined once and used for both finding and removing the size, so the two
# can never drift apart.
# US comes first, so "size US 8.5" is captured whole instead of being cut to "US".
SIZE_PATTERN = (
    r"\bsize\s+("
    r"US\s*\d+(?:\.\d+)?"
    r"|W\d+(?:\s+L\d+)?"
    r"|[A-Za-z]{1,3}(?:/[A-Za-z]{1,3})?"
    r"|\d+(?:\.\d+)?"
    r")\b"
)
 
PRICE_PATTERN = r"\b(?:under|below)\s*\$?(\d+(?:\.\d+)?)"
 
# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "outfit_input": None,        # the item suggest_outfit actually received (criterion 3)
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    
    # ── Parse maximum price ────────────────────────────────────────────────
    # Example:
    # "graphic tee under $30" -> 30.0
    price_match = re.search(PRICE_PATTERN, query, re.IGNORECASE)
 
    if price_match:
        max_price = float(price_match.group(1))
    else:
        max_price = None
 
    # ── Parse size ─────────────────────────────────────────────────────────
    # Handles examples such as:
    # size M
    # size XXS
    # size S/M
    # size W30 L30
    # size US 8.5
    size_match = re.search(SIZE_PATTERN, query, re.IGNORECASE)
 
    if size_match:
        size = size_match.group(1)
    else:
        size = None
 
 
    # ── Build the description ──────────────────────────────────────────────
    # Remove the price phrase from the search description.
    description = re.sub(PRICE_PATTERN, "", query, flags=re.IGNORECASE)
 
    # Remove the size phrase from the search description.
    description = re.sub(SIZE_PATTERN, "", description, flags=re.IGNORECASE)
 
    # Clean extra spaces and punctuation.
    description = " ".join(description.split()).strip(" ,.-")
 
 
    # Save parsed information in the session.
    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }
 
 
    # ── Planning loop ──────────────────────────────────────────────────────
 
    step = "search"
    count = 0
 
    while True:
 
        count += 1
 
        # Safety guard so the agent cannot loop forever.
        trace.check_iterations(count)
 
 
        # ── STEP 1: SEARCH ────────────────────────────────────────────────
        if step == "search":
 
            session["search_results"] = search_listings(
                description=session["parsed"]["description"],
                size=session["parsed"]["size"],
                max_price=session["parsed"]["max_price"],
            )
 
 
            # IMPORTANT BRANCH:
            # If search returned nothing, stop here.
            if not session["search_results"]:
 
                # Name what the user could change, using what they asked for.
                tips = []
                p = session["parsed"]
                if p["max_price"] is not None:
                    tips.append(f"raise your ${p['max_price']:.0f} price limit")
                if p["size"]:
                    tips.append(f"try a size other than {p['size']}")
                tips.append("use broader words like 'tee' or 'jacket'")
 
                session["error"] = (
                    "I couldn't find a matching item. Try: "
                    + "; ".join(tips) + "."
                )
 
                return session
 
 
            # Pick the first / best search result.
            session["selected_item"] = session["search_results"][0]
 
            # Next action depends on the successful search.
            step = "outfit"
            continue
 
 
        # ── STEP 2: SUGGEST OUTFIT ───────────────────────────────────────
        if step == "outfit":
 
            # Read the item back out of the session, and record exactly
            # what suggest_outfit received.
            item = session["selected_item"]
            session["outfit_input"] = item
 
            session["outfit_suggestion"] = suggest_outfit(
                item,
                session["wardrobe"],
            )
 
            step = "fit_card"
            continue
 
 
        # ── STEP 3: CREATE FIT CARD ──────────────────────────────────────
        if step == "fit_card":
 
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"],
                session["selected_item"],
            )
 
            return session
 
 
# ── display helper ────────────────────────────────────────────────────────────
 
def _show(session: dict) -> None:
 
    print(f"  parsed:   {session['parsed']}")
 
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(
            f"  fit_card is {session['fit_card']!r} "
            f"— it should still be None here"
        )
        return
 
    item = session["selected_item"] or {}
    received = session.get("outfit_input") or {}
 
    print(
        f"  found:    {item.get('title')} — "
        f"${item.get('price')} on {item.get('platform')}"
    )
    print(
        f"  state:    selected {item.get('id')} → "
        f"suggest_outfit received {received.get('id')}"
    )
 
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")
 



# ── running it directly ───────────────────────────────────────────────────────
"""
def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")
"""

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
