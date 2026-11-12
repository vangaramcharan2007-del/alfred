package nexus.auth;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.function.Consumer;

public class LoginPanel extends JPanel {
    private final Consumer<Void> onLoginSuccess;
    private int scanLineY = 0;
    private boolean scanDown = true;
    private Timer scanTimer;

    public LoginPanel(Consumer<Void> onLoginSuccess) {
        this.onLoginSuccess = onLoginSuccess;
        setLayout(new GridLayout(1, 2));
        setBackground(new Color(10, 10, 15));

        // Left Panel - Animated Scanner
        JPanel leftPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                int w = getWidth();
                int h = getHeight();
                
                Color color1 = new Color(5, 5, 15);
                Color color2 = new Color(20, 20, 40);
                GradientPaint gp = new GradientPaint(0, 0, color1, 0, h, color2);
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, w, h);

                // Grid background
                g2d.setColor(new Color(0, 255, 255, 20));
                for(int i = 0; i < w; i += 40) {
                    g2d.drawLine(i, 0, i, h);
                }
                for(int i = 0; i < h; i += 40) {
                    g2d.drawLine(0, i, w, i);
                }

                // Scan line
                g2d.setColor(new Color(0, 255, 255, 180));
                g2d.fillRect(0, scanLineY, w, 4);
                GradientPaint scanGlow = new GradientPaint(0, scanLineY - 20, new Color(0, 255, 255, 0), 0, scanLineY, new Color(0, 255, 255, 80));
                g2d.setPaint(scanGlow);
                g2d.fillRect(0, scanLineY - 20, w, 20);
            }
        };
        
        scanTimer = new Timer(16, e -> {
            if (scanDown) {
                scanLineY += 3;
                if (scanLineY > leftPanel.getHeight()) scanDown = false;
            } else {
                scanLineY -= 3;
                if (scanLineY < 0) scanDown = true;
            }
            leftPanel.repaint();
        });
        scanTimer.start();

        leftPanel.setLayout(new GridBagLayout());
        
        GridBagConstraints gbcLeft = new GridBagConstraints();
        gbcLeft.gridx = 0;
        gbcLeft.gridy = 0;
        gbcLeft.insets = new Insets(10, 10, 10, 10);
        
        JLabel titleLabel = new JLabel("NEXUS");
        titleLabel.setFont(new Font("Consolas", Font.BOLD, 75));
        titleLabel.setForeground(new Color(0, 255, 255));
        leftPanel.add(titleLabel, gbcLeft);
        
        gbcLeft.gridy = 1;
        JLabel subtitleLabel = new JLabel("ENTERPRISE PLATFORM v25.0 (REVIEW 3 FINAL)");
        subtitleLabel.setFont(new Font("Consolas", Font.PLAIN, 18));
        subtitleLabel.setForeground(new Color(0, 200, 255));
        leftPanel.add(subtitleLabel, gbcLeft);

        // Right Panel - Login Form & Account Switcher
        JPanel rightPanel = new JPanel(new GridBagLayout());
        rightPanel.setOpaque(false);
        
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 25, 8, 25);
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.weightx = 1.0;
        
        JLabel loginTitle = new JLabel("ACCESS TERMINAL");
        loginTitle.setFont(new Font("Consolas", Font.BOLD, 26));
        loginTitle.setForeground(Color.WHITE);
        loginTitle.setHorizontalAlignment(SwingConstants.CENTER);
        rightPanel.add(loginTitle, gbc);

        // Account Profile Selector Dropdown
        gbc.gridy++;
        gbc.insets = new Insets(20, 25, 6, 25);
        JLabel acctLabel = new JLabel("Select Active User Account:");
        acctLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        acctLabel.setForeground(new Color(148, 163, 184));
        rightPanel.add(acctLabel, gbc);

        gbc.gridy++;
        gbc.insets = new Insets(2, 25, 15, 25);
        JComboBox<UserProfile> userCombo = new JComboBox<>(AccountService.getInstance().getProfiles().toArray(new UserProfile[0]));
        userCombo.setFont(new Font("Segoe UI", Font.BOLD, 13));
        userCombo.setBackground(new Color(24, 30, 42));
        userCombo.setForeground(Color.WHITE);
        userCombo.setPreferredSize(new Dimension(280, 40));
        rightPanel.add(userCombo, gbc);
        
        gbc.gridy++;
        gbc.insets = new Insets(5, 25, 5, 25);
        JTextField usernameField = new JTextField("ramcharan.vanga");
        usernameField.setPreferredSize(new Dimension(280, 42));
        usernameField.setBackground(new Color(20, 20, 30));
        usernameField.setForeground(new Color(0, 255, 255));
        usernameField.setCaretColor(new Color(0, 255, 255));
        usernameField.setBorder(BorderFactory.createLineBorder(new Color(0, 150, 255), 1));
        usernameField.setFont(new Font("Consolas", Font.PLAIN, 15));
        rightPanel.add(usernameField, gbc);
        
        gbc.gridy++;
        gbc.insets = new Insets(5, 25, 20, 25);
        JPasswordField passwordField = new JPasswordField("••••••••");
        passwordField.setPreferredSize(new Dimension(280, 42));
        passwordField.setBackground(new Color(20, 20, 30));
        passwordField.setForeground(new Color(0, 255, 255));
        passwordField.setCaretColor(new Color(0, 255, 255));
        passwordField.setBorder(BorderFactory.createLineBorder(new Color(0, 150, 255), 1));
        passwordField.setFont(new Font("Consolas", Font.PLAIN, 15));
        rightPanel.add(passwordField, gbc);

        userCombo.addActionListener(e -> {
            UserProfile selected = (UserProfile) userCombo.getSelectedItem();
            if (selected != null) {
                AccountService.getInstance().switchProfile(selected);
                if (selected.getId().equals("USER-01")) {
                    usernameField.setText("ramcharan.vanga");
                } else if (selected.getId().equals("USER-02")) {
                    usernameField.setText("faculty.evaluator");
                } else {
                    usernameField.setText("srm.peer.guest");
                }
            }
        });
        
        gbc.gridy++;
        gbc.insets = new Insets(10, 25, 10, 25);
        JButton loginButton = new JButton("AUTHENTICATE");
        loginButton.setFont(new Font("Consolas", Font.BOLD, 17));
        loginButton.setForeground(Color.WHITE);
        
        Color buttonColor = new Color(0, 120, 255);
        Color hoverColor = new Color(0, 180, 255);
        
        loginButton.setBackground(buttonColor);
        loginButton.setFocusPainted(false);
        loginButton.setBorder(BorderFactory.createLineBorder(new Color(0, 255, 255), 2));
        loginButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        loginButton.setPreferredSize(new Dimension(280, 46));
        
        loginButton.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                if (loginButton.isEnabled()) {
                    loginButton.setBackground(hoverColor);
                }
            }
            @Override
            public void mouseExited(MouseEvent e) {
                if (loginButton.isEnabled()) {
                    loginButton.setBackground(buttonColor);
                }
            }
        });
        
        loginButton.addActionListener(e -> {
            loginButton.setText("VERIFYING BIOMETRICS...");
            loginButton.setEnabled(false);
            
            UserProfile sel = (UserProfile) userCombo.getSelectedItem();
            AccountService.getInstance().switchProfile(sel);

            Timer timer = new Timer(700, evt -> {
                onLoginSuccess.accept(null);
                loginButton.setText("AUTHENTICATE");
                loginButton.setEnabled(true);
            });
            timer.setRepeats(false);
            timer.start();
        });
        
        rightPanel.add(loginButton, gbc);
        
        JPanel rightWrapper = new JPanel(new GridBagLayout());
        rightWrapper.setBackground(new Color(10, 10, 15));
        rightWrapper.add(rightPanel);

        add(leftPanel);
        add(rightWrapper);
    }
}
