"""Canonical skill knowledge base.

Each skill carries:
  id: stable slug used everywhere in the API and database
  name: human readable label
  category: grouping used by the dashboard
  aliases: extra surface forms the resume parser should recognise
  keywords: single tokens used for token-overlap scoring
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    category: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    keywords: tuple[str, ...] = field(default_factory=tuple)


def _s(skill_id: str, name: str, category: str, aliases: tuple[str, ...] = (), keywords: tuple[str, ...] = ()) -> Skill:
    return Skill(skill_id, name, category, tuple(aliases), tuple(keywords))


SKILLS: tuple[Skill, ...] = (
    # ---------- Programming languages ----------
    _s("python", "Python", "Programming", ("python3", "py"), ("python",)),
    _s("javascript", "JavaScript", "Programming", ("js", "es6", "ecmascript"), ("javascript",)),
    _s("typescript", "TypeScript", "Programming", ("ts",), ("typescript",)),
    _s("java", "Java", "Programming", (), ("java",)),
    _s("cpp", "C++", "Programming", ("c plus plus",), ("cpp",)),
    _s("csharp", "C#", "Programming", ("c sharp", "dotnet", ".net"), ("csharp", "dotnet")),
    _s("go", "Go", "Programming", ("golang",), ("go", "golang")),
    _s("rust", "Rust", "Programming", (), ("rust",)),
    _s("php", "PHP", "Programming", (), ("php",)),
    _s("ruby", "Ruby", "Programming", (), ("ruby",)),
    _s("swift", "Swift", "Programming", (), ("swift",)),
    _s("kotlin", "Kotlin", "Programming", (), ("kotlin",)),
    _s("r", "R", "Programming", ("r programming", "r language", "rlang"), ("r",)),
    _s("scala", "Scala", "Programming", (), ("scala",)),
    _s("bash", "Shell Scripting", "Programming", ("bash", "shell", "sh", "zsh"), ("bash", "shell")),
    _s("sql", "SQL", "Programming", ("t-sql", "pl/sql", "ansi sql"), ("sql",)),
    # ---------- Web / frontend ----------
    _s("html", "HTML", "Web", ("html5",), ("html",)),
    _s("css", "CSS", "Web", ("css3", "sass", "scss", "tailwind", "bootstrap"), ("css",)),
    _s("react", "React", "Web", ("reactjs", "react.js", "next.js", "nextjs"), ("react",)),
    _s("vue", "Vue.js", "Web", ("vuejs", "vue.js", "nuxt"), ("vue",)),
    _s("angular", "Angular", "Web", ("angularjs",), ("angular",)),
    _s("svelte", "Svelte", "Web", ("sveltekit",), ("svelte",)),
    _s("nodejs", "Node.js", "Web", ("node", "express", "express.js", "nestjs", "nest.js"), ("node", "nodejs")),
    _s("restapi", "REST API Design", "Web", ("rest", "restful", "api design", "openapi", "swagger"), ("rest", "api")),
    _s("graphql", "GraphQL", "Web", ("apollo",), ("graphql", "apollo")),
    _s("redux", "State Management", "Web", ("redux", "mobx", "zustand", "context api"), ("redux", "state")),
    _s("webperf", "Web Performance", "Web", ("lighthouse", "core web vitals"), ("performance", "lighthouse")),
    _s("uiux", "UI/UX Design", "Web", ("figma", "user interface", "user experience", "prototyping"), ("figma", "design")),
    _s("responsive", "Responsive Design", "Web", ("mobile first", "media queries"), ("responsive", "mobile")),
    # ---------- Data / ML ----------
    _s("pandas", "Pandas", "Data", ("numpy", "dataframes"), ("pandas", "numpy")),
    _s("sqladvanced", "Advanced SQL", "Data", ("window functions", "etl", "data pipelines", "star schema"), ("sql",)),
    _s("statistics", "Statistics", "Data", ("statistical analysis", "probability", "hypothesis testing"), ("statistics", "probability")),
    _s("excel", "Spreadsheets", "Data", ("excel", "google sheets", "pivot table"), ("excel", "spreadsheet")),
    _s("datavis", "Data Visualization", "Data", ("tableau", "power bi", "matplotlib", "seaborn", "plotly"), ("tableau", "powerbi", "matplotlib")),
    _s("ml", "Machine Learning", "Data", ("scikit-learn", "sklearn", "machine learning"), ("machine", "learning", "sklearn")),
    _s("deeplearning", "Deep Learning", "Data", ("tensorflow", "pytorch", "keras", "neural networks", "cnn", "rnn"), ("deep", "learning", "tensorflow", "pytorch")),
    _s("nlp", "Natural Language Processing", "Data", ("nlp", "spacy", "nltk", "transformers", "llm"), ("nlp", "transformers", "spacy")),
    _s("computer_vision", "Computer Vision", "Data", ("opencv", "cv", "image processing", "yolo"), ("opencv", "vision", "yolo")),
    _s("dataeng", "Data Engineering", "Data", ("spark", "hadoop", "etl", "airflow", "kafka", "data warehouse"), ("spark", "airflow", "kafka", "etl")),
    _s("datascience", "Data Science", "Data", ("data scientist", "a-b testing", "experimentation"), ("data", "science")),
    _s("powerbi", "Business Intelligence", "Data", ("power bi", "tableau", "looker", "metabase", "dashboards"), ("bi", "dashboard")),
    # ---------- Cloud / DevOps ----------
    _s("aws", "AWS", "Cloud", ("amazon web services", "ec2", "s3", "lambda"), ("aws", "ec2", "s3", "lambda")),
    _s("azure", "Azure", "Cloud", ("microsoft azure",), ("azure",)),
    _s("gcp", "Google Cloud", "Cloud", ("gcp", "google cloud", "bigquery"), ("gcp", "bigquery")),
    _s("docker", "Docker", "Cloud", ("containerization", "containers", "podman"), ("docker", "container")),
    _s("kubernetes", "Kubernetes", "Cloud", ("k8s", "eks", "helm"), ("kubernetes", "k8s")),
    _s("cicd", "CI/CD", "Cloud", ("github actions", "gitlab ci", "jenkins", "continuous integration", "deployment pipeline"), ("ci", "cd", "pipeline")),
    _s("terraform", "Infrastructure as Code", "Cloud", ("terraform", "pulumi", "cloudformation"), ("terraform", "infrastructure")),
    _s("linux", "Linux", "Cloud", ("unix", "ubuntu", "centos"), ("linux", "unix")),
    _s("monitoring", "Observability", "Cloud", ("prometheus", "grafana", "datadog", "logging", "monitoring"), ("prometheus", "grafana", "datadog")),
    _s("devops", "DevOps", "Cloud", ("site reliability", "sre", "platform engineering"), ("devops", "sre")),
    # ---------- Mobile / Desktop ----------
    _s("android", "Android Development", "Mobile", ("android studio", "jetpack compose"), ("android",)),
    _s("ios", "iOS Development", "Mobile", ("xcode", "swiftui", "cocoa"), ("ios", "xcode", "swiftui")),
    _s("flutter", "Flutter", "Mobile", ("dart",), ("flutter", "dart")),
    _s("reactnative", "React Native", "Mobile", ("react-native", "expo"), ("native", "expo")),
    # ---------- Security ----------
    _s("cybersecurity", "Cybersecurity", "Security", ("infosec", "information security", "penetration testing", "pentest", "ethical hacking"), ("security", "pentest")),
    _s("networksecurity", "Network Security", "Security", ("firewall", "ids", "ips", "vpn"), ("network", "firewall")),
    _s("cryptography", "Cryptography", "Security", ("encryption", "tls", "ssl"), ("encryption", "crypto")),
    _s("ethical_hacking", "Ethical Hacking", "Security", ("ceh", "oscp", "bug bounty"), ("hacking", "ceh", "oscp")),
    # ---------- QA / Testing ----------
    _s("testing", "Automated Testing", "QA", ("unit testing", "pytest", "jest", "junit", "integration tests"), ("testing", "pytest", "jest")),
    _s("manualqa", "Manual QA", "QA", ("test case", "bug reporting", "test plan"), ("qa", "test")),
    _s("testautomation", "Test Automation", "QA", ("selenium", "cypress", "playwright", "appium"), ("selenium", "cypress", "playwright")),
    # ---------- Mobile / other ----------
    _s("git", "Git & Version Control", "Productivity", ("github", "gitlab", "bitbucket", "version control"), ("git", "github")),
    _s("project_management", "Project Management", "Business", ("agile", "scrum", "kanban", "jira", "pmp"), ("agile", "scrum", "jira")),
    _s("product_management", "Product Management", "Business", ("roadmap", "prd", "stakeholder", "product strategy"), ("product", "roadmap")),
    _s("communication", "Communication", "Business", ("presentation", "public speaking", "technical writing"), ("communication", "writing")),
    _s("leadership", "Leadership", "Business", ("team lead", "mentoring", "management"), ("leadership", "mentoring")),
    _s("marketing", "Digital Marketing", "Business", ("seo", "sem", "google ads", "social media marketing", "content marketing"), ("marketing", "seo")),
    _s("sales", "Sales", "Business", ("lead generation", "crm", "negotiation", "business development"), ("sales", "crm")),
    _s("finance", "Finance", "Business", ("accounting", "financial modelling", "excel modelling", "valuation"), ("finance", "accounting")),
    _s("business_analytics", "Business Analytics", "Business", ("kpi", "metrics", "stakeholder reporting", "insights"), ("analytics", "kpi")),
    _s("economics", "Economics", "Business", ("microeconomics", "macroeconomics", "econometrics"), ("economics",)),
    # ---------- Design / creative ----------
    _s("graphicdesign", "Graphic Design", "Design", ("photoshop", "illustrator", "canva", "branding"), ("photoshop", "design", "canva")),
    _s("videoediting", "Video Editing", "Design", ("premiere pro", "after effects", "davinci"), ("video", "editing")),
    _s("3d", "3D Modelling", "Design", ("blender", "maya", "3ds max", "unity", "unreal"), ("blender", "3d", "unity")),
    # ---------- Science / engineering ----------
    _s("electrical", "Electrical Engineering", "Engineering", ("circuits", "matlab", "power systems"), ("electrical", "circuit")),
    _s("mechanical", "Mechanical Engineering", "Engineering", ("cad", "solidworks", "autocad", "thermodynamics"), ("mechanical", "cad")),
    _s("civil", "Civil Engineering", "Engineering", ("structural", "autocad", "construction"), ("civil", "structural")),
    # ---------- Education / healthcare ----------
    _s("teaching", "Teaching", "Teaching", ("tutoring", "classroom", "curriculum", "lesson planning"), ("teaching", "tutor")),
    _s("research", "Research", "Teaching", ("publication", "thesis", "literature review", "academic writing"), ("research", "publication")),
    _s("clinical", "Clinical Knowledge", "Healthcare", ("patient care", "nursing", "medical", "diagnosis"), ("clinical", "patient", "medical")),
    # ---------- Supporting / specialist ----------
    _s("c", "C Language", "Programming", ("ansi c",), ("c",)),
    _s("database_design", "Database Design", "Data", ("schema design", "normalisation", "erd", "indexing", "query optimisation", "postgres", "mysql", "mongodb", "postgresql"), ("database", "schema", "sql")),
    _s("caching", "Caching & Performance", "Data", ("redis", "memcached", "query optimisation"), ("redis", "cache")),
    _s("spark", "Apache Spark", "Data", ("pyspark", "databricks"), ("spark", "pyspark")),
    _s("airflow", "Workflow Orchestration", "Data", ("apache airflow", "dbt", "prefect", "airbyte"), ("airflow", "dbt", "orchestration")),
    _s("mlops", "MLOps", "Data", ("model deployment", "mlflow", "feature store", "model serving"), ("mlops", "deployment", "mlflow")),
    _s("experimentation", "Experiment Design", "Data", ("a-b testing", "ab testing", "hypothesis testing", "significance"), ("experiment", "ab", "testing")),
    _s("networking", "Networking", "Cloud", ("tcp/ip", "dns", "load balancer", "subnet", "http"), ("network", "tcp", "dns")),
    _s("security_basics", "Application Security", "Security", ("owasp", "xss", "csrf", "secure coding", "sast"), ("owasp", "xss", "secure")),
    _s("figma", "Figma", "Design", ("sketch", "adobe xd"), ("figma", "sketch")),
    _s("process_mapping", "Process Modelling", "Business", ("bpmn", "workflow design", "sop", "as is to be"), ("process", "workflow")),
    _s("content_writing", "Content Writing", "Business", ("copywriting", "blogging", "editorial"), ("content", "writing")),
    _s("crm", "CRM Systems", "Business", ("salesforce", "hubspot", "pipedrive"), ("crm", "salesforce", "hubspot")),
    _s("electronics", "Electronics", "Engineering", ("pcb", "circuit design", "embedded systems", "arduino", "esp32"), ("electronics", "pcb", "embedded")),
    _s("manufacturing", "Manufacturing", "Engineering", ("lean", "six sigma", "production", "assembly"), ("manufacturing", "production")),
    _s("technical_writing", "Technical Writing", "Business", ("documentation", "api docs", "user guide"), ("documentation", "writing")),
)

SKILLS_BY_ID: dict[str, Skill] = {s.id: s for s in SKILLS}


def get_skill(skill_id: str) -> Skill | None:
    return SKILLS_BY_ID.get(skill_id)


def skill_name(skill_id: str) -> str:
    skill = SKILLS_BY_ID.get(skill_id)
    return skill.name if skill else skill_id


def all_categories() -> list[str]:
    seen: list[str] = []
    for s in SKILLS:
        if s.category not in seen:
            seen.append(s.category)
    return seen