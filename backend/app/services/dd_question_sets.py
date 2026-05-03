"""
TaoWAR Deep DD Question Sets
Provides domain question sets for the Deep DD Interrogation pass (Step 04).

Two sets:
- EARLY_STAGE_DOMAINS  — 72 questions, all stage_threshold: "all"
- SERIES_STAGE_DOMAINS — 148 questions, stage_threshold: all/seed/series_a/series_b

Each domain dict:
    {
        "name":      str,           # display name
        "agent":     str,           # TaoWAR agent assigned to this domain
        "questions": [
            {
                "text":            str,
                "stage_threshold": str   # "all" | "seed" | "series_a" | "series_b"
            },
            ...
        ]
    }

Usage:
    from app.services.dd_question_sets import get_domain_set
    DOMAINS = get_domain_set(company_stage_selection)   # "early_stage" | "series_stage"
"""

from typing import List, Dict, Any

# ══════════════════════════════════════════════════════════════════════════════
# EARLY STAGE — 72 questions  (all stage_threshold: "all")
# Calibrated for pre-seed / seed-ready companies.
# Absence of traction is expected, not penalised.
# ══════════════════════════════════════════════════════════════════════════════

EARLY_STAGE_DOMAINS: List[Dict[str, Any]] = [

    # ── 1. Identity & Stage ── 13 questions ── Lady Kaede ─────────────────────
    {
        "name": "IDENTITY & STAGE",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "What problem is the company solving, and for whom?", "stage_threshold": "all"},
            {"text": "What stage of development is the company at today?", "stage_threshold": "all"},
            {"text": "What is the founding story and core thesis?", "stage_threshold": "all"},
            {"text": "How does the company define its primary market and target user?", "stage_threshold": "all"},
            {"text": "What is the company's current TRL (Technology Readiness Level)?", "stage_threshold": "all"},
            {"text": "Has the team articulated a clear value proposition in one sentence?", "stage_threshold": "all"},
            {"text": "What assumptions underpin the core business thesis?", "stage_threshold": "all"},
            {"text": "What is the company's origin — academic spinout, corporate pivot, or greenfield?", "stage_threshold": "all"},
            {"text": "Has the team validated that the problem is real through direct user research?", "stage_threshold": "all"},
            {"text": "What would make this company's thesis fundamentally wrong?", "stage_threshold": "all"},
            {"text": "Does the company have a clear name, brand, and legal entity established?", "stage_threshold": "all"},
            {"text": "What is the company's geographic focus at launch?", "stage_threshold": "all"},
            {"text": "Has the founding team articulated why they are uniquely positioned to solve this?", "stage_threshold": "all"},
        ]
    },

    # ── 2. Technology & Innovation ── 11 questions ── Lord Reyoku ─────────────
    {
        "name": "TECHNOLOGY & INNOVATION",
        "agent": "Lord Reyoku",
        "questions": [
            {"text": "What is the core technology or methodology underpinning the solution?", "stage_threshold": "all"},
            {"text": "Is there a working prototype, proof of concept, or MVP?", "stage_threshold": "all"},
            {"text": "What makes the technical approach novel compared to existing solutions?", "stage_threshold": "all"},
            {"text": "What are the key technical risks or unknowns at this stage?", "stage_threshold": "all"},
            {"text": "Is any intellectual property being developed or protected?", "stage_threshold": "all"},
            {"text": "What is the build-vs-buy decision on core technology components?", "stage_threshold": "all"},
            {"text": "How dependent is the solution on third-party platforms or infrastructure?", "stage_threshold": "all"},
            {"text": "Has the technology been tested with any real users or in a real environment?", "stage_threshold": "all"},
            {"text": "What is the product roadmap for the next 12 months?", "stage_threshold": "all"},
            {"text": "Are there any open-source components that could create licensing issues?", "stage_threshold": "all"},
            {"text": "What is the team's plan if the primary technical approach fails?", "stage_threshold": "all"},
        ]
    },

    # ── 3. Jurisdiction & Regulation ── 9 questions ── Shingen Iron Wolf ───────
    {
        "name": "JURISDICTION & REGULATION",
        "agent": "Shingen Iron Wolf",
        "questions": [
            {"text": "In which jurisdictions does the company plan to operate or sell?", "stage_threshold": "all"},
            {"text": "Are there sector-specific licences or regulatory approvals required?", "stage_threshold": "all"},
            {"text": "Has the team taken legal advice on the regulatory environment?", "stage_threshold": "all"},
            {"text": "Does the product handle personal data? If so, under what legal framework?", "stage_threshold": "all"},
            {"text": "Are there any export controls or trade restrictions relevant to the technology?", "stage_threshold": "all"},
            {"text": "What is the regulatory risk if rules change in the primary market?", "stage_threshold": "all"},
            {"text": "Has the company secured any regulatory sandbox access or pre-engagement with regulators?", "stage_threshold": "all"},
            {"text": "Is the company incorporated in the most advantageous jurisdiction for IP and investment?", "stage_threshold": "all"},
            {"text": "Are there any known legal disputes, claims, or encumbrances on the business?", "stage_threshold": "all"},
        ]
    },

    # ── 4. Capital & Business Model ── 13 questions ── Lord Renji ─────────────
    {
        "name": "CAPITAL & BUSINESS MODEL",
        "agent": "Lord Renji",
        "questions": [
            {"text": "What is the proposed revenue model — how will the company make money?", "stage_threshold": "all"},
            {"text": "What funding has been raised to date, and from whom?", "stage_threshold": "all"},
            {"text": "What is the current monthly burn rate?", "stage_threshold": "all"},
            {"text": "How much runway does the company have at the current burn rate?", "stage_threshold": "all"},
            {"text": "What is the fundraising ask and what will the capital be used for?", "stage_threshold": "all"},
            {"text": "Has the team modelled the path to first revenue?", "stage_threshold": "all"},
            {"text": "What are the assumed unit economics — cost to acquire vs. lifetime value?", "stage_threshold": "all"},
            {"text": "Are there any grants, competitions, or non-dilutive funding sources in place?", "stage_threshold": "all"},
            {"text": "What is the pricing strategy and how was it derived?", "stage_threshold": "all"},
            {"text": "What are the key cost drivers of the business at scale?", "stage_threshold": "all"},
            {"text": "Has the company identified its first paying customer or signed letter of intent?", "stage_threshold": "all"},
            {"text": "What is the cap table structure and are there any problematic shareholders?", "stage_threshold": "all"},
            {"text": "What milestones must be achieved with this round to reach the next funding event?", "stage_threshold": "all"},
        ]
    },

    # ── 5. Market & Competition ── 13 questions ── Lady Asami ─────────────────
    {
        "name": "MARKET & COMPETITION",
        "agent": "Lady Asami",
        "questions": [
            {"text": "How large is the addressable market and how was that estimate derived?", "stage_threshold": "all"},
            {"text": "Who are the direct and indirect competitors?", "stage_threshold": "all"},
            {"text": "What is the company's sustainable competitive advantage?", "stage_threshold": "all"},
            {"text": "Why has no well-funded company solved this problem already?", "stage_threshold": "all"},
            {"text": "What is the go-to-market strategy for reaching early customers?", "stage_threshold": "all"},
            {"text": "What early market signals — if any — validate demand for the solution?", "stage_threshold": "all"},
            {"text": "How will the company win its first 10 customers?", "stage_threshold": "all"},
            {"text": "What are the key distribution channels and why were they chosen?", "stage_threshold": "all"},
            {"text": "Is the market growing, contracting, or being disrupted by a new technology?", "stage_threshold": "all"},
            {"text": "What would a well-resourced incumbent need to do to replicate this solution?", "stage_threshold": "all"},
            {"text": "Has the team spoken to potential customers and documented their feedback?", "stage_threshold": "all"},
            {"text": "What is the customer acquisition strategy and estimated cost?", "stage_threshold": "all"},
            {"text": "Are there any network effects or switching costs that could create defensibility?", "stage_threshold": "all"},
        ]
    },

    # ── 6. Team & Credibility ── 13 questions ── Lady Kaede ───────────────────
    {
        "name": "TEAM & CREDIBILITY",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "Who are the founders and what are their relevant backgrounds?", "stage_threshold": "all"},
            {"text": "Does the team have the technical skills needed to build the product?", "stage_threshold": "all"},
            {"text": "Does the team have the commercial skills needed to sell and scale?", "stage_threshold": "all"},
            {"text": "Are all founders full-time committed to the company?", "stage_threshold": "all"},
            {"text": "What is the equity split between founders and is it vesting?", "stage_threshold": "all"},
            {"text": "Has the team worked together before?", "stage_threshold": "all"},
            {"text": "Who are the advisors and what value do they bring?", "stage_threshold": "all"},
            {"text": "What key hires are needed in the next 12 months?", "stage_threshold": "all"},
            {"text": "Has any founder previously built and exited a company?", "stage_threshold": "all"},
            {"text": "What is the team's unfair advantage in this specific domain?", "stage_threshold": "all"},
            {"text": "How does the team handle disagreement and make decisions?", "stage_threshold": "all"},
            {"text": "Are there any conflicts of interest or competing obligations among the founders?", "stage_threshold": "all"},
            {"text": "What would cause a key founder to leave, and what happens if they do?", "stage_threshold": "all"},
        ]
    },
]

# Validate count
_early_total = sum(len(d["questions"]) for d in EARLY_STAGE_DOMAINS)
assert _early_total == 72, f"Early stage question count mismatch: {_early_total}"


# ══════════════════════════════════════════════════════════════════════════════
# SERIES STAGE — 148 questions
# stage_threshold: "all" | "seed" | "series_a" | "series_b"
# ══════════════════════════════════════════════════════════════════════════════

SERIES_STAGE_DOMAINS: List[Dict[str, Any]] = [

    # ── 1. Identity & Stage ── 24 questions ── Lady Kaede ─────────────────────
    {
        "name": "IDENTITY & STAGE",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "What is the company's core mission and how has it evolved since founding?", "stage_threshold": "all"},
            {"text": "What stage of funding is the company seeking and at what valuation?", "stage_threshold": "all"},
            {"text": "What is the founding story and what insight unlocked the opportunity?", "stage_threshold": "all"},
            {"text": "How does the company define its primary and secondary markets?", "stage_threshold": "all"},
            {"text": "Has the company's thesis changed materially since the last funding round?", "stage_threshold": "all"},
            {"text": "What is the company's current TRL and product maturity level?", "stage_threshold": "all"},
            {"text": "What is the company's north star metric?", "stage_threshold": "all"},
            {"text": "How does the company articulate its category and position within it?", "stage_threshold": "all"},
            {"text": "What assumptions have been invalidated through trading and how was that handled?", "stage_threshold": "seed"},
            {"text": "Has the company achieved product-market fit and how is that defined?", "stage_threshold": "seed"},
            {"text": "What is the company's stated path to market leadership in its category?", "stage_threshold": "seed"},
            {"text": "What is the company's exit thesis — IPO, strategic acquisition, or other?", "stage_threshold": "series_a"},
            {"text": "How has the company positioned itself relative to category leaders?", "stage_threshold": "series_a"},
            {"text": "What comparable companies have been acquired or gone public in this space?", "stage_threshold": "series_a"},
            {"text": "What is the company's international expansion narrative?", "stage_threshold": "series_a"},
            {"text": "Has the company retained its founding culture through scale?", "stage_threshold": "series_a"},
            {"text": "What is the company's M&A strategy — acquirer or target?", "stage_threshold": "series_b"},
            {"text": "Has the company identified specific acquisition targets to accelerate growth?", "stage_threshold": "series_b"},
            {"text": "What is the revenue run rate and growth trajectory over the last four quarters?", "stage_threshold": "series_b"},
            {"text": "How does the company's unit economics compare to public market peers?", "stage_threshold": "series_b"},
            {"text": "What is the company's investor relations and board governance structure?", "stage_threshold": "series_b"},
            {"text": "Has the company stress-tested its business model in a downturn scenario?", "stage_threshold": "series_b"},
            {"text": "What is the company's ESG or impact narrative for institutional investors?", "stage_threshold": "series_b"},
            {"text": "Is the company on a credible path to profitability within the next 24 months?", "stage_threshold": "series_b"},
        ]
    },

    # ── 2. Technology & Innovation ── 22 questions ── Lord Reyoku ─────────────
    {
        "name": "TECHNOLOGY & INNOVATION",
        "agent": "Lord Reyoku",
        "questions": [
            {"text": "What is the core technology or methodology underpinning the solution?", "stage_threshold": "all"},
            {"text": "What makes the technical approach defensible against well-resourced competitors?", "stage_threshold": "all"},
            {"text": "What is the current state of the IP portfolio and freedom to operate?", "stage_threshold": "all"},
            {"text": "What are the key technical risks remaining at this stage?", "stage_threshold": "all"},
            {"text": "What is the product roadmap for the next 18 months?", "stage_threshold": "all"},
            {"text": "How does the company manage technical debt as it scales?", "stage_threshold": "seed"},
            {"text": "What is the architecture decision that would be hardest to undo?", "stage_threshold": "seed"},
            {"text": "Has the product achieved meaningful uptime and reliability at current scale?", "stage_threshold": "seed"},
            {"text": "What is the data strategy — how is proprietary data generated and protected?", "stage_threshold": "seed"},
            {"text": "Has the company filed or been granted any patents?", "stage_threshold": "seed"},
            {"text": "What third-party technology dependencies create concentration risk?", "stage_threshold": "seed"},
            {"text": "What is the company's AI or machine learning strategy and current capability?", "stage_threshold": "series_a"},
            {"text": "How does the technology scale — what are the bottlenecks at 10x current volume?", "stage_threshold": "series_a"},
            {"text": "What is the engineering team size and velocity relative to the roadmap?", "stage_threshold": "series_a"},
            {"text": "Has the company passed any third-party security or penetration audits?", "stage_threshold": "series_a"},
            {"text": "What is the company's approach to regulatory technology compliance at scale?", "stage_threshold": "series_a"},
            {"text": "Has a technical due diligence audit been conducted by a credible third party?", "stage_threshold": "series_b"},
            {"text": "What is the company's technology licensing or platform strategy?", "stage_threshold": "series_b"},
            {"text": "How does the company's R&D spend compare to revenue and to competitors?", "stage_threshold": "series_b"},
            {"text": "Is the core technology proprietary enough to withstand open-source competition?", "stage_threshold": "series_b"},
            {"text": "What is the company's approach to AI safety, bias, or explainability?", "stage_threshold": "series_b"},
            {"text": "Has the company experienced any significant technical incidents and how were they handled?", "stage_threshold": "series_b"},
        ]
    },

    # ── 3. Jurisdiction & Regulation ── 18 questions ── Shingen Iron Wolf ──────
    {
        "name": "JURISDICTION & REGULATION",
        "agent": "Shingen Iron Wolf",
        "questions": [
            {"text": "In which jurisdictions is the company currently operating and selling?", "stage_threshold": "all"},
            {"text": "What sector-specific regulatory approvals are required and what is the status?", "stage_threshold": "all"},
            {"text": "How does the company handle cross-border data transfer and localisation?", "stage_threshold": "all"},
            {"text": "Has the company received any regulatory notices, fines, or investigations?", "stage_threshold": "all"},
            {"text": "What is the regulatory risk if primary-market rules change?", "stage_threshold": "all"},
            {"text": "Does the company have dedicated legal counsel for regulatory matters?", "stage_threshold": "seed"},
            {"text": "What is the company's GDPR or equivalent data protection compliance posture?", "stage_threshold": "seed"},
            {"text": "Are there export controls or trade restrictions on the company's technology?", "stage_threshold": "seed"},
            {"text": "Has the company engaged proactively with regulators or a regulatory sandbox?", "stage_threshold": "seed"},
            {"text": "What is the company's insurance coverage for regulatory and legal risk?", "stage_threshold": "seed"},
            {"text": "Does the company have a compliance function or designated compliance officer?", "stage_threshold": "series_a"},
            {"text": "What is the company's anti-money-laundering and KYC posture if applicable?", "stage_threshold": "series_a"},
            {"text": "Has the company conducted a legal review of its terms of service and privacy policy?", "stage_threshold": "series_a"},
            {"text": "What are the regulatory barriers to entry in planned expansion markets?", "stage_threshold": "series_a"},
            {"text": "Does the company have a government relations or public affairs function?", "stage_threshold": "series_b"},
            {"text": "Has the company been subject to any competition authority scrutiny?", "stage_threshold": "series_b"},
            {"text": "What is the company's strategy for navigating AI regulation as it evolves?", "stage_threshold": "series_b"},
            {"text": "Are there any pending legal disputes that could materially affect the business?", "stage_threshold": "series_b"},
        ]
    },

    # ── 4. Capital & Business Model ── 28 questions ── Lord Renji ─────────────
    {
        "name": "CAPITAL & BUSINESS MODEL",
        "agent": "Lord Renji",
        "questions": [
            {"text": "What is the current revenue model and how does the company charge customers?", "stage_threshold": "all"},
            {"text": "What is the current monthly recurring revenue and growth rate?", "stage_threshold": "all"},
            {"text": "What is the monthly burn rate and current runway?", "stage_threshold": "all"},
            {"text": "What is the fundraising ask and use of proceeds?", "stage_threshold": "all"},
            {"text": "What are the gross margins and how do they compare to industry benchmarks?", "stage_threshold": "all"},
            {"text": "What is the customer acquisition cost and how has it trended?", "stage_threshold": "all"},
            {"text": "What is the average contract value or revenue per customer?", "stage_threshold": "all"},
            {"text": "What is the net revenue retention rate?", "stage_threshold": "seed"},
            {"text": "What is the customer lifetime value and LTV:CAC ratio?", "stage_threshold": "seed"},
            {"text": "How diversified is the revenue base — what is the top customer concentration?", "stage_threshold": "seed"},
            {"text": "What is the payback period on customer acquisition?", "stage_threshold": "seed"},
            {"text": "Are there any revenue quality issues — discounts, one-off deals, or deferred revenue?", "stage_threshold": "seed"},
            {"text": "Has the company modelled the full path to profitability?", "stage_threshold": "seed"},
            {"text": "What is the cap table and are there any preference stack issues?", "stage_threshold": "seed"},
            {"text": "What milestones will this round fund to reach the next capital event?", "stage_threshold": "seed"},
            {"text": "What is the company's annual recurring revenue and ARR growth rate year-on-year?", "stage_threshold": "series_a"},
            {"text": "How does the company's rule of 40 score compare to category peers?", "stage_threshold": "series_a"},
            {"text": "What is the churn rate by cohort and how has it trended?", "stage_threshold": "series_a"},
            {"text": "Has the company achieved contribution margin positivity?", "stage_threshold": "series_a"},
            {"text": "What is the company's approach to multi-year contracts and prepaid revenue?", "stage_threshold": "series_a"},
            {"text": "What secondary revenue streams or upsell opportunities have been validated?", "stage_threshold": "series_a"},
            {"text": "What is the company's EBITDA margin and target for the next 24 months?", "stage_threshold": "series_b"},
            {"text": "Has the company stress-tested its unit economics in a demand contraction?", "stage_threshold": "series_b"},
            {"text": "What is the company's capital efficiency relative to comparable public companies?", "stage_threshold": "series_b"},
            {"text": "Does the company have a credit facility or debt financing in place?", "stage_threshold": "series_b"},
            {"text": "What is the weighted average cost of capital and target capital structure?", "stage_threshold": "series_b"},
            {"text": "Are there any off-balance-sheet liabilities or contingent obligations?", "stage_threshold": "series_b"},
            {"text": "What is the company's dividend or capital return policy post-IPO?", "stage_threshold": "series_b"},
        ]
    },

    # ── 5. Market & Competition ── 32 questions ── Lady Asami ─────────────────
    {
        "name": "MARKET & COMPETITION",
        "agent": "Lady Asami",
        "questions": [
            {"text": "What is the total addressable market size and how is it calculated?", "stage_threshold": "all"},
            {"text": "Who are the top five direct competitors and how does the company differentiate?", "stage_threshold": "all"},
            {"text": "What is the serviceable addressable market the company can realistically reach?", "stage_threshold": "all"},
            {"text": "What is the company's go-to-market motion — direct, channel, or PLG?", "stage_threshold": "all"},
            {"text": "What is the company's core positioning statement?", "stage_threshold": "all"},
            {"text": "What is the competitive moat and how durable is it?", "stage_threshold": "all"},
            {"text": "How does the company win deals — what is the primary buying trigger?", "stage_threshold": "seed"},
            {"text": "What is the average sales cycle length and how does it vary by customer size?", "stage_threshold": "seed"},
            {"text": "What is the win rate against named competitors?", "stage_threshold": "seed"},
            {"text": "Has the company lost a significant customer and why?", "stage_threshold": "seed"},
            {"text": "What is the current pipeline volume and conversion rate?", "stage_threshold": "seed"},
            {"text": "What percentage of revenue comes from inbound vs. outbound?", "stage_threshold": "seed"},
            {"text": "What market signals suggest the category is growing?", "stage_threshold": "seed"},
            {"text": "Are there adjacent markets the company plans to enter and when?", "stage_threshold": "seed"},
            {"text": "What is the net promoter score or equivalent customer satisfaction measure?", "stage_threshold": "seed"},
            {"text": "What is the company's pricing power — can it raise prices without losing customers?", "stage_threshold": "series_a"},
            {"text": "What is the company's account expansion motion and land-and-expand strategy?", "stage_threshold": "series_a"},
            {"text": "Has the company entered international markets and what is the international revenue share?", "stage_threshold": "series_a"},
            {"text": "What is the company's partner or channel ecosystem strategy?", "stage_threshold": "series_a"},
            {"text": "How has the competitive landscape changed in the last 12 months?", "stage_threshold": "series_a"},
            {"text": "Is there evidence of category consolidation that the company should lead or respond to?", "stage_threshold": "series_a"},
            {"text": "What is the company's analyst and market perception — Gartner, Forrester, or equivalent?", "stage_threshold": "series_a"},
            {"text": "What is the company's share of voice in its category?", "stage_threshold": "series_a"},
            {"text": "Has the company identified a beachhead segment it dominates?", "stage_threshold": "series_a"},
            {"text": "What is the company's market share in its primary segment?", "stage_threshold": "series_b"},
            {"text": "Has the company been recognised by Gartner Magic Quadrant or equivalent ranking?", "stage_threshold": "series_b"},
            {"text": "What is the company's strategy to defend against a well-funded new entrant?", "stage_threshold": "series_b"},
            {"text": "Has the company stress-tested its go-to-market in a demand downturn?", "stage_threshold": "series_b"},
            {"text": "What is the company's pricing model evolution over the last 24 months?", "stage_threshold": "series_b"},
            {"text": "What is the company's net revenue retention compared to best-in-class peers?", "stage_threshold": "series_b"},
            {"text": "Does the company have platform or ecosystem lock-in that raises switching costs?", "stage_threshold": "series_b"},
            {"text": "What is the company's strategy for markets where competitors are entrenched?", "stage_threshold": "series_b"},
        ]
    },

    # ── 6. Team & Credibility ── 24 questions ── Lady Kaede ───────────────────
    {
        "name": "TEAM & CREDIBILITY",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "Who are the founders and what are their domain-relevant backgrounds?", "stage_threshold": "all"},
            {"text": "Does the leadership team have the skills to take the company to the next stage?", "stage_threshold": "all"},
            {"text": "What is the total headcount and how is the team structured?", "stage_threshold": "all"},
            {"text": "What key leadership roles are open and what is the hiring plan?", "stage_threshold": "all"},
            {"text": "Has any founder previously built, scaled, or exited a company?", "stage_threshold": "all"},
            {"text": "What is the employee retention rate and what drives attrition?", "stage_threshold": "seed"},
            {"text": "Does the company have a credible board with relevant experience?", "stage_threshold": "seed"},
            {"text": "Are there any gaps in the leadership team that represent execution risk?", "stage_threshold": "seed"},
            {"text": "What is the equity ownership structure across founders, employees, and investors?", "stage_threshold": "seed"},
            {"text": "What is the employee option pool size and vesting schedule?", "stage_threshold": "seed"},
            {"text": "How does the leadership team handle strategic disagreements?", "stage_threshold": "seed"},
            {"text": "Has the company made any executive hires that have not worked out and why?", "stage_threshold": "seed"},
            {"text": "Does the CEO have the profile to raise a Series A or beyond?", "stage_threshold": "series_a"},
            {"text": "Has the company hired a CFO or VP Finance with relevant scale experience?", "stage_threshold": "series_a"},
            {"text": "What is the company's approach to culture as it scales past 50 employees?", "stage_threshold": "series_a"},
            {"text": "Has the board been refreshed with independent directors who can challenge management?", "stage_threshold": "series_a"},
            {"text": "Does the company have a credible Chief Revenue Officer or equivalent?", "stage_threshold": "series_a"},
            {"text": "What is the Glassdoor or equivalent employer rating and trend?", "stage_threshold": "series_a"},
            {"text": "Has the company built a leadership bench — can any C-level be back-filled quickly?", "stage_threshold": "series_b"},
            {"text": "Has the company hired a General Counsel or Head of Legal with IPO experience?", "stage_threshold": "series_b"},
            {"text": "What is the board composition and does it meet institutional governance standards?", "stage_threshold": "series_b"},
            {"text": "Has the CEO articulated a credible personal vision for the company at scale?", "stage_threshold": "series_b"},
            {"text": "What is the company's succession plan for the CEO role?", "stage_threshold": "series_b"},
            {"text": "Has the management team been stress-tested through a significant operational crisis?", "stage_threshold": "series_b"},
        ]
    },
]

# Validate count
_series_total = sum(len(d["questions"]) for d in SERIES_STAGE_DOMAINS)
assert _series_total == 148, f"Series stage question count mismatch: {_series_total}"


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def get_domain_set(company_stage_selection: str) -> List[Dict[str, Any]]:
    """
    Return the appropriate domain question set.

    Args:
        company_stage_selection: "early_stage" or "series_stage"

    Returns:
        List of domain dicts with "name", "agent", and "questions" keys.
        Defaults to SERIES_STAGE_DOMAINS for unrecognised values.
    """
    if company_stage_selection == "early_stage":
        return EARLY_STAGE_DOMAINS
    return SERIES_STAGE_DOMAINS
