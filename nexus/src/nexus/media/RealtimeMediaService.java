package nexus.media;

import org.jsoup.Jsoup;
import java.awt.Image;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

public class RealtimeMediaService {
    private static final String SEARCH_URL = "https://api.tvmaze.com/search/shows?q=";

    public static List<MediaItem> searchShowsOnline(String query) {
        List<MediaItem> results = new ArrayList<>();
        if (query == null || query.trim().isEmpty()) {
            query = "batman";
        }
        try {
            String encodedQuery = URLEncoder.encode(query.trim(), StandardCharsets.UTF_8.name());
            String json = Jsoup.connect(SEARCH_URL + encodedQuery)
                    .ignoreContentType(true)
                    .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) NEXUS/10.0")
                    .timeout(6000)
                    .get()
                    .body()
                    .text();

            // Match each show object block
            Pattern showPattern = Pattern.compile("\\{\"score\":[0-9.]+,\\s*\"show\":\\{(.*?)\\}\\}(?:,\t*|$)");
            // Alternatively split by "show":{"
            String[] parts = json.split("\"show\":\\{");
            for (int i = 1; i < parts.length; i++) {
                String block = parts[i];
                String name = extractString(block, "\"name\":\"(.*?)\"");
                String premiered = extractString(block, "\"premiered\":\"(.*?)\"");
                String year = premiered.length() >= 4 ? premiered.substring(0, 4) : "2026";
                
                // Genres
                String genresStr = "Drama";
                Matcher gm = Pattern.compile("\"genres\":\\[(.*?)\\]").matcher(block);
                if (gm.find()) {
                    genresStr = gm.group(1).replace("\"", "").replace(",", ", ");
                    if (genresStr.trim().isEmpty()) genresStr = "General";
                }

                // Rating
                double rating = 7.5;
                Matcher rm = Pattern.compile("\"rating\":\\{\"average\":([0-9.]+)\\}").matcher(block);
                if (rm.find()) {
                    rating = Double.parseDouble(rm.group(1));
                }

                // Summary
                String rawSummary = extractString(block, "\"summary\":\"(.*?)\"");
                String cleanSummary = rawSummary.replaceAll("<[^>]*>", "").replace("\\\"", "\"").replace("\\n", " ");
                if (cleanSummary.length() > 200) {
                    cleanSummary = cleanSummary.substring(0, 197) + "...";
                }

                // Image URL
                String posterUrl = extractString(block, "\"medium\":\"(.*?)\"");
                if (posterUrl.isEmpty()) {
                    posterUrl = extractString(block, "\"original\":\"(.*?)\"");
                }
                posterUrl = posterUrl.replace("\\/", "/");

                if (!name.isEmpty()) {
                    MediaItem item = new MediaItem(name, MediaType.TV_SHOW, genresStr, rating, cleanSummary, posterUrl);
                    item.setYear(year);
                    results.add(item);
                }
            }
        } catch (Exception e) {
            System.err.println("[RealtimeMedia] Online search failed: " + e.getMessage());
            // Fallback rich entries
            results.add(new MediaItem("Breaking Bad", MediaType.TV_SHOW, "Crime, Drama, Thriller", 9.5, 
                    "A chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.", ""));
            results.add(new MediaItem("Inception", MediaType.MOVIE, "Action, Sci-Fi", 8.8, 
                    "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.", ""));
            results.add(new MediaItem("The Dark Knight", MediaType.MOVIE, "Action, Crime, Drama", 9.0, 
                    "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.", ""));
        }
        return results;
    }

    public static ImageIcon loadScaledPoster(String imageUrl, int width, int height) {
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            return null;
        }
        try {
            Image img = ImageIO.read(new URL(imageUrl));
            if (img != null) {
                Image scaled = img.getScaledInstance(width, height, Image.SCALE_SMOOTH);
                return new ImageIcon(scaled);
            }
        } catch (Exception e) {
            // ignore failure
        }
        return null;
    }

    private static String extractString(String text, String regex) {
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(text);
        if (m.find()) {
            return m.group(1);
        }
        return "";
    }
}
