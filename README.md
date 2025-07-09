# Reinforce Secure Agent

### 프로젝트 개요 (Project Overview)

&nbsp;최근 다양한 사이버 보안 이슈가 연이어 발생하면서, 기존의 웹 보안 체계에 대한 근본적인 재검토 필요성이 커지고 있습니다. 특히 Web Application Firewall(WAF)과 같은 시그니처 기반 보안 시스템은 공백 삽입, Base64/URL 인코딩, 제로데이(0-day) 공격 등으로 쉽게 우회될 수 있으며, 새로운 유형의 공격에 대해서는 탐지와 실시간 대응 모두에 한계가 있습니다.

&nbsp;본 프로젝트는 이러한 문제를 해결하기 위해, LLM 기반의 적응형 보안 게이트웨이 시스템을 설계·구현하였습니다. 기존의 정적 룰 중심 탐지 방식에서 벗어나, LLM의 추론 능력과 외부 도구 활용을 결합한 ReAct(Reasoning + Acting) 기반 판단 구조를 통해 복합적인 공격 패턴에 대한 실시간 대응을 가능하게 합니다.

&nbsp;시스템은 웹 전단에 배치된 Secure Gateway Agent가 1차 필터링과 요청 분석을 수행하고, 내부의 Monitoring Agent가 실시간 행위 기반 탐지를 담당하는 구조로 구성됩니다. 탐지된 위협은 LLM에 Few-shot 형태로 피드백되어, 유사 공격에 대한 감지 성능을 지속적으로 향상시킬 수 있도록 설계되어 있습니다.

&nbsp;또한, 본 시스템은 단순 룰 기반 보안 체계를 넘어서 Actor–Critic 구조 기반의 적응형 보안 아키텍처를 채택하였으며, 과거 강화학습 기반 유체 제어 연구에서의 구조적 설계를 참조하여 실시간 학습 및 강화가 가능하도록 구현하였습니다.

&nbsp;전체 시스템은 Reverse Proxy – Secure Gateway – LLM Agent – Monitoring Agent 간의 트래픽 흐름 속에서 동작하며, 실시간 판단과 사후 대응의 연계를 통해 실제 서비스 환경에서도 효과적인 보안 방어 기능을 제공할 수 있도록 설계되었습니다.

<br>

### 목표 및 기대효과
-  &nbsp;기존 보안 체계가 탐지하기 어려운 복합 인코딩, Shell Injection, 시스템 우회형 공격에 대한 정밀 탐지

- ReAct 기반 문맥 분석 구조를 통한 공격 의도 파악

- Actor–Critic 구조의 Feedback Loop을 통해 지속적 보안 강화

- 실사용 가능한 환경에서의 PoC 구현 및 검증

- 향후 상용 API 형태의 보안 게이트웨이 플랫폼으로 확장 가능성


<br>

### Architecture & Data Flow Simulation 

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/bc7c0988-d230-4df6-8f28-0ae0570965df" alt="Image" width="600px" />
  <p style="text-align: center;"><em>Figure 1. Secure Gateway와 Secure Log Monitoring 간의 데이터 흐름 관계도</em></p>
</div>

<br>

1. <b>Encrypted Request 수신</b> <br>
&nbsp; - 클라이언트로부터 TLS 기반 암호화된 요청 수신, 민감 정보 노출 위험은 낮음.

2. <b>Filtered Request 처리</b> <br>
&nbsp; - Secure Gateway가 위험 여부 판단 후 안전한 요청만 Nginx로 전달, 로그는 실시간 수집됨.

3. <b>Polling 메커니즘</b> <br>
&nbsp; - Monitoring Agent가 Queue에서 실시간 로그 데이터를 수집(polling), 기본 1000건 단위 처리.

4. <b>Blacklist 등록</b> <br>
&nbsp; - 분석 결과 위험 IP는 자동으로 Secure Gateway의 Blacklist에 등록되어 차단됨.

5. <b>Few-shot 기반 피드백</b> <br>
&nbsp; - 사후 악성 판별 요청은 Few-shot 예시로 Vector DB에 저장, 향후 유사 공격 탐지에 활용됨.

<br>

해당 레포지토리에는 총 3개의 패키지가 포함되어 있습니다:

``` text
📦 Repository Structure

├── message.queue
│   └── 로그 전달(Message Queue)용 모듈 (Spring Boot Message Queue)
│ 
└── reinforced_secure_agent
    ├── security_gateway_agent      → Secure Gateway Agent 기능
    └── security_monitoring_agent   → Secure Monitoring Agent 기능
```
<br>

## 환경 구성 및 Vector Database 설치 안내

&nbsp; 클라우드 환경이 제공되지 않아, 본 프로젝트는 로컬 환경을 기준으로 시스템을 구성하였습니다. Nginx 로그는 별도로 개인 서버에서 수집하였으며, 아래 표는 Windows PC 기준 설치 정보를 정리한 것입니다. Linux 기반 설치가 필요하시면 별도로 안내해드릴 수 있습니다.

<br>

### 시스템 구성 요소

<br>

<div align="center">

| 구성 요소               | 설명                                                   | 포트  |
|------------------------|--------------------------------------------------------|-------|
| **Vector Database**     | Qdrant 컨테이너 기반 설치, UI 별도 제공 (ui-git사이트)   | 6333  |
| **Message Queue**       | Spring Boot 기반 경량 MQ 모듈 (직접 제작)               | 9000  |
| **Secure Gateway Agent** | FastAPI 기반, 악성 요청 차단 담당                       | 8000  |
| **Secure Monitoring Agent** | FastAPI 기반, 로그 요약 및 평가 담당                   | 8001  |

</div>

<br>

#### - 시스템 실행 순서 -
```1. Vector Database (Qdrant) 실행 → 2. Message Queue 서비스 실행 → 3. Secure Gateway Agent 실행 → 4. Secure Monitoring Agent 실행```

<br>


### <b>1. Qdrant Vector Database 설치 방법</b>

&nbsp;  Docker Desktop 환경에서 다음 명령어를 통해 Qdrant를 설치할 수 있습니다 (Linux상에서는 Docker 설치후 바로 실행 가능):

```shell
docker pull qdrant/qdrant
docker volume create qdrant_data
docker run -d --name qdrant -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

&nbsp; 컨테이너는 경량화된 프로세스로 동작하며, 데이터를 저장할 별도의 스토리지(볼륨)를 마운트해야 합니다. 또한, Docker 내부의 가상 네트워크 및 MAC 주소와 호스트 OS의 포트를 연결하여 실행하는 구조입니다. 위 명령어는 이 과정을 모두 반영한 실행 명령입니다. 저는 Qdrant UI 설치 및 사용은 다음 사이트를 참고했습니다. <a href="https://github.com/qdrant/qdrant-web-ui" target="_blank" rel="noopener noreferrer">Qdrant GitHub UI</a>

<br>

### 2. Message Queue 사용 방법

&nbsp; 일반적으로 프로덕션 환경에서는 Logstash, FileBeat, Kafka 등 검증된 로그 파이프라인 도구를 활용하여 로그 수집 및 전송을 수행합니다. 하지만 이번 프로젝트에서는 Spring Boot 기반으로 직접 개발한 경량 Message Queue를 사용하였습니다. 해당 Message Queue는 Yaml 설정 파일에서 특정 디렉터리를 지정하면, 해당 경로 내의 .log 및 .gz 파일을 자동으로 읽어 큐에 적재합니다. ```.gz``` 파일은 초기 한 번 전체를 읽고, ```.log``` 파일은 tail 방식으로 실시간으로 신규 로그를 감시하며 큐에 전달합니다.

아래는 application.yaml 설정 정보입니다.

```yaml
server:
  port: 9000

spring:
  application:
    name: message.queue

log:
  dir:
    path: "your logs directory path"
```
```log.dir.path```에 로그 파일이 위치한 디렉터리 경로를 지정하면 됩니다. 이후 Message Queue가 해당 경로를 감시하며 로그 데이터를 수집하여 소비자(Consumer)에게 전달합니다.

<br>

해당 Message Queue에서 제공하는 ```API```는 다음 두 가지입니다:

1. ```GET /new-logs``` <br>
  최대 max개(기본 100)의 로그 메시지를 한 번에 가져옵니다. (예: /new-logs?max=50)

2. ```GET /queue-size``` <br>
  현재 큐에 저장된 로그 메시지 수를 조회합니다.

이 API들을 통해 소비자는 실시간으로 적재된 로그를 효율적으로 폴링(polling)하며 처리할 수 있으며, 현재 처리 가능한 메시지 수를 확인하여 적절한 폴링 주기를 조절할 수 있습니다.

<br>

### 3. Secure Gateway Agent 사용 방법

&nbsp; 1. Python 버전: 3.11.9 

&nbsp; 2. 필수 조건: Vector DB가 사전에 실행되어 있어야 함

<br>

```main.py``` 내부에 uvicorn 실행 코드가 포함되어 있으므로, 아래와 같이 실행 가능합니다. 

``` bash
python main.py
```
PATH 환경변수를 설정한 상태라면, 별도의 uvicorn 명령 없이도 위와 같이 바로 실행됩니다.

<br>

🔁 <b>API Gateway 기능</b> <br>

&nbsp;  본 Gateway는 Black List / White List 관리 기능을 포함하며, POST 요청을 통해 설정하고, GET 요청을 통해 확인할 수 있습니다. 라우팅 기능 또한 포함되어 있으나, 현재는 테스트 목적으로 비워두었습니다. 필요 시, 수동으로 원하는 주소를 다음 함수의 인자로 지정해 사용할 수 있습니다.

``` pytohn
# main.py내부
routing_url(request, "http://routing_ip/path", request_body)
```
&nbsp; 실제 API Gateway처럼 도메인 기반 라우팅을 처리하려면 별도의 router 구성 또는 도메인 관리 모듈이 필요하지만, 본 프로젝트의 핵심 목적은 아니므로 해당 기능은 구현되어 있지 않습니다.

<br>

1. <b>Black List IP 추가</b> : 주로 Monitoring Agent가 자동으로 위협 판단 시 호출하는 API입니다.
``` http
POST http://localhost:8000/gateway/blacklist
Content-Type: application/json

{
  "ipList": [
    "https://www.good_url/shot",
    "https://www.great_url/hot",
    "https://www.taylee.link/analysis/t-test"
  ]
}
``` 

2. <b>현재 Black List 조회</b> : 운영자나 사람이 직접 확인하는 용도로 사용됩니다.
``` http
GET http://localhost:8000/gateway/blacklist
```

<br>

### 4. Secure Monitoring Agent 사용 방법

&nbsp; 1. Python 버전: 3.11.9 

&nbsp; 2. 필수 조건: 
- Vector DB가 사전에 실행되어 있어야 합니다.
- Gateway가 실행 중이어야 합니다. (실행되지 않더라도 Monitoring 자체는 기동 가능하지만, Blacklist 추가 등의 기능은 제한됩니다.)

<br>

```main.py``` 내부에는 무한 루프 기반의 모니터링 시스템이 포함되어 있습니다.

안전하고 안정적인 실행을 위해 아래 두 가지 방식 중 선택적으로 실행하실 수 있습니다

```bash
# 일반적인 Python 실행 방식
python main.py

# Uvicorn ASGI 서버 실행 권장 방식
uvicorn main:app --port 8001
```

<br>

📂 <b>Summary 파일 및 시각화</b> <br>

&nbsp; ```summary_file``` 디렉토리 내에 ```monitor.html``` 파일이 포함되어 있습니다. 이 HTML 파일은 모니터링 에이전트가 실행되며 생성한 ```summary_log.txt```를 기반으로 시각화된 결과를 보여줍니다.
요약 및 분석된 로그 데이터는 자동으로 ```summary_log.txt```에 저장됩니다.

<br>

📡 <b>Monitoring System 개요</b> <br>

&nbsp; 본 시스템은 실시간 보안 이벤트를 모니터링하기 위해 Stream 방식으로 설계되었습니다.
```로그 수집 → 분석 → 요약 → 시각화```의 파이프라인을 통해 보안 위협 흐름을 직관적으로 확인할 수 있습니다.


<br><br>

## Result (결과)
---

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/b11f0aeb-0c86-432e-a411-30a0573d411b" alt="Image" width="1200px" />
  <p style="text-align: center;"><em>Figure 2. Monitoring System Console 동작 화면</em></p>
</div>

<br>
&nbsp; Figure 2는 Monitoring System의 실시간 콘솔 동작 화면으로, Monitoring Agent가 웹 요청을 분석하고 요약하는 과정을 직관적으로 보여줍니다.

&nbsp; 위의 GIF는 실제 Monitoring Agent가 콘솔 창에서 실행되는 모습을 보여줍니다. 해당 화면에서는 <b>메시지 메모리 관리</b> 현황도 함께 모니터링되며, ```SystemMessage```, ```HumanMessage```, ```ToolMessage```, ```AIMessage``` 등의 메시지 유형별로 상태를 확인할 수 있습니다. Monitoring Agent는 ```pre_model_hook``` 노드에서 메시지를 토큰 기준으로 트리밍하여 처리합니다.

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/9f14b22d-3748-4746-ba28-d604eeea99de" alt="Few-shot Storage Visualization" width="1200px" />
  <p style="text-align: center;"><em>Figure 3. Few-shot 예제 생성 및 저장 구조 시각화</em></p>
</div>

<br>

&nbsp; Figure 3에서는 Monitoring Agent가 Few-shot 예제를 지정된 형식에 맞게 잘 추가하고 있는지를 시각적으로 확인할 수 있도록 구성하였습니다.
또한, 각 예제가 요청-응답-사유 구조를 정확히 따르며 높은 생성 정확도를 보이는지도 함께 나타냅니다.

&nbsp; 모든 예시가 완벽하게 저장되지는 않으며, 일부는 chunk_size에 따라 잘릴 수 있습니다. 현재 설정된 chunk_size=1000은 가장 합리적인 수준으로 평가되며, chunk_overlap을 적용하지 않은 이유는 예제의 문맥을 Few-shot 단위로 온전히 저장하기 위함입니다. 이때 사용된 분할 도구는 ```RecursiveCharacterTextSplitter```입니다.


<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/2a2724e9-6313-4c90-91c8-4d00b8d16527" alt="Summary_log" width="1200px" />
  <p style="text-align: center;"><em>Figure 4. summary_log.txt를 UI에 표기하는 컨셉</em></p>
</div>

<br>

&nbsp; Figure 4에서는 summary_log.txt의 일부 내용을 발췌하여, 해당 요약 정보가 monitor.html UI에 정확히 시각화되고 있는지를 보여줍니다.
Monitoring Agent가 생성한 로그 요약이 실제 인터페이스에서 어떻게 반영되는지를 컨셉을 확인 할 수 있습니다.

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/e33f3924-fc17-4a93-b6d1-1ff98c2d2ed5" alt="Blacklist" width="1200px" />
  <img src="https://github.com/user-attachments/assets/5e8a4d55-58ea-48cf-afed-43a73b22166a" alt="img" width="1200px">
  <p style="text-align: center;"><em>igure 5. BlackList 추가 기능 동작 예시</em></p>
</div>

<br>

&nbsp; Figure 5는 BlackList 추가 기능이 정상적으로 동작하는지를 보여주는 예시입니다.
API를 통해 특정 URL 또는 IP가 보안 위협으로 판단되어 차단 목록에 성공적으로 반영되는 과정을 확인할 수 있습니다.
