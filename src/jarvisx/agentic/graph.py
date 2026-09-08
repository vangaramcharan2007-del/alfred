"""Task graph: a DAG of work items the scheduler executes in dependency waves."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from jarvisx.agentic.types import TaskNode, new_id


class GraphError(ValueError):
    """Raised for malformed graphs (cycles, dangling dependencies, duplicate ids)."""


class TaskGraph:
    """Validated DAG over :class:`TaskNode` objects."""

    def __init__(self, nodes: Sequence[TaskNode], graph_id: str | None = None):
        self.graph_id = graph_id or new_id("graph")
        self._nodes: Dict[str, TaskNode] = {}
        for node in nodes:
            self.add(node)
        self._validate()

    # -- construction ------------------------------------------------------ #

    def add(self, node: TaskNode) -> None:
        if node.id in self._nodes:
            raise GraphError(f"duplicate node id '{node.id}'")
        self._nodes[node.id] = node

    # -- accessors --------------------------------------------------------- #

    @property
    def nodes(self) -> List[TaskNode]:
        return list(self._nodes.values())

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self):
        return iter(self._nodes.values())

    def get(self, node_id: str) -> TaskNode:
        try:
            return self._nodes[node_id]
        except KeyError:
            raise GraphError(f"unknown node '{node_id}'") from None

    def roots(self) -> List[TaskNode]:
        return [n for n in self._nodes.values() if not n.depends_on]

    def dependents(self, node_id: str) -> List[TaskNode]:
        return [n for n in self._nodes.values() if node_id in n.depends_on]

    def downstream(self, node_id: str) -> List[str]:
        """Every node transitively depending on `node_id`."""
        found: List[str] = []
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for child in self.dependents(current):
                if child.id not in found:
                    found.append(child.id)
                    frontier.append(child.id)
        return found

    # -- validation -------------------------------------------------------- #

    def _validate(self) -> None:
        for node in self._nodes.values():
            for dep in node.depends_on:
                if dep not in self._nodes:
                    raise GraphError(
                        f"node '{node.id}' depends on unknown node '{dep}'"
                    )
                if dep == node.id:
                    raise GraphError(f"node '{node.id}' depends on itself")
        if self._find_cycle():
            raise GraphError(f"cycle detected in graph: {self._find_cycle()}")

    def _find_cycle(self) -> List[str] | None:
        WHITE, GREY, BLACK = 0, 1, 2
        colour: Dict[str, int] = {nid: WHITE for nid in self._nodes}
        path: List[str] = []

        def visit(node_id: str) -> List[str] | None:
            colour[node_id] = GREY
            path.append(node_id)
            for dep in self._nodes[node_id].depends_on:
                if colour[dep] == GREY:
                    return path[path.index(dep):] + [dep]
                if colour[dep] == WHITE:
                    found = visit(dep)
                    if found:
                        return found
            path.pop()
            colour[node_id] = BLACK
            return None

        for node_id in self._nodes:
            if colour[node_id] == WHITE:
                found = visit(node_id)
                if found:
                    return found
        return None

    # -- execution planning ------------------------------------------------ #

    def topological_order(self) -> List[TaskNode]:
        """Kahn's algorithm; raises on cycles."""
        remaining = {nid: set(node.depends_on) for nid, node in self._nodes.items()}
        ordered: List[TaskNode] = []
        while remaining:
            ready = sorted(nid for nid, deps in remaining.items() if not deps)
            if not ready:
                raise GraphError(f"cycle among {sorted(remaining)}")
            for node_id in ready:
                ordered.append(self._nodes[node_id])
                del remaining[node_id]
            for deps in remaining.values():
                deps.difference_update(ready)
        return ordered

    def waves(self) -> List[List[TaskNode]]:
        """Group nodes into batches that can safely run in parallel."""
        waves: List[List[TaskNode]] = []
        done: set[str] = set()
        pending = list(self._nodes.values())
        while pending:
            ready = [n for n in pending if set(n.depends_on) <= done]
            if not ready:
                raise GraphError(
                    f"unresolvable dependencies for {[n.id for n in pending]}"
                )
            ready.sort(key=lambda n: n.id)
            waves.append(ready)
            done.update(n.id for n in ready)
            pending = [n for n in pending if n.id not in done]
        return waves

    def to_dict(self) -> Dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "waves": [[n.id for n in wave] for wave in self.waves()],
        }

    def render(self) -> str:
        """Compact ASCII rendering, handy in logs and demos."""
        lines = [f"TaskGraph {self.graph_id}"]
        for index, wave in enumerate(self.waves(), start=1):
            lines.append(f"  wave {index}:")
            for node in wave:
                deps = f"  <- {','.join(node.depends_on)}" if node.depends_on else ""
                lines.append(f"    [{node.id}] ({node.role}) {node.instruction[:70]}{deps}")
        return "\n".join(lines)
