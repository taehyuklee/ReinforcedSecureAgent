package com.agent.message.queue.config.memory;

import com.agent.message.queue.config.etc.Message;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Queue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;

@Configuration
public class QueueMemory {

    @Bean
    public Queue<Message> getPriorityBlockingQueue(){
        return new PriorityBlockingQueue<Message>();
    }

    @Bean
    public BlockingQueue<String> logQueue() {
        return new LinkedBlockingQueue<>(50000);
    }


}
