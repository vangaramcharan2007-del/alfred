package nexus;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

import nexus.auth.LoginPanel;
import nexus.dashboard.DashboardPanel;
import nexus.dashboard.DashboardService;
import nexus.tasks.TaskPanel;
import nexus.tasks.TaskService;
import nexus.finance.FinancePanel;
import nexus.finance.FinanceService;
import nexus.goals.GoalPanel;
import nexus.goals.GoalService;
import nexus.market.MarketPanel;
import nexus.market.MarketService;
import nexus.analytics.AnalyticsPanel;
import nexus.analytics.AnalyticsService;

public class ScreenshotGenerator {
    public static void main(String[] args) throws Exception {
        try {
            UIManager.setLookAndFeel(new com.formdev.flatlaf.FlatDarkLaf());
        } catch(Exception ex) {}

        takeScreenshot(new LoginPanel(e -> {}), "01_Login.png");
        takeScreenshot(new DashboardPanel(new DashboardService()), "02_Dashboard.png");
        takeScreenshot(new TaskPanel(new TaskService()), "03_Tasks.png");
        takeScreenshot(new FinancePanel(new FinanceService()), "04_Finance.png");
        takeScreenshot(new AnalyticsPanel(new AnalyticsService()), "05_Analytics.png");
        
        System.exit(0);
    }

    private static void takeScreenshot(JPanel panel, String filename) throws Exception {
        JFrame frame = new JFrame();
        frame.setUndecorated(true);
        frame.add(panel);
        frame.setSize(800, 600);
        frame.setVisible(true);
        Thread.sleep(500);

        BufferedImage img = new BufferedImage(800, 600, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = img.createGraphics();
        panel.paint(g2d);
        g2d.dispose();

        ImageIO.write(img, "png", new File(System.getProperty("user.home") + "\\Desktop\\" + filename));
        frame.dispose();
    }
}
