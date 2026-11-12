package nexus.media;

import javax.swing.ImageIcon;
import nexus.common.IdGenerator;

public class MediaItem {
    private String id;
    private String title;
    private MediaType type;
    private MediaStatus status;
    private int rating; // User star rating 1 to 5
    private String posterUrl;
    private String genres;
    private double ratingScore; // e.g. IMDB 8.4
    private String summary;
    private String year;
    private String trailerUrl;
    private String teaserUrl;
    private transient ImageIcon posterImage;

    public MediaItem(String title, MediaType type) {
        this(title, type, "General", 0.0, "", "");
    }

    public MediaItem(String title, MediaType type, String genres, double ratingScore, String summary, String posterUrl) {
        this(title, type, genres, ratingScore, summary, posterUrl, "", "");
    }

    public MediaItem(String title, MediaType type, String genres, double ratingScore, String summary, 
                     String posterUrl, String trailerUrl, String teaserUrl) {
        this.id = IdGenerator.generateId();
        this.title = title;
        this.type = type != null ? type : MediaType.MOVIE;
        this.status = MediaStatus.WANT_TO_CONSUME;
        this.rating = 0;
        this.genres = genres != null ? genres : "General";
        this.ratingScore = ratingScore;
        this.summary = summary != null ? summary : "";
        this.posterUrl = posterUrl != null ? posterUrl : "";
        this.year = "2026";
        this.trailerUrl = trailerUrl != null ? trailerUrl : "";
        this.teaserUrl = teaserUrl != null ? teaserUrl : "";
    }

    public MediaItem(String id, String title, MediaType type, MediaStatus status, int rating, 
                     String posterUrl, String genres, double ratingScore, String summary, String year) {
        this(id, title, type, status, rating, posterUrl, genres, ratingScore, summary, year, "", "");
    }

    public MediaItem(String id, String title, MediaType type, MediaStatus status, int rating, 
                     String posterUrl, String genres, double ratingScore, String summary, String year,
                     String trailerUrl, String teaserUrl) {
        this.id = id;
        this.title = title;
        this.type = type != null ? type : MediaType.MOVIE;
        this.status = status != null ? status : MediaStatus.WANT_TO_CONSUME;
        this.rating = rating;
        this.posterUrl = posterUrl != null ? posterUrl : "";
        this.genres = genres != null ? genres : "General";
        this.ratingScore = ratingScore;
        this.summary = summary != null ? summary : "";
        this.year = year != null ? year : "";
        this.trailerUrl = trailerUrl != null ? trailerUrl : "";
        this.teaserUrl = teaserUrl != null ? teaserUrl : "";
    }

    public String getId() { return id; }
    public String getTitle() { return title; }
    public MediaType getType() { return type; }
    public MediaStatus getStatus() { return status; }
    public int getRating() { return rating; }
    public String getPosterUrl() { return posterUrl; }
    public String getGenres() { return genres; }
    public double getRatingScore() { return ratingScore; }
    public String getSummary() { return summary; }
    public String getYear() { return year; }
    public String getTrailerUrl() { return trailerUrl; }
    public String getTeaserUrl() { return teaserUrl; }
    public ImageIcon getPosterImage() { return posterImage; }

    public void setStatus(MediaStatus status) { this.status = status; }
    public void setRating(int rating) { this.rating = rating; }
    public void setPosterUrl(String posterUrl) { this.posterUrl = posterUrl; }
    public void setGenres(String genres) { this.genres = genres; }
    public void setRatingScore(double ratingScore) { this.ratingScore = ratingScore; }
    public void setSummary(String summary) { this.summary = summary; }
    public void setYear(String year) { this.year = year; }
    public void setTrailerUrl(String trailerUrl) { this.trailerUrl = trailerUrl; }
    public void setTeaserUrl(String teaserUrl) { this.teaserUrl = teaserUrl; }
    public void setPosterImage(ImageIcon posterImage) { this.posterImage = posterImage; }

    @Override
    public String toString() {
        return String.format("[%s] %s (%s) - %s ★%d", type, title, year, status, rating);
    }
}
