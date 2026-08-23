import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from neo4j import GraphDatabase
from app.config import COGNODB_URI, COGNODB_USER, COGNODB_PASSWORD

ROLES = [
    ("software-engineer", "Software Engineer", "Engineering", "Builds and maintains production software systems."),
    ("frontend-engineer", "Frontend Engineer", "Engineering", "Builds accessible, responsive and interactive web interfaces."),
    ("backend-engineer", "Backend Engineer", "Engineering", "Designs APIs, services, data access and distributed backend systems."),
    ("data-scientist", "Data Scientist", "Data", "Uses statistics, experimentation and machine learning to solve data problems."),
    ("machine-learning-engineer", "Machine Learning Engineer", "AI / ML", "Builds, evaluates and deploys machine learning systems."),
    ("ai-engineer", "AI Engineer", "AI / ML", "Turns modern AI models into reliable applications and products."),
    ("devops-engineer", "DevOps Engineer", "Infrastructure", "Automates deployment, observability and reliable infrastructure."),
]

SKILLS = [
    ("python", "Python", "Programming"), ("javascript", "JavaScript", "Programming"), ("typescript", "TypeScript", "Programming"),
    ("sql", "SQL", "Data"), ("git", "Git", "Developer Tools"), ("rest-apis", "REST APIs", "Backend"),
    ("react", "React", "Frontend"), ("fastapi", "FastAPI", "Backend"), ("docker", "Docker", "DevOps"),
    ("linux", "Linux", "Systems"), ("pandas", "Pandas", "Data"), ("scikit-learn", "Scikit-learn", "Machine Learning"),
    ("machine-learning", "Machine Learning", "AI / ML"), ("statistics", "Statistics", "Data"),
    ("pytorch", "PyTorch", "Deep Learning"), ("llm-apps", "LLM Application Development", "Generative AI"),
    ("prompt-engineering", "Prompt Engineering", "Generative AI"), ("testing", "Software Testing", "Engineering"),
    ("system-design", "System Design", "Architecture"), ("cloud", "Cloud Fundamentals", "Infrastructure"),
]

PROJECTS = [
    ("rag-knowledge-assistant", "RAG Knowledge Assistant", "Retrieval-augmented assistant with document search and citations."),
    ("career-dashboard", "Career Analytics Dashboard", "Interactive dashboard for skill and role exploration."),
    ("image-classifier", "Image Classification API", "Production-style image classifier exposed through a REST API."),
    ("ci-cd-pipeline", "CI/CD Deployment Pipeline", "Automated test and deployment workflow for a containerized service."),
]

TECH = [
    ("python", "Python", "Language"), ("react", "React", "Frontend"), ("fastapi", "FastAPI", "Backend"),
    ("postgresql", "PostgreSQL", "Database"), ("docker", "Docker", "DevOps"), ("pytorch", "PyTorch", "ML"),
    ("scikit-learn", "Scikit-learn", "ML"), ("git", "Git", "Developer Tools"), ("github-actions", "GitHub Actions", "CI/CD"),
    ("openai-api", "LLM APIs", "Generative AI"),
]

ROLE_SKILLS = {
    "software-engineer": ["python", "javascript", "git", "rest-apis", "testing", "system-design", "sql"],
    "frontend-engineer": ["javascript", "typescript", "react", "git", "rest-apis", "testing"],
    "backend-engineer": ["python", "sql", "git", "rest-apis", "fastapi", "docker", "system-design", "testing"],
    "data-scientist": ["python", "sql", "git", "pandas", "statistics", "scikit-learn", "machine-learning"],
    "machine-learning-engineer": ["python", "sql", "git", "pandas", "scikit-learn", "machine-learning", "pytorch", "docker", "cloud"],
    "ai-engineer": ["python", "git", "rest-apis", "docker", "pytorch", "llm-apps", "prompt-engineering", "cloud", "testing"],
    "devops-engineer": ["python", "git", "docker", "linux", "cloud", "testing", "system-design"],
}

ROLE_TECH = {
    "software-engineer": ["python", "react", "postgresql", "git"],
    "frontend-engineer": ["react", "git"],
    "backend-engineer": ["python", "fastapi", "postgresql", "docker", "git"],
    "data-scientist": ["python", "postgresql", "scikit-learn", "git"],
    "machine-learning-engineer": ["python", "pytorch", "scikit-learn", "docker", "git"],
    "ai-engineer": ["python", "pytorch", "openai-api", "docker", "git"],
    "devops-engineer": ["python", "docker", "github-actions", "git"],
}

RELATED = [("machine-learning", "statistics"), ("machine-learning", "pytorch"), ("python", "pandas"),
           ("rest-apis", "fastapi"), ("docker", "cloud"), ("javascript", "typescript"),
           ("llm-apps", "prompt-engineering"), ("system-design", "cloud"), ("sql", "pandas")]


PROJECT_TECH = {
    "rag-knowledge-assistant": ["python", "fastapi", "openai-api"],
    "career-dashboard": ["react", "python", "postgresql"],
    "image-classifier": ["python", "pytorch", "docker"],
    "ci-cd-pipeline": ["docker", "github-actions", "git"],
}

PROJECT_SKILLS = {
    "rag-knowledge-assistant": ["python", "rest-apis", "llm-apps", "prompt-engineering"],
    "career-dashboard": ["javascript", "react", "sql"],
    "image-classifier": ["python", "pytorch", "machine-learning", "docker"],
    "ci-cd-pipeline": ["git", "docker", "cloud", "testing"],
}

def main():
    if not COGNODB_URI or not COGNODB_PASSWORD:
        raise SystemExit("Missing COGNODB_URI or COGNODB_PASSWORD. Create a .env file first.")
    driver = GraphDatabase.driver(COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        session.run("CREATE CONSTRAINT role_slug_unique IF NOT EXISTS FOR (n:Role) REQUIRE n.slug IS UNIQUE")
        session.run("CREATE CONSTRAINT skill_slug_unique IF NOT EXISTS FOR (n:Skill) REQUIRE n.slug IS UNIQUE")
        session.run("CREATE CONSTRAINT technology_slug_unique IF NOT EXISTS FOR (n:Technology) REQUIRE n.slug IS UNIQUE")
        session.run("CREATE CONSTRAINT project_slug_unique IF NOT EXISTS FOR (n:Project) REQUIRE n.slug IS UNIQUE")
        session.run("UNWIND $rows AS row CREATE (:Role {slug: row[0], name: row[1], category: row[2], description: row[3]})", rows=ROLES)
        session.run("UNWIND $rows AS row CREATE (:Skill {slug: row[0], name: row[1], category: row[2]})", rows=SKILLS)
        session.run("UNWIND $rows AS row CREATE (:Technology {slug: row[0], name: row[1], category: row[2]})", rows=TECH)
        session.run("UNWIND $rows AS row CREATE (:Project {slug: row[0], name: row[1], description: row[2]})", rows=PROJECTS)
        for role, skills in ROLE_SKILLS.items():
            session.run("MATCH (r:Role {slug:$role}) MATCH (s:Skill) WHERE s.slug IN $skills CREATE (r)-[:REQUIRES]->(s)", role=role, skills=skills)
        for role, tech in ROLE_TECH.items():
            session.run("MATCH (r:Role {slug:$role}) MATCH (t:Technology) WHERE t.slug IN $tech CREATE (r)-[:USES]->(t)", role=role, tech=tech)
        for a, b in RELATED:
            session.run("MATCH (a:Skill {slug:$a}), (b:Skill {slug:$b}) CREATE (a)-[:RELATED_TO]->(b)", a=a, b=b)
        for project, techs in PROJECT_TECH.items():
            session.run("MATCH (p:Project {slug:$project}) MATCH (t:Technology) WHERE t.slug IN $techs CREATE (p)-[:USES]->(t)", project=project, techs=techs)
        for project, skills in PROJECT_SKILLS.items():
            session.run("MATCH (p:Project {slug:$project}) MATCH (s:Skill) WHERE s.slug IN $skills CREATE (p)-[:DEMONSTRATES]->(s)", project=project, skills=skills)
    driver.close()
    print("Seed complete: 7 roles, 20 skills, 10 technologies, 4 projects and graph relationships created.")


if __name__ == "__main__":
    main()
