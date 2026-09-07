// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week3;

public class CreditCardPayment implements PaymentGateway, Refundable {
    private String cardNumber;
    private String cvv;

    public CreditCardPayment(String cardNumber, String cvv) {
        this.cardNumber = cardNumber;
        this.cvv = cvv;
    }

    @Override
    public boolean processPayment(String transactionId, double _amt) {
        System.out.println("[CreditCard] Authorizing txn " + transactionId + " for _amt " + _amt);
        return _amt > 0 && cvv.length() == 3;
    }

    @Override
    public boolean processRefund(String transactionId, double refundAmount) {
        System.out.println("[CreditCard] Reversing txn " + transactionId);
        return true;
    }

    @Override
    public String getProviderName() { return "MasterCard-Visa-Gateway"; }
}