package nexus.finance;

public class FinancialCalculator {

    public static class EmiResult {
        public final double monthlyEmi;
        public final double totalInterest;
        public final double totalAmount;

        public EmiResult(double monthlyEmi, double totalInterest, double totalAmount) {
            this.monthlyEmi = monthlyEmi;
            this.totalInterest = totalInterest;
            this.totalAmount = totalAmount;
        }
    }

    public static class CompoundInterestResult {
        public final double futureValue;
        public final double interestEarned;
        public final double growthMultiplier;

        public CompoundInterestResult(double futureValue, double interestEarned, double growthMultiplier) {
            this.futureValue = futureValue;
            this.interestEarned = interestEarned;
            this.growthMultiplier = growthMultiplier;
        }
    }

    public static class SipResult {
        public final double totalInvested;
        public final double estimatedReturns;
        public final double totalMaturityValue;

        public SipResult(double totalInvested, double estimatedReturns, double totalMaturityValue) {
            this.totalInvested = totalInvested;
            this.estimatedReturns = estimatedReturns;
            this.totalMaturityValue = totalMaturityValue;
        }
    }

    public static class DiscountTaxResult {
        public final double discountSavings;
        public final double discountedPrice;
        public final double taxAmount;
        public final double finalPayable;

        public DiscountTaxResult(double discountSavings, double discountedPrice, double taxAmount, double finalPayable) {
            this.discountSavings = discountSavings;
            this.discountedPrice = discountedPrice;
            this.taxAmount = taxAmount;
            this.finalPayable = finalPayable;
        }
    }

    /**
     * EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
     */
    public static EmiResult calculateEmi(double principal, double annualRatePercent, int tenureMonths) {
        if (principal <= 0 || tenureMonths <= 0) {
            return new EmiResult(0, 0, 0);
        }
        if (annualRatePercent <= 0) {
            double emi = principal / tenureMonths;
            return new EmiResult(emi, 0, principal);
        }
        double r = (annualRatePercent / 12.0) / 100.0;
        double pow = Math.pow(1.0 + r, tenureMonths);
        double emi = (principal * r * pow) / (pow - 1.0);
        double totalAmount = emi * tenureMonths;
        double totalInterest = totalAmount - principal;
        return new EmiResult(emi, totalInterest, totalAmount);
    }

    /**
     * A = P * (1 + r/n)^(nt)
     */
    public static CompoundInterestResult calculateCompoundInterest(double principal, double annualRatePercent, int timesCompoundedPerYear, double years) {
        if (principal <= 0 || years <= 0) {
            return new CompoundInterestResult(0, 0, 0);
        }
        double r = annualRatePercent / 100.0;
        int n = Math.max(1, timesCompoundedPerYear);
        double a = principal * Math.pow(1.0 + (r / n), n * years);
        double interest = a - principal;
        double multiplier = a / principal;
        return new CompoundInterestResult(a, interest, multiplier);
    }

    /**
     * SIP = P * [ (1 + i)^n - 1 ] / i * (1 + i)
     */
    public static SipResult calculateSip(double monthlyInvestment, double expectedAnnualReturnPercent, int months) {
        if (monthlyInvestment <= 0 || months <= 0) {
            return new SipResult(0, 0, 0);
        }
        double i = (expectedAnnualReturnPercent / 12.0) / 100.0;
        double totalInvested = monthlyInvestment * months;
        double maturity;
        if (i <= 0) {
            maturity = totalInvested;
        } else {
            maturity = monthlyInvestment * ((Math.pow(1.0 + i, months) - 1.0) / i) * (1.0 + i);
        }
        double returns = Math.max(0, maturity - totalInvested);
        return new SipResult(totalInvested, returns, maturity);
    }

    /**
     * Discount & GST calculation
     */
    public static DiscountTaxResult calculateDiscountAndTax(double price, double discountPercent, double gstPercent) {
        double discSavings = price * (Math.max(0, discountPercent) / 100.0);
        double discounted = Math.max(0, price - discSavings);
        double tax = discounted * (Math.max(0, gstPercent) / 100.0);
        double finalPayable = discounted + tax;
        return new DiscountTaxResult(discSavings, discounted, tax, finalPayable);
    }
}
