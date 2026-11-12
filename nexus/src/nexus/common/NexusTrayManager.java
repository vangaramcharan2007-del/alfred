package nexus.common;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class NexusTrayManager implements NexusListener {
    private TrayIcon trayIcon;

    public NexusTrayManager(JFrame mainFrame) {
        if (!SystemTray.isSupported()) {
            System.out.println("System tray is not supported!");
            return;
        }

        SystemTray tray = SystemTray.getSystemTray();
        
        // Create a simple icon for the tray
        BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2 = img.createGraphics();
        g2.setColor(Color.CYAN);
        g2.fillOval(0, 0, 16, 16);
        g2.dispose();
        
        trayIcon = new TrayIcon(img, "NEXUS Application");
        trayIcon.setImageAutoSize(true);

        PopupMenu popup = new PopupMenu();
        
        MenuItem showItem = new MenuItem("Show");
        showItem.addActionListener(e -> {
            mainFrame.setVisible(true);
            mainFrame.setExtendedState(JFrame.NORMAL);
        });
        
        MenuItem quitItem = new MenuItem("Quit");
        quitItem.addActionListener(e -> System.exit(0));

        popup.add(showItem);
        popup.add(quitItem);
        
        trayIcon.setPopupMenu(popup);
        trayIcon.addActionListener(e -> {
            mainFrame.setVisible(true);
            mainFrame.setExtendedState(JFrame.NORMAL);
        });

        try {
            tray.add(trayIcon);
        } catch (AWTException e) {
            e.printStackTrace();
        }

        EventBus.getInstance().subscribe("TASK_COMPLETED", this);
        EventBus.getInstance().subscribe("PRODUCT_PURCHASED", this);
    }

    @Override
    public void onEvent(NexusEvent event) {
        if (trayIcon != null) {
            if ("TASK_COMPLETED".equals(event.getType())) {
                trayIcon.displayMessage("NEXUS Update", "Task Completed! Score increased.", TrayIcon.MessageType.INFO);
            } else if ("PRODUCT_PURCHASED".equals(event.getType())) {
                trayIcon.displayMessage("NEXUS Update", "Product Purchased!", TrayIcon.MessageType.INFO);
            }
        }
    }
}
