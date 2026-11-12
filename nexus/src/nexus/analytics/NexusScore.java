package nexus.analytics;

public class NexusScore {
    private int score;
    
    public NexusScore(int score) {
        this.score = score;
    }
    
    public int getScore() { return score; }
    public void addPoints(int points) { score += points; }
    public void deductPoints(int points) { score -= points; }
}
