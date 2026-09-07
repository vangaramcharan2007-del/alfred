// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week4;

public class Week4BankingTest {
    public static void main(String[] args) {
        System.out.println("Running Week 4 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        SavingsAccount sa = new SavingsAccount("SA-101", "Ram Charan", 10000, 4.5);
        CurrentAccount ca = new CurrentAccount("CA-202", "Ram Charan Enterprise", 20000, 15000);
        
        try {
            sa.withdraw(2000);
            assert sa.getBalance() == 8000;
            ca.withdraw(25000);
            assert ca.getBalance() == -5000;
        } catch (Exception e) {
            assert false : "Unexpected exception: " + e.getMessage();
        }
        System.out.println("WEEK 4 TESTS PASSED (100%)");
    }
}