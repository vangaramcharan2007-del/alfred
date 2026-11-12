import os

NEXUS_DIR = r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\NEXUS\src\nexus"

def update_file(rel_path, target, replacement):
    path = os.path.join(NEXUS_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if target in content:
        new_content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {rel_path}")
    else:
        print(f"Target not found in {rel_path}")

# --- NeuralVisualizerPanel.java ---
target_nv = """public class NeuralVisualizerPanel extends JPanel implements NexusListener {"""
replacement_nv = """/**
 * The NeuralVisualizerPanel is a custom graphical component that provides a futuristic, 
 * node-based representation of the application's internal state.
 * 
 * It visually displays the core modules (Dashboard, Finance, Tasks, etc.) as connected nodes.
 * By implementing NexusListener, it can react to global events (like budget changes) 
 * and animate particles flowing between nodes to represent data movement.
 */
public class NeuralVisualizerPanel extends JPanel implements NexusListener {"""
update_file("dashboard/NeuralVisualizerPanel.java", target_nv, replacement_nv)

target_nv2 = """    @Override
    protected void paintComponent(Graphics g) {"""
replacement_nv2 = """    /**
     * This method is the heart of the custom graphics. It is called repeatedly by the Swing framework
     * (triggered by our Timer) to redraw the screen frame-by-frame, creating a smooth animation.
     */
    @Override
    protected void paintComponent(Graphics g) {"""
update_file("dashboard/NeuralVisualizerPanel.java", target_nv2, replacement_nv2)

target_nv3 = """        // Draw connections
        g2.setColor(new Color(0, 255, 255, 30));
        for (int i = 0; i < nodeNames.length; i++) {
            for (int j = i + 1; j < nodeNames.length; j++) {
                Point p1 = getPoint(i, cx, cy, radius);
                Point p2 = getPoint(j, cx, cy, radius);
                g2.drawLine(p1.x, p1.y, p2.x, p2.y);
            }
            Point p = getPoint(i, cx, cy, radius);
            g2.drawLine(cx, cy, p.x, p.y);
        }"""
replacement_nv3 = """        // Step 1: Draw lines connecting all nodes to each other, creating a 'web' effect.
        // We use a semi-transparent cyan color (alpha = 30) for a subtle tech look.
        g2.setColor(new Color(0, 255, 255, 30));
        for (int i = 0; i < nodeNames.length; i++) {
            for (int j = i + 1; j < nodeNames.length; j++) {
                Point p1 = getPoint(i, cx, cy, radius);
                Point p2 = getPoint(j, cx, cy, radius);
                g2.drawLine(p1.x, p1.y, p2.x, p2.y); // Draw line between two peripheral nodes
            }
            Point p = getPoint(i, cx, cy, radius);
            g2.drawLine(cx, cy, p.x, p.y); // Draw line from center to the peripheral node
        }"""
update_file("dashboard/NeuralVisualizerPanel.java", target_nv3, replacement_nv3)

target_nv4 = """        pulsePhase += 0.05f;
        int pulseAlpha = (int) (155 + 100 * Math.sin(pulsePhase));
        if(pulseAlpha < 0) pulseAlpha = 0;
        if(pulseAlpha > 255) pulseAlpha = 255;"""
replacement_nv4 = """        // Step 2: Calculate the glowing effect of the central core.
        // Math.sin creates a smooth oscillation between -1 and 1.
        // By mapping this to our alpha (transparency) channel, we get a breathing/pulsing effect.
        pulsePhase += 0.05f;
        int pulseAlpha = (int) (155 + 100 * Math.sin(pulsePhase));
        if(pulseAlpha < 0) pulseAlpha = 0;
        if(pulseAlpha > 255) pulseAlpha = 255;"""
update_file("dashboard/NeuralVisualizerPanel.java", target_nv4, replacement_nv4)

