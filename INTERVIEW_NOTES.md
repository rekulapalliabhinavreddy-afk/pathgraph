# Wexa Interview Notes — PathGraph

## 30-second explanation

PathGraph is a graph-backed career exploration application. A role connects to the skills it requires and the technologies it uses. Skills can also connect to related skills. This lets the app answer relationship-heavy questions such as finding adjacent roles through shared skills and exploring a bounded graph neighborhood around a target role.

## Why CognoDB?

The core data is a network. The product needs traversals across roles, skills and technologies. Cypher expresses these paths directly, while a relational implementation would need repeated joins or recursive queries for the same relationship exploration.

## Why FastAPI?

It gives a small, explicit API layer with type validation, clear HTTP errors and easy deployment in Python. The official Neo4j driver is used directly from the repository layer.

## Why parameterized Cypher?

User-controlled values such as the selected role and current skills are passed as driver parameters. This avoids string-concatenating user input into Cypher and keeps query structure separate from data.

## Explain the two-hop query

`Role -> REQUIRES -> Skill <- REQUIRES <- Role`

Starting from the target role, we traverse to its skills and then back to other roles that require those same skills. Counting the shared skills gives a simple relevance signal for adjacent roles.

## Explain the graph-native query

The repository includes a bounded variable-length neighborhood traversal and a shortest-path query. Variable-length traversal is useful when the number of relationship hops is part of the question rather than a fixed number of joins.

## Error handling

The API performs a database health check before database-backed operations. If CognoDB is unavailable or credentials are missing, the API returns a controlled 503 response instead of exposing a stack trace. The frontend turns the response into a human-readable error banner.

## Security

Credentials are read from environment variables. `.env` is ignored by Git and only `.env.example` is committed.

## If asked what you would improve next

1. Add authentication and user profiles.
2. Persist a user's saved career plan.
3. Add richer project-to-skill evidence and confidence scores.
4. Add graph indexes/constraints and query profiling as the dataset grows.
5. Add automated tests and CI for the API and seed process.
