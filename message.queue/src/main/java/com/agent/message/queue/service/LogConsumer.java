//package com.agent.message.queue.service;
//
//import org.springframework.stereotype.Component;
//
//import java.util.concurrent.BlockingQueue;
//
//@Component
//public class LogConsumer {
//
//    private final BlockingQueue<String> queue;
//
//    public LogConsumer(BlockingQueue<String> queue) {
//        this.queue = queue;
//        startConsumer();
//    }
//
//    private void startConsumer() {
//        new Thread(() -> {
//            while (true) {
//                try {
//                    String logLine = queue.take();
//                    // 여기서 처리 (예: ElasticSearch 전송 등)
//                    System.out.println("Consumed: " + logLine);
//                } catch (InterruptedException e) {
//                    Thread.currentThread().interrupt();
//                    break;
//                }
//            }
//        }).start();
//    }
//}
