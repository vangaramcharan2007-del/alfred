package nexus.market;

import nexus.common.IdGenerator;

public class Product {
    private String id;
    private String name;
    private double price;
    private String category;
    private java.awt.Image image;
    
    public Product(String name, double price) {
        this.id = IdGenerator.generateId();
        this.name = name;
        this.price = price;
    }

    public Product(String name, double price, String category, java.awt.Image image) {
        this.id = IdGenerator.generateId();
        this.name = name;
        this.price = price;
        this.category = category;
        this.image = image;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public double getPrice() { return price; }
    public String getCategory() { return category; }
    public java.awt.Image getImage() { return image; }
}
