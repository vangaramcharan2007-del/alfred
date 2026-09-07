// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week3;

public interface PaymentGateway {
    boolean processPayment(String transactionId, double _amt);
    String getProviderName();
}