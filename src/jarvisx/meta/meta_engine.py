from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.meta.capability_introspection import CapabilityIntrospector
from jarvisx.meta.system_graph import SystemKnowledgeGraph
from jarvisx.meta.performance_monitor import PerformanceMonitor
from jarvisx.meta.performance_analyzer import PerformanceAnalyzer
from jarvisx.meta.failure_memory import FailureMemory
from jarvisx.meta.failure_analyzer import FailureAnalyzer
from jarvisx.meta.improvement_planner import ImprovementPlanner
from jarvisx.meta.meta_memory import MetaMemory
from jarvisx.meta.decision_engine import EnhancedDecisionEngine
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.coding.metrics import CodingMetrics

class MetaCognitionEngine:
    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.registry = registry or CapabilityRegistry()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

        self.introspector = CapabilityIntrospector(registry=self.registry)
        self.system_graph = SystemKnowledgeGraph()
        self.perf_monitor = PerformanceMonitor(metrics=self.metrics)
        self.perf_analyzer = PerformanceAnalyzer(monitor=self.perf_monitor)
        self.failure_memory = FailureMemory()
        self.failure_analyzer = FailureAnalyzer(failure_memory=self.failure_memory)
        self.planner = ImprovementPlanner(performance_analyzer=self.perf_analyzer, failure_analyzer=self.failure_analyzer)
        self.meta_memory = MetaMemory()
        self.decision_engine = EnhancedDecisionEngine(introspector=self.introspector, performance_monitor=self.perf_monitor)

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="meta.engine",
                name="Jarvis X Meta-Cognition Engine",
                version="1.0.0",
                author="Jarvis X",
                category="meta",
                supported_actions=["introspect", "analyze_performance", "plan_improvement", "evaluate_decision"],
                handler=self.execute_meta_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        self.introspector.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def build_system_knowledge_graph(self) -> SystemKnowledgeGraph:

        caps_graph = self.introspector.scan_registered_capabilities()
        for node in caps_graph.list_nodes():
            self.system_graph.add_node(
                entity_id=node.id,
                entity_type="capability",
                name=node.name,
                metadata={"actions": node.actions}
            )

        # Pre-populate provider/model entities
        self.system_graph.add_node("provider.goose", "provider", "Goose Autonomous Engineer")
        self.system_graph.add_node("provider.openhands", "provider", "OpenHands Software Engineer")
        self.system_graph.add_node("model.ollama.qwen", "model", "qwen2.5-coder:7b")

        self.system_graph.add_edge("provider.goose", "capability.coding.agent", "improves")
        self.system_graph.add_edge("provider.openhands", "capability.coding.agent", "improves")
        self.system_graph.add_edge("capability.meta.engine", "provider.goose", "uses")

        return self.system_graph

    async def run_self_analysis(self) -> Dict[str, Any]:
        start_t = time.time()

        # 1. Capability Introspection
        cap_summary = self.introspector.introspect()
        await self.bus.publish(Event(
            type="meta.capability.discovered",
            source="meta_engine",
            payload={"count": cap_summary["total_capabilities"]}
        ))

        # 2. Build System Graph
        await self.build_system_knowledge_graph()

        # 3. Performance & Gap Analysis
        degraded = self.perf_analyzer.detect_degraded_capabilities()
        if degraded:
            await self.bus.publish(Event(
                type="meta.knowledge.gap.detected",
                source="performance_analyzer",
                payload={"degraded": degraded}
            ))

        # 4. Self-Improvement Plan
        improvement_plans = self.planner.generate_improvement_plan()
        await self.bus.publish(Event(
            type="meta.improvement.planned",
            source="improvement_planner",
            payload={"plans_count": len(improvement_plans), "plans": [p.to_dict() for p in improvement_plans]}
        ))

        # 5. Record Memory Snapshot
        snap = self.meta_memory.record_evolution_step(
            milestone="Self-Analysis Completed",
            capability_count=cap_summary["total_capabilities"],
            confidence=0.96
        )

        duration = time.time() - start_t
        self.metrics.self_analysis_runs += 1
        self.metrics.capability_count = cap_summary["total_capabilities"]
        self.metrics.improvement_plans = len(improvement_plans)
        self.metrics.system_confidence = 0.96

        await self.bus.publish(Event(
            type="meta.self_analysis.completed",
            source="meta_engine",
            payload={"duration": round(duration, 3), "confidence": 0.96}
        ))

        return {
            "capabilities_summary": cap_summary,
            "system_graph": self.system_graph.to_dict(),
            "improvement_plans": [p.to_dict() for p in improvement_plans],
            "evolution_snapshot": snap.milestone,
            "confidence": 0.96
        }

    async def execute_meta_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "introspect":
            return self.introspector.introspect()
        elif action == "analyze_performance":
            return self.perf_monitor.get_performance_summary()
        elif action == "plan_improvement":
            plans = self.planner.generate_improvement_plan()
            return {"improvement_plans": [p.to_dict() for p in plans]}
        elif action == "evaluate_decision":
            task = kwargs.get("task_description", "Generic task")
            return self.decision_engine.evaluate_task_execution(task)

        raise NotImplementedError(f"Action '{action}' is not supported by MetaCognitionEngine.")
