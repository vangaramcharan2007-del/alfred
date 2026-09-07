// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week6;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public class OrderProcessorPool {
    private final BlockingQueue<Order> queue = new LinkedBlockingQueue<>(100);
    private final ExecutorService executor = Executors.newFixedThreadPool(4);
    private final AtomicInteger processedCount = new AtomicInteger(0);
    private final AtomicLong totalRevenue = new AtomicLong(0);
    private volatile boolean running = true;

    public OrderProcessorPool() {
        for (int i = 0; i < 4; i++) {
            executor.submit(this::workerLoop);
        }
    }

    public boolean submitOrder(Order o) {
        return queue.offer(o);
    }

    private void workerLoop() {
        while (running || !queue.isEmpty()) {
            try {
                Order o = queue.poll(100, TimeUnit.MILLISECONDS);
                if (o != null) {
                    o.setProcessed(true);
                    processedCount.incrementAndGet();
                    totalRevenue.addAndGet((long) o.getAmount());
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    public int getProcessedCount() { return processedCount.get(); }
    public long getTotalRevenue() { return totalRevenue.get(); }

    public void shutdown() {
        running = false;
        executor.shutdown();
    }
}