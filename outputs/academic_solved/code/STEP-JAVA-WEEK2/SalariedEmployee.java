// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week2;

public class SalariedEmployee extends Employee {
    private double fixedAllowance;

    public SalariedEmployee(String empId, String name, String department, double baseSalary, double fixedAllowance) {
        super(empId, name, department, baseSalary);
        this.fixedAllowance = fixedAllowance;
    }

    @Override
    public double calculateMonthlyGross() {
        return baseSalary + fixedAllowance;
    }
}