package com.agent.message.queue.service;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;

import org.apache.commons.io.input.Tailer;
import org.apache.commons.io.input.TailerListener;
import org.apache.commons.io.input.TailerListenerAdapter;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;
import java.util.zip.GZIPInputStream;

@Slf4j
@Service
public class LogWatcherService {

    private final BlockingQueue<String> queue;
    private final Map<Path, Tailer> tailers = new ConcurrentHashMap<>();
    private static final Logger logger = LoggerFactory.getLogger(LogWatcherService.class);


    @Value("${log.dir.path}")
    private String logDirPath;

    public LogWatcherService(BlockingQueue<String> queue) {
        this.queue = queue;
    }

    @PostConstruct
    public void init() {
        Path dir = Paths.get(logDirPath);
        try (Stream<Path> paths = Files.walk(dir)) {
            paths.filter(Files::isRegularFile).forEach(this::handleFile);
            System.out.println();
        } catch (IOException e) {
            logger.error("Failed to initialize log loading from directory: {}", logDirPath, e);
        }
    }

    private void handleFile(Path path) {
        if (path.toString().endsWith(".gz")) {
            loadGzFile(path); // gzip 파일은 처음에 전부 읽음
        } else if (path.toString().endsWith(".log")) {
            tailFile(path); // log 파일은 tail 처리
        }
    }

    private void loadGzFile(Path path) {
        try (GZIPInputStream gzip = new GZIPInputStream(new FileInputStream(path.toFile()));
             BufferedReader reader = new BufferedReader(new InputStreamReader(gzip))) {
            String line;
            while ((line = reader.readLine()) != null) {
                Boolean success = queue.offer(line);
            }
        } catch (IOException e) {
            logger.error("Failed to load and parse GZIP file: {}. Reason: {}", path, e.getMessage(), e);
        }
    }


    private void tailFile(Path path) {

        // Listener 객체를 만들어서 Tailer만들때 넣어주면, 해당 Tailer가 보고 있는 경로의 파일을 감시하게 된다.
        // 그리고 변경이 일어나는 Event가 발생할때마다 Call-back을 해준다.
        TailerListenerAdapter listener = new TailerListenerAdapter() {
            @Override
            public void handle(String line) {
                System.out.println("=====================");
                System.out.println(line);
                Boolean success = queue.offer(line);
            }
        };

        Tailer tailer = Tailer.builder()
                .setFile(path.toFile())
                .setTailFromEnd(true) // 기존 파일 처음부터가 아니라 마지막 줄부터 tail
                .setDelayDuration(Duration.ofMillis(1000))
                .setTailerListener(listener)
                .get();

        Thread tailerThread = new Thread(tailer);
        tailerThread.setDaemon(true); // 애플리케이션 종료시 자동 종료
        tailerThread.start();

        tailers.put(path, tailer);
    }
}
