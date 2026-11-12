package nexus.market;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import java.util.ArrayList;
import java.util.List;

public class MarketService implements NexusListener {
    private List<Product> availableProducts;
    private ShoppingCart cart;
    private boolean loading;
    
    public MarketService() {
        availableProducts = new ArrayList<>();
        cart = new ShoppingCart();
        loading = false;
        
        EventBus.getInstance().subscribe("XP_UPDATED", this);

        // Fetch initial Amazon products
        searchMarket("laptop");
    }

    public void searchMarket(String query) {
        loading = true;
        EventBus.getInstance().publish(new NexusEvent("MARKET_LOADING", true, "Market"));
        new Thread(() -> {
            List<Product> scrapedProducts = nexus.realtime.WebMarketScraper.scrapeMarket(query);
            availableProducts.clear();
            availableProducts.addAll(scrapedProducts);
            loading = false;
            EventBus.getInstance().publish(new NexusEvent("MARKET_UPDATED", null, "Market"));
        }).start();
    }
    
    public List<Product> getAvailableProducts() { return availableProducts; }
    public boolean isLoading() { return loading; }
    
    public void addToCart(Product product, int quantity) {
        cart.addItem(product, quantity);
        EventBus.getInstance().publish(new NexusEvent("CART_UPDATED", cart, "Market"));
    }
    
    public void checkout() {
        double total = cart.getTotal();
        if (total > 0) {
            EventBus.getInstance().publish(new NexusEvent("PRODUCT_PURCHASED", total, "Market"));
            for (CartItem item : cart.getItems()) {
                EventBus.getInstance().publish(new NexusEvent("ITEM_PURCHASED", item.getProduct(), "Market"));
            }
            cart.clear();
            EventBus.getInstance().publish(new NexusEvent("CART_UPDATED", cart, "Market"));
        }
    }
    
    public ShoppingCart getCart() { return cart; }

    @Override
    public void onEvent(NexusEvent event) {
        if ("XP_UPDATED".equals(event.getType())) {
            int score = (Integer) event.getPayload();
            double discount = 0.0;
            if (score >= 5000) discount = 0.15;
            else if (score >= 1000) discount = 0.05;
            
            cart.setDiscountRate(discount);
            EventBus.getInstance().publish(new NexusEvent("CART_UPDATED", cart, "Market"));
        }
    }
}
