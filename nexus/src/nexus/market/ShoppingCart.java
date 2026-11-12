package nexus.market;

import java.util.ArrayList;
import java.util.List;

public class ShoppingCart {
    private List<CartItem> items;
    private double discountRate = 0.0;
    
    public ShoppingCart() {
        items = new ArrayList<>();
    }
    
    public void addItem(Product product, int quantity) {
        items.add(new CartItem(product, quantity));
    }
    
    public List<CartItem> getItems() { return items; }
    
    public void clear() { items.clear(); }

    public void setDiscountRate(double rate) { this.discountRate = rate; }
    public double getDiscountRate() { return this.discountRate; }
    
    public double getTotal() {
        double baseTotal = items.stream().mapToDouble(CartItem::getTotalPrice).sum();
        return baseTotal * (1.0 - discountRate);
    }
}
