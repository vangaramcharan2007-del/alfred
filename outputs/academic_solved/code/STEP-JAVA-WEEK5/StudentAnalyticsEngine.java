// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week5;

import java.util.*;
import java.util.stream.Collectors;

public class StudentAnalyticsEngine {
    private List<Student> students = new ArrayList<>();

    public void registerStudent(Student s) { students.add(s); }

    public Map<String, List<Student>> groupStudentsByDepartment() {
        return students.stream().collect(Collectors.groupingBy(Student::getDepartment));
    }

    public Map<String, Double> getAverageCgpaPerDepartment() {
        return students.stream().collect(Collectors.groupingBy(
            Student::getDepartment,
            Collectors.averagingDouble(Student::getCgpa)
        ));
    }

    public List<Student> getTopPerformersWithSkill(String skill, double minCgpa) {
        return students.stream()
            .filter(s -> s.getCgpa() >= minCgpa && s.getTechnicalSkills().contains(skill))
            .sorted(Comparator.comparingDouble(Student::getCgpa).reversed())
            .collect(Collectors.toList());
    }
}