package com.agent.message.queue.service;

import com.agent.message.queue.config.etc.Message;
import com.agent.message.queue.config.memory.QueueMemory;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class MemoryService {

    private QueueMemory queueMemory;

    public void addMessage(Message message){
        queueMemory.getPriorityBlockingQueue().add(message);
    }

}
