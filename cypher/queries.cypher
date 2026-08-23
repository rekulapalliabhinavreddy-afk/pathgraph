// 1. Target role requirements
MATCH (r:Role {slug: $role_slug})-[:REQUIRES]->(s:Skill)
RETURN s.slug AS slug, s.name AS name, s.category AS category
ORDER BY s.name;

// 2. Two-hop traversal: target role -> shared skill -> related role
MATCH (target:Role {slug: $role_slug})-[:REQUIRES]->(shared:Skill)<-[:REQUIRES]-(related:Role)
WHERE related.slug <> target.slug
RETURN related.name AS related_role, count(DISTINCT shared) AS shared_skills
ORDER BY shared_skills DESC;

// 3. Bounded graph neighborhood
MATCH p=(r:Role {slug: $role_slug})-[:REQUIRES|USES|RELATED_TO*1..2]-(n)
RETURN p LIMIT 50;

// 4. Graph-native path between two roles
MATCH p=shortestPath((a:Role {slug: $from_role})-[:REQUIRES|USES|RELATED_TO*..4]-(b:Role {slug: $to_role}))
RETURN [node IN nodes(p) | coalesce(node.name, node.slug)] AS path;
