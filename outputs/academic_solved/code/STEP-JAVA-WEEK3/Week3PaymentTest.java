// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week3;

public class Week3PaymentTest {
    public static void main(String[] args) {
        System.out.println("Running Week 3 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        PaymentGateway upi = new UPIPayment("ramcharan@okhdfcbank");
        assert upi.processPayment("TXN-001", 1500.0) : "UPI transaction failed";
        
        PaymentGateway card = new CreditCardPayment("4111222233334444", "789");
        assert card.processPayment("TXN-002", 5000.0) : "Card payment authorization failed";
        System.out.println("WEEK 3 TESTS PASSED (100%)");
    }
}