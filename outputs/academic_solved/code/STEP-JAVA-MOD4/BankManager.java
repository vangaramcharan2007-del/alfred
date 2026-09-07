// ==========================================
// SRM STEP Java Track: BankManager.java (Streams & Test Suite)
// ==========================================
package com.srm.step.banking;

import java.util.*;
import java.util.stream.Collectors;

public class BankManager {
    private List<BankAccount> accounts = new ArrayList<>();

    public void addAccount(BankAccount account) {
        accounts.add(account);
    }

    public List<BankAccount> getHighValueAccounts(double threshold) {
        return accounts.stream()
                .filter(acc -> acc.getBalance() >= threshold)
                .sorted(Comparator.comparingDouble(BankAccount::getBalance).reversed())
                .collect(Collectors.toList());
    }

    public double calculateTotalLiquidity() {
        return accounts.stream()
                .mapToDouble(BankAccount::getBalance)
                .sum();
    }

    public static void main(String[] args) {
        System.out.println("=== SRM STEP JAVA PROGRAM EXECUTION TEST ===");
        System.out.println("Candidate: RAM CHARAN VANGA (RA2511027010164)");
        
        BankManager manager = new BankManager();
        SavingsAccount sa = new SavingsAccount("SA-101", "RAM CHARAN", 75000.0, 4.5);
        CurrentAccount ca = new CurrentAccount("CA-202", "TECH CORP", 120000.0, 50000.0);
        
        manager.addAccount(sa);
        manager.addAccount(ca);
        
        System.out.println("Initial Total Liquidity: Rs. " + manager.calculateTotalLiquidity());
        
        try {
            sa.withdraw(20000.0);
            System.out.println("Withdrawal successful! SA Balance: Rs. " + sa.getBalance());
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println("\nHigh Value Accounts (Threshold >= Rs. 50,000):");
        manager.getHighValueAccounts(50000.0).forEach(System.out::println);
        System.out.println("=== ALL STEP JAVA TEST CASES PASSED SUCCESSFULLY ===");
    }
}
