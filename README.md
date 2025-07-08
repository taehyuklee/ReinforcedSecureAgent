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
  <img src="https://github.com/user-attachments/assets/3b88619e-50a0-4bff-99a4-d1733d2ea89e" alt="Image" width="600px" />
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

#### 1. Qdrant Vector Database 설치 방법

&nbsp;  Docker Desktop 환경에서 다음 명령어를 통해 Qdrant를 설치할 수 있습니다 (Linux상에서는 Docker 설치후 바로 실행 가능):

```shell
docker pull qdrant/qdrant
docker volume create qdrant_data
docker run -d --name qdrant -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

&nbsp; 컨테이너는 경량화된 프로세스로 동작하며, 데이터를 저장할 별도의 스토리지(볼륨)를 마운트해야 합니다. 또한, Docker 내부의 가상 네트워크 및 MAC 주소와 호스트 OS의 포트를 연결하여 실행하는 구조입니다. 위 명령어는 이 과정을 모두 반영한 실행 명령입니다. 저는 Qdrant UI 설치 및 사용은 다음 사이트를 참고했습니다. <a href="https://github.com/qdrant/qdrant-web-ui" target="_blank" rel="noopener noreferrer">Qdrant GitHub UI</a>

<br>

#### 2. Message Queue 사용 방법

&nbsp;

