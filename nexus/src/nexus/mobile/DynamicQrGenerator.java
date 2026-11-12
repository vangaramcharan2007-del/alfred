package nexus.mobile;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * High-performance 2D QR visual matrix generator for NEXUS Mobile Passes.
 * Renders corner finder patterns, timing tracks, and deterministic encrypted payload bitfields.
 */
public class DynamicQrGenerator {

    public static BufferedImage generateQrImage(String payload, int size) {
        int modules = 25; // 25x25 grid
        boolean[][] matrix = new boolean[modules][modules];

        // 1. Draw standard Finder Patterns (7x7) in 3 corners
        drawFinderPattern(matrix, 0, 0);
        drawFinderPattern(matrix, modules - 7, 0);
        drawFinderPattern(matrix, 0, modules - 7);

        // 2. Draw Timing Patterns (row 6 and col 6)
        for (int i = 8; i < modules - 8; i++) {
            matrix[6][i] = (i % 2 == 0);
            matrix[i][6] = (i % 2 == 0);
        }

        // 3. Hash payload into deterministic bitstream
        byte[] hash = sha256(payload);
        int byteIdx = 0;
        int bitIdx = 0;

        for (int r = 0; r < modules; r++) {
            for (int c = 0; c < modules; c++) {
                // Skip finder pattern zones
                if ((r < 8 && c < 8) || (r < 8 && c >= modules - 8) || (r >= modules - 8 && c < 8)) {
                    continue;
                }
                if (r == 6 || c == 6) {
                    continue;
                }

                byte b = hash[byteIdx % hash.length];
                boolean bit = ((b >> (bitIdx % 8)) & 1) == 1;
                matrix[r][c] = bit;

                bitIdx++;
                if (bitIdx % 8 == 0) byteIdx++;
            }
        }

        // Render to BufferedImage
        BufferedImage img = new BufferedImage(size, size, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2 = img.createGraphics();
        g2.setColor(Color.WHITE);
        g2.fillRect(0, 0, size, size);

        g2.setColor(new Color(15, 23, 42)); // Deep Slate / Navy
        double cellSize = (double) size / modules;

        for (int r = 0; r < modules; r++) {
            for (int c = 0; c < modules; c++) {
                if (matrix[r][c]) {
                    int x = (int) Math.round(c * cellSize);
                    int y = (int) Math.round(r * cellSize);
                    int w = (int) Math.ceil(cellSize);
                    int h = (int) Math.ceil(cellSize);
                    g2.fillRect(x, y, w, h);
                }
            }
        }
        g2.dispose();
        return img;
    }

    private static void drawFinderPattern(boolean[][] matrix, int startRow, int startCol) {
        for (int r = 0; r < 7; r++) {
            for (int c = 0; c < 7; c++) {
                if (r == 0 || r == 6 || c == 0 || c == 6) {
                    matrix[startRow + r][startCol + c] = true;
                } else if (r >= 2 && r <= 4 && c >= 2 && c <= 4) {
                    matrix[startRow + r][startCol + c] = true;
                } else {
                    matrix[startRow + r][startCol + c] = false;
                }
            }
        }
    }

    private static byte[] sha256(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            return md.digest(text.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            return text.getBytes(StandardCharsets.UTF_8);
        }
    }
}