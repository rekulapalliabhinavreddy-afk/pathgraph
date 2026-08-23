from neo4j import Driver


class GraphRepository:
    def __init__(self, driver: Driver):
        self.driver = driver
        
    def health(self):
        self.driver.verify_connectivity()
        return True

    def roles(self):
        query = """
        MATCH (r:Role)
        RETURN r.slug AS slug, r.name AS name, r.category AS category, r.description AS description
        ORDER BY r.name
        """
        with self.driver.session() as session:
            return [dict(row) for row in session.run(query)]

    def skills(self):
        query = """
        MATCH (s:Skill)
        RETURN s.slug AS slug, s.name AS name, s.category AS category
        ORDER BY s.name
        """
        with self.driver.session() as session:
            return [dict(row) for row in session.run(query)]

    def profile(self, role_slug: str, current_skills: list[str]):
        query = """
        MATCH (r:Role {slug: $role_slug})
        OPTIONAL MATCH (r)-[:REQUIRES]->(required:Skill)
        WITH r, collect(required) AS required_skills
        UNWIND required_skills AS skill
        WITH r, skill, $current_skills AS current_slugs
        RETURN r.slug AS role_slug,
               r.name AS role_name,
               r.category AS category,
               r.description AS description,
               collect({
                   slug: skill.slug,
                   name: skill.name,
                   category: skill.category,
                   matched: skill.slug IN current_slugs
               }) AS skills
        """
        with self.driver.session() as session:
            record = session.run(query, role_slug=role_slug, current_skills=current_skills).single()
            if not record:
                return None
            data = record.data()
            skills = data.pop("skills", [])
            matched = [s for s in skills if s["matched"]]
            missing = [s for s in skills if not s["matched"]]
            score = round((len(matched) / len(skills)) * 100) if skills else 0
            return {**data, "skills": skills, "matched_skills": matched, "missing_skills": missing, "score": score}

    def related_roles(self, role_slug: str):
        # Two-hop graph traversal: Role -> Skill <- Role.
        query = """
        MATCH (target:Role {slug: $role_slug})-[:REQUIRES]->(shared:Skill)<-[:REQUIRES]-(related:Role)
        WHERE related.slug <> target.slug
        WITH related, count(DISTINCT shared) AS shared_skills
        RETURN related.slug AS slug,
               related.name AS name,
               related.category AS category,
               related.description AS description,
               shared_skills
        ORDER BY shared_skills DESC, related.name
        LIMIT 5
        """
        with self.driver.session() as session:
            return [dict(row) for row in session.run(query, role_slug=role_slug)]

    def technologies(self, role_slug: str):
        # Multi-hop: Role -> Skill <- Skill -> Technology is represented by
        # direct role technology links plus related skills in the graph.
        query = """
        MATCH (r:Role {slug: $role_slug})-[:USES]->(t:Technology)
        RETURN t.slug AS slug, t.name AS name, t.category AS category
        ORDER BY t.name
        """
        with self.driver.session() as session:
            return [dict(row) for row in session.run(query, role_slug=role_slug)]

        def neighborhood(self, role_slug: str):
            query = """
            MATCH p=(r:Role {slug: $role_slug})-[:REQUIRES|USES|RELATED_TO*1..2]-(n)
            WITH collect(p) AS paths
        UNWIND paths AS p
        UNWIND nodes(p) AS node
        WITH DISTINCT node
        WHERE node.slug IS NOT NULL
        RETURN labels(node)[0] AS type,
               node.slug AS slug,
               coalesce(node.name, '') AS name,
               coalesce(node.category, '') AS category
        LIMIT 80
        """

        edge_query = """
        MATCH p=(r:Role {slug: $role_slug})-[:REQUIRES|USES|RELATED_TO*1..2]-(n)
        UNWIND relationships(p) AS rel
        RETURN startNode(rel).slug AS source,
               endNode(rel).slug AS target,
               type(rel) AS relationship
        LIMIT 100
        """

        with self.driver.session() as session:
            nodes = [
                dict(row)
                for row in session.run(query, role_slug=role_slug)
            ]
            edges = [
                dict(row)
                for row in session.run(edge_query, role_slug=role_slug)
            ]

        return {"nodes": nodes, "edges": edges}
