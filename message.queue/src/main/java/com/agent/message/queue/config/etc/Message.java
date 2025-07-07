package com.agent.message.queue.config.etc;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class Message {

    private String message;

    public Message(String message){
        this.message = message;
    }


}
