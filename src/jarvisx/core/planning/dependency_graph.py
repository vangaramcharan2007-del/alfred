from typing import List, Dict, Any, Set
import collections

class DependencyGraph:
    """Manages the DAG of tasks to enforce ordering and detect cycles."""
    
    def __init__(self, tasks: List[Dict[str, Any]]):
        self.tasks = {t['id']: t for t in tasks}
        self.adj = collections.defaultdict(list)
        self.in_degree = collections.defaultdict(int)
        
        for task in tasks:
            tid = task['id']
            if tid not in self.in_degree:
                self.in_degree[tid] = 0
                
            for dep in task.get('depends_on', []):
                self.adj[dep].append(tid)
                self.in_degree[tid] += 1
                
    def detect_cycles(self) -> bool:
        """Returns True if there is a circular dependency."""
        in_degree_copy = self.in_degree.copy()
        queue = collections.deque([t for t, d in in_degree_copy.items() if d == 0])
        count = 0
        
        while queue:
            node = queue.popleft()
            count += 1
            for neighbor in self.adj[node]:
                in_degree_copy[neighbor] -= 1
                if in_degree_copy[neighbor] == 0:
                    queue.append(neighbor)
                    
        return count != len(self.tasks)
        
    def get_executable_tasks(self, completed_tasks: Set[str]) -> List[Dict[str, Any]]:
        """Returns tasks that have all dependencies met and are not yet completed."""
        executable = []
        for tid, task in self.tasks.items():
            if tid in completed_tasks:
                continue
            
            deps = task.get('depends_on', [])
            if all(dep in completed_tasks for dep in deps):
                executable.append(task)
                
        return executable
