// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week1;

import java.util.List;

public class Week1Test {
    public static void main(String[] args) {
        System.out.println("Running Week 1 Test Suite for RAM CHARAN VANGA (RA2511027010164)...");
        
        List<Integer> primes = PrimeOperations.sieveOfEratosthenes(30);
        assert primes.size() == 10 : "Expected 10 primes under 30";
        
        int[][] a = {{1, 2}, {{3, 4}}};
        int[][] b = {{2, 0}, {{1, 2}}};
        int[][] c = MatrixCompute.multiply(a, b);
        assert c[0][0] == 4 && c[0][1] == 4 : "Matrix multiplication mismatch";

        System.out.println("WEEK 1 TESTS PASSED (100%)");
    }
}