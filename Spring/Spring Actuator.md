# 로깅

# 운영을 고려한 백엔드 개발

## Spring Boot Actuator로 만드는 로그와 메트릭

---

## 1. 한 줄 정의

- Observability(관측 가능성) 란

> “서비스 내부 상태를 로그와 메트릭을 통해 외부에서 파악할 수 있는 능력”이다.
> 

백엔드 개발자는 **운영팀이 시스템을 이해할 수 있도록 정보(로그·메트릭)를 코드에서 만들어줘야 한다.**

---

## 2. 왜 백엔드가 로그·메트릭을 발생시켜야 하나?

운영 중 DevOps가 항상 묻는 질문

- 지금 서비스 정상인가?
- 언제부터 문제가 생겼나?
- 어디서 병목이 생겼나?

이 질문에 답하려면 **감이 아니라 데이터**가 필요하다.

### 역할 분리

- **메트릭**: 문제를 *빠르게 감지*
- **로그**: 문제의 *원인을 분석*

👉 메트릭이 없으면 장애를 늦게 발견하고

👉 로그가 없으면 원인을 찾지 못한다.

---

## 3. Spring Boot Actuator란?

**Spring Boot Actuator**는

애플리케이션의 상태와 메트릭을 **표준 엔드포인트로 노출**해주는 도구

예시:

- `/actuator/health` → 서비스 살아있나?
- `/actuator/metrics` → 요청 수, 응답 시간
- `/actuator/prometheus` → 모니터링 시스템 연동

👉 Actuator는 **운영을 위한 창구**

---

## 4. 메트릭은 어떻게 만들어지고 쓰이나?

### 흐름 요약

1. 애플리케이션 내부에서 메트릭 수집
2. Actuator가 메트릭을 엔드포인트로 노출
3. Prometheus 같은 시스템이 주기적으로 가져감
4. Grafana에서 시각화 + 알람

👉 백엔드는 “측정”하고

👉 DevOps는 “수집·시각화·알람” 설정

---

## 5. 백엔드가 직접 만들어야 하는 메트릭

자동 메트릭만으로는 부족하다.

**비즈니스 기준 메트릭**은 개발자가 정의해야 한다.

### 대표 예시

- **Counter (횟수)**
    - 로그인 실패 횟수
    - 결제 실패 건수
    - 특정 예외 발생 수

→ “5분간 실패 100건 이상이면 알람”

- **Timer (시간)**
    - API 응답 시간
    - 핵심 로직 처리 시간

→ 평균이 아니라 **p95, p99 지연** 확인 가능

👉 “느려졌다”를 숫자로 말할 수 있게 된다.

```java
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Component;

@Component
public class SignupMetrics {
    private final Counter signupFailCounter;

    public SignupMetrics(MeterRegistry registry) {
        this.signupFailCounter = Counter.builder("app.signup.fail.count")
            .description("회원가입 실패 횟수")
            .register(registry);
    }

    public void increaseFail() {
        signupFailCounter.increment(); // 실패 1회 증가
    }
}

```

---

## 6. 로그는 어떻게 봐야 하나?

- 로그는 “많이”가 아니라 **“의미 있게”**
- 장애 알람은 메트릭으로 받고
- 원인 분석은 로그로 들어간다

Actuator를 쓰면

- 운영 중에도 로그 레벨을 조절 가능
- 장애 순간에만 DEBUG 활성화 가능

---

## 7. 정리

> 운영을 고려한 백엔드 개발이란
> 
> 
> **기능을 만드는 것뿐 아니라, 상태를 설명할 수 있는 코드를 작성하는 것**이다.
> 

Spring Boot Actuator는

그 출발점이 되는 가장 현실적인 도구다.

## 질문

---

- 액츄에이터 사용방식예제??

제일 간단한 커스텀 메트릭 (Counter)

```java
@RestController
public class HelloController {

    private final Counter helloCounter;

    public HelloController(MeterRegistry registry) {
        this.helloCounter = Counter.builder("hello.request.count")
            .description("hello API 호출 횟수")
            .register(registry);
    }

    @GetMapping("/hello")
    public String hello() {
        helloCounter.increment(); // 호출될 때마다 +1
        return "hello";
    }
}
```

## 메트릭 확인 방법

### 1) Prometheus 포맷으로 확인

```
http://localhost:8080/actuator/prometheus
```

예상 출력 (일부):

```
# HELP hello_request_count hello API 호출 횟수
# TYPE hello_request_count counter
hello_request_count 5.0
```

---

### 2) Actuator metrics 엔드포인트로 확인

```
http://localhost:8080/actuator/metrics/hello.request.count
```

```json
{
  "name": "hello.request.count",
  "measurements": [
    {
      "statistic": "COUNT",
      "value": 5
    }
  ]
}
```

---