package nexus.media;

import javax.swing.*;
import java.awt.*;
import java.util.*;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

public class MediaPanel extends JPanel implements NexusListener {
    private final MediaService service;
    private final ConcurrentHashMap<String, ImageIcon> posterCache = new ConcurrentHashMap<>();
    private final LiveDistrictCinemaService cinemaService = LiveDistrictCinemaService.getInstance();

    // Seat Allocation State
    private final Map<String, CinemaSeat> seatMap = new LinkedHashMap<>();
    private final Map<String, JButton> seatButtons = new HashMap<>();
    private final List<String> selectedSeatCodes = new ArrayList<>();
    private JPanel seatMatrixGrid;

    // Booking Summary Components
    private JLabel districtInfoLabel;
    private JLabel selectedSeatsLabel;
    private JLabel subtotalLabel;
    private JLabel discountLabel;
    private JLabel totalPayableLabel;
    private JTextField promoCodeField;
    private JComboBox<String> paymentMethodCombo;
    private JLabel activeOfferLabel;
    private double currentDiscount = 0.0;
    private String currentPromoCode = "SRMSTUDENT";

    // Cinema Form Pickers & Poster Preview
    private JComboBox<String> districtCombo;
    private JComboBox<String> movieCombo;
    private JComboBox<String> theatreCombo;
    private JComboBox<String> showtimeCombo;
    private JLabel liveOccupancyBadge;
    private JLabel moviePosterPreviewLabel;
    private JLabel screenFormatLabel;

    // Tabs
    private JTabbedPane mainTabs;
    private JPanel bookingsGrid;
    private JPanel watchlistGrid;
    private JPanel liveSearchGrid;
    private JTextField searchField;

    public MediaPanel(MediaService service) {
        this.service = service;
        setLayout(new BorderLayout());
        setBackground(new Color(15, 23, 42));

        mainTabs = new JTabbedPane();
        mainTabs.setFont(new Font("Segoe UI", Font.BOLD, 12));

        // Tab 1: BookMyShow Cinema Box Office
        mainTabs.addTab("🎟️ Cinema Box Office & Real-Time Booking", createBoxOfficePanel());

        // Tab 2: My Bookings
        mainTabs.addTab("🎫 My Movie Passes (Active Bookings)", createMyBookingsPanel());

        // Tab 3: IMDb Explorer & Watchlist
        mainTabs.addTab("🎬 IMDb Online Explorer, Watchlist & Trailers", createWatchlistAndSearchPanel());

        add(mainTabs, BorderLayout.CENTER);

        // Subscriptions
        EventBus.getInstance().subscribe("BOOKINGS_UPDATED", this);
        EventBus.getInstance().subscribe("MEDIA_UPDATED", this);
        EventBus.getInstance().subscribe("MEDIA_SEARCH_RESULTS", this);
        EventBus.getInstance().subscribe("USER_SWITCHED", this);

        renderBookings(service.getBookings());
        renderWatchlist(service.getMediaItems());
    }

    // --- TAB 1: BOOKMYSHOW & DISTRICT BOX OFFICE ---
    private JPanel createBoxOfficePanel() {
        JPanel panel = new JPanel(new BorderLayout(15, 10));
        panel.setBackground(new Color(15, 23, 42));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 12, 10, 12));

        // Top Master Selector Container
        JPanel topContainer = new JPanel();
        topContainer.setLayout(new BoxLayout(topContainer, BoxLayout.Y_AXIS));
        topContainer.setBackground(new Color(30, 41, 59));
        topContainer.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)
        ));

        // Row 1: District & Location Header + Live Sync Pill
        JPanel locationBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 4));
        locationBar.setOpaque(false);

        JLabel locIcon = new JLabel("📍 Select District / Location:");
        locIcon.setFont(new Font("Segoe UI", Font.BOLD, 12));
        locIcon.setForeground(new Color(56, 189, 248));
        locationBar.add(locIcon);

        List<String> districts = cinemaService.getDistricts();
        districtCombo = new JComboBox<>(districts.toArray(new String[0]));
        districtCombo.setFont(new Font("Segoe UI", Font.BOLD, 11));
        districtCombo.setPreferredSize(new Dimension(270, 26));
        districtCombo.addActionListener(e -> onDistrictChanged());
        locationBar.add(districtCombo);

        JButton detectCampusBtn = new JButton("🎯 Detect My Campus");
        detectCampusBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        detectCampusBtn.setBackground(new Color(59, 130, 246));
        detectCampusBtn.setForeground(Color.WHITE);
        detectCampusBtn.setFocusPainted(false);
        detectCampusBtn.setToolTipText("Auto-select SRM KTR & Chengalpattu Campus District");
        detectCampusBtn.addActionListener(e -> {
            districtCombo.setSelectedItem("SRM KTR & Chengalpattu Campus District");
            JOptionPane.showMessageDialog(this, "Location set to SRM KTR & Chengalpattu Campus Zone!", "Campus Location Synced", JOptionPane.INFORMATION_MESSAGE);
        });
        locationBar.add(detectCampusBtn);

        JLabel liveSyncPill = new JLabel("🟢 " + cinemaService.getActiveSource().displayName + " (" + cinemaService.getActiveSource().latency + ")");
        liveSyncPill.setFont(new Font("Segoe UI", Font.BOLD, 10));
        liveSyncPill.setForeground(new Color(52, 211, 153));
        liveSyncPill.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(16, 185, 129)),
                BorderFactory.createEmptyBorder(2, 6, 2, 6)
        ));
        locationBar.add(liveSyncPill);

        JButton switchFeedBtn = new JButton("🔄 Switch to District Feed");
        switchFeedBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        switchFeedBtn.setBackground(new Color(30, 41, 59));
        switchFeedBtn.setForeground(new Color(251, 191, 36));
        switchFeedBtn.setFocusPainted(false);
        switchFeedBtn.setToolTipText("Toggle between BookMyShow and District (Zomato) live ticketing feeds");
        switchFeedBtn.addActionListener(e -> {
            if (cinemaService.getActiveSource() == LiveDistrictCinemaService.DataFeedSource.BOOK_MY_SHOW) {
                cinemaService.setActiveSource(LiveDistrictCinemaService.DataFeedSource.DISTRICT_ZOMATO);
                switchFeedBtn.setText("🔄 Switch to BookMyShow Feed");
                liveSyncPill.setText("🟢 " + cinemaService.getActiveSource().displayName + " (" + cinemaService.getActiveSource().latency + ")");
            } else {
                cinemaService.setActiveSource(LiveDistrictCinemaService.DataFeedSource.BOOK_MY_SHOW);
                switchFeedBtn.setText("🔄 Switch to District Feed");
                liveSyncPill.setText("🟢 " + cinemaService.getActiveSource().displayName + " (" + cinemaService.getActiveSource().latency + ")");
            }
            onShowSelectionChanged();
        });
        locationBar.add(switchFeedBtn);

        JButton bmsJsoupSyncBtn = new JButton("📡 Sync BMS (Jsoup Live)");
        bmsJsoupSyncBtn.setFont(new Font("Segoe UI", Font.BOLD, 10));
        bmsJsoupSyncBtn.setBackground(new Color(225, 29, 72));
        bmsJsoupSyncBtn.setForeground(Color.WHITE);
        bmsJsoupSyncBtn.setFocusPainted(false);
        bmsJsoupSyncBtn.setToolTipText("Scrape BookMyShow Chennai live cinema catalog using Jsoup in real time");
        bmsJsoupSyncBtn.addActionListener(e -> {
            bmsJsoupSyncBtn.setEnabled(false);
            bmsJsoupSyncBtn.setText("📡 Scraping BMS...");
            new SwingWorker<Integer, Void>() {
                @Override
                protected Integer doInBackground() {
                    return cinemaService.syncWithBookMyShowJsoup("chennai");
                }
                @Override
                protected void done() {
                    bmsJsoupSyncBtn.setEnabled(true);
                    bmsJsoupSyncBtn.setText("📡 Sync BMS (Jsoup Live)");
                    try {
                        int count = get();
                        refreshMovieCombo();
                        liveSyncPill.setText("🟢 " + cinemaService.getActiveSource().displayName + " (" + cinemaService.getActiveSource().latency + ")");
                        JOptionPane.showMessageDialog(MediaPanel.this,
                                "BookMyShow Jsoup Real-Time Engine Active!\nSynced " + count + " verified 2026 movies & showtimes.",
                                "BookMyShow Jsoup Scraper", JOptionPane.INFORMATION_MESSAGE);
                    } catch (Exception ignored) {}
                }
            }.execute();
        });
        locationBar.add(bmsJsoupSyncBtn);

        topContainer.add(locationBar);
        topContainer.add(Box.createVerticalStrut(4));

        // Row 2: Movie, Multiplex, Showtime, Trailer Actions & Poster Preview
        JPanel movieControlsBar = new JPanel(new BorderLayout(10, 0));
        movieControlsBar.setOpaque(false);

        // Left Movie Poster Preview
        moviePosterPreviewLabel = new JLabel();
        moviePosterPreviewLabel.setPreferredSize(new Dimension(50, 72));
        moviePosterPreviewLabel.setOpaque(true);
        moviePosterPreviewLabel.setBackground(new Color(15, 23, 42));
        moviePosterPreviewLabel.setHorizontalAlignment(SwingConstants.CENTER);
        movieControlsBar.add(moviePosterPreviewLabel, BorderLayout.WEST);

        // Center Dropdowns
        JPanel pickersGrid = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 4));
        pickersGrid.setOpaque(false);

        List<String> movies = cinemaService.getMovies();
        movieCombo = new JComboBox<>(movies.toArray(new String[0]));
        movieCombo.setFont(new Font("Segoe UI", Font.BOLD, 11));
        movieCombo.setPreferredSize(new Dimension(220, 26));
        movieCombo.addActionListener(e -> onMovieChanged());

        List<String> initialTheatres = cinemaService.getTheatresForDistrict((String) districtCombo.getSelectedItem());
        theatreCombo = new JComboBox<>(initialTheatres.toArray(new String[0]));
        theatreCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        theatreCombo.setPreferredSize(new Dimension(260, 26));
        theatreCombo.addActionListener(e -> onShowSelectionChanged());

        String[] showtimes = {
                "Today • 10:30 AM (Morning Concession)",
                "Today • 02:15 PM (Matinee Laser)",
                "Today • 06:45 PM (Prime IMAX 3D)",
                "Today • 10:30 PM (Night Special)"
        };
        showtimeCombo = new JComboBox<>(showtimes);
        showtimeCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        showtimeCombo.setPreferredSize(new Dimension(210, 26));
        showtimeCombo.addActionListener(e -> onShowSelectionChanged());

        pickersGrid.add(new JLabel("Film:"));
        pickersGrid.add(movieCombo);
        pickersGrid.add(new JLabel("Multiplex:"));
        pickersGrid.add(theatreCombo);
        pickersGrid.add(new JLabel("Time:"));
        pickersGrid.add(showtimeCombo);

        // Live Occupancy Badge
        liveOccupancyBadge = new JLabel("🟡 Fast Filling (12 Seats Left)");
        liveOccupancyBadge.setFont(new Font("Segoe UI", Font.BOLD, 10));
        liveOccupancyBadge.setForeground(new Color(251, 191, 36));
        pickersGrid.add(liveOccupancyBadge);

        movieControlsBar.add(pickersGrid, BorderLayout.CENTER);

        // Right Trailer & Teaser Action Buttons
        JPanel videoButtonsPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 4));
        videoButtonsPanel.setOpaque(false);

        JButton watchTrailerBtn = new JButton("▶ 🎬 Watch Trailer");
        watchTrailerBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        watchTrailerBtn.setBackground(new Color(225, 29, 72)); // Crimson / YouTube Red
        watchTrailerBtn.setForeground(Color.WHITE);
        watchTrailerBtn.setFocusPainted(false);
        watchTrailerBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        watchTrailerBtn.setToolTipText("Open Official 4K Trailer in Web Browser");
        watchTrailerBtn.addActionListener(e -> playCurrentMovieTrailer(false));

        JButton watchTeaserBtn = new JButton("🔥 Watch Teaser");
        watchTeaserBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        watchTeaserBtn.setBackground(new Color(217, 119, 6)); // Amber / Flame
        watchTeaserBtn.setForeground(Color.WHITE);
        watchTeaserBtn.setFocusPainted(false);
        watchTeaserBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        watchTeaserBtn.setToolTipText("Open Official Teaser in Web Browser");
        watchTeaserBtn.addActionListener(e -> playCurrentMovieTrailer(true));

        JButton movieInfoBtn = new JButton("ℹ️ Specs");
        movieInfoBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        movieInfoBtn.setBackground(new Color(51, 65, 85));
        movieInfoBtn.setForeground(Color.WHITE);
        movieInfoBtn.setFocusPainted(false);
        movieInfoBtn.setToolTipText("View Censor Rating, Duration, Cast & Audio Tracks");
        movieInfoBtn.addActionListener(e -> showMovieDetailsDialog((String) movieCombo.getSelectedItem()));

        videoButtonsPanel.add(watchTrailerBtn);
        videoButtonsPanel.add(watchTeaserBtn);
        videoButtonsPanel.add(movieInfoBtn);

        movieControlsBar.add(videoButtonsPanel, BorderLayout.EAST);
        topContainer.add(movieControlsBar);

        panel.add(topContainer, BorderLayout.NORTH);

        // Center Split: Left = Seat Matrix | Right = Checkout & Promo
        JPanel centerGrid = new JPanel(new BorderLayout(15, 0));
        centerGrid.setOpaque(false);

        // SEAT MATRIX PANEL
        JPanel seatArea = new JPanel(new BorderLayout(8, 8));
        seatArea.setBackground(new Color(24, 30, 42));
        seatArea.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));

        screenFormatLabel = new JLabel("--- 🎬 SCREEN THIS WAY • LASER 4K DOLBY ATMOS (ALL EYES FRONT) 🎬 ---", SwingConstants.CENTER);
        screenFormatLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        screenFormatLabel.setForeground(new Color(56, 189, 248));
        screenFormatLabel.setOpaque(true);
        screenFormatLabel.setBackground(new Color(15, 23, 42));
        screenFormatLabel.setBorder(BorderFactory.createEmptyBorder(6, 10, 6, 10));
        seatArea.add(screenFormatLabel, BorderLayout.NORTH);

        seatMatrixGrid = new JPanel(new GridLayout(6, 10, 6, 6));
        seatMatrixGrid.setOpaque(false);
        initSeatMatrix(seatMatrixGrid);
        seatArea.add(seatMatrixGrid, BorderLayout.CENTER);

        JPanel legend = new JPanel(new FlowLayout(FlowLayout.CENTER, 14, 4));
        legend.setOpaque(false);
        legend.add(createLegendChip("Available", new Color(51, 65, 85)));
        legend.add(createLegendChip("Selected", new Color(16, 185, 129)));
        legend.add(createLegendChip("Booked (Live Feed)", new Color(220, 38, 38)));
        legend.add(new JLabel("• VIP Recliner: $350 | Club: $250 | Executive: $150"));
        seatArea.add(legend, BorderLayout.SOUTH);

        centerGrid.add(seatArea, BorderLayout.CENTER);

        // Right Checkout Panel
        JPanel checkoutPanel = createCheckoutPanel();
        checkoutPanel.setPreferredSize(new Dimension(340, 520));
        centerGrid.add(checkoutPanel, BorderLayout.EAST);

        panel.add(centerGrid, BorderLayout.CENTER);

        updateMoviePosterPreview();
        updateOccupancyBadge();

        return panel;
    }

    private void onDistrictChanged() {
        String district = (String) districtCombo.getSelectedItem();
        List<String> theatres = cinemaService.getTheatresForDistrict(district);
        theatreCombo.removeAllItems();
        for (String t : theatres) {
            theatreCombo.addItem(t);
        }
        if (districtInfoLabel != null) {
            districtInfoLabel.setText(district);
        }
        onShowSelectionChanged();
    }

    private void onMovieChanged() {
        updateMoviePosterPreview();
        onShowSelectionChanged();
    }

    private void onShowSelectionChanged() {
        if (seatMatrixGrid != null) {
            initSeatMatrix(seatMatrixGrid);
            seatMatrixGrid.revalidate();
            seatMatrixGrid.repaint();
        }
        updateOccupancyBadge();
        updatePricingSummary();
    }

    private void updateOccupancyBadge() {
        String dist = (String) districtCombo.getSelectedItem();
        String theatre = (String) theatreCombo.getSelectedItem();
        String movie = (String) movieCombo.getSelectedItem();
        String show = (String) showtimeCombo.getSelectedItem();

        LiveDistrictCinemaService.OccupancyInfo info = cinemaService.getOccupancy(dist, theatre, movie, show);
        if (liveOccupancyBadge != null) {
            liveOccupancyBadge.setText(info.statusBadge);
            liveOccupancyBadge.setForeground(Color.decode(info.colorHex));
        }
        if (screenFormatLabel != null && movie != null) {
            String format = movie.contains("IMAX") ? "IMAX 3D LASER" : (movie.contains("4DX") ? "4DX MOTION ATMOS" : "4K DUAL LASER DOLBY ATMOS");
            screenFormatLabel.setText("--- 🎬 SCREEN THIS WAY • " + format + " (ALL EYES FRONT) 🎬 ---");
        }
    }

    private void updateMoviePosterPreview() {
        String movie = (String) movieCombo.getSelectedItem();
        String url = cinemaService.getPosterUrl(movie);
        loadPosterAsync(url, moviePosterPreviewLabel, 50, 72);
    }

    private void playCurrentMovieTrailer(boolean isTeaser) {
        String movie = (String) movieCombo.getSelectedItem();
        cinemaService.openDirectVideo(movie, isTeaser);
        cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), movie, isTeaser);
    }

    private void refreshMovieCombo() {
        if (movieCombo == null) return;
        String current = (String) movieCombo.getSelectedItem();
        movieCombo.removeAllItems();
        for (String m : cinemaService.getMovies()) {
            movieCombo.addItem(m);
        }
        if (current != null) {
            movieCombo.setSelectedItem(current);
        }
    }

    private void showMovieDetailsDialog(String movieTitle) {
        LiveDistrictCinemaService.MovieMeta meta = cinemaService.getMovieMeta(movieTitle);
        if (meta == null) return;

        JDialog dlg = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Film Synopsis & Screening Specs", true);
        dlg.setSize(580, 380);
        dlg.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(14, 12));
        p.setBackground(new Color(24, 30, 42));
        p.setBorder(BorderFactory.createEmptyBorder(15, 18, 15, 18));

        JLabel title = new JLabel(meta.title, SwingConstants.LEFT);
        title.setFont(new Font("Segoe UI", Font.BOLD, 16));
        title.setForeground(new Color(56, 189, 248));
        p.add(title, BorderLayout.NORTH);

        JLabel poster = new JLabel();
        poster.setPreferredSize(new Dimension(100, 145));
        poster.setOpaque(true);
        poster.setBackground(new Color(15, 23, 42));
        loadPosterAsync(meta.posterUrl, poster, 100, 145);

        JPanel center = new JPanel(new BorderLayout(12, 0));
        center.setOpaque(false);
        center.add(poster, BorderLayout.WEST);

        JTextArea info = new JTextArea();
        info.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        info.setEditable(false);
        info.setLineWrap(true);
        info.setWrapStyleWord(true);
        info.setBackground(new Color(15, 23, 42));
        info.setForeground(new Color(226, 232, 240));
        info.setBorder(BorderFactory.createEmptyBorder(8, 10, 8, 10));

        info.setText(String.format("""
                IMDb Rating     : ⭐ %.1f / 10
                Duration        : ⏱️ %s
                Censor Rating   : %s
                Genres          : %s
                Audio Tracks    : %s
                -------------------------------------------------
                Synopsis:
                %s
                """,
                meta.score, meta.duration, meta.censorRating, meta.genres, meta.audioTracks, meta.synopsis));

        center.add(new JScrollPane(info), BorderLayout.CENTER);
        p.add(center, BorderLayout.CENTER);

        JPanel btnBar = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 4));
        btnBar.setOpaque(false);

        JButton playTrBtn = new JButton("▶ 🎬 Watch In-App 4K Trailer");
        playTrBtn.setBackground(new Color(225, 29, 72));
        playTrBtn.setForeground(Color.WHITE);
        playTrBtn.setFocusPainted(false);
        playTrBtn.addActionListener(e -> cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), meta.title, false));

        JButton playTeBtn = new JButton("🔥 Watch Teaser");
        playTeBtn.setBackground(new Color(217, 119, 6));
        playTeBtn.setForeground(Color.WHITE);
        playTeBtn.setFocusPainted(false);
        playTeBtn.addActionListener(e -> cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), meta.title, true));

        JButton close = new JButton("Close");
        close.setBackground(new Color(51, 65, 85));
        close.setForeground(Color.WHITE);
        close.addActionListener(e -> dlg.dispose());

        btnBar.add(playTrBtn);
        btnBar.add(playTeBtn);
        btnBar.add(close);
        p.add(btnBar, BorderLayout.SOUTH);

        dlg.setContentPane(p);
        dlg.setVisible(true);
    }

    private void initSeatMatrix(JPanel grid) {
        seatMap.clear();
        seatButtons.clear();
        selectedSeatCodes.clear();
        grid.removeAll();

        String dist = (String) districtCombo.getSelectedItem();
        String theatre = (String) theatreCombo.getSelectedItem();
        String movie = (String) movieCombo.getSelectedItem();
        String show = (String) showtimeCombo.getSelectedItem();

        Set<String> bookedCodes = cinemaService.generateBookedSeatCodes(dist, theatre, movie, show);

        char[] rows = {'A', 'B', 'C', 'D', 'E', 'F'};

        for (char row : rows) {
            String tier;
            double price;
            if (row == 'A' || row == 'B') {
                tier = "VIP Recliner";
                price = 350.0;
            } else if (row == 'C' || row == 'D') {
                tier = "Club Premium";
                price = 250.0;
            } else {
                tier = "Executive";
                price = 150.0;
            }

            for (int col = 1; col <= 10; col++) {
                String code = "" + row + col;
                CinemaSeat seat = new CinemaSeat(code, tier, price);
                if (bookedCodes.contains(code)) {
                    seat.setBooked(true);
                }
                seatMap.put(code, seat);

                JButton btn = new JButton(code);
                btn.setFont(new Font("Consolas", Font.BOLD, 10));
                btn.setFocusPainted(false);
                btn.setMargin(new Insets(2, 2, 2, 2));

                if (seat.isBooked()) {
                    btn.setBackground(new Color(220, 38, 38));
                    btn.setForeground(Color.WHITE);
                    btn.setEnabled(false);
                    btn.setToolTipText("Seat " + code + " - Booked on Live BookMyShow Feed");
                } else {
                    btn.setBackground(new Color(51, 65, 85));
                    btn.setForeground(Color.WHITE);
                    btn.setToolTipText("Seat " + code + " (" + tier + " - $" + String.format("%.0f", price) + ")");
                    btn.addActionListener(e -> toggleSeat(code, btn));
                }

                seatButtons.put(code, btn);
                grid.add(btn);
            }
        }
    }

    private void toggleSeat(String code, JButton btn) {
        CinemaSeat seat = seatMap.get(code);
        if (seat == null || seat.isBooked()) return;

        if (selectedSeatCodes.contains(code)) {
            selectedSeatCodes.remove(code);
            seat.setSelected(false);
            btn.setBackground(new Color(51, 65, 85));
        } else {
            selectedSeatCodes.add(code);
            seat.setSelected(true);
            btn.setBackground(new Color(16, 185, 129));
        }
        updatePricingSummary();
    }

    private void updatePricingSummary() {
        if (selectedSeatCodes.isEmpty()) {
            selectedSeatsLabel.setText("None Selected");
            subtotalLabel.setText("$0.00");
            discountLabel.setText("-$0.00");
            totalPayableLabel.setText("$0.00");
            currentDiscount = 0.0;
            return;
        }

        double subtotal = 0;
        for (String code : selectedSeatCodes) {
            CinemaSeat seat = seatMap.get(code);
            if (seat != null) subtotal += seat.getPrice();
        }

        selectedSeatsLabel.setText(String.join(", ", selectedSeatCodes));
        subtotalLabel.setText(String.format("$%,.2f", subtotal));

        currentDiscount = service.calculateDiscount(subtotal, currentPromoCode);
        discountLabel.setText(String.format("-$%,.2f (%s)", currentDiscount, currentPromoCode.isEmpty() ? "None" : currentPromoCode));

        double payable = Math.max(0, subtotal - currentDiscount);
        totalPayableLabel.setText(String.format("$%,.2f", payable));
    }

    private JPanel createCheckoutPanel() {
        JPanel panel = new JPanel(new BorderLayout(10, 8));
        panel.setBackground(new Color(30, 41, 59));
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(12, 14, 12, 14)
        ));

        JLabel title = new JLabel("🎟️ BOOKING & PROMO SUMMARY");
        title.setFont(new Font("Segoe UI", Font.BOLD, 13));
        title.setForeground(new Color(56, 189, 248));
        panel.add(title, BorderLayout.NORTH);

        JPanel details = new JPanel();
        details.setLayout(new BoxLayout(details, BoxLayout.Y_AXIS));
        details.setOpaque(false);

        districtInfoLabel = new JLabel("SRM KTR Campus Zone");
        districtInfoLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        districtInfoLabel.setForeground(new Color(147, 197, 253));

        selectedSeatsLabel = new JLabel("None Selected");
        selectedSeatsLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        selectedSeatsLabel.setForeground(new Color(52, 211, 153));

        subtotalLabel = new JLabel("$0.00");
        subtotalLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        subtotalLabel.setForeground(Color.WHITE);

        discountLabel = new JLabel("-$0.00 (None)");
        discountLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        discountLabel.setForeground(new Color(248, 113, 113));

        totalPayableLabel = new JLabel("$0.00");
        totalPayableLabel.setFont(new Font("Segoe UI", Font.BOLD, 20));
        totalPayableLabel.setForeground(new Color(52, 211, 153));

        details.add(createRow("District / City:", districtInfoLabel));
        details.add(Box.createVerticalStrut(3));
        details.add(createRow("Allocated Seats:", selectedSeatsLabel));
        details.add(Box.createVerticalStrut(3));
        details.add(createRow("Base Subtotal:", subtotalLabel));
        details.add(Box.createVerticalStrut(3));
        details.add(createRow("Applied Discount:", discountLabel));
        details.add(Box.createVerticalStrut(3));
        details.add(createRow("Total Amount:", totalPayableLabel));
        details.add(Box.createVerticalStrut(8));

        // PAYMENT MODES SELECTOR
        JLabel payLabel = new JLabel("Select Payment Mode:");
        payLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        payLabel.setForeground(new Color(203, 213, 225));
        details.add(payLabel);
        details.add(Box.createVerticalStrut(3));

        String[] payMethods = {
                "💳 NEXUS Capital Wallet (Instant 1-Click)",
                "⚡ UPI / Google Pay (VPA Scan & Pay)",
                "🏦 Credit / Debit Card (Visa/Mastercard)",
                "🎓 SRM Student Concession Card",
                "🪙 Crypto Pay (BTC / Lightning)"
        };
        paymentMethodCombo = new JComboBox<>(payMethods);
        paymentMethodCombo.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        paymentMethodCombo.setMaximumSize(new Dimension(320, 26));
        details.add(paymentMethodCombo);
        details.add(Box.createVerticalStrut(8));

        // PROMO CONCESSIONS
        JLabel offersLabel = new JLabel("Active Offers & Concessions:");
        offersLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        offersLabel.setForeground(new Color(251, 191, 36));
        details.add(offersLabel);
        details.add(Box.createVerticalStrut(4));

        JPanel offersGrid = new JPanel(new GridLayout(2, 2, 4, 4));
        offersGrid.setOpaque(false);
        offersGrid.setMaximumSize(new Dimension(320, 52));
        offersGrid.add(createOfferChip("SRMSTUDENT", "25% Student"));
        offersGrid.add(createOfferChip("NEXUS50", "$50 Flat"));
        offersGrid.add(createOfferChip("FIRSTSHOW", "15% Morning"));
        offersGrid.add(createOfferChip("WEEKEND", "10% Binge"));
        details.add(offersGrid);
        details.add(Box.createVerticalStrut(8));

        // PROMO CODE FIELD
        JPanel promoRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 0));
        promoRow.setOpaque(false);
        promoCodeField = new JTextField(9);
        promoCodeField.setFont(new Font("Consolas", Font.BOLD, 11));
        promoCodeField.setText("SRMSTUDENT");

        JButton applyPromoBtn = new JButton("Apply");
        applyPromoBtn.setFont(new Font("Segoe UI", Font.BOLD, 10));
        applyPromoBtn.setBackground(new Color(59, 130, 246));
        applyPromoBtn.setForeground(Color.WHITE);
        applyPromoBtn.addActionListener(e -> applyPromo(promoCodeField.getText().trim()));

        promoRow.add(new JLabel("Promo:"));
        promoRow.add(promoCodeField);
        promoRow.add(applyPromoBtn);
        details.add(promoRow);
        details.add(Box.createVerticalStrut(4));

        activeOfferLabel = new JLabel("✓ SRMSTUDENT: 25% Concession Active");
        activeOfferLabel.setFont(new Font("Segoe UI", Font.ITALIC, 10));
        activeOfferLabel.setForeground(new Color(52, 211, 153));
        details.add(activeOfferLabel);

        panel.add(details, BorderLayout.CENTER);

        JButton bookBtn = new JButton("🎟️ Confirm & Generate Pass");
        bookBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        bookBtn.setBackground(new Color(16, 185, 129));
        bookBtn.setForeground(Color.WHITE);
        bookBtn.setPreferredSize(new Dimension(280, 42));
        bookBtn.setFocusPainted(false);
        bookBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        bookBtn.addActionListener(e -> confirmBooking());
        panel.add(bookBtn, BorderLayout.SOUTH);

        return panel;
    }

    private JButton createOfferChip(String code, String desc) {
        JButton btn = new JButton("<html><center><b>" + code + "</b> (" + desc + ")</center></html>");
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        btn.setBackground(new Color(30, 41, 59));
        btn.setForeground(new Color(251, 191, 36));
        btn.setBorder(BorderFactory.createLineBorder(new Color(245, 158, 11), 1));
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.addActionListener(e -> applyPromo(code));
        return btn;
    }

    private void applyPromo(String code) {
        currentPromoCode = code.trim().toUpperCase();
        promoCodeField.setText(currentPromoCode);
        updatePricingSummary();
        if (activeOfferLabel != null) {
            activeOfferLabel.setText("✓ " + currentPromoCode + " Applied! Discount: $" + String.format("%.2f", currentDiscount));
        }
    }

    private void confirmBooking() {
        if (selectedSeatCodes.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please select at least one seat from the matrix.", "No Seats Selected", JOptionPane.WARNING_MESSAGE);
            return;
        }

        String district = (String) districtCombo.getSelectedItem();
        String movie = (String) movieCombo.getSelectedItem();
        String theatre = (String) theatreCombo.getSelectedItem();
        String show = (String) showtimeCombo.getSelectedItem();
        String payment = paymentMethodCombo != null ? (String) paymentMethodCombo.getSelectedItem() : "NEXUS Capital Wallet";

        double subtotal = 0;
        for (String code : selectedSeatCodes) {
            CinemaSeat seat = seatMap.get(code);
            if (seat != null) subtotal += seat.getPrice();
        }
        double payable = Math.max(0, subtotal - currentDiscount);

        CinemaBooking booking = service.createBooking(movie, theatre, district, show, new ArrayList<>(selectedSeatCodes), 
                subtotal, currentDiscount, currentPromoCode, payable, payment);

        for (String code : selectedSeatCodes) {
            CinemaSeat seat = seatMap.get(code);
            if (seat != null) seat.setBooked(true);
            JButton btn = seatButtons.get(code);
            if (btn != null) {
                btn.setBackground(new Color(220, 38, 38));
                btn.setEnabled(false);
            }
        }
        selectedSeatCodes.clear();
        updatePricingSummary();

        showDigitalTicketDialog(booking);
        mainTabs.setSelectedIndex(1);
    }

    private void showDigitalTicketDialog(CinemaBooking b) {
        JDialog dlg = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Digital Cinema Pass - Confirmed", true);
        dlg.setSize(720, 460);
        dlg.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(12, 10));
        p.setBackground(new Color(24, 30, 42));
        p.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        JLabel header = new JLabel("🎟️ NEXUS CINEMA BOARDING PASS", SwingConstants.CENTER);
        header.setFont(new Font("Segoe UI", Font.BOLD, 16));
        header.setForeground(new Color(56, 189, 248));
        p.add(header, BorderLayout.NORTH);

        // Left Poster in Ticket Dialog
        JLabel ticketPosterLabel = new JLabel();
        ticketPosterLabel.setPreferredSize(new Dimension(110, 160));
        ticketPosterLabel.setOpaque(true);
        ticketPosterLabel.setBackground(new Color(15, 23, 42));
        ticketPosterLabel.setHorizontalAlignment(SwingConstants.CENTER);
        String posterUrl = cinemaService.getPosterUrl(b.getMovieTitle());
        loadPosterAsync(posterUrl, ticketPosterLabel, 110, 160);

        JPanel centerPanel = new JPanel(new BorderLayout(10, 0));
        centerPanel.setOpaque(false);
        centerPanel.add(ticketPosterLabel, BorderLayout.WEST);

        JTextArea info = new JTextArea();
        info.setFont(new Font("Consolas", Font.PLAIN, 12));
        info.setEditable(false);
        info.setBackground(new Color(15, 23, 42));
        info.setForeground(Color.WHITE);
        info.setText(String.format("""
                BOOKING REF : %s
                STATUS      : CONFIRMED (PAID)
                -----------------------------------
                LOCATION    : %s
                THEATRE     : %s
                MOVIE       : %s
                SHOWTIME    : %s
                SEATS       : %s
                -----------------------------------
                PAYMENT MODE: %s
                PROMO CODE  : %s (-$%.2f)
                BASE FARE   : $%.2f
                TOTAL PAID  : $%.2f
                ===================================
                VALID FOR CINEMA ADMISSION GATE
                BOOKMYSHOW REAL-TIME INTEGRATION
                """,
                b.getId(), b.getDistrict(), b.getTheatre(), b.getMovieTitle(), b.getShowTime(),
                b.getSeatsFormatted(), b.getPaymentMethod(), b.getPromoCode(), b.getDiscount(),
                b.getBasePrice(), b.getFinalTotal()));

        centerPanel.add(new JScrollPane(info), BorderLayout.CENTER);

        // Right side: Real 2D QR Code Matrix
        JPanel qrPanel = new JPanel(new BorderLayout(0, 4));
        qrPanel.setOpaque(false);
        qrPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(6, 8, 6, 8)
        ));

        String qrPayload = nexus.mobile.MobilePassService.getInstance().generateFullPayload(
                nexus.mobile.MobilePassService.getInstance().getCurrentWindow());
        java.awt.image.BufferedImage qrImg = nexus.mobile.DynamicQrGenerator.generateQrImage(qrPayload, 130);

        JLabel qrLabel = new JLabel(new ImageIcon(qrImg));
        qrLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JLabel qrMeta = new JLabel("<html><center><font color='#38bdf8'><b>GATE SCAN PASS</b></font><br><font color='#94a3b8' size='2'>15s Dynamic Anti-Scalp</font></center></html>", SwingConstants.CENTER);

        qrPanel.add(qrLabel, BorderLayout.CENTER);
        qrPanel.add(qrMeta, BorderLayout.SOUTH);

        centerPanel.add(qrPanel, BorderLayout.EAST);
        p.add(centerPanel, BorderLayout.CENTER);

        JPanel btm = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        btm.setOpaque(false);

        JButton trailerBtn = new JButton("▶ 🎬 In-App Trailer");
        trailerBtn.setBackground(new Color(225, 29, 72));
        trailerBtn.setForeground(Color.WHITE);
        trailerBtn.setFocusPainted(false);
        trailerBtn.addActionListener(e -> cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), b.getMovieTitle(), false));

        JButton mobilePassBtn = new JButton("📱 Test Gate Scanner Simulator");
        mobilePassBtn.setBackground(new Color(59, 130, 246));
        mobilePassBtn.setForeground(Color.WHITE);
        mobilePassBtn.setFocusPainted(false);
        mobilePassBtn.addActionListener(e -> {
            nexus.auth.UserProfile prof = nexus.auth.AccountService.getInstance().getCurrentProfile();
            nexus.mobile.MobilePassService.getInstance().updateActiveBooking(
                    b.getId(), b.getMovieTitle(), b.getSeatsFormatted(),
                    prof != null ? prof.getName() : "Ram Charan Vanga",
                    prof != null ? prof.getRegNo() : "RA2511027010164"
            );
            dlg.dispose();
            EventBus.getInstance().publish(new NexusEvent("NAVIGATION_REQUEST", "Mobile QR Pass (P9)", "Media"));
        });

        JButton close = new JButton("Close Pass");
        close.setBackground(new Color(16, 185, 129));
        close.setForeground(Color.WHITE);
        close.setFocusPainted(false);
        close.addActionListener(e -> dlg.dispose());

        btm.add(trailerBtn);
        btm.add(mobilePassBtn);
        btm.add(close);
        p.add(btm, BorderLayout.SOUTH);

        dlg.setContentPane(p);
        dlg.setVisible(true);
    }

    private JPanel createRow(String labelText, JLabel valLabel) {
        JPanel row = new JPanel(new BorderLayout(6, 0));
        row.setOpaque(false);
        JLabel l = new JLabel(labelText);
        l.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        l.setForeground(new Color(203, 213, 225));
        row.add(l, BorderLayout.WEST);
        row.add(valLabel, BorderLayout.EAST);
        return row;
    }

    private JLabel createLegendChip(String text, Color bg) {
        JLabel l = new JLabel(" " + text + " ");
        l.setFont(new Font("Segoe UI", Font.BOLD, 10));
        l.setOpaque(true);
        l.setBackground(bg);
        l.setForeground(Color.WHITE);
        return l;
    }

    // --- TAB 2: MY BOOKINGS ---
    private JPanel createMyBookingsPanel() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBackground(new Color(15, 23, 42));
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JLabel title = new JLabel("🎫 MY ACTIVE CINEMA PASSES & RESERVATIONS");
        title.setFont(new Font("Segoe UI", Font.BOLD, 13));
        title.setForeground(new Color(56, 189, 248));
        panel.add(title, BorderLayout.NORTH);

        bookingsGrid = new JPanel();
        bookingsGrid.setLayout(new BoxLayout(bookingsGrid, BoxLayout.Y_AXIS));
        bookingsGrid.setBackground(new Color(15, 23, 42));

        JScrollPane scroll = new JScrollPane(bookingsGrid);
        scroll.setBorder(BorderFactory.createEmptyBorder());
        panel.add(scroll, BorderLayout.CENTER);

        return panel;
    }

    private void renderBookings(List<CinemaBooking> bookings) {
        bookingsGrid.removeAll();
        if (bookings == null || bookings.isEmpty()) {
            JLabel empty = new JLabel("No cinema tickets booked yet. Use the Box Office tab to reserve seats!");
            empty.setFont(new Font("Segoe UI", Font.ITALIC, 13));
            empty.setForeground(new Color(156, 163, 175));
            empty.setBorder(BorderFactory.createEmptyBorder(25, 25, 25, 25));
            bookingsGrid.add(empty);
        } else {
            for (CinemaBooking b : bookings) {
                bookingsGrid.add(createBookingCard(b));
                bookingsGrid.add(Box.createVerticalStrut(10));
            }
        }
        bookingsGrid.revalidate();
        bookingsGrid.repaint();
    }

    private JPanel createBookingCard(CinemaBooking b) {
        JPanel card = new JPanel(new BorderLayout(15, 6));
        card.setBackground(new Color(30, 41, 59));
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 4, 0, 0, new Color(16, 185, 129)),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));
        card.setMaximumSize(new Dimension(2000, 115));

        // Poster image thumbnail on each card
        JLabel cardPosterLabel = new JLabel();
        cardPosterLabel.setPreferredSize(new Dimension(50, 75));
        cardPosterLabel.setOpaque(true);
        cardPosterLabel.setBackground(new Color(15, 23, 42));
        cardPosterLabel.setHorizontalAlignment(SwingConstants.CENTER);
        String posterUrl = cinemaService.getPosterUrl(b.getMovieTitle());
        loadPosterAsync(posterUrl, cardPosterLabel, 50, 75);
        card.add(cardPosterLabel, BorderLayout.WEST);

        JPanel left = new JPanel();
        left.setLayout(new BoxLayout(left, BoxLayout.Y_AXIS));
        left.setOpaque(false);

        JLabel ref = new JLabel(b.getId() + " • " + b.getStatus() + "  |  📍 " + b.getDistrict());
        ref.setFont(new Font("Consolas", Font.BOLD, 11));
        ref.setForeground(new Color(52, 211, 153));

        JLabel title = new JLabel(b.getMovieTitle());
        title.setFont(new Font("Segoe UI", Font.BOLD, 14));
        title.setForeground(Color.WHITE);

        JLabel venue = new JLabel(b.getTheatre() + "  |  " + b.getShowTime());
        venue.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        venue.setForeground(new Color(147, 197, 253));

        JLabel payMeta = new JLabel("💳 " + b.getPaymentMethod() + (!"NONE".equalsIgnoreCase(b.getPromoCode()) ? "  •  Promo: " + b.getPromoCode() + " (-$" + String.format("%.2f", b.getDiscount()) + ")" : ""));
        payMeta.setFont(new Font("Segoe UI", Font.BOLD, 10));
        payMeta.setForeground(new Color(56, 189, 248));

        left.add(ref);
        left.add(Box.createVerticalStrut(2));
        left.add(title);
        left.add(Box.createVerticalStrut(2));
        left.add(venue);
        left.add(Box.createVerticalStrut(2));
        left.add(payMeta);

        card.add(left, BorderLayout.CENTER);

        JPanel right = new JPanel();
        right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
        right.setOpaque(false);

        JLabel seats = new JLabel("Seats: " + b.getSeatsFormatted());
        seats.setFont(new Font("Consolas", Font.BOLD, 13));
        seats.setForeground(Color.YELLOW);

        JLabel price = new JLabel(String.format("Paid: $%,.2f", b.getFinalTotal()));
        price.setFont(new Font("Segoe UI", Font.BOLD, 14));
        price.setForeground(Color.WHITE);

        JPanel actionBtnRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 4, 2));
        actionBtnRow.setOpaque(false);

        JButton trailerBtn = new JButton("▶ In-App");
        trailerBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        trailerBtn.setBackground(new Color(225, 29, 72));
        trailerBtn.setForeground(Color.WHITE);
        trailerBtn.setFocusPainted(false);
        trailerBtn.addActionListener(e -> {
            cinemaService.openDirectVideo(b.getMovieTitle(), false);
            cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), b.getMovieTitle(), false);
        });

        JButton teaserBtn = new JButton("⚡ Teaser");
        teaserBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        teaserBtn.setBackground(new Color(217, 119, 6));
        teaserBtn.setForeground(Color.WHITE);
        teaserBtn.setFocusPainted(false);
        teaserBtn.addActionListener(e -> {
            cinemaService.openDirectVideo(b.getMovieTitle(), true);
            cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), b.getMovieTitle(), true);
        });

        JButton viewPassBtn = new JButton("View Pass");
        viewPassBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        viewPassBtn.setBackground(new Color(59, 130, 246));
        viewPassBtn.setForeground(Color.WHITE);
        viewPassBtn.addActionListener(e -> showDigitalTicketDialog(b));

        actionBtnRow.add(trailerBtn);
        actionBtnRow.add(teaserBtn);
        actionBtnRow.add(viewPassBtn);

        right.add(seats);
        right.add(price);
        right.add(Box.createVerticalStrut(2));
        right.add(actionBtnRow);

        card.add(right, BorderLayout.EAST);
        return card;
    }

    // --- TAB 3: IMDB WATCHLIST & DISCOVERY ---
    private JPanel createWatchlistAndSearchPanel() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBackground(new Color(15, 23, 42));
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JPanel searchBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 4));
        searchBar.setBackground(new Color(30, 41, 59));
        searchBar.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));

        searchField = new JTextField("Avengers", 18);
        JButton searchBtn = new JButton("🔍 Search IMDb / TVMaze");
        searchBtn.setBackground(new Color(59, 130, 246));
        searchBtn.setForeground(Color.WHITE);
        searchBtn.addActionListener(e -> {
            String q = searchField.getText().trim();
            if (!q.isEmpty()) service.searchOnline(q);
        });

        searchBar.add(new JLabel("IMDb Search:"));
        searchBar.add(searchField);
        searchBar.add(searchBtn);

        JButton matchmakerBtn = new JButton("🎯 Smart Cinephile Matchmaker");
        matchmakerBtn.setBackground(new Color(16, 185, 129));
        matchmakerBtn.setForeground(Color.WHITE);
        matchmakerBtn.setFocusPainted(false);
        matchmakerBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        matchmakerBtn.addActionListener(e -> {
            String q = searchField.getText().trim();
            if (q.isEmpty()) q = "Blockbuster Sci-Fi & Action";
            final String finalQ = q;
            JOptionPane.showMessageDialog(this, "Analyzing entertainment preferences for: " + finalQ + "...", "Cinephile Matchmaker", JOptionPane.INFORMATION_MESSAGE);
            new Thread(() -> {
                String rec = nexus.copilot.NexusAiClient.queryAi(
                        "Recommend 2 top rated movies or series matching: " + finalQ + " for an engineering student with brief reasons and IMDb score.",
                        "You are NEXUS Smart Movie Recommender. Respond in concise bullet points."
                );
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, rec, "🎬 Cinephile Recommendations (" + finalQ + ")", JOptionPane.INFORMATION_MESSAGE);
                });
            }).start();
        });
        searchBar.add(matchmakerBtn);
        panel.add(searchBar, BorderLayout.NORTH);

        JSplitPane split = new JSplitPane(JSplitPane.VERTICAL_SPLIT);
        split.setResizeWeight(0.5);
        split.setOpaque(false);
        split.setBorder(null);

        watchlistGrid = new JPanel();
        watchlistGrid.setLayout(new BoxLayout(watchlistGrid, BoxLayout.Y_AXIS));
        watchlistGrid.setBackground(new Color(20, 24, 33));
        JScrollPane ws = new JScrollPane(watchlistGrid);
        ws.setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)), "Personal Watchlist (Click ▶ for Trailer)", 0, 0, new Font("Segoe UI", Font.BOLD, 12), Color.CYAN));
        split.setTopComponent(ws);

        liveSearchGrid = new JPanel();
        liveSearchGrid.setLayout(new BoxLayout(liveSearchGrid, BoxLayout.Y_AXIS));
        liveSearchGrid.setBackground(new Color(20, 24, 33));
        JScrollPane ss = new JScrollPane(liveSearchGrid);
        ss.setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)), "Live Online Search Results (With 4K Trailers)", 0, 0, new Font("Segoe UI", Font.BOLD, 12), Color.GREEN));
        split.setBottomComponent(ss);

        panel.add(split, BorderLayout.CENTER);
        return panel;
    }

    private void renderWatchlist(List<MediaItem> items) {
        watchlistGrid.removeAll();
        for (MediaItem item : items) {
            JPanel card = new JPanel(new BorderLayout(10, 0));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createEmptyBorder(6, 10, 6, 10));
            card.setMaximumSize(new Dimension(2000, 58));

            JLabel poster = new JLabel();
            poster.setPreferredSize(new Dimension(35, 45));
            poster.setOpaque(true);
            poster.setBackground(new Color(15, 23, 42));
            loadPosterAsync(item.getPosterUrl(), poster, 35, 45);
            card.add(poster, BorderLayout.WEST);

            JLabel title = new JLabel(item.getTitle() + " (" + item.getType() + ") - " + item.getStatus() + " ★" + item.getRating());
            title.setForeground(Color.WHITE);
            title.setFont(new Font("Segoe UI", Font.BOLD, 12));
            card.add(title, BorderLayout.CENTER);

            JPanel rightBtnRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 4, 0));
            rightBtnRow.setOpaque(false);

            JButton playTrailerBtn = new JButton("▶ In-App");
            playTrailerBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
            playTrailerBtn.setBackground(new Color(225, 29, 72));
            playTrailerBtn.setForeground(Color.WHITE);
            playTrailerBtn.addActionListener(e -> {
                cinemaService.openDirectVideo(item.getTitle(), false);
                cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), item.getTitle(), false);
            });

            JButton del = new JButton("🗑️");
            del.addActionListener(e -> service.deleteMedia(item.getId()));

            rightBtnRow.add(playTrailerBtn);
            rightBtnRow.add(del);
            card.add(rightBtnRow, BorderLayout.EAST);

            watchlistGrid.add(card);
            watchlistGrid.add(Box.createVerticalStrut(4));
        }
        watchlistGrid.revalidate();
        watchlistGrid.repaint();
    }

    private void renderLiveSearchResults(List<MediaItem> items) {
        liveSearchGrid.removeAll();
        for (MediaItem item : items) {
            JPanel card = new JPanel(new BorderLayout(10, 0));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createEmptyBorder(6, 10, 6, 10));
            card.setMaximumSize(new Dimension(2000, 65));

            JLabel poster = new JLabel();
            poster.setPreferredSize(new Dimension(40, 55));
            poster.setOpaque(true);
            poster.setBackground(new Color(15, 23, 42));
            loadPosterAsync(item.getPosterUrl(), poster, 40, 55);
            card.add(poster, BorderLayout.WEST);

            JLabel title = new JLabel(item.getTitle() + " (" + item.getYear() + ") ⭐ " + item.getRatingScore() + "/10 - " + item.getGenres());
            title.setForeground(Color.WHITE);
            title.setFont(new Font("Segoe UI", Font.BOLD, 12));
            card.add(title, BorderLayout.CENTER);

            JPanel actionRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 4, 0));
            actionRow.setOpaque(false);

            JButton playTrailerBtn = new JButton("▶ In-App");
            playTrailerBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
            playTrailerBtn.setBackground(new Color(225, 29, 72));
            playTrailerBtn.setForeground(Color.WHITE);
            playTrailerBtn.addActionListener(e -> {
                cinemaService.openDirectVideo(item.getTitle(), false);
                cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), item.getTitle(), false);
            });

            JButton playTeaserBtn = new JButton("🔥 In-App");
            playTeaserBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
            playTeaserBtn.setBackground(new Color(217, 119, 6));
            playTeaserBtn.setForeground(Color.WHITE);
            playTeaserBtn.addActionListener(e -> {
                cinemaService.openDirectVideo(item.getTitle(), true);
                cinemaService.playInApp((Frame) SwingUtilities.getWindowAncestor(this), item.getTitle(), true);
            });

            JButton addWatchlistBtn = new JButton("+ Watchlist");
            addWatchlistBtn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
            addWatchlistBtn.setBackground(new Color(16, 185, 129));
            addWatchlistBtn.setForeground(Color.WHITE);
            addWatchlistBtn.addActionListener(e -> {
                service.addMediaItem(item);
                JOptionPane.showMessageDialog(this, "Added '" + item.getTitle() + "' to watchlist!", "Watchlist", JOptionPane.INFORMATION_MESSAGE);
            });

            actionRow.add(playTrailerBtn);
            actionRow.add(playTeaserBtn);
            actionRow.add(addWatchlistBtn);
            card.add(actionRow, BorderLayout.EAST);

            liveSearchGrid.add(card);
            liveSearchGrid.add(Box.createVerticalStrut(4));
        }
        liveSearchGrid.revalidate();
        liveSearchGrid.repaint();
    }

    private void loadPosterAsync(String url, JLabel label, int width, int height) {
        if (url == null || url.isEmpty()) {
            label.setText("🎬");
            label.setForeground(Color.GRAY);
            return;
        }
        if (posterCache.containsKey(url)) {
            label.setIcon(posterCache.get(url));
            label.setText("");
            return;
        }
        label.setText("⌛");
        new Thread(() -> {
            ImageIcon icon = RealtimeMediaService.loadScaledPoster(url, width, height);
            SwingUtilities.invokeLater(() -> {
                if (icon != null) {
                    posterCache.put(url, icon);
                    label.setIcon(icon);
                    label.setText("");
                } else {
                    label.setText("🎬");
                }
            });
        }).start();
    }

    @Override
    public void onEvent(NexusEvent event) {
        SwingUtilities.invokeLater(() -> {
            if ("BOOKINGS_UPDATED".equals(event.getType())) {
                @SuppressWarnings("unchecked")
                List<CinemaBooking> updated = (List<CinemaBooking>) event.getPayload();
                renderBookings(updated);
            } else if ("MEDIA_UPDATED".equals(event.getType())) {
                @SuppressWarnings("unchecked")
                List<MediaItem> updated = (List<MediaItem>) event.getPayload();
                renderWatchlist(updated);
            } else if ("MEDIA_SEARCH_RESULTS".equals(event.getType())) {
                @SuppressWarnings("unchecked")
                List<MediaItem> results = (List<MediaItem>) event.getPayload();
                renderLiveSearchResults(results);
            } else if ("USER_SWITCHED".equals(event.getType())) {
                nexus.auth.UserProfile profile = (nexus.auth.UserProfile) event.getPayload();
                syncUserProfile(profile);
            }
        });
    }

    private void syncUserProfile(nexus.auth.UserProfile profile) {
        if (profile == null) return;
        if (paymentMethodCombo != null) {
            String def = profile.getDefaultPaymentMethod();
            if (def.contains("Faculty") || def.contains("Concession")) {
                paymentMethodCombo.setSelectedItem("🎓 SRM Student Concession Card");
            } else if (def.contains("UPI")) {
                paymentMethodCombo.setSelectedItem("⚡ UPI / Google Pay (VPA Scan & Pay)");
            } else {
                paymentMethodCombo.setSelectedItem("💳 NEXUS Capital Wallet (Instant 1-Click)");
            }
        }
    }
}
