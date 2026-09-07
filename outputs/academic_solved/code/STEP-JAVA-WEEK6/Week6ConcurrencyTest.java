// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week6;

public class Week6ConcurrencyTest {
    public static void main(String[] args) throws Exception {
        System.out.println("Running Week 6 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        OrderProcessorPool pool = new OrderProcessorPool();
        for (int i = 0; i < 50; i++) {
            pool.submitOrder(new Order("ORD-" + i, "CUST-" + i, 100.0));
        }
        Thread.sleep(600);
        pool.shutdown();
        assert pool.getProcessedCount() == 50 : "Not all orders processed concurrently";
        assert pool.getTotalRevenue() == 5000 : "Total revenue calculation failed";
        System.out.println("WEEK 6 TESTS PASSED (100%)");
    }
}