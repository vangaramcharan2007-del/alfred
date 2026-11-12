package nexus.analytics;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Arc2D;
import java.util.Map;

public class PieChartPanel extends JPanel {
    private Map<String, Double> data;
    private Color[] colors = {new Color(56, 189, 248), new Color(244, 63, 94), new Color(16, 185, 129), new Color(245, 158, 11)};

    public PieChartPanel() {
        setBackground(new Color(30, 35, 45));
    }

    public void setData(Map<String, Double> data) {
        this.data = data;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (data == null || data.isEmpty()) return;

        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        double total = data.values().stream().mapToDouble(Double::doubleValue).sum();
        if (total == 0) return;

        int w = getWidth();
        int h = getHeight();
        int size = Math.min(w, h) - 60;
        int x = (w - size) / 2;
        int y = (h - size) / 2 + 30;

        double currentAngle = 90;
        int colorIdx = 0;

        for (Map.Entry<String, Double> entry : data.entrySet()) {
            double value = entry.getValue();
            if (value <= 0) continue;

            double angle = (value / total) * 360;
            
            // Draw Pie Slice
            g2.setColor(colors[colorIdx % colors.length]);
            g2.fill(new Arc2D.Double(x, y, size, size, currentAngle, -angle, Arc2D.PIE));
            
            // Draw Label
            double labelAngle = Math.toRadians(currentAngle - (angle / 2));
            int labelX = (int) (x + size/2 + Math.cos(labelAngle) * (size/2 + 35));
            int labelY = (int) (y + size/2 - Math.sin(labelAngle) * (size/2 + 35));
            
            g2.setColor(Color.WHITE);
            g2.setFont(new Font("Segoe UI", Font.BOLD, 12));
            String label = String.format("%s (%.0f%%)", entry.getKey(), (value / total) * 100);
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(label, labelX - fm.stringWidth(label)/2, labelY);

            currentAngle -= angle;
            colorIdx++;
        }
        
        // Title
        g2.setColor(Color.CYAN);
        g2.setFont(new Font("Consolas", Font.BOLD, 16));
        String title = "BUDGET DISTRIBUTION";
        g2.drawString(title, (w - g2.getFontMetrics().stringWidth(title))/2, 25);

        g2.dispose();
    }
}

