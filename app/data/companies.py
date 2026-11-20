"""Target company / role knowledge used for company-aware recommendations.

Each company lists the careers it hires for and a small set of skill
emphases. `extra_skills` are the skills that employer tends to value beyond the
generic career requirements, which lets the engine explain why a candidate is
(or is not) a fit for that specific organisation.

Every entry below is a real, active employer. Headcount, role and emphasis data
are indicative and are used for ranking only, never as a hiring promise.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Company:
    id: str
    name: str
    industry: str
    location: str
    size: str
    description: str
    hiring: tuple[str, ...]
    extra_skills: dict[str, float] = field(default_factory=dict)
    culture: tuple[str, ...] = field(default_factory=tuple)


def _co(
    company_id: str,
    name: str,
    industry: str,
    location: str,
    size: str,
    description: str,
    hiring: tuple[str, ...],
    extra: dict[str, float],
    culture: tuple[str, ...] = (),
) -> Company:
    return Company(company_id, name, industry, location, size, description, hiring, extra, culture)


COMPANIES: tuple[Company, ...] = (
    # ------------------------------------------------------------------
    # Product & Internet (India)
    # ------------------------------------------------------------------
    _co(
        "flipkart", "Flipkart", "Product & Internet", "Bengaluru, India", "5,000+",
        "Large-scale retail marketplace with heavy investment in search, ranking, logistics and fraud prevention.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "machine-learning-engineer", "devops-engineer", "product-manager", "mobile-developer", "software-engineering-manager"),
        {"java": 0.2, "kubernetes": 0.15, "sql": 0.1, "caching": 0.1},
        ("ownership", "high-impact", "fast-paced"),
    ),
    _co(
        "swiggy", "Swiggy", "Product & Internet", "Bengaluru, India", "5,000+",
        "Real-time logistics platform: matching, routing, ETA prediction and dispatch at city scale.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "machine-learning-engineer", "devops-engineer", "mobile-developer", "software-engineering-manager"),
        {"python": 0.2, "spark": 0.15, "monitoring": 0.1},
        ("fast-paced", "ownership", "on-call"),
    ),
    _co(
        "zomato", "Zomato", "Product & Internet", "Gurugram, India", "2,000+",
        "Consumer marketplace where engineering effort concentrates on discovery, logistics and reliability.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "data-analyst", "product-manager", "mobile-developer"),
        {"react": 0.15, "sql": 0.15, "experimentation": 0.1},
        ("ownership", "user-obsessed", "pragmatic"),
    ),
    _co(
        "razorpay", "Razorpay", "Banking, Markets & Fintech", "Bengaluru, India", "1,000-5,000",
        "Payments infrastructure where correctness, auditability and secure coding are non-negotiable.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "cybersecurity-analyst", "penetration-tester", "data-engineer", "product-manager", "software-engineering-manager"),
        {"cryptography": 0.2, "database_design": 0.15, "security_basics": 0.15},
        ("ownership", "detail-obsessed", "high-trust"),
    ),
    _co(
        "paytm", "Paytm", "Banking, Markets & Fintech", "Noida, India", "5,000+",
        "Digital payments and commerce platform with one of India's largest engineering footprints.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-engineer", "devops-engineer", "penetration-tester", "sales-representative", "digital-marketing-specialist", "software-engineering-manager"),
        {"java": 0.2, "aws": 0.15, "communication": 0.1},
        ("scale", "ownership", "growth-driven"),
    ),
    _co(
        "meesho", "Meesho", "Product & Internet", "Bengaluru, India", "1,000-5,000",
        "Zero-commission social commerce platform onboarding millions of small businesses.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "machine-learning-engineer", "data-analyst", "devops-engineer", "product-manager"),
        {"python": 0.15, "sql": 0.15, "aws": 0.1},
        ("ownership", "fast-iterating", "impact-driven"),
    ),
    _co(
        "phonepe", "PhonePe", "Banking, Markets & Fintech", "Bengaluru, India", "1,000-5,000",
        "UPI-led payments platform known for strong engineering and data practices.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "data-engineer", "mobile-developer", "cybersecurity-analyst", "penetration-tester"),
        {"caching": 0.2, "java": 0.15, "sql": 0.1},
        ("ownership", "data-driven", "high-trust"),
    ),
    _co(
        "ola", "Ola Electric", "Product & Internet", "Bengaluru, India", "5,000+",
        "Electric vehicle and ride-hailing company building both hardware and consumer software.",
        ("mobile-developer", "backend-developer", "frontend-developer", "data-scientist", "mechanical-engineer", "electrical-engineer", "devops-engineer"),
        {"kotlin": 0.2, "electronics": 0.15, "networking": 0.15},
        ("hardware-software", "ownership", "sustainability"),
    ),
    _co(
        "nykaa", "Nykaa", "Product & Internet", "Mumbai, India", "1,000-5,000",
        "Beauty commerce platform with a fast-growing in-house technology organisation.",
        ("digital-marketing-specialist", "fullstack-developer", "frontend-developer", "data-analyst", "product-manager", "backend-developer", "business-analyst", "ui-ux-designer"),
        {"marketing": 0.2, "content_writing": 0.15, "datavis": 0.1},
        ("consumer", "fast-paced", "brand-led"),
    ),
    _co(
        "groww", "Groww", "Banking, Markets & Fintech", "Bengaluru, India", "500-1,000",
        "Investment and trading platform making the stock market accessible to first-time investors.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "devops-engineer", "product-manager", "sales-representative"),
        {"python": 0.2, "sql": 0.15, "monitoring": 0.1},
        ("ownership", "data-driven", "user-first"),
    ),
    _co(
        "zerodha", "Zerodha", "Banking, Markets & Fintech", "Bengaluru, India", "500-1,000",
        "India's largest stock broker by active accounts, with a deliberately small engineering team.",
        ("backend-developer", "frontend-developer", "data-analyst", "software-qa-engineer", "project-manager", "cybersecurity-analyst", "sales-representative"),
        {"monitoring": 0.2, "sql": 0.15, "finance": 0.15},
        ("minimal", "ownership", "cost-conscious"),
    ),
    _co(
        "unacademy", "Unacademy", "EdTech", "Gurugram, India", "1,000-5,000",
        "Online learning platform connecting students with expert teachers.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "data-scientist", "machine-learning-engineer", "mobile-developer", "product-manager", "ui-ux-designer", "digital-marketing-specialist"),
        {"react": 0.15, "videoediting": 0.15, "sql": 0.1},
        ("fast-paced", "learner-obsessed", "impact-driven"),
    ),
    _co(
        "vedantu", "Vedantu", "EdTech", "Bengaluru, India", "500-1,000",
        "Live interactive learning platform with strong in-house content technology.",
        ("data-scientist", "machine-learning-engineer", "data-scientist-researcher", "backend-developer", "fullstack-developer"),
        {"nlp": 0.2, "deeplearning": 0.15, "python": 0.15},
        ("research-y", "ownership", "learner-first"),
    ),
    # ------------------------------------------------------------------
    # Enterprise software & developer tools
    # ------------------------------------------------------------------
    _co(
        "zoho", "Zoho", "Enterprise Software", "Chennai, India", "10,000+",
        "One of India's largest independent software companies, running its own datacentre network.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "devops-engineer", "cloud-engineer", "data-analyst", "technical-writer", "software-qa-engineer", "software-engineering-manager"),
        {"networking": 0.2, "linux": 0.15, "sql": 0.1},
        ("independent", "long-term", "remote-friendly"),
    ),
    _co(
        "freshworks", "Freshworks", "Enterprise Software", "Chennai, India", "1,000-5,000",
        "Customer support and ITSM software company with a strong remote-first engineering culture.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "devops-engineer", "product-manager", "data-analyst", "sales-representative", "technical-writer", "ui-ux-designer"),
        {"restapi": 0.15, "sql": 0.15, "communication": 0.1},
        ("remote-first", "customer-focused", "ownership"),
    ),
    _co(
        "postman", "Postman", "Enterprise Software", "Bengaluru, India / Remote", "500-1,000",
        "API platform used by millions of developers; values product thinking and clear documentation.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "technical-writer", "product-manager", "software-qa-engineer", "devops-engineer"),
        {"restapi": 0.25, "technical_writing": 0.2, "nodejs": 0.15},
        ("remote-friendly", "documentation-first", "product-minded"),
    ),
    _co(
        "browserstack", "BrowserStack", "Enterprise Software", "Mumbai, India / Remote", "500-1,000",
        "Cloud-based testing infrastructure serving millions of developers across the world.",
        ("backend-developer", "devops-engineer", "cloud-engineer", "fullstack-developer", "software-qa-engineer", "data-analyst", "frontend-developer"),
        {"aws": 0.2, "monitoring": 0.15, "cicd": 0.1},
        ("remote-first", "global", "quality-driven"),
    ),
    _co(
        "hasura", "Hasura", "Enterprise Software", "Bengaluru, India / Remote", "100-500",
        "Instant realtime GraphQL backend-as-a-service loved by developer teams.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "devops-engineer", "technical-writer", "cloud-engineer"),
        {"graphql": 0.2, "restapi": 0.15, "kubernetes": 0.1},
        ("open-source", "remote-friendly", "developer-first"),
    ),
    _co(
        "adobe", "Adobe", "Enterprise Software", "Noida, India", "10,000+",
        "Creative and document technology company with a large India R&D centre.",
        ("frontend-developer", "ui-ux-designer", "fullstack-developer", "backend-developer", "cloud-engineer", "software-qa-engineer", "software-engineering-manager"),
        {"uiux": 0.2, "webperf": 0.15, "react": 0.15},
        ("creative", "inclusive", "craft-focused"),
    ),
    _co(
        "atlassian", "Atlassian", "Enterprise Software", "Bengaluru, India / Remote", "10,000+",
        "Jira, Confluence and Trello developer with a large distributed India engineering team.",
        ("backend-developer", "fullstack-developer", "frontend-developer", "devops-engineer", "cloud-engineer", "data-scientist", "technical-writer", "software-qa-engineer"),
        {"java": 0.2, "cicd": 0.15, "restapi": 0.1},
        ("remote-first", "global", "playful"),
    ),
    _co(
        "oracle", "Oracle", "Enterprise Software", "Bengaluru, Hyderabad, India", "100,000+",
        "Database and enterprise application vendor with an extensive India development organisation.",
        ("backend-developer", "cloud-engineer", "devops-engineer", "data-engineer", "business-analyst", "sales-representative", "project-manager", "software-qa-engineer"),
        {"sql": 0.25, "database_design": 0.2, "java": 0.1},
        ("structured", "enterprise", "process-driven"),
    ),
    _co(
        "microsoft", "Microsoft", "Global Technology", "Bengaluru, Hyderabad, India", "100,000+",
        "Azure, Office and developer tooling organisations with deep India engineering presence.",
        ("backend-developer", "frontend-developer", "cloud-engineer", "devops-engineer", "data-scientist", "cybersecurity-analyst", "penetration-tester", "software-engineering-manager", "technical-writer"),
        {"azure": 0.2, "csharp": 0.15, "networking": 0.1},
        ("global", "structured", "collaborative"),
    ),
    # ------------------------------------------------------------------
    # Global technology
    # ------------------------------------------------------------------
    _co(
        "google", "Google", "Global Technology", "Bengaluru, Gurgaon, Hyderabad, India", "100,000+",
        "Search, ads, cloud and AI research organisation with one of the largest engineering footprints in India.",
        ("machine-learning-engineer", "data-scientist", "data-scientist-researcher", "backend-developer", "frontend-developer", "devops-engineer", "cloud-engineer", "software-engineering-manager", "ui-ux-designer", "product-manager"),
        {"statistics": 0.25, "caching": 0.2, "python": 0.1},
        ("scale", "research", "open-source"),
    ),
    _co(
        "amazon", "Amazon", "Global Technology", "Bengaluru, Hyderabad, India", "100,000+",
        "AWS, retail and logistics technology organisation with a strong leadership-principle culture.",
        ("backend-developer", "frontend-developer", "machine-learning-engineer", "devops-engineer", "cloud-engineer", "data-scientist", "data-engineer", "software-qa-engineer", "software-engineering-manager", "business-analyst"),
        {"aws": 0.2, "caching": 0.15, "java": 0.1},
        ("leadership-principles", "scale", "ownership"),
    ),
    _co(
        "ibm", "IBM", "Global Technology", "Bengaluru, Hyderabad, India", "100,000+",
        "Hybrid cloud, consulting and enterprise technology organisation.",
        ("backend-developer", "cloud-engineer", "devops-engineer", "data-analyst", "cybersecurity-analyst", "sales-representative", "project-manager", "technical-writer"),
        {"aws": 0.2, "communication": 0.15, "cicd": 0.1},
        ("consultative", "global", "structured"),
    ),
    # ------------------------------------------------------------------
    # IT services & consulting
    # ------------------------------------------------------------------
    _co(
        "tcs", "Tata Consultancy Services", "IT Services & Consulting", "Pune, Mumbai, Bengaluru, India", "100,000+",
        "Largest Indian IT services company, delivering digital transformation at global scale.",
        ("software-qa-engineer", "devops-engineer", "data-analyst", "business-analyst", "cloud-engineer", "project-manager", "sales-representative", "frontend-developer"),
        {"communication": 0.2, "project_management": 0.15, "excel": 0.1},
        ("structured", "client-facing", "process-driven"),
    ),
    _co(
        "infosys", "Infosys", "IT Services & Consulting", "Bengaluru, Hyderabad, Pune, India", "100,000+",
        "Global delivery partner with a strong focus on engineering and digital platforms.",
        ("software-qa-engineer", "data-analyst", "devops-engineer", "cloud-engineer", "business-analyst", "project-manager", "technical-writer", "frontend-developer"),
        {"java": 0.15, "communication": 0.15, "sql": 0.1},
        ("structured", "learning-driven", "process-driven"),
    ),
    _co(
        "wipro", "Wipro", "IT Services & Consulting", "Bengaluru, India", "100,000+",
        "Diversified technology company with engineering and consulting businesses.",
        ("software-qa-engineer", "cloud-engineer", "devops-engineer", "data-analyst", "project-manager", "business-analyst", "frontend-developer"),
        {"aws": 0.2, "communication": 0.15, "cicd": 0.1},
        ("structured", "global", "process-driven"),
    ),
    _co(
        "hcltech", "HCLTech", "IT Services & Consulting", "Noida, Bengaluru, India", "200,000+",
        "Large IT services and engineering organisation serving global enterprises.",
        ("software-qa-engineer", "devops-engineer", "cloud-engineer", "data-analyst", "business-analyst", "project-manager", "frontend-developer"),
        {"cicd": 0.15, "communication": 0.15, "aws": 0.15},
        ("structured", "client-facing", "process-driven"),
    ),
    _co(
        "cognizant", "Cognizant", "IT Services & Consulting", "Chennai, Bengaluru, India", "100,000+",
        "Engineering and healthcare technology services with strong India delivery centres.",
        ("software-qa-engineer", "data-analyst", "cloud-engineer", "devops-engineer", "business-analyst", "project-manager", "sales-representative"),
        {"communication": 0.2, "sql": 0.15, "project_management": 0.1},
        ("structured", "client-facing", "process-driven"),
    ),
    _co(
        "techmahindra", "Tech Mahindra", "IT Services & Consulting", "Pune, Mumbai, India", "100,000+",
        "Telecom-focused technology services company expanding rapidly into AI and cloud.",
        ("software-qa-engineer", "devops-engineer", "cloud-engineer", "data-analyst", "cybersecurity-analyst", "project-manager", "frontend-developer"),
        {"networking": 0.2, "aws": 0.15, "communication": 0.15},
        ("structured", "telecom-domain", "process-driven"),
    ),
    _co(
        "accenture", "Accenture", "IT Services & Consulting", "Bengaluru, Hyderabad, Mumbai, India", "50,000+",
        "Large-scale technology consulting and delivery partner across industries.",
        ("business-analyst", "project-manager", "software-qa-engineer", "cloud-engineer", "devops-engineer", "data-analyst", "sales-representative", "ui-ux-designer"),
        {"communication": 0.2, "project_management": 0.15, "excel": 0.1},
        ("client-facing", "structured", "process-driven"),
    ),
    _co(
        "persistent", "Persistent Systems", "IT Services & Consulting", "Pune, India", "10,000+",
        "Product-focused engineering partner building platforms for global software companies.",
        ("backend-developer", "fullstack-developer", "cloud-engineer", "devops-engineer", "data-analyst", "software-qa-engineer", "frontend-developer"),
        {"java": 0.2, "aws": 0.15, "restapi": 0.1},
        ("product-engineering", "structured", "client-facing"),
    ),
    _co(
        "tata-elxsi", "Tata Elxsi", "IT Services & Consulting", "Bengaluru, Thiruvananthapuram, India", "10,000+",
        "Engineering and design services company working on automotive and embedded systems.",
        ("mechanical-engineer", "electrical-engineer", "software-qa-engineer", "backend-developer", "ui-ux-designer", "data-analyst"),
        {"electronics": 0.2, "mechanical": 0.15, "manufacturing": 0.15},
        ("engineering-focused", "domain-focused", "structured"),
    ),
    _co(
        "deloitte", "Deloitte", "IT Services & Consulting", "Mumbai, Bengaluru, Hyderabad, India", "50,000+",
        "Audit, consulting and analytics firm hiring heavily in technology and data roles.",
        ("business-analyst", "data-analyst", "finance-analyst", "project-manager", "software-qa-engineer", "sales-representative", "cybersecurity-analyst"),
        {"excel": 0.25, "communication": 0.2, "business_analytics": 0.15},
        ("client-facing", "structured", "domain-focused"),
    ),
    _co(
        "pwc", "PwC India", "IT Services & Consulting", "Mumbai, Bengaluru, Hyderabad, India", "50,000+",
        "Assurance, tax and advisory firm with a large risk and analytics practice.",
        ("business-analyst", "finance-analyst", "data-analyst", "project-manager", "sales-representative", "software-qa-engineer"),
        {"excel": 0.25, "business_analytics": 0.2, "communication": 0.15},
        ("client-facing", "structured", "detail-obsessed"),
    ),
    _co(
        "kpmg", "KPMG India", "IT Services & Consulting", "Mumbai, Bengaluru, Hyderabad, India", "50,000+",
        "Advisory firm with strong technology risk and data analytics practices.",
        ("business-analyst", "finance-analyst", "data-analyst", "project-manager", "cybersecurity-analyst", "penetration-tester"),
        {"excel": 0.25, "finance": 0.2, "business_analytics": 0.15},
        ("client-facing", "structured", "detail-obsessed"),
    ),
    _co(
        "ey", "EY India", "IT Services & Consulting", "Mumbai, Bengaluru, Hyderabad, India", "50,000+",
        "Consultancy with dedicated technology and data analytics service lines.",
        ("business-analyst", "data-analyst", "finance-analyst", "project-manager", "digital-marketing-specialist", "sales-representative"),
        {"excel": 0.2, "communication": 0.2, "business_analytics": 0.15},
        ("client-facing", "structured", "consultative"),
    ),
    # ------------------------------------------------------------------
    # Global banking, markets & fintech
    # ------------------------------------------------------------------
    _co(
        "goldman-sachs", "Goldman Sachs", "Banking, Markets & Fintech", "Bengaluru, Mumbai, India", "50,000+",
        "Global investment bank with a large technology organisation in Bengaluru.",
        ("backend-developer", "data-scientist", "cybersecurity-analyst", "penetration-tester", "finance-analyst", "data-engineer", "software-engineering-manager", "project-manager"),
        {"finance": 0.2, "sql": 0.15, "cryptography": 0.15},
        ("high-trust", "detail-obsessed", "global"),
    ),
    _co(
        "morgan-stanley", "Morgan Stanley", "Banking, Markets & Fintech", "Mumbai, Bengaluru, India", "50,000+",
        "Investment bank with one of India's largest technology engineering workforces.",
        ("backend-developer", "data-scientist", "finance-analyst", "cybersecurity-analyst", "penetration-tester", "data-engineer", "project-manager"),
        {"monitoring": 0.2, "java": 0.15, "sql": 0.1},
        ("global", "process-driven", "detail-obsessed"),
    ),
    _co(
        "icici-bank", "ICICI Bank", "Banking, Markets & Fintech", "Mumbai, India", "100,000+",
        "One of India's largest private sector banks with significant technology investment.",
        ("finance-analyst", "data-analyst", "business-analyst", "cybersecurity-analyst", "penetration-tester", "cloud-engineer", "sales-representative"),
        {"finance": 0.2, "sql": 0.15, "excel": 0.15},
        ("high-trust", "process-driven", "customer-focused"),
    ),
    _co(
        "hdfc-bank", "HDFC Bank", "Banking, Markets & Fintech", "Mumbai, India", "200,000+",
        "Largest private bank in India, known for technology-led operations.",
        ("finance-analyst", "data-analyst", "business-analyst", "cybersecurity-analyst", "penetration-tester", "project-manager"),
        {"finance": 0.2, "excel": 0.2, "sql": 0.15},
        ("high-trust", "process-driven", "scale"),
    ),
    _co(
        "bajaj-finserv", "Bajaj Finserv", "Banking, Markets & Fintech", "Pune, Mumbai, India", "50,000+",
        "Diversified financial services group spanning insurance, lending and asset management.",
        ("finance-analyst", "data-analyst", "data-scientist", "business-analyst", "sales-representative", "software-qa-engineer"),
        {"finance": 0.2, "excel": 0.2, "business_analytics": 0.15},
        ("detail-obsessed", "structured", "customer-focused"),
    ),
    # ------------------------------------------------------------------
    # Core engineering, infrastructure & industry
    # ------------------------------------------------------------------
    _co(
        "tata-motors", "Tata Motors", "Core Engineering & Industry", "Pune, Jamshedpur, India", "50,000+",
        "India's largest commercial vehicle manufacturer, increasingly software-defined.",
        ("mechanical-engineer", "electrical-engineer", "devops-engineer", "civil-engineer", "data-scientist", "software-qa-engineer"),
        {"electronics": 0.2, "mechanical": 0.15, "manufacturing": 0.15},
        ("engineering", "scale", "safety-critical"),
    ),
    _co(
        "mahindra", "Mahindra Group", "Core Engineering & Industry", "Nashik, Pune, India", "100,000+",
        "Diversified group across automotive, farm equipment and real estate.",
        ("mechanical-engineer", "electrical-engineer", "civil-engineer", "sales-representative", "digital-marketing-specialist", "data-analyst"),
        {"mechanical": 0.2, "manufacturing": 0.15, "business_analytics": 0.1},
        ("engineering", "diversified", "field-oriented"),
    ),
    _co(
        "maruti-suzuki", "Maruti Suzuki", "Core Engineering & Industry", "Gurugram, Manesar, India", "50,000+",
        "India's largest car manufacturer with large-scale manufacturing operations.",
        ("mechanical-engineer", "electrical-engineer", "sales-representative", "digital-marketing-specialist"),
        {"manufacturing": 0.25, "testing": 0.15, "mechanical": 0.15},
        ("manufacturing", "quality-focused", "scale"),
    ),
    _co(
        "bosch-india", "Bosch India", "Core Engineering & Industry", "Bengaluru, Pune, India", "10,000+",
        "Global engineering supplier with major India R&D and manufacturing presence.",
        ("mechanical-engineer", "electrical-engineer", "data-engineer", "cybersecurity-analyst", "data-scientist", "software-qa-engineer"),
        {"electronics": 0.2, "manufacturing": 0.2, "testing": 0.15},
        ("engineering", "quality-focused", "global"),
    ),
    _co(
        "siemens-india", "Siemens India", "Core Engineering & Industry", "Mumbai, Pune, Bengaluru, India", "10,000+",
        "Industrial automation and infrastructure technology company.",
        ("electrical-engineer", "civil-engineer", "cloud-engineer", "devops-engineer", "mechanical-engineer", "sales-representative"),
        {"electronics": 0.2, "networking": 0.2, "cicd": 0.1},
        ("engineering", "industrial", "global"),
    ),
    _co(
        "larsen-toubro", "Larsen & Toubro", "Core Engineering & Industry", "Mumbai, Chennai, India", "50,000+",
        "India's largest infrastructure and engineering conglomerate.",
        ("civil-engineer", "mechanical-engineer", "electrical-engineer", "project-manager", "business-analyst", "sales-representative"),
        {"project_management": 0.2, "business_analytics": 0.15, "testing": 0.15},
        ("site", "safety-critical", "large-scale"),
    ),
    _co(
        "hindustan-construction", "Hindustan Construction", "Core Engineering & Industry", "Mumbai, India", "10,000+",
        "Large infrastructure and construction company delivering highways and urban projects.",
        ("civil-engineer", "project-manager", "mechanical-engineer", "sales-representative"),
        {"project_management": 0.25, "business_analytics": 0.2, "testing": 0.15},
        ("site", "execution-focused", "safety-critical"),
    ),
    _co(
        "nhai", "NHAI", "Core Engineering & Industry", "New Delhi, India", "5,000+",
        "National Highways Authority of India, responsible for national highway development.",
        ("civil-engineer", "project-manager", "electrical-engineer", "business-analyst"),
        {"project_management": 0.25, "business_analytics": 0.2, "testing": 0.15},
        ("public-service", "site", "process-driven"),
    ),
    _co(
        "airports-authority", "Airports Authority of India", "Core Engineering & Industry", "Multiple, India", "10,000+",
        "Operates and maintains India's civil aviation network infrastructure.",
        ("civil-engineer", "electrical-engineer", "project-manager", "cybersecurity-analyst"),
        {"project_management": 0.2, "testing": 0.2, "networking": 0.1},
        ("public-service", "safety-critical", "structured"),
    ),
    # ------------------------------------------------------------------
    # Research & defence
    # ------------------------------------------------------------------
    _co(
        "isro", "ISRO", "Research & Defence", "Bengaluru, Thiruvananthapuram, India", "10,000+",
        "India's national space agency, hiring across engineering and research disciplines.",
        ("mechanical-engineer", "electrical-engineer", "data-scientist-researcher", "software-qa-engineer", "cybersecurity-analyst"),
        {"research": 0.25, "electronics": 0.15, "testing": 0.15},
        ("mission-driven", "research", "discipline"),
    ),
    _co(
        "drdo", "DRDO", "Research & Defence", "Bengaluru, New Delhi, India", "10,000+",
        "Defence Research and Development Organisation working on defence technology programmes.",
        ("cybersecurity-analyst", "penetration-tester", "data-scientist-researcher", "electrical-engineer", "mechanical-engineer"),
        {"cryptography": 0.25, "networking": 0.2, "research": 0.2},
        ("formal", "documentation-heavy", "security-focused"),
    ),
    _co(
        "barc", "BARC", "Research & Defence", "Mumbai, India", "5,000+",
        "Bhabha Atomic Research Centre conducting fundamental and applied science research.",
        ("data-scientist-researcher", "cybersecurity-analyst", "electrical-engineer", "mechanical-engineer"),
        {"research": 0.3, "statistics": 0.2, "testing": 0.15},
        ("research", "rigorous", "discipline"),
    ),
    _co(
        "bel", "Bharat Electronics", "Research & Defence", "Bengaluru, New Delhi, India", "10,000+",
        "Defence electronics manufacturer producing radars, communication and missile systems.",
        ("electrical-engineer", "mechanical-engineer", "cybersecurity-analyst", "devops-engineer", "software-qa-engineer"),
        {"electronics": 0.25, "networking": 0.15, "testing": 0.15},
        ("formal", "safety-critical", "security-focused"),
    ),
)

COMPANIES_BY_ID: dict[str, Company] = {c.id: c for c in COMPANIES}


def get_company(company_id: str) -> Company | None:
    return COMPANIES_BY_ID.get(company_id)


def companies_hiring(career_id: str) -> list[Company]:
    return [c for c in COMPANIES if career_id in c.hiring]


def all_industries() -> list[str]:
    seen: list[str] = []
    for c in COMPANIES:
        if c.industry not in seen:
            seen.append(c.industry)
    return seen
