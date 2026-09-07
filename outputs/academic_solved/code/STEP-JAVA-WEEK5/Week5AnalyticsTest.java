// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week5;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class Week5AnalyticsTest {
    public static void main(String[] args) {
        System.out.println("Running Week 5 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        StudentAnalyticsEngine engine = new StudentAnalyticsEngine();
        engine.registerStudent(new Student("RA2511027010164", "Ram Charan", "Big Data", 9.85, Arrays.asList("Java", "Spark", "SQL")));
        engine.registerStudent(new Student("RA2511027010165", "Vignesh", "AI-ML", 9.20, Arrays.asList("Python", "Java")));
        
        Map<String, Double> avgMap = engine.getAverageCgpaPerDepartment();
        assert avgMap.get("Big Data") == 9.85;
        
        List<Student> javaDevs = engine.getTopPerformersWithSkill("Java", 9.0);
        assert javaDevs.size() == 2;
        System.out.println("WEEK 5 TESTS PASSED (100%)");
    }
}