// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week6;

public class Order {
    private String orderId;
    private String customerId;
    private double _amt;
    private boolean processed = false;

    public Order(String orderId, String customerId, double _amt) {
        this.orderId = orderId;
        this.customerId = customerId;
        this._amt = _amt;
    }

    public String getOrderId() { return orderId; }
    public double getAmount() { return _amt; }
    public boolean isProcessed() { return processed; }
    public void setProcessed(boolean p) { this.processed = p; }
}