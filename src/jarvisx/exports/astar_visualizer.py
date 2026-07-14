import heapq
import random
import os
import sys

# Ensure Jarvis Vault Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from jarvisx.tools.db_manager import DatabaseManager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

class Node:
    def __init__(self, x, y, walk=True):
        self.x = x
        self.y = y
        self.walkable = walk
        self.parent = None
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')

    def __lt__(self, other):
        return self.f < other.f

def manhattan(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def generate_grid(width, height, density):
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            if (x == 0 and y == 0) or (x == width-1 and y == height-1):
                row.append(Node(x, y, True))
            else:
                walk = random.random() > density
                row.append(Node(x, y, walk))
        grid.append(row)
    return grid

def get_neighbors(grid, node, width, height):
    neighbors = []
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dx, dy in dirs:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < width and 0 <= ny < height:
            if grid[ny][nx].walkable:
                neighbors.append(grid[ny][nx])
    return neighbors

def astar(grid, start_node, end_node, width, height):
    open_set = []
    start_node.g = 0
    start_node.h = manhattan(start_node, end_node)
    start_node.f = start_node.g + start_node.h
    heapq.heappush(open_set, start_node)
    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)
        
        if current.x == end_node.x and current.y == end_node.y:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        for neighbor in get_neighbors(grid, current, width, height):
            if (neighbor.x, neighbor.y) in closed_set:
                continue

            tentative_g = current.g + 1
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = manhattan(neighbor, end_node)
                neighbor.f = neighbor.g + neighbor.h
                if not any(n for n in open_set if n.x == neighbor.x and n.y == neighbor.y):
                    heapq.heappush(open_set, neighbor)

    return None

def print_grid(grid, path, width, height):
    path_set = set(path) if path else set()
    for y in range(height):
        line = ""
        for x in range(width):
            if (x, y) in path_set:
                line += "* "
            elif not grid[y][x].walkable:
                line += "# "
            else:
                line += ". "
        print(line)

async def telemetry_log():
    if DB_AVAILABLE:
        db = DatabaseManager()
        await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
        await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                               ("A-Star Algorithm Generated", "src/jarvisx/exports/astar_visualizer.py"))
    else:
        print("[MOCK TELEMETRY] A-Star Algorithm Generated")

if __name__ == '__main__':
    W, H = 20, 20
    DENSITY = 0.25
    grid = generate_grid(W, H, DENSITY)
    start = grid[0][0]
    end = grid[H-1][W-1]
    
    path = astar(grid, start, end, W, H)
    if not path:
        print("No valid path found due to RNG obstacles. Re-running with empty grid.")
        # Guarantee path
        grid = generate_grid(W, H, 0.0)
        start = grid[0][0]
        end = grid[H-1][W-1]
        path = astar(grid, start, end, W, H)
        
    print_grid(grid, path, W, H)
    
    # Run async telemetry
    import asyncio
    asyncio.run(telemetry_log())
