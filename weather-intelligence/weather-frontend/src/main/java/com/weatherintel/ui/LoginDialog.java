package com.weatherintel.ui;

import com.weatherintel.ui.services.ApiClient;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

/**
 * Modern, professional login dialog for the Weather Intelligence & Monitoring System.
 * Supports credential validation, role selection, one-click demo login, and standalone authentication.
 */
public class LoginDialog extends JDialog {

    private final ApiClient apiClient;
    private JTextField usernameField;
    private JPasswordField passwordField;
    private JCheckBox showPasswordCheck;
    private JCheckBox rememberMeCheck;
    private JLabel errorLabel;
    private JButton loginButton;
    private JButton quickDemoButton;
    private JButton exitButton;

    private boolean authenticated = false;
    private ApiClient.UserProfile authenticatedUser = null;

    public LoginDialog(Frame parent, ApiClient apiClient) {
        super(parent, "Weather Intelligence - Sign In", true);
        this.apiClient = (apiClient != null) ? apiClient : new ApiClient();

        initUI();
    }

    private void initUI() {
        setDefaultCloseOperation(DISPOSE_ON_CLOSE);
        setSize(480, 640);
        setResizable(false);
        setLocationRelativeTo(getParent());

        JPanel mainPanel = new JPanel(new BorderLayout(0, 0));
        mainPanel.setBackground(new Color(24, 28, 36));

        // 1. Header Banner
        JPanel headerPanel = createHeaderPanel();
        mainPanel.add(headerPanel, BorderLayout.NORTH);

        // 2. Central Form Panel
        JPanel formCard = createFormCard();
        mainPanel.add(formCard, BorderLayout.CENTER);

        // 3. Footer / Demo Credentials Panel
        JPanel footerPanel = createFooterPanel();
        mainPanel.add(footerPanel, BorderLayout.SOUTH);

        setContentPane(mainPanel);

        // Enter key triggers login
        KeyAdapter enterKeyAdapter = new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                    performLogin();
                }
            }
        };
        usernameField.addKeyListener(enterKeyAdapter);
        passwordField.addKeyListener(enterKeyAdapter);
    }

    private JPanel createHeaderPanel() {
        JPanel header = new JPanel();
        header.setLayout(new BoxLayout(header, BoxLayout.Y_AXIS));
        header.setBackground(new Color(20, 45, 95));
        header.setBorder(new EmptyBorder(25, 20, 20, 20));

        JLabel iconLabel = new JLabel("\u2601");
        iconLabel.setFont(new Font("Segoe UI", Font.BOLD, 42));
        iconLabel.setForeground(new Color(110, 195, 255));
        iconLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel titleLabel = new JLabel("Weather Intelligence");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        titleLabel.setForeground(Color.WHITE);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subtitleLabel = new JLabel("Advanced Meteorological & Analytics System");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        subtitleLabel.setForeground(new Color(190, 215, 245));
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        header.add(iconLabel);
        header.add(Box.createVerticalStrut(6));
        header.add(titleLabel);
        header.add(Box.createVerticalStrut(4));
        header.add(subtitleLabel);

        return header;
    }

    private JPanel createFormCard() {
        JPanel card = new JPanel();
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        card.setOpaque(false);
        card.setBorder(new EmptyBorder(20, 35, 10, 35));

        // Error / Status Message
        errorLabel = new JLabel(" ");
        errorLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        errorLabel.setForeground(new Color(245, 85, 85));
        errorLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        card.add(errorLabel);
        card.add(Box.createVerticalStrut(10));

        // Username Field
        JLabel userLabel = new JLabel("Username or Email");
        userLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        userLabel.setForeground(new Color(210, 215, 225));
        userLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        card.add(userLabel);
        card.add(Box.createVerticalStrut(6));

        usernameField = new JTextField("admin");
        usernameField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        usernameField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        usernameField.setAlignmentX(Component.LEFT_ALIGNMENT);
        card.add(usernameField);
        card.add(Box.createVerticalStrut(14));

        // Password Field
        JLabel passLabel = new JLabel("Password");
        passLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        passLabel.setForeground(new Color(210, 215, 225));
        passLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        card.add(passLabel);
        card.add(Box.createVerticalStrut(6));

        passwordField = new JPasswordField("admin123");
        passwordField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        passwordField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        passwordField.setAlignmentX(Component.LEFT_ALIGNMENT);
        card.add(passwordField);
        card.add(Box.createVerticalStrut(8));

        // Options Row (Show Password & Remember Me)
        JPanel optionsRow = new JPanel(new BorderLayout());
        optionsRow.setOpaque(false);
        optionsRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 26));
        optionsRow.setAlignmentX(Component.LEFT_ALIGNMENT);

        showPasswordCheck = new JCheckBox("Show password");
        showPasswordCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        showPasswordCheck.setOpaque(false);
        showPasswordCheck.setForeground(new Color(170, 180, 195));
        showPasswordCheck.addActionListener(e -> {
            if (showPasswordCheck.isSelected()) {
                passwordField.setEchoChar((char) 0);
            } else {
                passwordField.setEchoChar('\u2022');
            }
        });

        rememberMeCheck = new JCheckBox("Remember me", true);
        rememberMeCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        rememberMeCheck.setOpaque(false);
        rememberMeCheck.setForeground(new Color(170, 180, 195));

        optionsRow.add(showPasswordCheck, BorderLayout.WEST);
        optionsRow.add(rememberMeCheck, BorderLayout.EAST);
        card.add(optionsRow);
        card.add(Box.createVerticalStrut(18));

        // Action Buttons
        loginButton = new JButton("Sign In");
        loginButton.setFont(new Font("Segoe UI", Font.BOLD, 14));
        loginButton.setBackground(new Color(28, 95, 210));
        loginButton.setForeground(Color.WHITE);
        loginButton.setMaximumSize(new Dimension(Integer.MAX_VALUE, 40));
        loginButton.setAlignmentX(Component.LEFT_ALIGNMENT);
        loginButton.setFocusPainted(false);
        loginButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        loginButton.addActionListener(e -> performLogin());
        card.add(loginButton);
        card.add(Box.createVerticalStrut(8));

        quickDemoButton = new JButton("\u26A1 Quick Demo Login (System Admin)");
        quickDemoButton.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        quickDemoButton.setBackground(new Color(40, 48, 62));
        quickDemoButton.setForeground(new Color(140, 205, 255));
        quickDemoButton.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        quickDemoButton.setAlignmentX(Component.LEFT_ALIGNMENT);
        quickDemoButton.setFocusPainted(false);
        quickDemoButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        quickDemoButton.addActionListener(e -> {
            usernameField.setText("admin");
            passwordField.setText("admin123");
            performLogin();
        });
        card.add(quickDemoButton);

        return card;
    }

    private JPanel createFooterPanel() {
        JPanel footer = new JPanel();
        footer.setLayout(new BoxLayout(footer, BoxLayout.Y_AXIS));
        footer.setOpaque(false);
        footer.setBorder(new EmptyBorder(0, 35, 20, 35));

        // Demo accounts pill badges
        JPanel demoBox = new JPanel(new GridLayout(2, 2, 8, 6));
        demoBox.setBackground(new Color(30, 36, 48));
        demoBox.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(55, 65, 82), 1, true),
                new EmptyBorder(8, 12, 8, 12)
        ));

        demoBox.add(createQuickAccountButton("Admin", "admin", "admin123"));
        demoBox.add(createQuickAccountButton("Analyst", "analyst", "analyst123"));
        demoBox.add(createQuickAccountButton("Operator", "operator", "operator123"));
        demoBox.add(createQuickAccountButton("Guest", "guest", "guest123"));

        JLabel hintLabel = new JLabel("Select a test profile to autofill credentials:");
        hintLabel.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        hintLabel.setForeground(new Color(145, 155, 170));
        hintLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        exitButton = new JButton("Exit");
        exitButton.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        exitButton.setForeground(new Color(175, 180, 190));
        exitButton.setContentAreaFilled(false);
        exitButton.setBorderPainted(false);
        exitButton.setFocusPainted(false);
        exitButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        exitButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        exitButton.addActionListener(e -> {
            authenticated = false;
            dispose();
        });

        footer.add(hintLabel);
        footer.add(Box.createVerticalStrut(6));
        footer.add(demoBox);
        footer.add(Box.createVerticalStrut(10));
        footer.add(exitButton);

        return footer;
    }

    private JButton createQuickAccountButton(String label, String user, String pass) {
        JButton btn = new JButton(label + " (" + user + ")");
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        btn.setBackground(new Color(42, 50, 66));
        btn.setForeground(new Color(200, 215, 235));
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.addActionListener(e -> {
            usernameField.setText(user);
            passwordField.setText(pass);
            errorLabel.setText(" ");
        });
        return btn;
    }

    private void performLogin() {
        String username = usernameField.getText().trim();
        String password = new String(passwordField.getPassword()).trim();

        if (username.isEmpty() || password.isEmpty()) {
            errorLabel.setText("Please enter both username and password.");
            return;
        }

        loginButton.setEnabled(false);
        loginButton.setText("Signing In...");

        SwingUtilities.invokeLater(() -> {
            try {
                ApiClient.UserProfile profile = apiClient.login(username, password);
                if (profile != null) {
                    this.authenticated = true;
                    this.authenticatedUser = profile;
                    dispose();
                } else {
                    errorLabel.setText("Invalid username or password.");
                    loginButton.setEnabled(true);
                    loginButton.setText("Sign In");
                }
            } catch (Exception ex) {
                errorLabel.setText("Login failed: " + ex.getMessage());
                loginButton.setEnabled(true);
                loginButton.setText("Sign In");
            }
        });
    }

    public boolean isAuthenticated() {
        return authenticated;
    }

    public ApiClient.UserProfile getAuthenticatedUser() {
        return authenticatedUser;
    }
}
