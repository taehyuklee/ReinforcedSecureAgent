# import platform
#
# print(platform.system())  # 예: 'Linux', 'Windows'
# print(platform.release())  # 커널 릴리즈 정보
# print(platform.version())  # 상세 커널 버전
# print(platform.uname())  # 전체 OS 정보 (namedtuple)

# /proc/version
# uptime 정보
# with open("/proc/uptime", "r") as f:
#     uptime_seconds = float(f.readline().split()[0])
#     print(f"Uptime: {uptime_seconds / 3600:.2f} hours")


# import psutil
#
# print("CPU 사용률:", psutil.cpu_percent(interval=1))
# print("메모리 상태:", psutil.virtual_memory())
# print("부팅 시간:", psutil.boot_time())


def check_deleted(agent_graph, config, sentence):
    print(sentence)
    messages = agent_graph.get_state(config).values["messages"]
    for message in messages:
        message.pretty_print()
