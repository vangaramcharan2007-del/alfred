// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week2;

public abstract class Employee {
    protected String empId;
    protected String name;
    protected String department;
    protected double baseSalary;

    public Employee(String empId, String name, String department, double baseSalary) {
        this.empId = empId;
        this.name = name;
        this.department = department;
        this.baseSalary = baseSalary;
    }

    public abstract double calculateMonthlyGross();

    public double calculateNetSalary() {
        double gross = calculateMonthlyGross();
        double tax = gross > 50000 ? gross * 0.15 : gross * 0.05;
        double pf = gross * 0.12;
        return gross - tax - pf;
    }

    public String getEmpId() { return empId; }
    public String getName() { return name; }
    public String getDepartment() { return department; }
}