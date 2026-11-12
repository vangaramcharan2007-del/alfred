package nexus.mobile;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class MobilePassPanel extends JPanel {
    private final MobilePassService service = MobilePassService.getInstance();
    private final JLabel qrImageLabel;
    private final JLabel otpCodeLabel;
    private final JProgressBar countdownBar;
    private final JLabel countdownLabel;
    private final JTextArea gateConsole;
    private final Timer refreshTimer;

    public MobilePassPanel() {
        setLayout(new BorderLayout(15, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER
        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("📱 MOBILE APP & DYNAMIC 15s ROTATING QR PASS (PHASE 9)");
        title.setFont(new Font("Consolas", Font.BOLD, 15));
        title.setForeground(new Color(56, 189, 248));

        JLabel antiFraudBadge = new JLabel("🛡️ ZERO-FRAUD TOTP PROTOCOL ACTIVE");
        antiFraudBadge.setFont(new Font("Segoe UI", Font.BOLD, 12));
        antiFraudBadge.setForeground(new Color(52, 211, 153));

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(antiFraudBadge, BorderLayout.EAST);
        add(headerBar, BorderLayout.NORTH);

        // 2. CENTER: LEFT = PHONE PASSBOOK | RIGHT = GATE SCANNER
        JPanel centerGrid = new JPanel(new GridLayout(1, 2, 15, 0));
        centerGrid.setOpaque(false);

        // LEFT: SIMULATED SMARTPHONE SCREEN
        JPanel phoneWrapper = new JPanel(new BorderLayout(0, 8));
        phoneWrapper.setBackground(new Color(24, 30, 42));
        phoneWrapper.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85), 2),
                BorderFactory.createEmptyBorder(12, 16, 12, 16)
        ));

        JPanel phoneHeader = new JPanel(new BorderLayout());
        phoneHeader.setOpaque(false);
        JLabel brand = new JLabel("📱 NEXUS WALLET PASSBOOK", SwingConstants.CENTER);
        brand.setFont(new Font("Segoe UI", Font.BOLD, 12));
        brand.setForeground(new Color(148, 163, 184));
        phoneHeader.add(brand, BorderLayout.CENTER);
        phoneWrapper.add(phoneHeader, BorderLayout.NORTH);

        // Ticket Details & Dynamic QR Card
        JPanel ticketCard = new JPanel();
        ticketCard.setLayout(new BoxLayout(ticketCard, BoxLayout.Y_AXIS));
        ticketCard.setBackground(new Color(15, 23, 42));
        ticketCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(59, 130, 246), 1),
                BorderFactory.createEmptyBorder(10, 10, 10, 10)
        ));

        JLabel movieLabel = new JLabel(service.getActiveMovie());
        movieLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        movieLabel.setForeground(Color.WHITE);
        movieLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel seatsLabel = new JLabel("Seats: " + service.getActiveSeats());
        seatsLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        seatsLabel.setForeground(new Color(251, 191, 36));
        seatsLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel studentLabel = new JLabel(service.getStudentName() + " (" + service.getRegNo() + ")");
        studentLabel.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        studentLabel.setForeground(new Color(147, 197, 253));
        studentLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // QR Image
        qrImageLabel = new JLabel();
        qrImageLabel.setPreferredSize(new Dimension(180, 180));
        qrImageLabel.setMaximumSize(new Dimension(180, 180));
        qrImageLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // Rolling OTP & Countdown
        otpCodeLabel = new JLabel("OTP: ------");
        otpCodeLabel.setFont(new Font("Consolas", Font.BOLD, 18));
        otpCodeLabel.setForeground(new Color(52, 211, 153));
        otpCodeLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        countdownBar = new JProgressBar(0, 15);
        countdownBar.setMaximumSize(new Dimension(180, 8));
        countdownBar.setForeground(new Color(56, 189, 248));
        countdownBar.setBackground(new Color(30, 41, 59));
        countdownBar.setAlignmentX(Component.CENTER_ALIGNMENT);

        countdownLabel = new JLabel("Refreshes in 15s (Screenshots blocked)");
        countdownLabel.setFont(new Font("Segoe UI", Font.ITALIC, 10));
        countdownLabel.setForeground(new Color(148, 163, 184));
        countdownLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        ticketCard.add(movieLabel);
        ticketCard.add(Box.createVerticalStrut(2));
        ticketCard.add(seatsLabel);
        ticketCard.add(Box.createVerticalStrut(2));
        ticketCard.add(studentLabel);
        ticketCard.add(Box.createVerticalStrut(8));
        ticketCard.add(qrImageLabel);
        ticketCard.add(Box.createVerticalStrut(8));
        ticketCard.add(otpCodeLabel);
        ticketCard.add(Box.createVerticalStrut(4));
        ticketCard.add(countdownBar);
        ticketCard.add(Box.createVerticalStrut(3));
        ticketCard.add(countdownLabel);

        phoneWrapper.add(ticketCard, BorderLayout.CENTER);
        centerGrid.add(phoneWrapper);

        // RIGHT: MULTIPLEX GATE TURNSTILE SCANNER
        JPanel gateWrapper = new JPanel(new BorderLayout(0, 10));
        gateWrapper.setBackground(new Color(24, 30, 42));
        gateWrapper.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(12, 14, 12, 14)
        ));

        JLabel gateTitle = new JLabel("🎟️ MULTIPLEX TURNSTILE GATE VALIDATOR");
        gateTitle.setFont(new Font("Segoe UI", Font.BOLD, 13));
        gateTitle.setForeground(new Color(56, 189, 248));
        gateWrapper.add(gateTitle, BorderLayout.NORTH);

        gateConsole = new JTextArea();
        gateConsole.setEditable(false);
        gateConsole.setFont(new Font("Consolas", Font.PLAIN, 12));
        gateConsole.setBackground(new Color(10, 15, 30));
        gateConsole.setForeground(new Color(52, 211, 153));
        gateConsole.setText("""
                [GATE SCANNER READY]
                Waiting for mobile dynamic pass presentation...
                Protocols: TOTP-15s Hash / BLE Proximity / SRM Identity
                --------------------------------------------------------
                """);

        gateWrapper.add(new JScrollPane(gateConsole), BorderLayout.CENTER);

        // Scanner Actions
        JPanel scannerActions = new JPanel(new GridLayout(2, 1, 6, 6));
        scannerActions.setOpaque(false);

        JButton scanBtn = new JButton("⚡ Scan Valid Active Dynamic Pass at Turnstile");
        scanBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        scanBtn.setBackground(new Color(16, 185, 129));
        scanBtn.setForeground(Color.WHITE);
        scanBtn.setFocusPainted(false);
        scanBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        scanBtn.addActionListener(e -> simulateSuccessfulScan());

        JButton fraudBtn = new JButton("🚫 Test Simulated Screenshot / Expired OTP Replay");
        fraudBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        fraudBtn.setBackground(new Color(220, 38, 38));
        fraudBtn.setForeground(Color.WHITE);
        fraudBtn.setFocusPainted(false);
        fraudBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        fraudBtn.addActionListener(e -> simulateFraudulentScan());

        scannerActions.add(scanBtn);
        scannerActions.add(fraudBtn);
        gateWrapper.add(scannerActions, BorderLayout.SOUTH);

        centerGrid.add(gateWrapper);
        add(centerGrid, BorderLayout.CENTER);

        // 3. BOTTOM BLE GEOFENCE STATUS STRIP
        JPanel bottomBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 4));
        bottomBar.setBackground(new Color(30, 41, 59));
        bottomBar.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));

        JLabel bleStatus = new JLabel("📍 SRM BLE Beacon Detected: Kattankulathur Multiplex Gate #2 (RSSI -48 dBm)");
        bleStatus.setFont(new Font("Segoe UI", Font.BOLD, 11));
        bleStatus.setForeground(new Color(52, 211, 153));

        JLabel passStatus = new JLabel("• Mobile Pass Status: AUTHORIZED & ARMED");
        passStatus.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        passStatus.setForeground(new Color(147, 197, 253));

        bottomBar.add(bleStatus);
        bottomBar.add(passStatus);
        add(bottomBar, BorderLayout.SOUTH);

        // Real-time 1-Second Timer for Dynamic QR & OTP Rotation
        refreshTimer = new Timer(1000, e -> updatePassState());
        refreshTimer.start();
        updatePassState();
    }

    private void updatePassState() {
        long window = service.getCurrentWindow();
        int secLeft = service.getSecondsRemaining();
        String otp = service.generateTotpCode(window);
        String payload = service.generateFullPayload(window);

        countdownBar.setValue(secLeft);
        countdownLabel.setText("Regenerating in " + secLeft + "s (Anti-Scalp Protection Active)");
        otpCodeLabel.setText("TOTP: " + otp.substring(0, 3) + " " + otp.substring(3));

        // Generate dynamic visual QR image
        BufferedImage qrImg = DynamicQrGenerator.generateQrImage(payload, 170);
        qrImageLabel.setIcon(new ImageIcon(qrImg));
    }

    private void simulateSuccessfulScan() {
        long win = service.getCurrentWindow();
        String otp = service.generateTotpCode(win);
        gateConsole.append(String.format("""
                >>> SCAN EVENT DETECTED:
                [TOKEN RECEIVED] : %s (Window #%d)
                [VERIFICATION]   : SUCCESSFUL (HMAC Matches Key)
                [STUDENT]        : %s (%s)
                [RESERVATION]    : %s - %s
                [GATE STATUS]    : TURNSTILE UNLOCKED (ADMISSION CONFIRMED)
                --------------------------------------------------------
                """, otp, win, service.getStudentName(), service.getRegNo(), service.getActiveMovie(), service.getActiveSeats()));
        gateConsole.setCaretPosition(gateConsole.getDocument().getLength());
    }

    private void simulateFraudulentScan() {
        gateConsole.append("""
                >>> FRAUD ATTEMPT DETECTED:
                [TOKEN RECEIVED] : 994201 (EXPIRED OR SCREENSHOT COPY)
                [VERIFICATION]   : FAILED - REPLAY ATTACK BLOCKED
                [SECURITY ALERT] : Ticket token out of bounds by >15 seconds.
                [GATE STATUS]    : TURNSTILE LOCKED - ADMISSION REJECTED
                --------------------------------------------------------
                """);
        gateConsole.setCaretPosition(gateConsole.getDocument().getLength());
    }
}