// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week1;

import java.util.ArrayList;
import java.util.List;

public class MatrixCompute {
    public static int[][] multiply(int[][] a, int[][] b) {
        int r1 = a.length, c1 = a[0].length;
        int r2 = b.length, c2 = b[0].length;
        if (c1 != r2) throw new IllegalArgumentException("Matrix dimensions do not match for multiplication.");

        int[][] result = new int[r1][c2];
        for (int i = 0; i < r1; i++) {
            for (int j = 0; j < c2; j++) {
                for (int k = 0; k < c1; k++) {
                    result[i][j] += a[i][k] * b[k][j];
                }
            }
        }
        return result;
    }

    public static List<Integer> spiralOrder(int[][] matrix) {
        List<Integer> result = new ArrayList<>();
        if (matrix == null || matrix.length == 0) return result;
        int top = 0, bottom = matrix.length - 1;
        int left = 0, right = matrix[0].length - 1;

        while (top <= bottom && left <= right) {
            for (int j = left; j <= right; j++) result.add(matrix[top][j]);
            top++;
            for (int i = top; i <= bottom; i++) result.add(matrix[i][right]);
            right--;
            if (top <= bottom) {
                for (int j = right; j >= left; j--) result.add(matrix[bottom][j]);
                bottom--;
            }
            if (left <= right) {
                for (int i = bottom; i >= top; i--) result.add(matrix[i][left]);
                left++;
            }
        }
        return result;
    }
}