package nexus.tenant;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

/**
 * Phase 16 UI Panel: Multi-Tenant Campus Sharding & RBAC 2.0 Governance.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class TenantPanel extends JPanel {
    private final TenantService service = TenantService.getInstance();

    private final JComboBox<CampusTenant> campusCombo;
    private final JLabel populationLabel;
    private final JLabel hostelsLabel;
    private final JLabel namespaceLabel;
    private final JLabel capitalLabel;

    private final JComboBox<TenantRole> testRoleCombo;
    private final JComboBox<TenantPermission> testPermCombo;
    private final JLabel authResultBadge;
    private final JTextArea authLogArea;

    public TenantPanel() {
        setLayout(new BorderLayout(10, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER & CAMPUS TENANT SELECTOR
        JPanel topContainer = new JPanel(new BorderLayout(0, 8));
        topContainer.setOpaque(false);

        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("🏛️ MULTI-TENANT CAMPUS SHARDING & RBAC 2.0 HIERARCHY (PHASE 16)");
        title.setFont(new Font("Consolas", Font.BOLD, 14));
        title.setForeground(new Color(56, 189, 248));

        JPanel selectorPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        selectorPanel.setOpaque(false);

        JLabel selectLabel = new JLabel("Active Campus Partition:");
        selectLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        selectLabel.setForeground(new Color(148, 163, 184));

        campusCombo = new JComboBox<>(service.getTenants().toArray(new CampusTenant[0]));
        campusCombo.setFont(new Font("Segoe UI", Font.BOLD, 11));
        campusCombo.setBackground(new Color(15, 23, 42));
        campusCombo.setForeground(Color.WHITE);
        campusCombo.setPreferredSize(new Dimension(280, 28));
        campusCombo.addActionListener(e -> {
            CampusTenant sel = (CampusTenant) campusCombo.getSelectedItem();
            if (sel != null) {
                service.switchTenant(sel);
                updateTenantHud();
                logAuth("🏛️ Switched active tenant partition to: " + sel.getCampusName() + " [" + sel.getPartitionDbNamespace() + "]");
            }
        });

        selectorPanel.add(selectLabel);
        selectorPanel.add(campusCombo);

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(selectorPanel, BorderLayout.EAST);
        topContainer.add(headerBar, BorderLayout.NORTH);

        // 2. TENANT SHARDING HUD CARDS (4 Cards)
        JPanel hudGrid = new JPanel(new GridLayout(1, 4, 10, 0));
        hudGrid.setOpaque(false);

        populationLabel = new JLabel("42,000");
        hostelsLabel = new JLabel("4 Blocks");
        namespaceLabel = new JLabel("srm_ktr_partition_wal");
        capitalLabel = new JLabel("₹12,50,000");

        hudGrid.add(createCard("STUDENT POPULATION", populationLabel, new Color(59, 130, 246)));
        hudGrid.add(createCard("HOSTEL RESIDENCES", hostelsLabel, new Color(16, 185, 129)));
        hudGrid.add(createCard("SHARD DATABASE NAMESPACE", namespaceLabel, new Color(168, 85, 247)));
        hudGrid.add(createCard("CAMPUS WORKING CAPITAL", capitalLabel, new Color(245, 158, 11)));

        topContainer.add(hudGrid, BorderLayout.SOUTH);
        add(topContainer, BorderLayout.NORTH);

        // 3. CENTER: LEFT = RBAC PERMISSION MATRIX | RIGHT = POLICY EVALUATION ENGINE
        JPanel centerGrid = new JPanel(new GridLayout(1, 2, 12, 0));
        centerGrid.setOpaque(false);

        // Left: Permission Matrix Table
        JPanel leftPanel = new JPanel(new BorderLayout(0, 8));
        leftPanel.setBackground(new Color(24, 30, 42));
        leftPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        JLabel matrixTitle = new JLabel("🛡️ RBAC 2.0 ROLE-PERMISSION MATRIX (CRYPTOGRAPHIC AUDIT COMPLIANT):");
        matrixTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        matrixTitle.setForeground(new Color(56, 189, 248));
        leftPanel.add(matrixTitle, BorderLayout.NORTH);

        String[] cols = {"Campus Role", "Market", "Cinema", "Disburse", "Outing", "Sign Grade", "Audit"};
        DefaultTableModel model = new DefaultTableModel(cols, 0);

        for (TenantRole r : TenantRole.values()) {
            model.addRow(new Object[]{
                    r.title,
                    r.hasPermission(TenantPermission.ORDER_MARKET) ? "✓" : "—",
                    r.hasPermission(TenantPermission.BOOK_CINEMA) ? "✓" : "—",
                    r.hasPermission(TenantPermission.DISBURSE_BUDGET) ? "✓" : "—",
                    r.hasPermission(TenantPermission.APPROVE_OUTING) ? "✓" : "—",
                    r.hasPermission(TenantPermission.SIGN_EVALUATION) ? "✓" : "—",
                    r.hasPermission(TenantPermission.AUDIT_PLATFORM_LEDGER) ? "✓" : "—"
            });
        }

        JTable table = new JTable(model);
        table.setRowHeight(26);
        table.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        table.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 11));

        DefaultTableCellRenderer centerRender = new DefaultTableCellRenderer();
        centerRender.setHorizontalAlignment(SwingConstants.CENTER);
        for (int i = 1; i < cols.length; i++) {
            table.getColumnModel().getColumn(i).setCellRenderer(centerRender);
        }

        leftPanel.add(new JScrollPane(table), BorderLayout.CENTER);
        centerGrid.add(leftPanel);

        // Right: Real-Time Policy Simulator
        JPanel rightPanel = new JPanel(new BorderLayout(0, 8));
        rightPanel.setBackground(new Color(24, 30, 42));
        rightPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        JLabel simTitle = new JLabel("⚡ REAL-TIME SECURITY POLICY EVALUATOR & ZERO-TRUST GATE:");
        simTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        simTitle.setForeground(new Color(52, 211, 153));
        rightPanel.add(simTitle, BorderLayout.NORTH);

        JPanel simForm = new JPanel(new GridLayout(3, 1, 0, 6));
        simForm.setOpaque(false);

        // Role Selector Row
        JPanel roleRow = new JPanel(new BorderLayout(6, 0));
        roleRow.setOpaque(false);
        JLabel rl = new JLabel("Acting Principal Role:");
        rl.setFont(new Font("Segoe UI", Font.BOLD, 11));
        rl.setForeground(new Color(203, 213, 225));
        testRoleCombo = new JComboBox<>(TenantRole.values());
        testRoleCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        roleRow.add(rl, BorderLayout.WEST);
        roleRow.add(testRoleCombo, BorderLayout.CENTER);
        simForm.add(roleRow);

        // Permission Action Row
        JPanel permRow = new JPanel(new BorderLayout(6, 0));
        permRow.setOpaque(false);
        JLabel pl = new JLabel("Requested Action:");
        pl.setFont(new Font("Segoe UI", Font.BOLD, 11));
        pl.setForeground(new Color(203, 213, 225));
        testPermCombo = new JComboBox<>(TenantPermission.values());
        testPermCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        permRow.add(pl, BorderLayout.WEST);
        permRow.add(testPermCombo, BorderLayout.CENTER);
        simForm.add(permRow);

        // Action Buttons Row
        JPanel actionRow = new JPanel(new BorderLayout(8, 0));
        actionRow.setOpaque(false);

        authResultBadge = new JLabel(" [SELECT ACTION & TEST POLICY] ");
        authResultBadge.setFont(new Font("Segoe UI", Font.BOLD, 11));
        authResultBadge.setOpaque(true);
        authResultBadge.setBackground(new Color(30, 41, 59));
        authResultBadge.setForeground(Color.LIGHT_GRAY);

        JButton testBtn = new JButton("Test RBAC Policy ⚡");
        testBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        testBtn.setBackground(new Color(16, 185, 129));
        testBtn.setForeground(Color.WHITE);
        testBtn.addActionListener(e -> evaluatePolicy());

        actionRow.add(authResultBadge, BorderLayout.CENTER);
        actionRow.add(testBtn, BorderLayout.EAST);
        simForm.add(actionRow);

        JPanel rightCenter = new JPanel(new BorderLayout(0, 8));
        rightCenter.setOpaque(false);
        rightCenter.add(simForm, BorderLayout.NORTH);

        authLogArea = new JTextArea();
        authLogArea.setEditable(false);
        authLogArea.setFont(new Font("Consolas", Font.PLAIN, 11));
        authLogArea.setBackground(new Color(10, 15, 30));
        authLogArea.setForeground(new Color(0, 255, 200));
        authLogArea.setText("""
                [PHASE 16 MULTI-TENANT RBAC GATEWAY ACTIVE]
                • Zero-Trust access model enforced across campus partitions.
                • Strict data isolation: SRM-KTR, SRM-RMP, SRM-VDP, SRM-NCR.
                --------------------------------------------------------------
                """);
        JScrollPane logScroll = new JScrollPane(authLogArea);
        logScroll.setPreferredSize(new Dimension(300, 140));
        rightCenter.add(logScroll, BorderLayout.CENTER);

        rightPanel.add(rightCenter, BorderLayout.CENTER);
        centerGrid.add(rightPanel);

        add(centerGrid, BorderLayout.CENTER);

        updateTenantHud();
    }

    private void updateTenantHud() {
        CampusTenant t = service.getActiveTenant();
        populationLabel.setText(String.format("%,d Students", t.getStudentPopulation()));
        hostelsLabel.setText(t.getActiveHostels().size() + " Blocks (" + String.join(", ", t.getActiveHostels()) + ")");
        namespaceLabel.setText(t.getPartitionDbNamespace());
        capitalLabel.setText(String.format("₹%,.0f", t.getLocalWorkingCapital()));
    }

    private void evaluatePolicy() {
        TenantRole role = (TenantRole) testRoleCombo.getSelectedItem();
        TenantPermission perm = (TenantPermission) testPermCombo.getSelectedItem();

        if (role == null || perm == null) return;

        boolean allowed = service.authorizeAction(role, perm);

        if (allowed) {
            authResultBadge.setText(" ✅ 200 OK - PERMITTED: " + role.title + " GRANTED " + perm.name() + " ");
            authResultBadge.setBackground(new Color(6, 78, 59));
            authResultBadge.setForeground(new Color(52, 211, 153));
            logAuth(String.format("✓ AUTHORIZED: Role [%s] possesses permission [%s] in partition [%s].",
                    role.title, perm.name(), service.getActiveTenant().getTenantId()));
        } else {
            authResultBadge.setText(" 🛑 403 FORBIDDEN - DENIED: " + role.title + " LACKS " + perm.name() + " ");
            authResultBadge.setBackground(new Color(127, 29, 29));
            authResultBadge.setForeground(new Color(248, 113, 113));
            logAuth(String.format("🚨 DENIED (403): Role [%s] attempted unauthorized action [%s]. Blocked by RBAC 2.0 policy gate.",
                    role.title, perm.name()));
        }
    }

    private JPanel createCard(String title, JLabel val, Color accent) {
        JPanel card = new JPanel(new BorderLayout(2, 2));
        card.setBackground(new Color(30, 41, 59));
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 3, 0, 0, accent),
                BorderFactory.createEmptyBorder(6, 8, 6, 8)
        ));

        JLabel t = new JLabel(title);
        t.setFont(new Font("Segoe UI", Font.BOLD, 9));
        t.setForeground(new Color(148, 163, 184));

        val.setFont(new Font("Segoe UI", Font.BOLD, 12));
        val.setForeground(Color.WHITE);

        card.add(t, BorderLayout.NORTH);
        card.add(val, BorderLayout.CENTER);
        return card;
    }

    private void logAuth(String msg) {
        authLogArea.append(msg + "\n");
        authLogArea.setCaretPosition(authLogArea.getDocument().getLength());
    }
}
