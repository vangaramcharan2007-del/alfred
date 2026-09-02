from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.architecture_models import SystemArchitecture, Component, ArchitectureDecision

class ArchitecturePlanner:
    def propose_architecture(
        self,
        idea_description: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> SystemArchitecture:
        idea_lower = idea_description.lower()
        constraints = constraints or {}

        project_name = constraints.get("project_name") or self._extract_project_name(idea_description)

        # Default multi-tier AI architectural template tailored to the query
        reqs = [
            f"Fulfill core requirement: {idea_description}",
            "Ensure high availability and low latency streaming/response times",
            "Provide safe data persistence and secure API endpoints",
            "Support modular agentic extensibility"
        ]

        if "meeting" in idea_lower or "audio" in idea_lower or "real-time" in idea_lower:
            components = [
                Component(
                    name="AudioStreamingClient",
                    responsibility="Captures real-time audio input and streams chunks via WebSocket",
                    dependencies=["APIGateway"],
                    interfaces=["WebSocket /ws/stream"]
                ),
                Component(
                    name="APIGateway",
                    responsibility="Handles authentication, request routing, and rate limiting",
                    dependencies=["AuthService", "TranscriberService"],
                    interfaces=["REST /api/v1", "WebSocket /ws"]
                ),
                Component(
                    name="TranscriberService",
                    responsibility="Processes streaming audio into text transcripts",
                    dependencies=["MeetingIntelligenceAgent"],
                    interfaces=["Internal gRPC / Event Bus"]
                ),
                Component(
                    name="MeetingIntelligenceAgent",
                    responsibility="Extracts summaries, key takeaways, and action items using LLM",
                    dependencies=["DatabaseStore"],
                    interfaces=["Internal Agent API"]
                ),
                Component(
                    name="DatabaseStore",
                    responsibility="Persists users, meeting metadata, transcripts, and summaries",
                    dependencies=[],
                    interfaces=["SQL / ORM Interface"]
                )
            ]

            tech_stack = {
                "frontend": constraints.get("frontend", "Next.js + Tailwind CSS"),
                "backend": constraints.get("backend", "FastAPI (Python)"),
                "database": constraints.get("database", "PostgreSQL + Redis"),
                "ai_layer": constraints.get("ai_layer", "Whisper STT + Gemini / Local LLM"),
                "infrastructure": constraints.get("infrastructure", "Docker + Kubernetes")
            }

            data_flow = [
                "Client -> WebSocket connection -> APIGateway",
                "APIGateway -> AudioStream -> TranscriberService",
                "TranscriberService -> Real-time Text Transcript -> MeetingIntelligenceAgent",
                "MeetingIntelligenceAgent -> Summary & Action Items -> DatabaseStore",
                "DatabaseStore -> REST API -> Client Dashboard"
            ]

            api_design = [
                {"endpoint": "POST /api/v1/meetings", "description": "Create new meeting session"},
                {"endpoint": "WS /ws/v1/meetings/{id}/audio", "description": "Real-time audio streaming connection"},
                {"endpoint": "GET /api/v1/meetings/{id}/summary", "description": "Fetch AI-generated summary and action items"}
            ]

            database_design = [
                {"table": "users", "columns": ["id (UUID)", "email (VARCHAR)", "created_at (TIMESTAMP)"]},
                {"table": "meetings", "columns": ["id (UUID)", "user_id (UUID)", "title (VARCHAR)", "status (VARCHAR)"]},
                {"table": "transcripts", "columns": ["id (UUID)", "meeting_id (UUID)", "speaker (VARCHAR)", "text (TEXT)"]},
                {"table": "summaries", "columns": ["id (UUID)", "meeting_id (UUID)", "summary (TEXT)", "action_items (JSONB)"]}
            ]

            decisions = [
                ArchitectureDecision(
                    decision="Use FastAPI for Backend Service",
                    alternatives_considered=["Django", "Express.js", "Flask"],
                    reasoning="Native async support for WebSocket streaming and high-performance integration with Python AI libraries",
                    tradeoffs=["Smaller built-in admin interface compared to Django"]
                ),
                ArchitectureDecision(
                    decision="Use PostgreSQL + Redis Hybrid Storage",
                    alternatives_considered=["MongoDB", "DynamoDB"],
                    reasoning="PostgreSQL handles relational integrity for users/transcripts while Redis provides instant caching for active streams",
                    tradeoffs=["Requires managing dual database instances"]
                )
            ]
        else:
            components = [
                Component(
                    name="FrontendClient",
                    responsibility="User interface and interaction layer",
                    dependencies=["APIService"],
                    interfaces=["HTTP / REST"]
                ),
                Component(
                    name="APIService",
                    responsibility="Core backend application logic and endpoint controller",
                    dependencies=["DatabaseStore", "AIEngine"],
                    interfaces=["REST API / JSON"]
                ),
                Component(
                    name="AIEngine",
                    responsibility="Generative AI and task orchestration",
                    dependencies=["DatabaseStore"],
                    interfaces=["Internal Service API"]
                ),
                Component(
                    name="DatabaseStore",
                    responsibility="Application state and data storage",
                    dependencies=[],
                    interfaces=["SQL / NoSQL API"]
                )
            ]

            tech_stack = {
                "frontend": constraints.get("frontend", "React / TypeScript"),
                "backend": constraints.get("backend", "FastAPI / Python"),
                "database": constraints.get("database", "PostgreSQL"),
                "ai_layer": constraints.get("ai_layer", "Jarvis X Cognitive Engine"),
                "infrastructure": constraints.get("infrastructure", "Docker Containers")
            }

            data_flow = [
                "User -> FrontendClient -> REST Request -> APIService",
                "APIService -> Task Payload -> AIEngine",
                "AIEngine -> Storage Read/Write -> DatabaseStore",
                "DatabaseStore -> Results -> APIService -> FrontendClient"
            ]

            api_design = [
                {"endpoint": "GET /api/v1/health", "description": "Service health check"},
                {"endpoint": "POST /api/v1/tasks", "description": "Submit asynchronous processing task"}
            ]

            database_design = [
                {"table": "tasks", "columns": ["id", "description", "status", "created_at"]}
            ]

            decisions = [
                ArchitectureDecision(
                    decision="Modular Microservice Architecture",
                    alternatives_considered=["Monolithic Application"],
                    reasoning="Decouples frontend presentation from high-compute AI workloads",
                    tradeoffs=["Slightly increased network latency between services"]
                )
            ]

        risks = [
            "Network latency spikes during real-time streaming",
            "High concurrency memory spikes on AI inference workers",
            "Unmanaged schema migrations across component releases"
        ]

        return SystemArchitecture(
            project_name=project_name,
            requirements=reqs,
            components=components,
            technology_stack=tech_stack,
            data_flow=data_flow,
            api_design=api_design,
            database_design=database_design,
            risks=risks,
            decisions=decisions
        )

    def _extract_project_name(self, idea_description: str) -> str:
        words = [w for w in idea_description.split() if len(w) > 3]
        if words:
            return "".join(w.capitalize() for w in words[:3]) + "System"
        return "JarvisXSystem"
