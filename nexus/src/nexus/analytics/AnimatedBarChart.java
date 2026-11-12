package nexus.analytics;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Map;
import java.util.LinkedHashMap;

/**
 * A custom, animated bar chart that visualizes a Map of String to Double data.
 * The bars grow upwards smoothly over ~1 second when data is set.
 */
public class AnimatedBarChart extends JPanel {

    private Map<String, Double> data = new LinkedHashMap<>();
    private float animationProgress = 1.0f;
    private Timer animationTimer;
    private final int ANIMATION_DURATION_MS = 1000;
    private final int ANIMATION_FPS = 60;
    
    public AnimatedBarChart() {
        setPreferredSize(new Dimension(400, 300));
        setBackground(new Color(30, 30, 30)); // Clean dark background
    }

    /**
     * Updates the chart data and triggers the grow animation.
     * @param newData The new data to display
     */
    public void setData(Map<String, Double> newData) {
        this.data = new LinkedHashMap<>(newData);
        
        // Stop any running animation
        if (animationTimer != null && animationTimer.isRunning()) {
            animationTimer.stop();
        }
        
        // Reset animation progress
        animationProgress = 0.0f;
        
        // Calculate delay between frames based on FPS
        int delay = 1000 / ANIMATION_FPS;
        // Calculate the increment per frame so that it reaches 1.0 over the duration
        float increment = (float) delay / ANIMATION_DURATION_MS;
        
        animationTimer = new Timer(delay, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                animationProgress += increment;
                if (animationProgress >= 1.0f) {
                    animationProgress = 1.0f;
                    animationTimer.stop();
                }
                repaint();
            }
        });
        animationTimer.start();
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        
        // Use anti-aliasing for smooth rendering
        Graphics2D g2d = (Graphics2D) g.create();
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        
        int width = getWidth();
        int height = getHeight();
        
        // Padding around the chart area
        int padding = 40;
        int chartWidth = width - 2 * padding;
        int chartHeight = height - 2 * padding;
        
        // Draw subtle grid lines
        g2d.setColor(new Color(60, 60, 60));
        int numGridLines = 5;
        for (int i = 0; i <= numGridLines; i++) {
            int y = padding + i * (chartHeight / numGridLines);
            g2d.drawLine(padding, y, width - padding, y);
        }
        
        if (data.isEmpty()) {
            g2d.dispose();
            return;
        }
        
        // Find the maximum value to scale the bars properly
        double maxValue = 0.0;
        for (Double value : data.values()) {
            if (value > maxValue) {
                maxValue = value;
            }
        }
        
        // If max is 0, set it to 1 to avoid division by zero
        if (maxValue == 0) {
            maxValue = 1.0;
        }
        
        int numBars = data.size();
        // Calculate bar width leaving some space between bars
        int barSpacing = 20;
        int totalSpacing = (numBars + 1) * barSpacing;
        int barWidth = (chartWidth - totalSpacing) / numBars;
        
        int currentX = padding + barSpacing;
        
        // Draw bars and labels
        FontMetrics fm = g2d.getFontMetrics();
        for (Map.Entry<String, Double> entry : data.entrySet()) {
            String label = entry.getKey();
            double value = entry.getValue();
            
            // The mathematical height is proportional to the value / maxValue.
            // We multiply by animationProgress (0.0 to 1.0) so the bar grows over time.
            int targetBarHeight = (int) ((value / maxValue) * chartHeight);
            int currentBarHeight = (int) (targetBarHeight * animationProgress);
            
            int barY = padding + chartHeight - currentBarHeight;
            
            // Draw a bright cyan bar with rounded top corners
            g2d.setColor(new Color(0, 200, 255)); // Bright cyan
            g2d.fillRoundRect(currentX, barY, barWidth, currentBarHeight + 10, 10, 10);
            
            // Hide the bottom rounded corners by drawing a normal rectangle over the bottom 10px
            if (currentBarHeight > 0) {
                g2d.fillRect(currentX, barY + 10, barWidth, currentBarHeight - 10);
            }
            
            // Draw the label centered below the bar
            g2d.setColor(Color.WHITE);
            int labelWidth = fm.stringWidth(label);
            int labelX = currentX + (barWidth - labelWidth) / 2;
            int labelY = padding + chartHeight + fm.getAscent() + 5;
            g2d.drawString(label, labelX, labelY);
            
            // Draw the value above the bar
            String valueStr = String.format("%.0f", value);
            int valWidth = fm.stringWidth(valueStr);
            int valX = currentX + (barWidth - valWidth) / 2;
            int valY = barY - 5;
            g2d.drawString(valueStr, valX, valY);
            
            currentX += barWidth + barSpacing;
        }
        
        g2d.dispose();
    }
}
