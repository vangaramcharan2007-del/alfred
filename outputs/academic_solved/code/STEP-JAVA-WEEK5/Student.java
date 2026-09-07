// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week5;

import java.util.List;

public class Student {
    private String regNo;
    private String name;
    private String department;
    private double cgpa;
    private List<String> technicalSkills;

    public Student(String regNo, String name, String department, double cgpa, List<String> technicalSkills) {
        this.regNo = regNo;
        this.name = name;
        this.department = department;
        this.cgpa = cgpa;
        this.technicalSkills = technicalSkills;
    }

    public String getRegNo() { return regNo; }
    public String getName() { return name; }
    public String getDepartment() { return department; }
    public double getCgpa() { return cgpa; }
    public List<String> getTechnicalSkills() { return technicalSkills; }
}