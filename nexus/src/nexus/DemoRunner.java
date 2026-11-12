package nexus;

import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Font;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import nexus.common.EventBus;
import nexus.common.NexusEvent;

public class DemoRunner {
    public static void main(String[] args) {
        try {
            com.formdev.flatlaf.FlatDarkLaf.setup();
            UIManager.put("defaultFont", new Font("Segoe UI", Font.PLAIN, 14));
        } catch (Exception e) {
            e.printStackTrace();
        }

        SwingUtilities.invokeLater(() -> {

            NexusApplication app = new NexusApplication();
            app.setVisible(true);

            // Start a new thread to simulate events and capture screenshot
            new Thread(() -> {
                try {
                    Thread.sleep(1000); // Wait for UI to render
                    
                    // Fire events to trigger Neural Visualizer particles
                    EventBus.getInstance().publish(new NexusEvent("TRANSACTION_ADDED", null, "Finance"));
                    Thread.sleep(200);
                    EventBus.getInstance().publish(new NexusEvent("TASK_COMPLETED", null, "Tasks"));
                    Thread.sleep(200);
                    EventBus.getInstance().publish(new NexusEvent("INSIGHT_GENERATED", null, "Analytics"));
                    
                    Thread.sleep(200); // Let particles move a bit
                    
                    // Capture screenshot of the JFrame
                    SwingUtilities.invokeAndWait(() -> {
                        try {
                            BufferedImage image = new BufferedImage(app.getWidth(), app.getHeight(), BufferedImage.TYPE_INT_RGB);
                            app.paint(image.getGraphics());
                            File outputFile = new File("nexus_demo.png");
                            ImageIO.write(image, "png", outputFile);
                            System.out.println("Screenshot saved to: " + outputFile.getAbsolutePath());
                        } catch (Exception ex) {
                            ex.printStackTrace();
                        }
                    });
                    
                    System.exit(0);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }).start();
        });
    }
}
