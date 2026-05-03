"""
TaoWAR Deep DD Question Sets
Two sets managed here — select based on company_stage_selection field:
  - "early_stage"  → EARLY_STAGE_DOMAINS  (~80 questions)
  - "series_stage" → SERIES_STAGE_DOMAINS (148 questions)

Usage in run_dd:
    if company_stage_selection == "early_stage":
        DOMAINS = EARLY_STAGE_DOMAINS
    else:
        DOMAINS = SERIES_STAGE_DOMAINS
"""

# ── EARLY STAGE QUESTION SET ─────────────────────────────────────────────────
# ~80 questions calibrated for Grant · Accelerator · Friends & Family ·
# Pre-Seed · Crowdfunding · Seed stage companies.
# All questions use stage_threshold: "all" — they are already calibrated
# for this stage. Absence of revenue or traction is expected not penalised.
# Potential framing is the primary output for unanswered questions.

EARLY_STAGE_DOMAINS = [
    {
        "name": "IDENTITY & STAGE",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "What stage does this company actually demonstrate versus what it claims?", "stage_threshold": "all"},
            {"text": "Can the founder describe what this company does in one sentence a stranger finds specific?", "stage_threshold": "all"},
            {"text": "What is the founding date and current incorporation status?", "stage_threshold": "all"},
            {"text": "Is the product live in any form or still entirely pre-product?", "stage_threshold": "all"},
            {"text": "Has the company changed direction since founding and was it driven by evidence?", "stage_threshold": "all"},
            {"text": "What has the team actually built shipped or closed in the last 90 days?", "stage_threshold": "all"},
            {"text": "Is the public presence consistent with the stage claim?", "stage_threshold": "all"},
            {"text": "Has the company defined a clear use of funds for this raise?", "stage_threshold": "all"},
            {"text": "What IP does the company own or has begun to protect?", "stage_threshold": "all"},
            {"text": "Is there a cap table and is equity split defensible?", "stage_threshold": "all"},
            {"text": "Has the company defined its go-to-market motion even at a basic level?", "stage_threshold": "all"},
            {"text": "Is the seed document internally consistent on stage claims?", "stage_threshold": "all"},
            {"text": "What is the single most important milestone this raise needs to achieve?", "stage_threshold": "all"},
        ]
    },
    {
        "name": "TECHNOLOGY & INNOVATION",
        "agent": "Lord Reyoku",
        "questions": [
            {"text": "What is the hardest unsolved technical problem between here and a working product?", "stage_threshold": "all"},
            {"text": "What has been demonstrated in any environment versus what is promised?", "stage_threshold": "all"},
            {"text": "Is the core idea genuinely novel or a recombination of existing solutions?", "stage_threshold": "all"},
            {"text": "Does the product require the technical architecture it uses or is it cosmetic?", "stage_threshold": "all"},
            {"text": "What is the current TRL and is that claim honest?", "stage_threshold": "all"},
            {"text": "Has all IP been formally assigned from every founder and contributor?", "stage_threshold": "all"},
            {"text": "Is there a clear technology development roadmap with honest milestones?", "stage_threshold": "all"},
            {"text": "Does the team have the specific expertise to solve what technically remains?", "stage_threshold": "all"},
            {"text": "Is there a Zero to One test this technology passes?", "stage_threshold": "all"},
            {"text": "What would stop a well-resourced competitor from replicating this in 18 months?", "stage_threshold": "all"},
            {"text": "Is there a data strategy even at a basic level?", "stage_threshold": "all"},
        ]
    },
    {
        "name": "JURISDICTION & REGULATION",
        "agent": "Shingen Iron Wolf",
        "questions": [
            {"text": "Does the founder know what regulatory classification applies to their product?", "stage_threshold": "all"},
            {"text": "Could the product be classified as a collective investment scheme?", "stage_threshold": "all"},
            {"text": "Is the company subject to AML or KYC obligations and does the founder know this?", "stage_threshold": "all"},
            {"text": "Has the founder spoken to any legal counsel about the regulatory pathway?", "stage_threshold": "all"},
            {"text": "What is the VASP classification status if blockchain or tokens are involved?", "stage_threshold": "all"},
            {"text": "Is there an ongoing or threatened regulatory investigation or legal dispute?", "stage_threshold": "all"},
            {"text": "What consumer protection obligations apply and has the founder identified them?", "stage_threshold": "all"},
            {"text": "Has the company engaged with any relevant regulator or sandbox programme?", "stage_threshold": "all"},
            {"text": "What happens to the business model if the primary regulatory assumption is wrong?", "stage_threshold": "all"},
        ]
    },
    {
        "name": "CAPITAL & BUSINESS MODEL",
        "agent": "Lord Renji",
        "questions": [
            {"text": "What is the primary business model and is there a plausible path to revenue?", "stage_threshold": "all"},
            {"text": "What specific milestone does this raise need to reach to justify the next conversation with capital?", "stage_threshold": "all"},
            {"text": "Is the funding ask right-sized for the milestone it needs to fund?", "stage_threshold": "all"},
            {"text": "Does the use of funds reflect actual priorities at this stage?", "stage_threshold": "all"},
            {"text": "What happens to the business if the primary revenue assumption is wrong by 50 percent?", "stage_threshold": "all"},
            {"text": "Is there any early evidence of willingness to pay from a specific named person?", "stage_threshold": "all"},
            {"text": "What are the top three cost drivers and are they understood?", "stage_threshold": "all"},
            {"text": "Is there a plausible path to not needing continuous external capital?", "stage_threshold": "all"},
            {"text": "What revenue streams are planned and which is primary?", "stage_threshold": "all"},
            {"text": "Has the company modelled what happens in a downside scenario?", "stage_threshold": "all"},
            {"text": "Is there a three year financial projection with clearly stated assumptions?", "stage_threshold": "all"},
            {"text": "What is the current bank balance and monthly burn rate?", "stage_threshold": "all"},
            {"text": "How many months of runway does the company have at current burn?", "stage_threshold": "all"},
        ]
    },
    {
        "name": "MARKET & COMPETITION",
        "agent": "Lady Asami",
        "questions": [
            {"text": "Is the target market real and is the founder in contact with people who have the problem?", "stage_threshold": "all"},
            {"text": "What are customers doing instead of using this product right now?", "stage_threshold": "all"},
            {"text": "What does this company understand about its market that competitors do not?", "stage_threshold": "all"},
            {"text": "What specific structural shift makes this the right moment for this product?", "stage_threshold": "all"},
            {"text": "Who are the direct competitors and what is their current status?", "stage_threshold": "all"},
            {"text": "Who are the indirect competitors that could enter this space quickly?", "stage_threshold": "all"},
            {"text": "Has the founder validated market size with any primary research?", "stage_threshold": "all"},
            {"text": "Has the company identified its beachhead market precisely?", "stage_threshold": "all"},
            {"text": "What barriers to entry does the company create over time?", "stage_threshold": "all"},
            {"text": "Are there network effects that would compound the competitive moat?", "stage_threshold": "all"},
            {"text": "Has the company defined its ideal customer profile at even a basic level?", "stage_threshold": "all"},
            {"text": "Has the company identified any regulatory tailwinds or headwinds?", "stage_threshold": "all"},
            {"text": "Is there any early evidence of organic word-of-mouth interest?", "stage_threshold": "all"},
        ]
    },
    {
        "name": "TEAM & CREDIBILITY",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "What specifically in each founder history makes them the right person for this problem?", "stage_threshold": "all"},
            {"text": "Has the full founding team worked or studied together before?", "stage_threshold": "all"},
            {"text": "Is the entire founding team working full-time and if not what are the barriers?", "stage_threshold": "all"},
            {"text": "What is the single biggest team gap and what is the plan to fill it?", "stage_threshold": "all"},
            {"text": "Have any co-founders departed and what were the circumstances?", "stage_threshold": "all"},
            {"text": "Is there evidence of founder-market fit beyond passion or interest?", "stage_threshold": "all"},
            {"text": "How does the team make decisions when there is genuine disagreement?", "stage_threshold": "all"},
            {"text": "What has the team built or accomplished in the last 90 days not on the original roadmap?", "stage_threshold": "all"},
            {"text": "What advisors are named and what have they specifically done in the last 90 days?", "stage_threshold": "all"},
            {"text": "Are there any legal disputes or civil matters involving founders personally?", "stage_threshold": "all"},
            {"text": "What did the founders do with their pre-funding time that signals genuine commitment?", "stage_threshold": "all"},
            {"text": "Has the team demonstrated coachability — have they changed something important based on feedback?", "stage_threshold": "all"},
            {"text": "What references are available for the founding team?", "stage_threshold": "all"},
        ]
    }
]


# ── SERIES STAGE QUESTION SET ────────────────────────────────────────────────
# 148 questions calibrated for Series A · Series B · Series C companies.
# Uses stage_threshold to classify questions appropriately per stage.

SERIES_STAGE_DOMAINS = [
    {
        "name": "IDENTITY & STAGE",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "What specific milestone triggers the next funding round?", "stage_threshold": "all"},
            {"text": "Is the one-line description defensible under scrutiny?", "stage_threshold": "all"},
            {"text": "What is the current TRL and what evidence supports it?", "stage_threshold": "all"},
            {"text": "Has the company defined its stage claim with precision?", "stage_threshold": "all"},
            {"text": "What is the founding date and incorporation status?", "stage_threshold": "all"},
            {"text": "Is there a clear pre-product or post-product distinction?", "stage_threshold": "all"},
            {"text": "What is the team size and headcount breakdown?", "stage_threshold": "all"},
            {"text": "Has the company achieved any revenue or paying customers?", "stage_threshold": "seed"},
            {"text": "What is the current funding status and round history?", "stage_threshold": "all"},
            {"text": "Is the product live or still in development?", "stage_threshold": "all"},
            {"text": "What is the company legal entity and jurisdiction?", "stage_threshold": "all"},
            {"text": "Has the company defined its use of funds clearly?", "stage_threshold": "all"},
            {"text": "What IP does the company own or license?", "stage_threshold": "all"},
            {"text": "Are PIIA agreements in place for all founders and staff?", "stage_threshold": "seed"},
            {"text": "Has a cap table been disclosed with full UBO visibility?", "stage_threshold": "seed"},
            {"text": "Are there any outstanding convertible instruments?", "stage_threshold": "seed"},
            {"text": "What vesting schedule is in place for founders?", "stage_threshold": "seed"},
            {"text": "Has the company defined a clear exit strategy?", "stage_threshold": "series_a"},
            {"text": "What governance structure is in place?", "stage_threshold": "seed"},
            {"text": "Is there a board of directors or advisors named?", "stage_threshold": "seed"},
            {"text": "What is the company burn rate and runway?", "stage_threshold": "seed"},
            {"text": "Has the company defined its go-to-market motion?", "stage_threshold": "all"},
            {"text": "What is the customer acquisition cost at current stage?", "stage_threshold": "seed"},
            {"text": "Is the seed document internally consistent on stage claims?", "stage_threshold": "all"}
        ]
    },
    {
        "name": "TECHNOLOGY & INNOVATION",
        "agent": "Lord Reyoku",
        "questions": [
            {"text": "What is the hardest unsolved technical problem?", "stage_threshold": "all"},
            {"text": "Does a clear technology development roadmap exist?", "stage_threshold": "all"},
            {"text": "What has been demonstrated versus what is promised?", "stage_threshold": "all"},
            {"text": "Is the core technology genuinely novel or recombinant?", "stage_threshold": "all"},
            {"text": "What is the replication timeline for a well-funded competitor?", "stage_threshold": "all"},
            {"text": "Has a third-party technical audit been conducted?", "stage_threshold": "seed"},
            {"text": "What patents are filed granted or pending?", "stage_threshold": "seed"},
            {"text": "What is the smart contract audit status if applicable?", "stage_threshold": "seed"},
            {"text": "Is there a clear data strategy and data moat?", "stage_threshold": "all"},
            {"text": "What open source dependencies create risk?", "stage_threshold": "seed"},
            {"text": "Has the technology been tested in a production environment?", "stage_threshold": "seed"},
            {"text": "What is the scalability ceiling of the current architecture?", "stage_threshold": "seed"},
            {"text": "Is there a Zero to One test that this technology passes?", "stage_threshold": "all"},
            {"text": "What technical debt exists in the current codebase?", "stage_threshold": "seed"},
            {"text": "Has the company defined its build versus buy strategy?", "stage_threshold": "seed"},
            {"text": "What cybersecurity posture has been documented?", "stage_threshold": "series_a"},
            {"text": "Is there a disaster recovery and business continuity plan?", "stage_threshold": "series_a"},
            {"text": "What is the technology dependency on third-party APIs?", "stage_threshold": "seed"},
            {"text": "Has the company defined its data privacy architecture?", "stage_threshold": "series_a"},
            {"text": "What monitoring and observability tooling is in place?", "stage_threshold": "series_a"},
            {"text": "Is there a defined QA and testing framework?", "stage_threshold": "seed"},
            {"text": "What is the current uptime and reliability record?", "stage_threshold": "series_a"}
        ]
    },
    {
        "name": "JURISDICTION & REGULATION",
        "agent": "Shingen Iron Wolf",
        "questions": [
            {"text": "What is the regulatory classification in each target market?", "stage_threshold": "all"},
            {"text": "Could the product be classified as a collective investment scheme?", "stage_threshold": "all"},
            {"text": "Is the company subject to AML and KYC obligations?", "stage_threshold": "all"},
            {"text": "Has a legal opinion been obtained on the regulatory status?", "stage_threshold": "seed"},
            {"text": "What licences are required and which have been obtained?", "stage_threshold": "seed"},
            {"text": "Is there an ongoing or threatened regulatory investigation?", "stage_threshold": "all"},
            {"text": "How does the company handle cross-border data transfer?", "stage_threshold": "series_a"},
            {"text": "What consumer protection obligations apply?", "stage_threshold": "seed"},
            {"text": "Has the company engaged with regulators proactively?", "stage_threshold": "seed"},
            {"text": "What is the VASP classification status if applicable?", "stage_threshold": "all"},
            {"text": "Is the company subject to Basel III or equivalent constraints?", "stage_threshold": "series_a"},
            {"text": "What sanctions screening is in place?", "stage_threshold": "seed"},
            {"text": "Has the company defined its regulatory change management process?", "stage_threshold": "series_a"},
            {"text": "What is the liability exposure in each jurisdiction?", "stage_threshold": "seed"},
            {"text": "Are terms of service and privacy policy legally reviewed?", "stage_threshold": "seed"},
            {"text": "Has the company obtained any regulatory sandbox approval?", "stage_threshold": "seed"},
            {"text": "What is the dispute resolution framework?", "stage_threshold": "series_a"},
            {"text": "Is there a dedicated compliance officer or team?", "stage_threshold": "series_a"}
        ]
    },
    {
        "name": "CAPITAL & BUSINESS MODEL",
        "agent": "Lord Renji",
        "questions": [
            {"text": "What happens if the primary revenue assumption is wrong by 50%?", "stage_threshold": "all"},
            {"text": "Are unit economics at scale documented and credible?", "stage_threshold": "seed"},
            {"text": "What is the current ARR or MRR?", "stage_threshold": "seed"},
            {"text": "What is the contribution margin per customer?", "stage_threshold": "series_a"},
            {"text": "Can the business model survive without continuous external capital?", "stage_threshold": "all"},
            {"text": "What are the top three cost drivers?", "stage_threshold": "all"},
            {"text": "Is there a clear path to profitability without heroic assumptions?", "stage_threshold": "all"},
            {"text": "What is the LTV to CAC ratio at current and projected scale?", "stage_threshold": "series_a"},
            {"text": "Has the company stress-tested the model against regulatory shifts?", "stage_threshold": "seed"},
            {"text": "What revenue streams are direct versus indirect?", "stage_threshold": "all"},
            {"text": "Is pricing strategy documented and validated with customers?", "stage_threshold": "seed"},
            {"text": "What is the gross margin profile at target scale?", "stage_threshold": "seed"},
            {"text": "Has the company defined its Rule of 40 trajectory?", "stage_threshold": "series_a"},
            {"text": "What working capital requirements exist at scale?", "stage_threshold": "series_a"},
            {"text": "Is there a clear fundraising plan with milestone alignment?", "stage_threshold": "all"},
            {"text": "What is the EBITDA trend over the last 12 months?", "stage_threshold": "series_b"},
            {"text": "Has the company defined its capital efficiency metrics?", "stage_threshold": "series_a"},
            {"text": "What debt obligations exist or are planned?", "stage_threshold": "seed"},
            {"text": "Is the funding ask proportionate to the milestones?", "stage_threshold": "all"},
            {"text": "What is the financial model sensitivity to churn?", "stage_threshold": "series_a"},
            {"text": "Has the company modelled a downside scenario?", "stage_threshold": "seed"},
            {"text": "What is the payback period per customer acquired?", "stage_threshold": "series_a"},
            {"text": "Is there a treasury management policy in place?", "stage_threshold": "series_a"},
            {"text": "What is the burn multiple at current revenue?", "stage_threshold": "seed"},
            {"text": "Has the company defined its investor return scenario?", "stage_threshold": "seed"},
            {"text": "What is the net revenue retention rate?", "stage_threshold": "series_a"},
            {"text": "Is there a defined dividend or distribution policy?", "stage_threshold": "series_b"},
            {"text": "What is the break-even timeline under base case?", "stage_threshold": "all"}
        ]
    },
    {
        "name": "MARKET & COMPETITION",
        "agent": "Lady Asami",
        "questions": [
            {"text": "Who are the direct competitors and what is their funding status?", "stage_threshold": "all"},
            {"text": "Who are the indirect competitors that could enter this space?", "stage_threshold": "all"},
            {"text": "Is the market sizing methodology bottom-up or top-down?", "stage_threshold": "all"},
            {"text": "What assumptions underpin the TAM SAM and SOM figures?", "stage_threshold": "all"},
            {"text": "What is the competitive response time if this company succeeds?", "stage_threshold": "all"},
            {"text": "Has the company validated market size with primary research?", "stage_threshold": "all"},
            {"text": "What switching costs exist for customers choosing this product?", "stage_threshold": "seed"},
            {"text": "Is there evidence of product-market fit from early adopters?", "stage_threshold": "seed"},
            {"text": "What is the customer concentration risk?", "stage_threshold": "series_a"},
            {"text": "Has the company defined its market entry sequencing?", "stage_threshold": "all"},
            {"text": "What barriers to entry does the company create over time?", "stage_threshold": "all"},
            {"text": "Is there a documented competitive intelligence process?", "stage_threshold": "series_a"},
            {"text": "What is the net promoter score or equivalent satisfaction metric?", "stage_threshold": "series_a"},
            {"text": "Has the company identified its beachhead market precisely?", "stage_threshold": "all"},
            {"text": "What is the market growth rate and what drives it?", "stage_threshold": "all"},
            {"text": "Are there network effects that compound the competitive moat?", "stage_threshold": "all"},
            {"text": "What is the sales cycle length and what drives it?", "stage_threshold": "seed"},
            {"text": "Has the company mapped the full customer journey?", "stage_threshold": "seed"},
            {"text": "What channel partnerships are in place or planned?", "stage_threshold": "seed"},
            {"text": "Is there a documented land and expand strategy?", "stage_threshold": "series_a"},
            {"text": "What is the average contract value and how does it trend?", "stage_threshold": "series_a"},
            {"text": "Has the company defined its ideal customer profile precisely?", "stage_threshold": "all"},
            {"text": "What is the churn rate and what are the primary churn drivers?", "stage_threshold": "series_a"},
            {"text": "Is there a documented win-loss analysis from sales?", "stage_threshold": "series_a"},
            {"text": "What is the pipeline coverage ratio?", "stage_threshold": "series_a"},
            {"text": "Has the company defined its category creation or entry strategy?", "stage_threshold": "all"},
            {"text": "What is the quota attainment rate of the sales team?", "stage_threshold": "series_b"},
            {"text": "What is the time to first value for a new customer?", "stage_threshold": "series_a"},
            {"text": "Has the company identified regulatory tailwinds or headwinds?", "stage_threshold": "all"},
            {"text": "Is there a documented referral or word-of-mouth growth loop?", "stage_threshold": "seed"},
            {"text": "What is the market concentration fragmented or consolidated?", "stage_threshold": "all"},
            {"text": "Has the company defined its pricing power over time?", "stage_threshold": "seed"}
        ]
    },
    {
        "name": "TEAM & CREDIBILITY",
        "agent": "Lady Kaede",
        "questions": [
            {"text": "Has the full founding team worked together before?", "stage_threshold": "all"},
            {"text": "What is the single biggest team gap and the plan to fill it?", "stage_threshold": "all"},
            {"text": "Do the founders have relevant domain expertise for this sector?", "stage_threshold": "all"},
            {"text": "Have any co-founders departed and under what circumstances?", "stage_threshold": "all"},
            {"text": "What is the equity split and is it defensible?", "stage_threshold": "all"},
            {"text": "Is there evidence of founder-market fit beyond biography?", "stage_threshold": "all"},
            {"text": "What is the combined execution history of the team?", "stage_threshold": "all"},
            {"text": "Are there any conflicts of interest among team members?", "stage_threshold": "all"},
            {"text": "What advisors are named and what is their actual involvement?", "stage_threshold": "all"},
            {"text": "Has the team demonstrated ability to hire and retain talent?", "stage_threshold": "seed"},
            {"text": "What is the leadership style and decision-making framework?", "stage_threshold": "seed"},
            {"text": "Are there any legal disputes involving founders personally?", "stage_threshold": "all"},
            {"text": "What is the team track record on previous commitments?", "stage_threshold": "all"},
            {"text": "Has the company defined its culture and values explicitly?", "stage_threshold": "series_a"},
            {"text": "Is there a succession plan for key person dependency?", "stage_threshold": "series_a"},
            {"text": "What is the team network strength in the target sector?", "stage_threshold": "all"},
            {"text": "Has the company defined its hiring plan for the next 18 months?", "stage_threshold": "seed"},
            {"text": "Are compensation packages market-competitive?", "stage_threshold": "series_a"},
            {"text": "Is there a defined performance management framework?", "stage_threshold": "series_a"},
            {"text": "Has the team demonstrated coachability under pressure?", "stage_threshold": "all"},
            {"text": "What references are available for the founding team?", "stage_threshold": "all"},
            {"text": "Is there a documented onboarding process for new hires?", "stage_threshold": "series_a"},
            {"text": "What is the current employee NPS?", "stage_threshold": "series_b"},
            {"text": "Has the company defined its remote or office working policy?", "stage_threshold": "series_a"}
        ]
    }
]


def get_domain_set(company_stage_selection: str) -> list:
    """
    Returns the appropriate question set based on company stage selection.
    
    Args:
        company_stage_selection: "early_stage" or "series_stage"
    
    Returns:
        List of domain dicts with questions
    """
    if company_stage_selection == "early_stage":
        return EARLY_STAGE_DOMAINS
    return SERIES_STAGE_DOMAINS


def count_questions(domains: list) -> int:
    """Returns total question count for a domain set."""
    return sum(len(d["questions"]) for d in domains)


# Verify counts
if __name__ == "__main__":
    early_count = count_questions(EARLY_STAGE_DOMAINS)
    series_count = count_questions(SERIES_STAGE_DOMAINS)
    print(f"Early stage questions: {early_count}")
    print(f"Series stage questions: {series_count}")
