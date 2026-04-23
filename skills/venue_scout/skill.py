"""
Venue Scout — Paradigm Events
Centaur skill for finding and ranking venues for Paradigm events.

Trigger examples (in Slack):
  @Centaur find me a venue for a fellow dinner, 30 people, Lower East Side NYC, intimate and warm
  @Centaur venue scout: offsite for 80, wine country, multi-day, craft-driven vibe
  @Centaur use venue scout — cocktail party 120 people SF, full buyout, design-forward
"""

SKILL_NAME = "venue_scout"
SKILL_DESCRIPTION = (
    "Finds and ranks venues for Paradigm events. "
    "Searches Eater, Infatuation, Resy, OpenTable, Reddit, Yelp, Instagram, and local press "
    "to surface the best matches — including new, under-the-radar spots — scored against "
    "Paradigm's criteria: food quality, private dining, neighborhood feel, design aesthetic, "
    "and logistics. Supports dinners, happy hours, offsites, flagship/tentpole events, and more."
)

# ── Paradigm's pre-vetted venue database ──────────────────────────────────────
PARADIGM_VENUES = {
    "sf": [
        "Saison", "Quince", "Benu", "Californios", "Birdsong", "Sons & Daughters",
        "Lazy Bear", "Niku", "Nisei", "Gary Danko", "Rich Table", "Nightbird",
        "The Progress", "Frances", "Octavia", "Nopa", "Rintaro", "Cotogna",
        "Flour + Water", "Che Fico", "Foreign Cinema", "Sorrel", "Spruce",
        "Liho Liho Yacht Club", "Ernest", "Wayfare Tavern", "Angler", "Miller & Lux",
        "Kokkari Estiatorio", "Mister Jiu's", "Penny Roma", "Good Good Culture Club",
        "Roaming Goat", "Macondray", "Bar Sprezzatura", "True Laurel", "ABV",
        "Pacific Cocktail Haven", "Trick Dog", "Wildhawk", "The Battery SF",
        "Shack15", "Fort Mason Gallery 308", "Hazie's", "Charmaine's Rooftop",
        "Local Edition", "Novela",
    ],
    "nyc": [
        "Atomix", "Crown Shy", "Gramercy Tavern", "Via Carota", "Don Angie",
        "Carbone", "Manhatta", "Rezdora", "Cote", "Jua", "Blue Hill", "Torrisi",
        "Peasant", "Balthazar", "Dirty French", "Gage & Tollner", "LaserWolf",
        "Death & Co", "Maison Premiere", "Aska", "Charlie Bird", "Altro Paradiso",
        "Shuka", "Union Square Cafe", "Dame", "Sushi Nakazawa", "Sushi Noz",
        "Tatiana by Kwame Onwuachi", "Semma", "Bar Calico", "Oxomoco",
        "Chinese Tuxedo", "Dhamaka", "Fish Cheeks", "Caffe Dante", "Bar Goto",
        "Bar Pisellino", "Dante West Village", "Buvette", "Sant Ambroeus",
        "Public Records", "Dead Letter No9", "Cervo's", "Nudibranch", "Gjelina NYC",
        "The Pool", "Crane Club", "Oiji Mi", "Atoboy", "Wayla", "Thai Diner",
        "Swan Room", "Broken Shaker",
    ],
    "las_vegas": [
        "Carbone Vegas", "Esther's Kitchen", "Cut by Wolfgang Puck",
        "Estiatorio Milos", "Spago", "Gjelina Vegas", "Motherwolf", "KYU",
        "Hakkasan", "The Bazaar by Jose Andres", "Nobu", "Scarpetta", "Momofuku",
    ],
    "resorts": [
        "Sun Valley Resort", "Big Sky Resort", "Snowbird", "Jackson Lake Lodge",
        "Fairmont Banff Springs", "Fairmont Chateau Lake Louise",
        "Cavallo Point", "Carneros Resort", "Post Ranch Inn", "Ventana Big Sur",
        "Auberge du Soleil", "Calistoga Ranch", "Bardessono", "Solage Calistoga",
        "Wildflower Farms", "Gurney's Montauk", "Shou Sugi Ban House",
        "AutoCamp", "Viceroy Snowmass",
    ],
}

EVENT_TYPE_GUIDANCE = {
    "dinner":       "Restaurant with private dining room or full buyout. Michelin-tier or elevated craft kitchen. ≤60 guests.",
    "fellow_dinner": "Same as dinner — intimate, celebratory, not a networking event. Fellows know each other.",
    "happy_hour":   "Bar, wine bar, or rooftop. Semi-private or full buyout. ≤150 guests.",
    "cocktail_party": "Same as happy hour — standing, mingling format.",
    "offsite":      "Multi-day resort or hotel. Wine country or mountain preferred. Full property or large block.",
    "flagship":     "Large resort buyout for 150–500+ guests. Sun Valley / Big Sky / Snowbird tier.",
    "tentpole":     "Same as flagship — Paradigm's marquee annual event.",
    "workshop":     "Intimate, quiet space with natural light. ≤40 guests. Focused work environment.",
    "conference":   "Private event space or club setting. 50–200 guests. A/V capability required.",
    "team_lunch":   "Casual, good food, walkable neighborhood. ≤30 guests.",
}

SYSTEM_PROMPT = """You are Paradigm's in-house venue researcher. Paradigm is a design-forward crypto/tech investment firm.
Your aesthetic: Michelin-caliber or craft-driven kitchens, design-forward spaces, natural light preferred,
neighborhood gems over tourist traps, never generic hotel ballrooms (unless full resort buyout).

You have access to Paradigm's pre-vetted venue database. Always prioritize those venues when they fit.
You also have web search — use it aggressively to surface current, real-world venue options including new openings.

SEARCH SOURCES (use all of these):
- Eater (eater.com/[city]) — new openings, private dining roundups, neighborhood guides
- The Infatuation (theinfatuation.com) — vibe matching, curated picks
- Resy blog + OpenTable Digest — trending restaurants, PDR availability
- Beli app lists — what's hot and highly rated right now
- Yelp — event spaces, private dining rooms, reviews
- Reddit (r/[city]food) — hidden gems, "best private dining" threads
- Instagram — "[city] new restaurant 2025", "[neighborhood] restaurant opening"
- Local press — SF Chronicle, Grub Street, NY Times Food, Time Out, local city mags

Run 5–6 searches minimum. Surface at least 1–2 venues that are new or under-the-radar.
Verify all venues are currently operating.

SCORING DIMENSIONS (return all five, 1–10):
- food_quality: Michelin tier, kitchen reputation, ingredient sourcing
- private_dining: PDR quality, buyout flexibility, dedicated event setup
- neighborhood_feel: authentic, walkable, not touristy or corporate
- design_aesthetic: interior design, natural light, visual cohesion
- logistics: capacity fit, A/V, accessibility, F&B minimum reasonableness

OUTPUT FORMAT — return ONLY a JSON array, no prose:
[
  {
    "name": "Venue Name",
    "location": "Neighborhood, City",
    "overall": 9.2,
    "fit_summary": "Short evocative phrase",
    "verdict": "2-3 sentences on fit — specific to the brief",
    "watch_out": "One honest concern",
    "scores": {
      "food_quality": 9, "private_dining": 8, "neighborhood_feel": 9,
      "design_aesthetic": 8, "logistics": 7
    },
    "outreach_hook": "One venue-specific sentence to open an outreach email"
  }
]"""


async def run(brief: str, tools, memory=None) -> dict:
    """
    Main skill entrypoint. Called by Centaur when the skill is triggered.

    Args:
        brief:  Natural language event description from the user
        tools:  Centaur tool proxy — use tools.websearch(), tools.llm(), tools.slack()
        memory: Optional Centaur memory context (past Paradigm events, preferences)

    Returns:
        dict with 'venues' list and 'sources_checked' list
    """
    # Pull any relevant past event context from memory
    past_context = ""
    if memory:
        past_events = await memory.query("Paradigm past events venues booked feedback", top_k=5)
        if past_events:
            past_context = "\n\nPAST PARADIGM EVENT CONTEXT (use to inform recommendations):\n"
            past_context += "\n".join(f"- {e['text']}" for e in past_events)

    # Build search queries from the brief
    search_queries = _build_search_queries(brief)
    search_results = []

    for query in search_queries:
        try:
            result = await tools.websearch(query=query)
            search_results.append({"query": query, "result": result})
        except Exception:
            pass

    # Synthesize with LLM
    search_context = "\n\n".join(
        f"Search: {r['query']}\nResults: {r['result']}" for r in search_results
    )

    # Build venue database context based on detected city
    city = _detect_city(brief)
    venue_db = _get_venue_db(city)

    full_prompt = f"""{SYSTEM_PROMPT}

PARADIGM'S PRE-VETTED VENUES FOR THIS CITY:
{venue_db}
{past_context}

WEB SEARCH RESULTS:
{search_context}

EVENT BRIEF:
{brief}

Return 5 venue recommendations as a JSON array only."""

    response = await tools.llm(
        prompt=full_prompt,
        model="claude-opus-4-5",
        max_tokens=4000,
    )

    # Extract JSON array from response
    import re, json
    match = re.search(r'\[[\s\S]*\]', response)
    if not match:
        return {"error": "Could not parse venue list", "raw": response}

    venues = json.loads(match.group(0))

    # Store this search in memory for future training
    if memory:
        await memory.store(
            text=f"Venue search: {brief[:200]} → Top pick: {venues[0]['name'] if venues else 'none'}",
            metadata={"type": "venue_search", "brief": brief, "venues": [v['name'] for v in venues]},
        )

    return {
        "venues": venues,
        "sources_checked": [r["query"] for r in search_results],
    }


async def record_booking(venue_name: str, brief: str, tools, memory=None, feedback: str = "") -> dict:
    """
    Call this after an event to record what was actually booked.
    Trains Centaur's memory for better future recommendations.

    Example Slack trigger:
      @Centaur venue scout: we booked Nisei for the fellow dinner, it was excellent
    """
    if not memory:
        return {"status": "no memory available"}

    record = (
        f"BOOKED: {venue_name} | Brief: {brief[:150]} | Feedback: {feedback or 'no feedback'}"
    )
    await memory.store(
        text=record,
        metadata={
            "type": "venue_booked",
            "venue": venue_name,
            "brief": brief,
            "feedback": feedback,
        },
    )

    # Also post confirmation to Slack if tools available
    try:
        await tools.slack(
            action="post_message",
            channel="#events-ops",
            text=f"📍 Venue booked logged: *{venue_name}*\n_{brief[:100]}_\n{feedback}",
        )
    except Exception:
        pass

    return {"status": "recorded", "venue": venue_name}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _detect_city(brief: str) -> str:
    brief_lower = brief.lower()
    if any(x in brief_lower for x in ["nyc", "new york", "manhattan", "brooklyn", "lower east", "west village", "soho"]):
        return "nyc"
    if any(x in brief_lower for x in ["sf", "san francisco", "soma", "mission", "hayes valley", "nopa", "fidi"]):
        return "sf"
    if any(x in brief_lower for x in ["las vegas", "vegas", "the strip"]):
        return "las_vegas"
    if any(x in brief_lower for x in ["resort", "offsite", "retreat", "mountain", "ski", "napa", "wine country", "sun valley", "big sky"]):
        return "resorts"
    return "nyc"  # default


def _get_venue_db(city: str) -> str:
    venues = PARADIGM_VENUES.get(city, PARADIGM_VENUES["nyc"])
    return ", ".join(venues)


def _build_search_queries(brief: str) -> list[str]:
    """Generate targeted search queries from the brief."""
    brief_lower = brief.lower()

    # Detect city for targeted searches
    city_map = {
        "nyc": "NYC New York",
        "sf": "San Francisco SF",
        "las_vegas": "Las Vegas",
        "resorts": "resort offsite",
    }
    city = _detect_city(brief)
    city_str = city_map.get(city, "New York")

    queries = [
        f"Eater {city_str} best private dining rooms 2025",
        f"Infatuation {city_str} best restaurants intimate dinner private",
        f"new restaurant opening {city_str} 2025 private dining events",
        f"reddit r/{city_str.lower().replace(' ', '')}food best private dining event space 2025",
        f"Resy {city_str} private dining room availability exclusive",
        f"Beli app top restaurants {city_str} 2025",
        f"Yelp {city_str} private dining room event space highly rated",
        f"{city_str} under the radar restaurant hidden gem 2025",
    ]

    # Add neighborhood-specific search if mentioned
    neighborhoods = [
        "lower east side", "west village", "soho", "nolita", "brooklyn",
        "mission", "hayes valley", "nopa", "soma", "russian hill",
    ]
    for hood in neighborhoods:
        if hood in brief_lower:
            queries.append(f"best restaurants {hood} {city_str} private dining 2025")
            break

    return queries[:8]  # cap at 8 searches
