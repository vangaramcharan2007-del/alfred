// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week2;

public class Week2PayrollTest {
    public static void main(String[] args) {
        System.out.println("Running Week 2 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        PayrollManager pm = new PayrollManager();
        pm.addEmployee(new SalariedEmployee("E101", "Ram Charan", "Big Data", 75000, 15000));
        pm.addEmployee(new HourlyEmployee("E102", "Alex Kumar", "Engineering", 350, 180));
        
        assert pm.getEmployeeCount() == 2 : "Workforce count mismatch";
        assert pm.calculateTotalPayroll() > 100000 : "Total payroll calculation failed";
        System.out.println("WEEK 2 TESTS PASSED (100%)");
    }
}