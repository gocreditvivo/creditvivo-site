from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GrowthDataSource:
    name: str
    category: str
    source_url: str
    what_growth_ai_gets: str
    first_action: str
    compliance_note: str


@dataclass(frozen=True)
class PublicPartnerLead:
    name: str
    partner_type: str
    geography: str
    public_contact: str
    source_url: str
    fit_reason: str
    recommended_campaign: str


@dataclass(frozen=True)
class MarketSignalSource:
    name: str
    category: str
    source_url: str
    demand_signal: str
    allowed_growth_use: str
    blocked_use: str
    recommended_campaign: str


GROWTH_DATA_SOURCES: List[GrowthDataSource] = [
    GrowthDataSource(
        name="Credit Vivo website events",
        category="owned_website",
        source_url="https://www.creditvivo.com",
        what_growth_ai_gets="Visitors, Join Free clicks, pricing views, campaign page visits, scan starts, scan completions.",
        first_action="Track every campaign page and Join Free submission with campaign/source tags.",
        compliance_note="Owned first-party data. Use consent and privacy-policy disclosures.",
    ),
    GrowthDataSource(
        name="Google Search Console",
        category="owned_analytics",
        source_url="https://search.google.com/search-console",
        what_growth_ai_gets="Search queries, pages getting impressions, click-through rate, ranking opportunities.",
        first_action="Connect creditvivo.com and export top credit-error questions weekly.",
        compliance_note="Use only aggregate search data, not private consumer identities.",
    ),
    GrowthDataSource(
        name="Google Analytics 4",
        category="owned_analytics",
        source_url="https://analytics.google.com",
        what_growth_ai_gets="Traffic source, campaign conversion, lead form conversion, page drop-off.",
        first_action="Connect GA4 events for join_clicked, lead_created, scan_started, scan_completed, paid_upgrade.",
        compliance_note="Avoid storing raw sensitive credit details in analytics tools.",
    ),
    GrowthDataSource(
        name="Vercel deployment and web performance",
        category="site_health",
        source_url="https://vercel.com",
        what_growth_ai_gets="Deploy status, site availability, frontend errors, performance signals.",
        first_action="Connect deploy alerts into Operator AI and Growth AI.",
        compliance_note="Operational data only; do not log customer report contents.",
    ),
    GrowthDataSource(
        name="Render scanner API health",
        category="scanner_health",
        source_url="https://render.com",
        what_growth_ai_gets="Scanner backend uptime, health checks, failed deploys, API availability.",
        first_action="Add the Render service URL to the founder dashboard once confirmed.",
        compliance_note="Operational data only; do not expose raw reports in logs.",
    ),
    GrowthDataSource(
        name="HUD approved housing counseling agencies",
        category="public_partner_directory",
        source_url="https://apps.hud.gov/offices/hsg/sfh/hcc/hcs_print.cfm?searchstate=va&weblistaction=search",
        what_growth_ai_gets="Public organizations serving renters, homebuyers, budgeting, credit, and housing counseling.",
        first_action="Build referral-partner outreach for housing counselors and homebuyer education providers.",
        compliance_note="Public business/agency contacts only. Do not scrape private consumer clients.",
    ),
    GrowthDataSource(
        name="211 Virginia housing and finance programs",
        category="public_partner_directory",
        source_url="https://search.211virginia.org/search?query=BH-3700.3200&query_label=HUD+Approved+Counseling+Agencies&query_type=taxonomy",
        what_growth_ai_gets="Community agencies that already help people with rental, housing, credit, and budgeting needs.",
        first_action="Find agency partnership opportunities and education/referral paths.",
        compliance_note="Use organization-level outreach only.",
    ),
    GrowthDataSource(
        name="Virginia Automobile Dealers Association",
        category="public_partner_source",
        source_url="https://vada.com/about/contact-us/",
        what_growth_ai_gets="Dealer association channel for consumers delayed or denied for auto financing.",
        first_action="Pitch Credit Vivo as a no-hard-pull credit check-in resource for dealer customers.",
        compliance_note="Contact association/business contacts, not dealership customers directly.",
    ),
    GrowthDataSource(
        name="Virginia Mortgage Bankers Association",
        category="public_partner_source",
        source_url="https://www.vabankers.org/post/virginia-mortgage-bankers-association",
        what_growth_ai_gets="Mortgage partner channel for applicants who need credit readiness before approval.",
        first_action="Pitch Credit Vivo as a pre-application credit report review resource.",
        compliance_note="Partner outreach only; no direct targeting of declined applicants without opt-in.",
    ),
    GrowthDataSource(
        name="U.S. Trustee approved credit counseling agencies",
        category="public_partner_directory",
        source_url="https://www.justice.gov/ust/list-credit-counseling-agencies-approved-pursuant-11-usc-111",
        what_growth_ai_gets="Approved nonprofit credit counseling organizations by state/district.",
        first_action="Identify compliant education/referral relationships.",
        compliance_note="Use public organization listings; avoid implying government endorsement.",
    ),
    GrowthDataSource(
        name="NFCC nonprofit credit counseling network",
        category="public_partner_directory",
        source_url="https://www.nfcc.org/",
        what_growth_ai_gets="National nonprofit counseling network and consumer education patterns.",
        first_action="Study partner-fit and content topics around debt, counseling, and credit education.",
        compliance_note="Do not copy content; use as market context and partner research.",
    ),
    GrowthDataSource(
        name="FCAA financial counseling association",
        category="public_partner_directory",
        source_url="https://fcaa.org/",
        what_growth_ai_gets="Financial counseling association and member ecosystem.",
        first_action="Research partner categories and possible education alliances.",
        compliance_note="Public organization research only.",
    ),
]


MARKET_SIGNAL_SOURCES: List[MarketSignalSource] = [
    MarketSignalSource(
        name="CFPB Consumer Complaint Database",
        category="government_complaint_data",
        source_url="https://www.consumerfinance.gov/data-research/consumer-complaints/",
        demand_signal="Credit reporting, debt collection, auto loan, mortgage, and credit card complaint trends.",
        allowed_growth_use="Analyze complaint volume by issue, company type, state, and trend to choose content topics and campaign pages.",
        blocked_use="Do not use complaint narratives or any personal details to contact individual consumers.",
        recommended_campaign="/collection-not-mine",
    ),
    MarketSignalSource(
        name="CFPB Consumer Complaint Database API",
        category="government_api",
        source_url="https://cfpb.github.io/api/ccdb/",
        demand_signal="Structured public complaint data that can be filtered by product, issue, state, and date.",
        allowed_growth_use="Build aggregate dashboards for top credit reporting and debt collection issues by state.",
        blocked_use="Do not create individual prospect lists from complaints.",
        recommended_campaign="/collection-not-mine",
    ),
    MarketSignalSource(
        name="BBB credit repair and debt relief research",
        category="business_complaint_research",
        source_url="https://www.bbb.org/all/scamstudies/debt-relief-study/debt-relief-full-study",
        demand_signal="Common consumer complaints about debt relief and credit repair providers, including high fees and poor service.",
        allowed_growth_use="Shape trust messaging, compliance language, and comparison content.",
        blocked_use="Do not scrape complainant names, reviewers, or complaint submitters for outreach.",
        recommended_campaign="/why",
    ),
    MarketSignalSource(
        name="BBB complaint and business directory",
        category="business_directory",
        source_url="https://www.bbb.org/file-a-complaint",
        demand_signal="Businesses, categories, and complaint themes in financial services.",
        allowed_growth_use="Research competitor pain points and identify accredited business partner categories.",
        blocked_use="Do not harvest private complaint submitters or reviewers.",
        recommended_campaign="/why",
    ),
    MarketSignalSource(
        name="Federal Reserve credit card delinquency data",
        category="aggregate_financial_data",
        source_url="https://fred.stlouisfed.org/series/DRCCLACBS",
        demand_signal="National credit card delinquency trends.",
        allowed_growth_use="Use aggregate trend data for content planning and investor dashboards.",
        blocked_use="Cannot identify people behind on credit card payments.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="Federal Reserve charge-off and delinquency rates",
        category="aggregate_financial_data",
        source_url="https://www.federalreserve.gov/releases/chargeoff/",
        demand_signal="Bank loan delinquency and charge-off rates by loan category.",
        allowed_growth_use="Monitor macro demand for credit education, debt, auto, mortgage, and credit card topics.",
        blocked_use="Do not imply Credit Vivo can access private bank delinquency files.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="New York Fed Household Debt and Credit Report",
        category="aggregate_financial_data",
        source_url="https://www.newyorkfed.org/microeconomics/hhdc",
        demand_signal="Household debt, mortgage, auto loan, student loan, and credit card trends.",
        allowed_growth_use="Investor-grade market sizing, content calendar, and state-of-consumer insights.",
        blocked_use="No individual targeting.",
        recommended_campaign="/mortgage-readiness",
    ),
    MarketSignalSource(
        name="Philadelphia Fed large bank credit card and mortgage data",
        category="aggregate_financial_data",
        source_url="https://www.philadelphiafed.org/surveys-and-data/large-bank-credit-card-and-mortgage-data",
        demand_signal="Large bank credit card and mortgage performance trends.",
        allowed_growth_use="Track stress in card and mortgage markets to pick educational campaigns.",
        blocked_use="No individual targeting.",
        recommended_campaign="/mortgage-readiness",
    ),
    MarketSignalSource(
        name="State open data portals",
        category="public_open_data",
        source_url="https://data.ny.gov/",
        demand_signal="State-level public datasets including finance, housing, consumer, business, and public records categories.",
        allowed_growth_use="Use aggregate patterns and public agency directories to find partner channels.",
        blocked_use="Do not target people because they appear in sensitive debt, judgment, or tax-delinquency records.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="NYC Open Data tax lien sale lists",
        category="public_record_high_sensitivity",
        source_url="https://data.cityofnewyork.us/City-Government/Tax-Lien-Sale-Lists/9rz4-mjek",
        demand_signal="Property tax lien stress by property and geography.",
        allowed_growth_use="Use only aggregate geographic trends and partner outreach to housing counselors, attorneys, and nonprofits.",
        blocked_use="Do not contact named property owners or households because they owe taxes.",
        recommended_campaign="/mortgage-readiness",
    ),
    MarketSignalSource(
        name="State court judgment and collection records",
        category="public_record_high_sensitivity",
        source_url="state and county court portals",
        demand_signal="Collection judgment and civil debt trends.",
        allowed_growth_use="Use aggregate trend analysis and partner/referral strategy with legal aid, consumer attorneys, and nonprofits.",
        blocked_use="Do not build a direct marketing list of defendants, debtors, or people with judgments.",
        recommended_campaign="/collection-not-mine",
    ),
    MarketSignalSource(
        name="County tax delinquency and property tax sites",
        category="public_record_high_sensitivity",
        source_url="county treasurer, tax collector, and assessor portals",
        demand_signal="Local property tax stress and homeownership hardship patterns.",
        allowed_growth_use="Use only aggregate location-level trends and referral partnerships with housing counselors.",
        blocked_use="Do not contact named taxpayers or households because they owe taxes.",
        recommended_campaign="/mortgage-readiness",
    ),
    MarketSignalSource(
        name="Credit forums, Reddit, car forums, and mortgage forums",
        category="public_discussion_research",
        source_url="public forum search and platform APIs where permitted",
        demand_signal="Questions people ask about denials, collections, credit cards, auto loans, mortgages, and bureau errors.",
        allowed_growth_use="Summarize themes, keywords, objections, and content ideas; post helpful content only where rules allow.",
        blocked_use="Do not scrape usernames, private messages, emails, or target individuals based on hardship posts.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="Credit card comparison and issuer sites",
        category="market_research",
        source_url="public credit card product pages and comparison pages",
        demand_signal="Approval requirements, secured-card demand, credit-building language, and denied-applicant questions.",
        allowed_growth_use="Create education content for people comparing cards or rebuilding credit.",
        blocked_use="Do not imply Credit Vivo can guarantee approval or access issuer private decline data.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="Equifax, Experian, and TransUnion public education pages",
        category="bureau_public_research",
        source_url="public bureau education and dispute pages",
        demand_signal="Official consumer language around reports, disputes, fraud, freezes, and rights.",
        allowed_growth_use="Use as reference points for plain-English education and customer journey design.",
        blocked_use="Do not copy protected content or imply bureau partnership without an agreement.",
        recommended_campaign="/learning",
    ),
    MarketSignalSource(
        name="Google, Bing, Yahoo, and other search engines",
        category="search_demand",
        source_url="search trends, search console, keyword tools, and ad platforms",
        demand_signal="Search volume for auto loan denial, credit report errors, collections, apartment denial, and mortgage readiness.",
        allowed_growth_use="Build SEO pages, paid search campaigns, and landing pages for opt-in visitors.",
        blocked_use="Do not use search ads that overpromise, shame, or target sensitive hardship in a manipulative way.",
        recommended_campaign="/auto-loan-denial",
    ),
]


PUBLIC_PARTNER_LEADS: List[PublicPartnerLead] = [
    PublicPartnerLead(
        name="Virginia Automobile Dealers Association",
        partner_type="Auto dealer association",
        geography="Virginia",
        public_contact="TeamVADA@vada.com",
        source_url="https://vada.com/about/contact-us/",
        fit_reason="Dealer customers may be denied, delayed, or quoted high APRs because of credit report issues.",
        recommended_campaign="/auto-loan-denial",
    ),
    PublicPartnerLead(
        name="Virginia Independent Automobile Dealers Association",
        partner_type="Independent auto dealer association",
        geography="Virginia",
        public_contact="dmv@viada.org",
        source_url="https://viada.org/",
        fit_reason="Independent dealers often serve buyers who may need credit readiness before financing.",
        recommended_campaign="/auto-loan-denial",
    ),
    PublicPartnerLead(
        name="Virginia Mortgage Bankers Association",
        partner_type="Mortgage association",
        geography="Virginia",
        public_contact="info@virginiamba.org",
        source_url="https://www.vabankers.org/post/virginia-mortgage-bankers-association",
        fit_reason="Mortgage applicants may need report review before qualification or underwriting.",
        recommended_campaign="/mortgage-readiness",
    ),
    PublicPartnerLead(
        name="Prince William County Housing Counseling",
        partner_type="Housing counseling agency",
        geography="Virginia",
        public_contact="housingcounseling@pwcgov.org",
        source_url="https://www.pwcva.gov/department/virginia-cooperative-extension/housing-support",
        fit_reason="Housing counseling clients may need credit report education before renting or buying.",
        recommended_campaign="/apartment-denial",
    ),
    PublicPartnerLead(
        name="People Incorporated of Virginia",
        partner_type="HUD approved housing counseling agency",
        geography="Virginia",
        public_contact="info@peopleinc.net",
        source_url="https://apps.hud.gov/offices/hsg/sfh/hcc/hcs_print.cfm?searchstate=va&weblistaction=search",
        fit_reason="Offers financial management and housing counseling, making it a natural education/referral partner.",
        recommended_campaign="/mortgage-readiness",
    ),
    PublicPartnerLead(
        name="Telamon Corporation - Danville Branch",
        partner_type="HUD approved housing counseling agency",
        geography="Virginia",
        public_contact="housing@telamon.org",
        source_url="https://apps.hud.gov/offices/hsg/sfh/hcc/hcs_print.cfm?searchstate=va&weblistaction=search",
        fit_reason="Provides financial, budgeting, credit, and homebuyer education services.",
        recommended_campaign="/mortgage-readiness",
    ),
    PublicPartnerLead(
        name="Appalachian Community Action & Development Agency",
        partner_type="HUD approved housing counseling agency",
        geography="Virginia",
        public_contact="rrobinette@appcaa.org",
        source_url="https://apps.hud.gov/offices/hsg/sfh/hcc/hcs_print.cfm?searchstate=va&weblistaction=search",
        fit_reason="Works with mortgage default, prepurchase counseling, and housing readiness.",
        recommended_campaign="/mortgage-readiness",
    ),
    PublicPartnerLead(
        name="Mortgage Bankers Association",
        partner_type="National mortgage association",
        geography="United States",
        public_contact="contact form / main office",
        source_url="https://www.mba.org/contact-us",
        fit_reason="National mortgage ecosystem can surface credit readiness partnership opportunities.",
        recommended_campaign="/mortgage-readiness",
    ),
    PublicPartnerLead(
        name="National Foundation for Credit Counseling",
        partner_type="Credit counseling network",
        geography="United States",
        public_contact="public contact channels",
        source_url="https://www.nfcc.org/",
        fit_reason="National counseling network shows high-fit education and referral ecosystem.",
        recommended_campaign="/collection-not-mine",
    ),
    PublicPartnerLead(
        name="Financial Counseling Association of America",
        partner_type="Financial counseling association",
        geography="United States",
        public_contact="public contact channels",
        source_url="https://fcaa.org/",
        fit_reason="Association ecosystem overlaps with budgeting, debt, credit education, and consumer support.",
        recommended_campaign="/collection-not-mine",
    ),
]


def data_source_to_dict(source: GrowthDataSource) -> Dict[str, str]:
    return source.__dict__


def partner_lead_to_dict(lead: PublicPartnerLead) -> Dict[str, str]:
    return lead.__dict__


def market_signal_to_dict(source: MarketSignalSource) -> Dict[str, str]:
    return source.__dict__


def build_growth_source_brief() -> Dict[str, object]:
    campaign_counts: Dict[str, int] = {}
    for lead in PUBLIC_PARTNER_LEADS:
        campaign_counts[lead.recommended_campaign] = campaign_counts.get(lead.recommended_campaign, 0) + 1

    return {
        "ok": True,
        "service": "credit-vivo-growth-ai-sources",
        "guardrail": "Use public business/referral sources and opt-in customer channels. Do not scrape or email private consumers about credit hardship without consent.",
        "data_sources": [data_source_to_dict(source) for source in GROWTH_DATA_SOURCES],
        "market_signal_sources": [market_signal_to_dict(source) for source in MARKET_SIGNAL_SOURCES],
        "public_partner_leads": [partner_lead_to_dict(lead) for lead in PUBLIC_PARTNER_LEADS],
        "counts": {
            "data_sources": len(GROWTH_DATA_SOURCES),
            "market_signal_sources": len(MARKET_SIGNAL_SOURCES),
            "public_partner_leads": len(PUBLIC_PARTNER_LEADS),
            "recommended_campaigns": campaign_counts,
        },
        "next_growth_ai_actions": [
            "Connect GA4/Search Console and first-party website events.",
            "Create referral links for /auto-loan-denial, /mortgage-readiness, /apartment-denial, and /collection-not-mine.",
            "Draft partner outreach for the Virginia list and wait for owner approval before sending.",
            "Track every partner reply, referral click, join, scan start, scan completion, and paid upgrade.",
            "Review weekly which channel brings the highest-quality completed scans.",
        ],
    }
