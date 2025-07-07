package com.agent.message.queue.controller;

import com.agent.message.queue.config.etc.Message;
import com.agent.message.queue.config.memory.QueueMemory;
import com.agent.message.queue.service.MemoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;

@RestController
@RequiredArgsConstructor
public class MemoryController {

    private final QueueMemory queueMemory;
    private final MemoryService memoryService;
    private final BlockingQueue<String> queue;

    @GetMapping("/new-logs")
    public List<String> pollLogs(@RequestParam(defaultValue = "100") int max) {
        List<String> logs = new ArrayList<>();
        queue.drainTo(logs, max); // 최대 max개까지 꺼냄
        System.out.println(queue.size());
        return logs;
    }

    @GetMapping("/queue-size")
    public int queueSize() {
        return queue.size();
    }

}
