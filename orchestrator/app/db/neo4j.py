from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver, Record
from app.config import settings


class Neo4jClient:
    _driver: Optional[AsyncDriver] = None

    @classmethod
    async def connect(cls):
        if cls._driver is None:
            cls._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connectivity
            async with cls._driver.session() as session:
                await session.run("RETURN 1")
        return cls._driver

    @classmethod
    async def close(cls):
        if cls._driver:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    async def create_system_node(cls, run_id: str, system_id: str, system_name: str, version: str, vendor: str):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                """MERGE (s:AISystem {system_id: $system_id})
                   SET s.system_name = $system_name, s.version = $version, s.vendor = $vendor
                   WITH s
                   MERGE (r:AuditRun {run_id: $run_id})
                   MERGE (s)-[:HAS_RUN]->(r)""",
                run_id=run_id, system_id=system_id, system_name=system_name,
                version=version, vendor=vendor,
            )

    @classmethod
    async def create_phase_node(cls, run_id: str, phase_number: int, status: str, artifact_hash: str):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                """MERGE (p:Phase {run_id: $run_id, phase_number: $phase_number})
                   SET p.status = $status, p.artifact_hash = $artifact_hash
                   WITH p
                   MATCH (r:AuditRun {run_id: $run_id})
                   MERGE (r)-[:INCLUDES_PHASE {order: $phase_number}]->(p)""",
                run_id=run_id, phase_number=phase_number, status=status, artifact_hash=artifact_hash,
            )

    @classmethod
    async def create_finding_node(cls, finding_id: str, severity: str, regulation: str, article: str):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                """MERGE (f:Finding {finding_id: $finding_id})
                   SET f.severity = $severity, f.regulation = $regulation, f.article = $article""",
                finding_id=finding_id, severity=severity, regulation=regulation, article=article,
            )

    @classmethod
    async def link_finding_to_phase(cls, finding_id: str, phase_number: int, run_id: str):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                """MATCH (f:Finding {finding_id: $finding_id})
                   MATCH (p:Phase {run_id: $run_id, phase_number: $phase_number})
                   MERGE (p)-[:RAISED_FINDING]->(f)""",
                finding_id=finding_id, run_id=run_id, phase_number=phase_number,
            )

    @classmethod
    async def link_phase_dependency(cls, run_id: str, phase_from: int, phase_to: int):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                """MATCH (p1:Phase {run_id: $run_id, phase_number: $phase_from})
                   MATCH (p2:Phase {run_id: $run_id, phase_number: $phase_to})
                   MERGE (p1)-[:DEPENDS_ON]->(p2)""",
                run_id=run_id, phase_from=phase_from, phase_to=phase_to,
            )

    @classmethod
    async def get_impact_graph(cls, run_id: str) -> list[Record]:
        assert cls._driver is not None
        async with cls._driver.session() as session:
            result = await session.run(
                """MATCH (r:AuditRun {run_id: $run_id})-[*1..3]-(n)
                   RETURN labels(n) as node_labels, n
                   LIMIT 200""",
                run_id=run_id,
            )
            return [record async for record in result]

    @classmethod
    async def get_reaudit_scope(cls, run_id: str, changed_components: list[str]) -> list[int]:
        """Returns phase numbers that need re-execution based on changed components."""
        assert cls._driver is not None
        async with cls._driver.session() as session:
            result = await session.run(
                """MATCH (p:Phase {run_id: $run_id})-[r:DEPENDS_ON]->(dep)
                   WHERE dep.status IN ['PASS', 'FAIL']
                   RETURN DISTINCT p.phase_number as phase_number""",
                run_id=run_id,
            )
            phases = [record["phase_number"] async for record in result]
            return phases

    @classmethod
    async def detach_delete_subject(cls, email_hash: str):
        assert cls._driver is not None
        async with cls._driver.session() as session:
            await session.run(
                "MATCH (p:PersonNode {email_hash: $email_hash}) DETACH DELETE p",
                email_hash=email_hash,
            )
