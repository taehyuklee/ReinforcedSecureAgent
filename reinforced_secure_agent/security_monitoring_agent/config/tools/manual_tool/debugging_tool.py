

def debug_check_messages():
    print("message 개수를 체크합니다.")
    from config.agent_config.agent_config import agent_graph, config
    new_message_list = agent_graph.get_state(config).values['messages']

    print(f"[DEBUG] message 수: {len(new_message_list)}")
