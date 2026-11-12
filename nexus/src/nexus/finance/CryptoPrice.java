package nexus.finance;

public class CryptoPrice {
    private final String symbol;
    private final String name;
    private final double priceUSD;
    private final double priceINR;
    private final double change24h;

    public CryptoPrice(String symbol, String name, double priceUSD, double priceINR, double change24h) {
        this.symbol = symbol;
        this.name = name;
        this.priceUSD = priceUSD;
        this.priceINR = priceINR;
        this.change24h = change24h;
    }

    public String getSymbol() { return symbol; }
    public String getName() { return name; }
    public double getPriceUSD() { return priceUSD; }
    public double getPriceINR() { return priceINR; }
    public double getChange24h() { return change24h; }

    @Override
    public String toString() {
        String sign = change24h >= 0 ? "+" : "";
        return String.format("%s: $%,.2f (₹%,.0f) %s%.2f%%", symbol, priceUSD, priceINR, sign, change24h);
    }
}
