package nexus.market;

import javax.swing.*;
import java.awt.*;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

public class MarketPanel extends JPanel implements NexusListener {
    private final MarketService service;
    private final JPanel productsContainer;
    private final JLabel cartLabel;
    private final JButton checkoutBtn;
    private final JTextField searchField;
    private final JLabel statusLabel;
    private final JLabel deliveryLabel;
    private final JLabel deliverySubLabel;
    private final JComboBox<String> paymentMethodCombo;
    private String currentDeliveryAddress;

    public MarketPanel(MarketService service) {
        this.service = service;
        setLayout(new BorderLayout(10, 10));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        setBackground(new Color(15, 23, 42));

        // 1. TOP AMAZON SEARCH & QUICK FILTER BAR
        JPanel topPanel = new JPanel();
        topPanel.setLayout(new BoxLayout(topPanel, BoxLayout.Y_AXIS));
        topPanel.setOpaque(false);

        // Search Bar
        JPanel searchBar = new JPanel(new BorderLayout(8, 0));
        searchBar.setBackground(new Color(30, 41, 59));
        searchBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)
        ));

        JLabel logo = new JLabel("🛒 AMAZON.IN REAL-TIME STOREFRONT");
        logo.setFont(new Font("Segoe UI", Font.BOLD, 13));
        logo.setForeground(new Color(251, 191, 36)); // Amazon Gold

        JPanel searchInputPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 0));
        searchInputPanel.setOpaque(false);

        searchField = new JTextField("laptop", 16);
        searchField.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        JButton searchBtn = new JButton("🔍 Live Search");
        searchBtn.setBackground(new Color(245, 158, 11));
        searchBtn.setForeground(Color.BLACK);
        searchBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        searchBtn.setFocusPainted(false);
        searchBtn.addActionListener(e -> executeSearch(searchField.getText().trim()));
        searchField.addActionListener(e -> executeSearch(searchField.getText().trim()));

        searchInputPanel.add(new JLabel("Search:"));
        searchInputPanel.add(searchField);
        searchInputPanel.add(searchBtn);

        searchBar.add(logo, BorderLayout.WEST);
        searchBar.add(searchInputPanel, BorderLayout.EAST);
        topPanel.add(searchBar);

        // DELIVERY LOCATION STRIP
        JPanel deliveryStrip = new JPanel(new BorderLayout(8, 0));
        deliveryStrip.setBackground(new Color(24, 30, 42));
        deliveryStrip.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(6, 12, 6, 12)
        ));

        nexus.auth.UserProfile currentProf = nexus.auth.AccountService.getInstance().getCurrentProfile();
        currentDeliveryAddress = currentProf != null ? currentProf.getDeliveryAddress() : "Room 402, Kaveri Hostel, SRM University Kattankulathur, Chennai";

        deliveryLabel = new JLabel("📍 Deliver to: " + (currentProf != null ? currentProf.getName() : "Student") + " - " + currentDeliveryAddress);
        deliveryLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        deliveryLabel.setForeground(new Color(56, 189, 248));

        JPanel deliveryRight = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 0));
        deliveryRight.setOpaque(false);

        JButton changeLocBtn = new JButton("📍 Change Campus Location ▼");
        changeLocBtn.setFont(new Font("Segoe UI", Font.BOLD, 10));
        changeLocBtn.setBackground(new Color(51, 65, 85));
        changeLocBtn.setForeground(Color.WHITE);
        changeLocBtn.setFocusPainted(false);
        changeLocBtn.addActionListener(e -> promptChangeLocation());

        JLabel etaBadge = new JLabel("⚡ SRM Express: 25 Mins ETA");
        etaBadge.setFont(new Font("Segoe UI", Font.BOLD, 10));
        etaBadge.setForeground(new Color(52, 211, 153));

        deliveryRight.add(etaBadge);
        deliveryRight.add(Box.createHorizontalStrut(8));
        deliveryRight.add(changeLocBtn);

        deliveryStrip.add(deliveryLabel, BorderLayout.CENTER);
        deliveryStrip.add(deliveryRight, BorderLayout.EAST);
        topPanel.add(deliveryStrip);

        // Quick Category Chips
        JPanel chipsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 6));
        chipsPanel.setOpaque(false);
        chipsPanel.add(createCategoryChip("💻 Laptops", "laptop"));
        chipsPanel.add(createCategoryChip("📱 Smartphones", "smartphone"));
        chipsPanel.add(createCategoryChip("🎧 Headphones", "headphones"));
        chipsPanel.add(createCategoryChip("🎮 Gaming", "gaming"));
        chipsPanel.add(createCategoryChip("⌚ Smartwatches", "smartwatch"));

        statusLabel = new JLabel("● Live Amazon India Gateway Connected");
        statusLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        statusLabel.setForeground(new Color(52, 211, 153));
        chipsPanel.add(Box.createHorizontalStrut(20));
        chipsPanel.add(statusLabel);

        topPanel.add(chipsPanel);
        add(topPanel, BorderLayout.NORTH);

        // 2. CENTER PRODUCT CARDS GRID
        productsContainer = new JPanel(new GridLayout(0, 4, 12, 12));
        productsContainer.setBackground(new Color(15, 23, 42));

        JScrollPane scrollPane = new JScrollPane(productsContainer);
        scrollPane.setBorder(BorderFactory.createEmptyBorder());
        scrollPane.getVerticalScrollBar().setUnitIncrement(16);
        add(scrollPane, BorderLayout.CENTER);

        // 3. BOTTOM CHECKOUT & CART BAR
        JPanel bottomPanel = new JPanel(new BorderLayout(15, 0));
        bottomPanel.setBackground(new Color(30, 41, 59));
        bottomPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));

        JPanel cartInfo = new JPanel();
        cartInfo.setLayout(new BoxLayout(cartInfo, BoxLayout.Y_AXIS));
        cartInfo.setOpaque(false);

        cartLabel = new JLabel("Cart Total: $0.00 (0 items)");
        cartLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        cartLabel.setForeground(Color.WHITE);

        deliverySubLabel = new JLabel("📍 Ship: " + currentDeliveryAddress);
        deliverySubLabel.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        deliverySubLabel.setForeground(new Color(148, 163, 184));

        cartInfo.add(cartLabel);
        cartInfo.add(deliverySubLabel);

        // Center Payment Method Selector
        JPanel payMethodPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        payMethodPanel.setOpaque(false);

        JLabel payLabel = new JLabel("Payment Mode:");
        payLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        payLabel.setForeground(new Color(203, 213, 225));

        String[] payOptions = {
                "💳 NEXUS Capital Wallet (Instant 1-Click)",
                "⚡ UPI / Google Pay (VPA Scan & Pay)",
                "🏦 Credit / Debit Card (•••• 4242)",
                "💵 Cash on Delivery (SRM Campus COD)",
                "🪙 Crypto Pay (BTC / USDT Lightning)"
        };
        paymentMethodCombo = new JComboBox<>(payOptions);
        paymentMethodCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        paymentMethodCombo.setPreferredSize(new Dimension(240, 30));

        payMethodPanel.add(payLabel);
        payMethodPanel.add(paymentMethodCombo);

        checkoutBtn = new JButton("💳 Complete Order & Charge Budget");
        checkoutBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        checkoutBtn.setBackground(new Color(16, 185, 129));
        checkoutBtn.setForeground(Color.WHITE);
        checkoutBtn.setFocusPainted(false);
        checkoutBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        checkoutBtn.addActionListener(e -> executeCheckout());

        bottomPanel.add(cartInfo, BorderLayout.WEST);
        bottomPanel.add(payMethodPanel, BorderLayout.CENTER);
        bottomPanel.add(checkoutBtn, BorderLayout.EAST);
        add(bottomPanel, BorderLayout.SOUTH);

        // Subscriptions
        EventBus.getInstance().subscribe("CART_UPDATED", this);
        EventBus.getInstance().subscribe("BUDGET_UPDATED", this);
        EventBus.getInstance().subscribe("MARKET_UPDATED", this);
        EventBus.getInstance().subscribe("MARKET_LOADING", this);
        EventBus.getInstance().subscribe("USER_SWITCHED", this);

        updateProducts();
    }

    private JButton createCategoryChip(String text, String query) {
        JButton btn = new JButton(text);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        btn.setBackground(new Color(30, 41, 59));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.addActionListener(e -> {
            searchField.setText(query);
            executeSearch(query);
        });
        return btn;
    }

    private void executeSearch(String q) {
        if (!q.isEmpty()) {
            statusLabel.setText("Connecting to Amazon India for '" + q + "'...");
            statusLabel.setForeground(Color.ORANGE);
            productsContainer.removeAll();
            JLabel loading = new JLabel("Streaming live Amazon product inventory...", SwingConstants.CENTER);
            loading.setFont(new Font("Segoe UI", Font.ITALIC, 14));
            loading.setForeground(Color.LIGHT_GRAY);
            productsContainer.add(loading);
            productsContainer.revalidate();
            productsContainer.repaint();

            service.searchMarket(q);
        }
    }

    private void updateProducts() {
        statusLabel.setText("● Live Amazon India Gateway Connected (" + service.getAvailableProducts().size() + " items live)");
        statusLabel.setForeground(new Color(52, 211, 153));
        productsContainer.removeAll();

        for (Product p : service.getAvailableProducts()) {
            JPanel card = new JPanel(new BorderLayout(6, 6));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(51, 65, 85), 1),
                    BorderFactory.createEmptyBorder(10, 10, 10, 10)
            ));

            // Product Image Thumbnail
            JLabel imgLabel = new JLabel();
            imgLabel.setPreferredSize(new Dimension(130, 130));
            imgLabel.setHorizontalAlignment(SwingConstants.CENTER);
            imgLabel.setOpaque(true);
            imgLabel.setBackground(Color.WHITE);

            if (p.getImage() != null) {
                imgLabel.setIcon(new ImageIcon(p.getImage()));
            } else {
                imgLabel.setText("📦 Product Image");
                imgLabel.setForeground(Color.GRAY);
            }
            card.add(imgLabel, BorderLayout.CENTER);

            // Info Panel
            JPanel infoPanel = new JPanel();
            infoPanel.setLayout(new BoxLayout(infoPanel, BoxLayout.Y_AXIS));
            infoPanel.setOpaque(false);
            infoPanel.setBorder(BorderFactory.createEmptyBorder(6, 0, 0, 0));

            JLabel titleLabel = new JLabel("<html><body style='width:140px; font-weight:bold; color:white;'>" + p.getName() + "</body></html>");
            titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));

            JLabel badgeLabel = new JLabel("✓ Amazon Prime Verified");
            badgeLabel.setFont(new Font("Segoe UI", Font.BOLD, 10));
            badgeLabel.setForeground(new Color(56, 189, 248)); // Prime Blue

            JLabel priceLabel = new JLabel(String.format("₹%,.0f ($%,.2f)", p.getPrice(), p.getPrice() / 83.0));
            priceLabel.setFont(new Font("Segoe UI", Font.BOLD, 15));
            priceLabel.setForeground(new Color(52, 211, 153)); // Green

            JButton buyBtn = new JButton("+ Add to Cart");
            buyBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
            buyBtn.setBackground(new Color(245, 158, 11)); // Amazon Gold
            buyBtn.setForeground(Color.BLACK);
            buyBtn.setFocusPainted(false);
            buyBtn.setMaximumSize(new Dimension(200, 30));
            buyBtn.addActionListener(e -> service.addToCart(p, 1));

            infoPanel.add(titleLabel);
            infoPanel.add(Box.createVerticalStrut(3));
            infoPanel.add(badgeLabel);
            infoPanel.add(Box.createVerticalStrut(3));
            infoPanel.add(priceLabel);
            infoPanel.add(Box.createVerticalStrut(6));
            infoPanel.add(buyBtn);

            card.add(infoPanel, BorderLayout.SOUTH);
            productsContainer.add(card);
        }
        productsContainer.revalidate();
        productsContainer.repaint();
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("CART_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> {
                ShoppingCart cart = (ShoppingCart) event.getPayload();
                if (cart.getDiscountRate() > 0) {
                    cartLabel.setText(String.format("Cart Total: $%,.2f (%.0f%% XP VIP Discount!)", cart.getTotal(), cart.getDiscountRate() * 100));
                    cartLabel.setForeground(new Color(52, 211, 153));
                } else {
                    cartLabel.setText(String.format("Cart Total: $%,.2f (%d items)", cart.getTotal(), cart.getItems().size()));
                    cartLabel.setForeground(Color.WHITE);
                }
            });
        } else if ("MARKET_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(this::updateProducts);
        } else if ("BUDGET_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> {
                nexus.finance.Budget budget = (nexus.finance.Budget) event.getPayload();
                boolean canBuy = budget.getRemaining() > 0;
                checkoutBtn.setEnabled(canBuy);
                if (!canBuy) {
                    cartLabel.setText("BUDGET INSUFFICIENT!");
                    cartLabel.setForeground(Color.RED);
                }
            });
        } else if ("USER_SWITCHED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> {
                nexus.auth.UserProfile prof = (nexus.auth.UserProfile) event.getPayload();
                if (prof != null) {
                    currentDeliveryAddress = prof.getDeliveryAddress();
                    deliveryLabel.setText("📍 Deliver to: " + prof.getName() + " - " + currentDeliveryAddress);
                    deliverySubLabel.setText("📍 Ship: " + currentDeliveryAddress);
                    String defPay = prof.getDefaultPaymentMethod();
                    if (defPay.contains("UPI")) {
                        paymentMethodCombo.setSelectedItem("⚡ UPI / Google Pay (VPA Scan & Pay)");
                    } else if (defPay.contains("Faculty") || defPay.contains("Card")) {
                        paymentMethodCombo.setSelectedItem("🏦 Credit / Debit Card (•••• 4242)");
                    } else {
                        paymentMethodCombo.setSelectedItem("💳 NEXUS Capital Wallet (Instant 1-Click)");
                    }
                }
            });
        }
    }

    private void promptChangeLocation() {
        String[] locations = {
                "Room 402, Kaveri Hostel, SRM University Kattankulathur, Chennai - 603203",
                "Tech Park #508, Faculty Block, SRMIST Main Campus, Chennai",
                "Adhiyaman Hostel Block-D, Room 112, SRMIST Kattankulathur",
                "Central Library Reception Desk, SRMIST Campus",
                "SRM Main Auditorium Stage Entry / Green Room",
                "Enter Custom Delivery Address..."
        };
        String selected = (String) JOptionPane.showInputDialog(
                this,
                "Select SRM Campus Delivery Destination:",
                "Change Delivery Location",
                JOptionPane.QUESTION_MESSAGE,
                null,
                locations,
                currentDeliveryAddress
        );

        if (selected != null) {
            if (selected.equals("Enter Custom Delivery Address...")) {
                String custom = JOptionPane.showInputDialog(this, "Enter Full Delivery Address:", currentDeliveryAddress);
                if (custom != null && !custom.trim().isEmpty()) {
                    currentDeliveryAddress = custom.trim();
                }
            } else {
                currentDeliveryAddress = selected;
            }
            nexus.auth.UserProfile currentProf = nexus.auth.AccountService.getInstance().getCurrentProfile();
            deliveryLabel.setText("📍 Deliver to: " + (currentProf != null ? currentProf.getName() : "Student") + " - " + currentDeliveryAddress);
            deliverySubLabel.setText("📍 Ship: " + currentDeliveryAddress);
        }
    }

    private void executeCheckout() {
        if (service.getCart().getTotal() > 0) {
            double total = service.getCart().getTotal();
            int count = service.getCart().getItems().size();
            String payment = (String) paymentMethodCombo.getSelectedItem();
            nexus.auth.UserProfile prof = nexus.auth.AccountService.getInstance().getCurrentProfile();
            String user = prof != null ? prof.getName() : "Customer";
            String orderId = "AMZ-IN-" + (100000 + new java.util.Random().nextInt(900000));

            service.checkout();

            // Order Confirmation Receipt Dialog
            JDialog dlg = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Amazon Order Confirmed - Receipt", true);
            dlg.setSize(520, 390);
            dlg.setLocationRelativeTo(this);

            JPanel p = new JPanel(new BorderLayout(10, 10));
            p.setBackground(new Color(24, 30, 42));
            p.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

            JLabel title = new JLabel("📦 AMAZON.IN & NEXUS ORDER CONFIRMED", SwingConstants.CENTER);
            title.setFont(new Font("Segoe UI", Font.BOLD, 15));
            title.setForeground(new Color(52, 211, 153));
            p.add(title, BorderLayout.NORTH);

            JTextArea receipt = new JTextArea();
            receipt.setEditable(false);
            receipt.setFont(new Font("Consolas", Font.PLAIN, 12));
            receipt.setBackground(new Color(15, 23, 42));
            receipt.setForeground(Color.WHITE);
            receipt.setText(String.format("""
                    ORDER ID       : %s
                    STATUS         : DISPATCHED (IN TRANSIT)
                    ----------------------------------------------
                    CUSTOMER       : %s
                    DESTINATION    : %s
                    ESTIMATED ETA  : Today within 25 mins (Campus Courier)
                    ----------------------------------------------
                    PAYMENT MODE   : %s
                    ITEMS COUNT    : %d item(s)
                    TOTAL CHARGED  : ₹%,.0f ($%,.2f)
                    ==============================================
                    LIVE TRACKING  : Active on SRM Campus Grid
                    Thank you for shopping on Amazon.in via NEXUS!
                    """, orderId, user, currentDeliveryAddress, payment, count, total * 83.0, total));

            p.add(new JScrollPane(receipt), BorderLayout.CENTER);

            JButton closeBtn = new JButton("Close Receipt");
            closeBtn.setBackground(new Color(16, 185, 129));
            closeBtn.setForeground(Color.WHITE);
            closeBtn.addActionListener(ev -> dlg.dispose());
            p.add(closeBtn, BorderLayout.SOUTH);

            dlg.setContentPane(p);
            dlg.setVisible(true);
        }
    }
}
