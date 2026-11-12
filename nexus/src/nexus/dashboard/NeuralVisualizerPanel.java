package nexus.dashboard;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.geom.Ellipse2D;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

/**
 * The NeuralVisualizerPanel is a custom graphical component that provides a futuristic, 
 * node-based representation of the application's internal state.
 * 
 * It visually displays the core modules (Dashboard, Finance, Tasks, etc.) as connected nodes.
 * By implementing NexusListener, it can react to global events (like budget changes) 
 * and animate particles flowing between nodes to represent data movement.
 */
public class NeuralVisualizerPanel extends JPanel implements NexusListener {
    private String[] nodeNames = {"Finance", "Market", "Tasks", "Goals", "Media", "Analytics"};
    private Map<String, Point> nodeCenters = new HashMap<>();
    private List<Particle> particles = new ArrayList<>();
    private Timer timer;
    private Color centerColor = Color.CYAN;
    private float pulsePhase = 0.0f;
    private float wireframeAngle = 0.0f;
    private boolean budgetExceeded = false;
    private int currentScore = 100;

    public NeuralVisualizerPanel() {
        setBackground(new Color(10, 10, 15));
        EventBus.getInstance().subscribeToAll(this);
        
        timer = new Timer(16, e -> {
            updateParticles();
            wireframeAngle += 0.02f;
            repaint();
        });
        timer.start();

        addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseClicked(java.awt.event.MouseEvent e) {
                int mx = e.getX();
                int my = e.getY();
                for (String node : nodeNames) {
                    Point p = nodeCenters.get(node);
                    if (p != null) {
                        double dist = Math.hypot(mx - p.x, my - p.y);
                        if (dist <= 25) {
                            EventBus.getInstance().publish(new NexusEvent("NAVIGATION_REQUEST", node, "Dashboard"));
                            break;
                        }
                    }
                }
            }
        });
        
        addMouseMotionListener(new java.awt.event.MouseMotionAdapter() {
            @Override
            public void mouseMoved(java.awt.event.MouseEvent e) {
                int mx = e.getX();
                int my = e.getY();
                boolean overNode = false;
                for (String node : nodeNames) {
                    Point p = nodeCenters.get(node);
                    if (p != null && Math.hypot(mx - p.x, my - p.y) <= 25) {
                        overNode = true;
                        break;
                    }
                }
                setCursor(new Cursor(overNode ? Cursor.HAND_CURSOR : Cursor.DEFAULT_CURSOR));
            }
        });
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int cx = getWidth() / 2;
        int cy = getHeight() / 2;
        int radius = Math.min(cx, cy) - 60;

        // Draw connections
        g2.setColor(new Color(0, 255, 255, 40));
        g2.setStroke(new BasicStroke(1.5f));
        for (int i = 0; i < nodeNames.length; i++) {
            for (int j = i + 1; j < nodeNames.length; j++) {
                Point p1 = getPoint(i, cx, cy, radius);
                Point p2 = getPoint(j, cx, cy, radius);
                g2.drawLine(p1.x, p1.y, p2.x, p2.y);
            }
            Point p = getPoint(i, cx, cy, radius);
            g2.drawLine(cx, cy, p.x, p.y);
        }

        pulsePhase += 0.05f;
        int pulseAlpha = (int) (150 + 100 * Math.sin(pulsePhase));
        if(pulseAlpha < 0) pulseAlpha = 0;
        if(pulseAlpha > 255) pulseAlpha = 255;

        // Heavy glowing effect with radial gradient
        float[] dist = {0.0f, 1.0f};
        Color[] colors = {new Color(centerColor.getRed(), centerColor.getGreen(), centerColor.getBlue(), 180), new Color(0, 0, 0, 0)};
        RadialGradientPaint rgp = new RadialGradientPaint(cx, cy, 150, dist, colors);
        g2.setPaint(rgp);
        g2.fillOval(cx - 150, cy - 150, 300, 300);

        // Draw rotating 3D wireframe
        g2.setColor(new Color(0, 255, 200, 100));
        g2.setStroke(new BasicStroke(2.0f));
        AffineTransform old = g2.getTransform();
        g2.translate(cx, cy);
        g2.rotate(wireframeAngle);
        for (int i = 0; i < 6; i++) {
            g2.rotate(Math.PI / 3);
            g2.drawOval(-40, -80, 80, 160);
        }
        g2.setTransform(old);

        // Draw center core
        g2.setColor(new Color(centerColor.getRed(), centerColor.getGreen(), centerColor.getBlue(), pulseAlpha));
        g2.fillOval(cx - 20, cy - 20, 40, 40);
        
        // Draw nodes
        for (int i = 0; i < nodeNames.length; i++) {
            Point p = getPoint(i, cx, cy, radius);
            nodeCenters.put(nodeNames[i], p);

            // Node glow
            RadialGradientPaint nodeRgp = new RadialGradientPaint(p.x, p.y, 40, dist, colors);
            g2.setPaint(nodeRgp);
            g2.fillOval(p.x - 40, p.y - 40, 80, 80);

            g2.setColor(Color.CYAN);
            g2.fillOval(p.x - 15, p.y - 15, 30, 30);
            g2.setColor(Color.WHITE);
            g2.fillOval(p.x - 5, p.y - 5, 10, 10);
            
            g2.setColor(new Color(220, 255, 255));
            g2.setFont(new Font("Segoe UI", Font.BOLD, 14));
            FontMetrics fm = g2.getFontMetrics();
            int sw = fm.stringWidth(nodeNames[i]);
            g2.drawString(nodeNames[i], p.x - sw / 2, p.y + 40);
        }

        // Draw particles
        g2.setColor(Color.WHITE);
        for (Particle p : particles) {
            g2.fillOval((int)p.x - 3, (int)p.y - 3, 6, 6);
            // particle glow
            g2.setColor(new Color(0, 255, 255, 150));
            g2.fillOval((int)p.x - 6, (int)p.y - 6, 12, 12);
            g2.setColor(Color.WHITE);
        }
    }

    private Point getPoint(int index, int cx, int cy, int r) {
        double angle = 2 * Math.PI * index / nodeNames.length - Math.PI / 2;
        int x = cx + (int) (r * Math.cos(angle));
        int y = cy + (int) (r * Math.sin(angle));
        return new Point(x, y);
    }

    private void updateParticles() {
        for (int i = particles.size() - 1; i >= 0; i--) {
            Particle p = particles.get(i);
            p.move();
            if (p.isDone()) {
                particles.remove(i);
            }
        }
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("BUDGET_UPDATED".equals(event.getType())) {
            nexus.finance.Budget budget = (nexus.finance.Budget) event.getPayload();
            budgetExceeded = budget.getRemaining() < 0;
            updateCenterColor();
        } else if ("XP_UPDATED".equals(event.getType())) {
            currentScore = (Integer) event.getPayload();
            updateCenterColor();
        }

        String sourceStr = event.getSource();
        if (sourceStr == null) return;
        Point startNode = nodeCenters.get(sourceStr);
        if (startNode == null) return;

        // Animate to all other nodes
        for (String node : nodeNames) {
            if (!node.equals(sourceStr)) {
                Point targetNode = nodeCenters.get(node);
                if (targetNode != null) {
                    particles.add(new Particle(startNode.x, startNode.y, targetNode.x, targetNode.y));
                }
            }
        }
    }

    private void updateCenterColor() {
        if (budgetExceeded) {
            centerColor = Color.RED;
        } else if (currentScore >= 150) {
            centerColor = Color.GREEN;
        } else {
            centerColor = Color.CYAN;
        }
    }

    private static class Particle {
        double x, y;
        double tx, ty;
        double dx, dy;
        double dist;
        double speed = 6.0;

        public Particle(double sx, double sy, double tx, double ty) {
            this.x = sx;
            this.y = sy;
            this.tx = tx;
            this.ty = ty;
            double angle = Math.atan2(ty - sy, tx - sx);
            this.dx = Math.cos(angle) * speed;
            this.dy = Math.sin(angle) * speed;
            this.dist = Math.hypot(tx - sx, ty - sy);
        }

        public void move() {
            x += dx;
            y += dy;
            dist -= speed;
        }

        public boolean isDone() {
            return dist <= 0;
        }
    }
}

