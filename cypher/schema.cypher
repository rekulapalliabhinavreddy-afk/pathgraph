// Run once in CognoDB.
CREATE CONSTRAINT role_slug_unique IF NOT EXISTS FOR (n:Role) REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT skill_slug_unique IF NOT EXISTS FOR (n:Skill) REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT technology_slug_unique IF NOT EXISTS FOR (n:Technology) REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT project_slug_unique IF NOT EXISTS FOR (n:Project) REQUIRE n.slug IS UNIQUE;
