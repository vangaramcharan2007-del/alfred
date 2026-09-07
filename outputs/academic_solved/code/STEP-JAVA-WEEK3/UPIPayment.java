// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week3;

public class UPIPayment implements PaymentGateway, Refundable {
    private String vpa;

    public UPIPayment(String vpa) {
        if (!vpa.contains("@")) throw new IllegalArgumentException("Invalid VPA handle.");
        this.vpa = vpa;
    }

    @Override
    public boolean processPayment(String transactionId, double _amt) {
        System.out.println("[UPI] Charging INR " + _amt + " to VPA: " + vpa);
        return _amt > 0 && _amt <= 100000;
    }

    @Override
    public boolean processRefund(String transactionId, double refundAmount) {
        System.out.println("[UPI] Crediting refund INR " + refundAmount + " to VPA: " + vpa);
        return true;
    }

    @Override
    public String getProviderName() { return "NPCI-UnifiedPaymentsInterface"; }
}