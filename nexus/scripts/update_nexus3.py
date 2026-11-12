import os

NEXUS_DIR = r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\NEXUS\src\nexus"

services = [
    ("dashboard/DashboardService.java", "DashboardService"),
    ("goals/GoalService.java", "GoalService"),
    ("tasks/TaskService.java", "TaskService"),
    ("finance/FinanceService.java", "FinanceService"),
    ("market/MarketService.java", "MarketService"),
    ("media/MediaService.java", "MediaService"),
    ("analytics/AnalyticsService.java", "AnalyticsService"),
]

for rel_path, class_name in services:
    path = os.path.join(NEXUS_DIR, rel_path)
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    target = f"public class {class_name}"
    
    replacement = f"""/**
 * The {class_name} acts as the 'Controller' or 'Business Logic' layer for its respective module.
 * 
 * In a professional software architecture (like MVC or MVVM), Services are responsible for:
 * 1. Managing data state (holding the lists of items, scores, or configurations).
 * 2. Processing business rules (e.g., verifying if an action is valid).
 * 3. Communicating with other parts of the application (publishing events to the EventBus).
 * 
 * By keeping this logic out of the GUI Panels, the code remains easy to test, maintain, and extend.
 */
public class {class_name}"""
    
    # Check if already has javadoc
    if "/**" not in content[:content.find(target)] and target in content:
        new_content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {rel_path}")
