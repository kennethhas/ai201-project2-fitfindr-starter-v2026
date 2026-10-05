"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""
import re
 
import config
from generate import generate
from utils.data_loader import load_listings
 
 
# Filler words that appear in queries but say nothing about the item.
STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "of", "to", "on",
    "i", "im", "me", "my", "looking", "want", "need", "find", "some",
    "under", "below", "size", "price", "t",
}
 
 
def _split_size(text: str) -> list[str]:
    """'S/M' → ['s', 'm'], 'XL (oversized)' → ['xl', 'oversized'], 'US 8.5' → ['us', '8.5']."""
    return (
        text.lower()
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("-", " ")
        .split()
    )
 

# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Filter listings by price ceiling (inclusive) and size (whole-token match),
    score the rest by how many query words appear as WHOLE words in the
    listing, drop zero scores, and return listing dicts best match first.
 
    Returns [] when nothing matches — never None, never an exception.
 
    Test:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    matches = []
 
    # Whole words only, no filler words, no bare numbers. A set, so a word
    # typed twice doesn't count twice.
    query_words = {
        w for w in re.findall(r"[a-z0-9]+", (description or "").lower())
        if w not in STOPWORDS and not w.isdigit()
    }
    if not query_words:
        return []
 
    for listing in listings:
        # Filter by maximum price
        if max_price is not None and listing["price"] > max_price:
            continue
 
        # Filter by size — every part of the requested size must be a whole
        # part of the listing's size. "M" matches "S/M"; "L" does not match "XL".
        # `if size:` (not `is not None`) so an empty string means "no filter".
        if size:
            wanted_parts = _split_size(size)
            listing_size_parts = _split_size(listing["size"])
            if not all(part in listing_size_parts for part in wanted_parts):
                continue
 
        # Put the searchable listing fields into one string
        searchable_text = " ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
            " ".join(listing["colors"]),
            listing["brand"] or "",
            listing["platform"],
        ]).lower()
 
        # Whole words only — so "hat" no longer matches "that",
        # and "red" no longer matches "structured".
        searchable_words = set(re.findall(r"[a-z0-9]+", searchable_text))
 
        # Count how many query words match
        score = sum(1 for word in query_words if word in searchable_words)
 
        # Ignore anything with no keyword match
        if score == 0:
            continue
 
        matches.append((score, listing))
 
    # Highest score first
    matches.sort(key=lambda item: item[0], reverse=True)
 
    return [listing for score, listing in matches[:config.SEARCH_RESULT_LIMIT]]
 


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Suggest one or two outfits built around new_item.
    Empty wardrobe → general styling advice. Always returns a non-empty string.
 
    Test:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
 
    item_block = f"""Title: {new_item.get("title", "")}
Category: {new_item.get("category", "")}
Colors: {", ".join(new_item.get("colors") or [])}
Style: {", ".join(new_item.get("style_tags") or [])}"""
 
    # Empty wardrobe
    if not items:
        prompt = f"""
You are a clothing stylist.
 
The user is considering this thrifted item:
 
{item_block}
 
The user has no wardrobe items saved yet.
 
Give one or two simple general styling ideas for this item.
Keep the response short and practical.
Plain text, under 120 words, no headings.
"""
 
        response = generate(prompt)
 
        if response and response.strip():
            return response.strip()
 
        return "Try pairing this item with simple neutral basics and shoes that match its overall style."
 
    # Wardrobe has items
    wardrobe_lines = []
 
    for item in items:
        # .get() so one wardrobe item missing a field can't crash the tool
        line = (
            f'- {item.get("name", "unnamed item")} | '
            f'category: {item.get("category", "")} | '
            f'colors: {", ".join(item.get("colors") or [])} | '
            f'style: {", ".join(item.get("style_tags") or [])}'
        )
 
        if item.get("notes"):
            line += f' | notes: {item["notes"]}'
 
        wardrobe_lines.append(line)
 
    wardrobe_text = "\n".join(wardrobe_lines)
 
    prompt = f"""
You are a clothing stylist.
 
The user is considering this thrifted item:
 
{item_block}
 
Here are the clothes already in the user's wardrobe:
 
{wardrobe_text}
 
Suggest one or two outfits using the new item and pieces the user already owns.
Only use pieces from the list above, and name them exactly as listed.
Keep the response short and practical.
Plain text, under 120 words, no headings.
"""
 
    response = generate(prompt)
 
    if response and response.strip():
        return response.strip()
 
    return "I could not generate a specific outfit suggestion for this item."
 

# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a 2–4 sentence caption mentioning the item, price and platform once each.
    Empty outfit → a descriptive message instead of raising.
 
    Test:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    price = f"${new_item['price']:.2f}"   # e.g. $24.00 — the one format criterion 4 checks for
 
    # Guard against an empty outfit
    if not outfit or not outfit.strip():
        return (
            f"I found {new_item['title']} for {price} "
            f"on {new_item['platform']}, but I don't have an outfit suggestion "
            f"to build the fit card from."
        )
 
    prompt = f"""
Write a short social-media-style fit card for this thrift find.
 
Item: {new_item["title"]}
Price: {price}
Platform: {new_item["platform"]}
Category: {new_item["category"]}
Colors: {", ".join(new_item.get("colors") or [])}
Style tags: {", ".join(new_item.get("style_tags") or [])}
 
Outfit suggestion:
{outfit}
 
Requirements:
- Write 2 to 4 sentences.
- Mention the item.
- Write the price exactly as {price}, exactly once.
- Mention the platform ({new_item["platform"]}) exactly once.
- Describe the overall vibe.
- Make it sound like a real post, not a product description.
- Don't invent details that aren't listed above.
- Output only the caption. No intro line, no quotes around it.
"""
 
    response = generate(prompt)
 
    if response and response.strip():
        return response.strip()
 
    # Short fallback — no longer pastes the whole outfit in, so it can't
    # blow past the 2–4 sentence target.
    return f"Thrifted the {new_item['title']} for {price} on {new_item['platform']}."
 