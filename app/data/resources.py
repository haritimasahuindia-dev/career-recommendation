"""Learning resource catalogue and project blueprints.

`RESOURCES` maps skill_id -> ordered list of learning resources. Order matters:
index 0 is treated as the recommended starting point when a roadmap is built.
`hours` is a rough estimate for a student with no prior exposure.

`PROJECT_IDEAS` maps skill_id -> project blueprints that prove that skill.
Each blueprint lists the skills it demonstrates, so the recommender can pick
projects that close a specific gap.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Resource:
    title: str
    kind: str  # course | docs | video | book | practice
    provider: str
    url: str = ""
    hours: int = 10


@dataclass(frozen=True)
class ProjectIdea:
    id: str
    title: str
    summary: str
    skills: tuple[str, ...]
    difficulty: str = "intermediate"  # beginner | intermediate | advanced
    hours: int = 40


def _r(title: str, kind: str, provider: str, url: str = "", hours: int = 10) -> Resource:
    return Resource(title, kind, provider, url, hours)


def _p(
    project_id: str,
    title: str,
    summary: str,
    skills: tuple[str, ...],
    difficulty: str = "intermediate",
    hours: int = 40,
) -> ProjectIdea:
    return ProjectIdea(project_id, title, summary, skills, difficulty, hours)


RESOURCES: dict[str, tuple[Resource, ...]] = {
    "python": (
        _r("Automate the Boring Stuff with Python", "book", "free online", "https://automatetheboringstuff.com/", 25),
        _r("CS50P: Introduction to Programming with Python", "course", "Harvard/edX", "https://cs50.harvard.edu/python/", 30),
        _r("Python for Everybody", "course", "Coursera", "", 25),
    ),
    "javascript": (
        _r("MDN JavaScript Guide", "docs", "Mozilla", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", 20),
        _r("JavaScript30", "practice", "freeCodeCamp", "https://javascript30.com/", 10),
        _r("Eloquent JavaScript", "book", "free online", "https://eloquentjavascript.net/", 30),
    ),
    "typescript": (
        _r("TypeScript Handbook", "docs", "Microsoft", "https://www.typescriptlang.org/docs/handbook/intro.html", 12),
        _r("TypeScript for Beginners", "video", "freeCodeCamp", "https://www.youtube.com/watch?v=kcWyIewO63Y", 3),
    ),
    "java": (
        _r("Java Programming Basics", "course", "Coursera", "", 30),
        _r("Baeldung Spring Guides", "docs", "Baeldung", "https://www.baeldung.com/spring-boot-tutorial", 20),
    ),
    "sql": (
        _r("SQLBolt", "practice", "SQLBolt", "https://sqlbolt.com/", 8),
        _r("Mode SQL Tutorial", "course", "Mode", "https://mode.com/sql-tutorial/", 15),
        _r("PostgreSQL Tutorial", "docs", "PostgreSQL", "https://www.postgresql.org/docs/current/tutorial.html", 15),
    ),
    "sqladvanced": (
        _r("Window Functions Tutorial", "docs", "PostgreSQL", "https://www.postgresql.org/docs/current/tutorial-window.html", 6),
        _r("Advanced SQL / Star Schema", "practice", "Mode", "https://mode.com/sql-tutorial/", 10),
    ),
    "database_design": (
        _r("Database Design for Developers", "video", "ThePrimeagen", "https://www.youtube.com/watch?v=gnPdzJiFz5Q", 4),
        _r("Use The Index, Luke", "docs", "free", "https://use-the-index-luke.com/", 12),
    ),
    "git": (
        _r("Pro Git", "book", "free online", "https://git-scm.com/book/en/v2", 15),
        _r("Git and GitHub for Beginners", "course", "Microsoft Learn", "", 8),
    ),
    "linux": (
        _r("The Linux Command Line", "book", "free online", "https://linuxcommand.org/tlcl.php", 25),
        _r("Linux Journey", "practice", "linuxjourney.com", "https://linuxjourney.com/", 10),
    ),
    "html": (
        _r("MDN HTML", "docs", "Mozilla", "https://developer.mozilla.org/en-US/docs/Web/HTML", 12),
        _r("HTML Crash Course", "video", "freeCodeCamp", "", 1),
    ),
    "css": (
        _r("MDN CSS", "docs", "Mozilla", "https://developer.mozilla.org/en-US/docs/Web/CSS", 15),
        _r("Flexbox & Grid Complete Guide", "docs", "CSS-Tricks", "https://css-tricks.com/snippets/css/a-guide-to-flexbox/", 6),
    ),
    "responsive": (
        _r("Responsive Web Design Certification", "course", "freeCodeCamp", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", 15),
        _r("Every Layout", "docs", "free", "https://every-layout.dev/", 8),
    ),
    "react": (
        _r("React Official Tutorial", "docs", "React", "https://react.dev/learn", 25),
        _r("freeCodeCamp React Course", "course", "freeCodeCamp", "", 30),
    ),
    "nodejs": (
        _r("Node.js Guides", "docs", "Node.js", "https://nodejs.org/en/learn/getting-started", 12),
        _r("Express Crash Course", "course", "freeCodeCamp", "", 3),
    ),
    "restapi": (
        _r("FastAPI Tutorial", "docs", "FastAPI", "https://fastapi.tiangolo.com/tutorial/", 10),
        _r("REST API Design Guide", "docs", "RESTful", "https://restfulapi.net/", 6),
    ),
    "redux": (
        _r("Redux Fundamentals", "docs", "Redux", "https://redux.js.org/tutorial/essentials", 10),
        _r("State Management in React", "video", "freeCodeCamp", "", 3),
    ),
    "webperf": (
        _r("Lighthouse Documentation", "docs", "Google", "https://developer.chrome.com/docs/lighthouse/overview", 4),
        _r("Core Web Vitals", "docs", "web.dev", "https://web.dev/articles/vitals", 4),
    ),
    "uiux": (
        _r("Google UX Design Certificate", "course", "Coursera", "", 40),
        _r("Laws of UX", "book", "free online", "https://lawsofux.com/", 6),
    ),
    "figma": (
        _r("Figma for Beginners", "course", "free", "https://help.figma.com/hc/en-us/articles/7803103289213-Getting-started", 6),
        _r("Figma Plugin Docs", "docs", "Figma", "https://www.figma.com/plugin-docs/", 10),
    ),
    "graphicdesign": (
        _r("Graphic Design Basics", "course", "free online", "", 15),
    ),
    "pandas": (
        _r("Kaggle Learn: Pandas", "course", "Kaggle", "https://www.kaggle.com/learn/pandas", 4),
        _r("Python Data Science Handbook", "book", "free online", "https://jakevdp.github.io/PythonDataScienceHandbook/", 30),
        _r("NumPy Absolute Beginners Guide", "docs", "NumPy", "https://numpy.org/doc/stable/user/absolute_beginners.html", 5),
    ),
    "statistics": (
        _r("Statistics for Data Science", "course", "Coursera", "", 25),
        _r("Kaggle Learn: Statistics", "course", "Kaggle", "https://www.kaggle.com/learn/statistics", 3),
    ),
    "ml": (
        _r("Machine Learning Specialization", "course", "Andrew Ng / Coursera", "", 45),
        _r("Hands-On ML (scikit-learn)", "book", "O'Reilly", "", 40),
    ),
    "deeplearning": (
        _r("DeepLearning.AI Specialization", "course", "Coursera", "", 60),
        _r("fast.ai Practical Deep Learning", "course", "fast.ai", "https://course.fast.ai/", 70),
    ),
    "nlp": (
        _r("NLP Specialization", "course", "deeplearning.ai", "", 50),
        _r("Hugging Face NLP Course", "course", "Hugging Face", "https://huggingface.co/learn/nlp-course", 20),
    ),
    "computer_vision": (
        _r("Computer Vision with OpenCV", "course", "freeCodeCamp", "", 10),
        _r("OpenCV Python Tutorials", "docs", "OpenCV", "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html", 15),
    ),
    "datavis": (
        _r("Data Visualization with Python", "course", "freeCodeCamp", "", 12),
        _r("Fundamentals of Data Visualization", "book", "free online", "https://clauswilke.com/dataviz/", 25),
    ),
    "dataeng": (
        _r("Data Engineering Cookbook", "book", "O'Reilly", "", 35),
        _r("Apache Airflow Best Practices", "docs", "Airflow", "https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html", 10),
    ),
    "spark": (
        _r("Spark SQL Programming Guide", "docs", "Apache", "https://spark.apache.org/docs/latest/sql-programming-guide.html", 15),
    ),
    "airflow": (
        _r("Airflow Best Practices", "docs", "Apache", "https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html", 8),
        _r("Astronomer Airflow Guide", "docs", "Astronomer", "https://www.astronomer.io/docs/learn/airflow-basics/", 10),
    ),
    "mlops": (
        _r("MLOps Specialization", "course", "Coursera", "", 30),
        _r("Made With ML MLOps Course", "course", "free online", "https://madewithml.com/course/mlops/", 20),
    ),
    "datascience": (
        _r("Data Science Roadmap", "docs", "free online", "https://roadmap.sh/data-science", 20),
        _r("Kaggle Data Science", "practice", "Kaggle", "https://www.kaggle.com/competitions", 20),
    ),
    "powerbi": (
        _r("Power BI Learning Path", "docs", "Microsoft", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/", 20),
    ),
    "excel": (
        _r("Excel Skills for Business", "course", "Macquarie", "", 15),
    ),
    "aws": (
        _r("AWS Certified Developer Associate", "course", "A Cloud Guru", "", 40),
        _r("AWS Well-Architected Framework", "docs", "AWS", "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html", 12),
    ),
    "azure": (
        _r("Azure Fundamentals", "docs", "Microsoft", "https://learn.microsoft.com/en-us/azure/architecture/", 20),
    ),
    "gcp": (
        _r("Google Cloud Digital Leader Path", "docs", "Google", "https://cloud.google.com/training", 20),
    ),
    "docker": (
        _r("Docker Get Started", "docs", "Docker", "https://docs.docker.com/get-started/", 8),
        _r("Docker Deep Dive", "course", "Nagarjun", "", 6),
    ),
    "kubernetes": (
        _r("Kubernetes Basics", "docs", "Kubernetes", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", 12),
        _r("Killercoda Kubernetes Scenarios", "practice", "Killercoda", "https://killercoda.com/kubernetes", 10),
    ),
    "cicd": (
        _r("GitHub Actions Documentation", "docs", "GitHub", "https://docs.github.com/en/actions", 10),
        _r("CI/CD Best Practices", "docs", "free online", "https://www.atlassian.com/git/tutorials/ci", 6),
    ),
    "terraform": (
        _r("Terraform Learn", "docs", "HashiCorp", "https://developer.hashicorp.com/terraform/tutorials", 15),
    ),
    "monitoring": (
        _r("Prometheus Documentation", "docs", "Prometheus", "https://prometheus.io/docs/introduction/overview/", 8),
        _r("Google SRE Book", "book", "free online", "https://sre.google/books/", 25),
    ),
    "devops": (
        _r("The DevOps Roadmap", "docs", "free online", "https://roadmap.sh/devops", 25),
    ),
    "networking": (
        _r("Computer Networking Top Down", "course", "Coursera", "", 30),
    ),
    "cybersecurity": (
        _r("Security+ Study Guide", "course", "CompTIA", "", 25),
        _r("TryHackMe SOC Level 1", "practice", "TryHackMe", "https://tryhackme.com/path/outline/soclevel1", 20),
    ),
    "networksecurity": (
        _r("Practical Packet Analysis", "book", "O'Reilly", "", 25),
        _r("Wireshark Documentation", "docs", "Wireshark", "https://www.wireshark.org/docs/wsug_html_chunked/", 10),
    ),
    "cryptography": (
        _r("Cryptography I", "course", "Coursera / Dan Boneh", "", 30),
    ),
    "ethical_hacking": (
        _r("TryHackMe Jr Penetration Tester", "practice", "TryHackMe", "https://tryhackme.com/path/outline/jrpenetrationtester", 35),
        _r("Hack The Box Academy", "course", "Hack The Box", "", 30),
    ),
    "security_basics": (
        _r("OWASP Top 10", "docs", "OWASP", "https://owasp.org/www-project-top-ten/", 5),
        _r("Secure Coding 101", "course", "PortSwigger", "", 10),
    ),
    "testing": (
        _r("Testing Fundamentals", "course", "freeCodeCamp", "", 5),
        _r("pytest Documentation", "docs", "pytest", "https://docs.pytest.org/en/stable/", 8),
    ),
    "testautomation": (
        _r("Selenium Python Tutorial", "docs", "Selenium", "https://selenium-python.readthedocs.io/", 10),
        _r("Playwright Docs", "docs", "Playwright", "https://playwright.dev/python/docs/intro", 10),
    ),
    "manualqa": (
        _r("Software Testing Basics", "course", "freeCodeCamp", "", 5),
    ),
    "android": (
        _r("Android Basics with Compose", "course", "Google", "https://developer.android.com/courses/basics-compose/course", 40),
    ),
    "ios": (
        _r("SwiftUI Tutorials", "docs", "Apple", "https://developer.apple.com/documentation/swiftui", 25),
    ),
    "flutter": (
        _r("Flutter Learning Journey", "docs", "Google", "https://docs.flutter.dev/get-started/learn", 25),
    ),
    "reactnative": (
        _r("React Native Tutorial", "docs", "React Native", "https://reactnative.dev/docs/tutorial-paths", 20),
    ),
    "project_management": (
        _r("Scrum Fundamentals", "course", "free online", "https://www.scrum.org/learning", 6),
        _r("PMP Basics", "course", "free online", "", 10),
    ),
    "product_management": (
        _r("Product Management Fundamentals", "course", "free online", "", 8),
        _r("Shape Up", "book", "free online", "https://basecamp.com/shapeup", 10),
    ),
    "communication": (
        _r("Technical Communication", "course", "free online", "", 8),
    ),
    "leadership": (
        _r("Leading Small Teams", "course", "free online", "", 8),
    ),
    "marketing": (
        _r("Google Digital Garage: SEO", "course", "Google", "https://learndigital.withgoogle.com/digitalgarage/course/basics-of-seo", 5),
        _r("Marketing Fundamentals", "book", "free online", "", 10),
    ),
    "content_writing": (
        _r("Content Writing Guide", "docs", "free online", "", 6),
    ),
    "sales": (
        _r("Sales Fundamentals", "course", "HubSpot Academy", "https://academy.hubspot.com/courses/sales-fundamentals", 5),
    ),
    "crm": (
        _r("HubSpot CRM Academy", "course", "HubSpot", "https://academy.hubspot.com/courses/hubspot-crm", 6),
    ),
    "finance": (
        _r("Financial Modelling Basics", "course", "CFI", "", 20),
        _r("Corporate Finance Basics", "course", "Coursera", "", 20),
    ),
    "business_analytics": (
        _r("Google Data Analytics Certificate", "course", "Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics", 45),
    ),
    "economics": (
        _r("Principles of Economics", "course", "Coursera", "", 20),
    ),
    "research": (
        _r("How to Do a Literature Review", "course", "free online", "", 8),
    ),
    "teaching": (
        _r("Teaching Methodology Basics", "course", "free online", "", 10),
    ),
    "technical_writing": (
        _r("Google Technical Writing", "course", "Coursera", "https://www.coursera.org/professional-certificates/technical-writing", 25),
        _r("Docs as Code", "docs", "free online", "https://www.writethedocs.org/guide/docs-as-code/", 6),
    ),
    "process_mapping": (
        _r("BPMN Introduction", "docs", "free online", "https://www.omg.org/bpmn/", 6),
    ),
    "caching": (
        _r("Redis Docs", "docs", "Redis", "https://redis.io/docs/latest/", 8),
    ),
    "clinical": (
        _r("Clinical Research Basics", "course", "free online", "", 15),
    ),
    "electrical": (
        _r("Circuit Analysis Course", "course", "Coursera", "", 25),
    ),
    "mechanical": (
        _r("Engineering Mechanics", "course", "free online", "", 25),
    ),
    "civil": (
        _r("Structural Analysis Basics", "course", "free online", "", 25),
    ),
    "3d": (
        _r("Blender Learn", "docs", "Blender", "https://www.blender.org/support/training/", 15),
    ),
    "electronics": (
        _r("Arduino Reference", "docs", "Arduino", "https://docs.arduino.cc/", 8),
        _r("Embedded Systems Course", "course", "free online", "", 20),
    ),
    "manufacturing": (
        _r("Lean Six Sigma", "course", "free online", "", 12),
    ),
}


PROJECT_IDEAS: dict[str, tuple[ProjectIdea, ...]] = {
    "python": (
        _p("py-cli", "Command-line task manager", "Build a CLI app with argument parsing, file/JSON persistence, unit tests and package structure.",
           ("python", "testing", "git"), "beginner", 20),
        _p("py-api", "FastAPI REST service", "A small REST API with validation, persistence, auth and auto-generated OpenAPI docs.",
           ("python", "restapi", "database_design", "docker"), "intermediate", 30),
    ),
    "javascript": (
        _p("js-dashboard", "Interactive dashboard", "Vanilla JS dashboard with fetch, debounced search, charts and keyboard navigation.",
           ("javascript", "restapi", "uiux"), "beginner", 20),
        _p("js-browser-ext", "Browser extension", "A Manifest V3 extension that adds a feature to any page and stores state locally.",
           ("javascript", "webperf"), "intermediate", 25),
    ),
    "react": (
        _p("react-shop", "E-commerce storefront", "Product listing, cart state, routing, responsive layout and error boundaries.",
           ("react", "redux", "responsive", "restapi", "testing"), "intermediate", 45),
        _p("react-admin", "Admin panel", "Authenticated admin tool with tables, forms, optimistic updates and accessible components.",
           ("react", "typescript", "testing", "uiux"), "advanced", 55),
    ),
    "nodejs": (
        _p("node-auth", "Auth service", "Session/JWT auth, rate limiting, structured logging and unit + integration tests.",
           ("nodejs", "restapi", "security_basics", "testing"), "intermediate", 30),
    ),
    "sql": (
        _p("sql-reporting", "Analytics reporting layer", "Design a star schema, write window-function queries and build recurring reports.",
           ("sql", "sqladvanced", "database_design", "business_analytics"), "intermediate", 25),
    ),
    "database_design": (
        _p("db-modelling", "Schema design exercise", "Model an e-commerce domain, normalise it, justify indexes and write migration scripts.",
           ("database_design", "sql", "caching"), "intermediate", 20),
    ),
    "pandas": (
        _p("eda-dataset", "Exploratory data analysis", "Clean a messy public dataset, handle missing values and document findings.",
           ("pandas", "datavis", "statistics"), "beginner", 18),
    ),
    "statistics": (
        _p("ab-test", "A/B test analysis", "Design an experiment, run power analysis and report significance with caveats.",
           ("statistics", "experimentation", "pandas", "business_analytics"), "intermediate", 20),
    ),
    "ml": (
        _p("ml-pipeline", "End-to-end ML pipeline", "Feature engineering, cross-validated model selection, metrics and a written model card.",
           ("python", "ml", "pandas", "datavis", "git"), "intermediate", 40),
        _p("ml-recommender", "Recommendation system", "Build a content-based recommender over a public dataset and evaluate ranking quality.",
           ("ml", "python", "pandas", "webperf"), "advanced", 45),
    ),
    "deeplearning": (
        _p("dl-image", "Image classifier", "Train a CNN, use transfer learning, and serve predictions through an API.",
           ("deeplearning", "python", "mlops", "docker"), "advanced", 50),
    ),
    "nlp": (
        _p("nlp-chatbot", "Support ticket classifier", "Classify support tickets, handle imbalance, and expose predictions via API.",
           ("nlp", "python", "ml", "restapi"), "advanced", 45),
    ),
    "computer_vision": (
        _p("cv-dashboard", "Vision analytics tool", "Object detection over video frames with tracking and an annotated export.",
           ("computer_vision", "python", "datavis"), "advanced", 45),
    ),
    "mlops": (
        _p("mlops-serving", "Model serving service", "Package a model, containerise it, add CI, health checks and drift monitoring.",
           ("mlops", "docker", "cicd", "monitoring", "aws"), "advanced", 55),
    ),
    "dataeng": (
        _p("de-pipeline", "Batch + streaming pipeline", "Ingest CSV/API data into a warehouse, model it, and orchestrate with Airflow.",
           ("dataeng", "airflow", "sql", "python", "aws"), "advanced", 55),
    ),
    "spark": (
        _p("spark-bigdata", "Large-scale aggregation", "Process a large public dataset with Spark SQL and compare against pandas results.",
           ("spark", "dataeng", "sql"), "advanced", 35),
    ),
    "powerbi": (
        _p("bi-dashboard", "Stakeholder dashboard", "A Power BI / Looker dashboard with documented metrics and refresh automation.",
           ("powerbi", "datavis", "sql", "business_analytics"), "intermediate", 25),
    ),
    "datavis": (
        _p("viz-dashboard", "Interactive visualisation", "Publish an interactive chart set with honest axes, annotations and a written narrative.",
           ("datavis", "python", "communication"), "intermediate", 20),
    ),
    "docker": (
        _p("dockerise", "Containerised service", "Containerise a service, add a health check, and cut image size in half.",
           ("docker", "cicd", "restapi"), "intermediate", 15),
    ),
    "kubernetes": (
        _p("k8s-deploy", "Kubernetes deployment", "Deploy a service with a deployment, service, ingress, autoscaling and monitoring.",
           ("kubernetes", "docker", "monitoring", "networking"), "advanced", 40),
    ),
    "cicd": (
        _p("cicd-pipeline", "Automated CI/CD", "Lint, test, build, push, deploy on merge with a preview environment per branch.",
           ("cicd", "docker", "git", "aws"), "intermediate", 25),
    ),
    "terraform": (
        _p("iac-infra", "Infrastructure as code", "Provision a full environment (network, database, compute) from Terraform modules.",
           ("terraform", "aws", "devops"), "advanced", 35),
    ),
    "aws": (
        _p("aws-serverless", "Serverless API", "Build a serverless API with auth, a database and IaC, deployed on AWS.",
           ("aws", "restapi", "terraform", "monitoring"), "advanced", 45),
    ),
    "monitoring": (
        _p("obs-stack", "Observability stack", "Metrics, logs and traces for a small service, with alerts and an SLO dashboard.",
           ("monitoring", "devops", "cicd"), "intermediate", 25),
    ),
    "cybersecurity": (
        _p("soc-dashboard", "SOC alert triage lab", "Build a small SIEM-style lab: ingest logs, triage alerts, document an incident.",
           ("cybersecurity", "monitoring", "linux", "networksecurity"), "intermediate", 30),
    ),
    "ethical_hacking": (
        _p("pentest-report", "Authorised pentest report", "Run a scoped assessment on a deliberately vulnerable lab and write the remediation report.",
           ("ethical_hacking", "cybersecurity", "cryptography", "technical_writing"), "advanced", 40),
    ),
    "uiux": (
        _p("ux-case-study", "UX case study", "Research, journey map, wireframes, prototype and a documented usability test.",
           ("uiux", "figma", "research", "communication"), "intermediate", 35),
    ),
    "figma": (
        _p("design-system", "Design system", "A token-based component library in Figma with documented usage states.",
           ("figma", "uiux", "responsive"), "intermediate", 30),
    ),
    "testing": (
        _p("test-suite", "Automated test suite", "Unit, integration and contract tests with coverage reporting wired into CI.",
           ("testing", "cicd", "python", "git"), "intermediate", 20),
    ),
    "testautomation": (
        _p("e2e-suite", "End-to-end automation", "Playwright suite with data-driven scenarios and flake handling.",
           ("testautomation", "testing", "cicd", "javascript"), "advanced", 30),
    ),
    "android": (
        _p("android-compose", "Compose app", "A Jetpack Compose app with MVVM, navigation and offline caching.",
           ("android", "kotlin", "testing"), "advanced", 45),
    ),
    "ios": (
        _p("ios-swiftui", "SwiftUI app", "A SwiftUI app with Combine, async/await networking and unit tests.",
           ("ios", "swift", "testing"), "advanced", 45),
    ),
    "flutter": (
        _p("flutter-app", "Cross-platform app", "One Flutter codebase for Android and iOS with API integration and tests.",
           ("flutter", "restapi", "testing"), "advanced", 40),
    ),
    "reactnative": (
        _p("rn-app", "React Native app", "Cross-platform app with native modules, offline storage and release pipeline.",
           ("reactnative", "javascript", "testing"), "advanced", 45),
    ),
    "restapi": (
        _p("api-design", "Public API", "Design, document and version a REST API with OpenAPI, pagination, errors and rate limits.",
           ("restapi", "database_design", "testing", "technical_writing"), "intermediate", 30),
    ),
    "webperf": (
        _p("perf-budget", "Performance budget", "Set and enforce performance budgets, then show the before/after with Lighthouse.",
           ("webperf", "monitoring", "javascript"), "intermediate", 18),
    ),
    "caching": (
        _p("cache-layer", "Caching layer", "Add Redis caching with invalidation strategy and measure the hit-rate impact.",
           ("caching", "database_design", "monitoring", "docker"), "advanced", 30),
    ),
    "business_analytics": (
        _p("kpi-dashboard", "KPI dashboard", "Define business metrics, model them in SQL and publish a dashboard with written insight.",
           ("business_analytics", "sql", "datavis", "communication"), "intermediate", 25),
    ),
    "product_management": (
        _p("prd-project", "Product spec + launch", "Write a PRD, define success metrics, run a launch and report results.",
           ("product_management", "business_analytics", "communication", "uiux"), "intermediate", 35),
    ),
    "project_management": (
        _p("pm-plan", "Delivery plan", "Plan a real project with scope, risk register, timeline and a stakeholder update pack.",
           ("project_management", "process_mapping", "excel", "communication"), "intermediate", 20),
    ),
    "marketing": (
        _p("growth-experiment", "Growth experiment", "Design a measurable acquisition experiment and report CAC/ROAS honestly.",
           ("marketing", "business_analytics", "content_writing"), "intermediate", 25),
    ),
    "finance": (
        _p("financial-model", "Three-statement model", "Build a linked three-statement model with a scenario sensitivity table.",
           ("finance", "excel", "business_analytics"), "advanced", 35),
    ),
    "technical_writing": (
        _p("docs-project", "Documentation site", "Ship versioned API docs with quickstarts, runnable examples and a docs-as-code pipeline.",
           ("technical_writing", "restapi", "html", "git"), "intermediate", 25),
    ),
    "research": (
        _p("research-report", "Reproducible research report", "A literature review plus a reproducible analysis with documented method.",
           ("research", "statistics", "python", "technical_writing"), "advanced", 40),
    ),
    "electrical": (
        _p("circuit-design", "Circuit design project", "Design, simulate and prototype a small circuit with measurements and a report.",
           ("electrical", "electronics"), "intermediate", 30),
    ),
    "mechanical": (
        _p("cad-part", "Parametric part design", "A fully parametric part with tolerance analysis and a manufacturing drawing.",
           ("mechanical", "3d", "manufacturing"), "intermediate", 30),
    ),
    "civil": (
        _p("structural-study", "Structural study", "Load analysis, structural design and a written specification for a small structure.",
           ("civil", "excel", "project_management"), "advanced", 35),
    ),
    "electronics": (
        _p("embedded-sensor", "Embedded sensor node", "Firmware plus hardware for a sensor node with power management and telemetry.",
           ("electronics", "electrical", "c"), "advanced", 40),
    ),
}


def resources_for(skill_id: str) -> tuple[Resource, ...]:
    return RESOURCES.get(skill_id, ())


def projects_for(skill_id: str) -> tuple[ProjectIdea, ...]:
    return PROJECT_IDEAS.get(skill_id, ())