# 2–3 Minute Demo Script

## 0:00–0:20 — Problem
"PathGraph helps a person understand the relationship between their current skills and a target software or AI role. The key idea is that careers are networks, so the application uses a graph rather than treating the data as isolated rows."

## 0:20–0:50 — Explore
Select **Machine Learning Engineer**. Select Python, SQL and Git. Click **Build my career path**.

## 0:50–1:25 — Career path
Point out the match percentage, skills already covered, missing skills, adjacent roles and recommended technologies.

Say: "The related-role section is powered by a two-hop Cypher traversal: role to required skill to another role requiring that skill."

## 1:25–2:05 — Graph
Open **Graph**. Explain the central role and connected nodes.

Say: "This is the graph neighborhood stored in CognoDB. The UI is not a mock visualization—the API queries the graph and turns the returned nodes into this view."

## 2:05–2:30 — Engineering
Show the repository briefly. Point to `scripts/seed.py`, `cypher/queries.cypher`, `.env.example`, the repository layer and README.

Say: "Database credentials are environment variables, all user-controlled Cypher values are parameters, and the API has a controlled 503 state when the database is unavailable."

## 2:30–2:45 — Close
"The application is intentionally small, but the data model and queries are designed around graph relationships so the database choice is meaningful rather than incidental."
