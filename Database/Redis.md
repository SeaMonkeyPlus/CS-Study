# Redis

## Redis란?

- Redis(Remote Dictionary Server)
- 메모리 기반(In-Memory)의 **`Key-Value`** 저장소
- 디스크가 아니라 RAM에 데이터를 저장하기 때문에 매우 빠름
- 데이터에 접근시 키로 접근

### Redis의 핵심 특징

- **메모리에 저장** (디스크 I/O가 거의 없음 → ms 단위 응답)
- 문자열, 리스트, 해시, 집합(Set), 정렬된 집합(Sorted Set) 등 다양한 자료형 지원
- **TTL**(Time To Live) 설정 가능 → 캐시 만료 기능
- **단일 스레드 기반** (명령 실행 순서 보장)
- Pub/Sub, Stream, Lua Script, Transaction 등 고급 기능 존재
    - Stream - Redis 5.0 이후 추가된 **`스트림(Stream)`** 은 “시간순으로 쌓이는 데이터 로그”
        - Kafka나 RabbitMQ보다 가볍고, Redis 안에서 바로 다룰 수 있음
        - 실시간 이벤트 로그, 채팅, 알림 큐, 비동기 처리용 파이프라인에 사용
        
        ```sql
        XADD mystream * user lee message "hello"
        XRANGE mystream - +
        XREAD COUNT 1 STREAMS mystream 0
        ```
        
        - `XADD`: 메시지 추가
        - `XRANGE`: 전체 읽기
        - `XREAD`: 마지막 이후 새 데이터만 읽기
        - 단, Redis는 메모리 기반이라 **`장기 로그 저장용으론 적합하지 않음.`**
    - Lua Script - 여러 명령을 한 번에, 원자적으로 실행
        - Redis는 **`단일 스레드`** 이기 때문에 여러 명령을 연속으로 보낼 때 중간에 다른 요청이 끼어들 수도 있음
        - 이걸 막고, 여러 명령을 하나의 트랜잭션처럼 처리하려면 Lua 스크립트를 사용
        
        ```sql
        EVAL "local v = redis.call('GET', KEYS[1]); if not v then redis.call('SET', KEYS[1], ARGV[1]); end" 1 mykey default
        ```
        
        - 👉 `mykey`가 없을 때만 기본값 세팅.
        - 여러 명령을 묶어도 서버 내부에서 한 번에 실행돼서 빠르고 안전하다.
        - 분산 락(lock) 구현 (SETNX + TTL)
        - 레이트리밋(요청 횟수 제한)
        - 복잡한 조건부 캐시 로직
    - Transaction — 여러 명령을 순서대로, 원자적으로 처리
        - Redis 트랜잭션은 SQL처럼 롤백 기능이 있는 건 아니고,
        “모두 실행하거나, 하나도 실행 안 하거나”
        
        ```sql
        MULTI         # 트랜잭션 시작
        SET key1 "a"
        SET key2 "b"
        EXEC          # 커밋
        ```
        
        - 실행 중 에러가 나도 일부 명령은 이미 반영될 수 있음..
        - 조건부 로직은 Lua 스크립트가 더 안전함.

## 주요 사용 케이스

| 케이스 | 설명 |
| --- | --- |
| **캐싱 (Cache)** | DB나 외부 API 조회 결과를 Redis에 저장해 재사용 → 응답 속도 향상 |
| **세션 저장소** | 로그인 세션/토큰을 Redis에 저장 → 서버 간 세션 공유 |
| **Rate Limiting** | API 호출 횟수 제한 (예: 1분에 10회) 관리 |
| **실시간 순위/점수판** | Sorted Set을 이용한 실시간 랭킹 |
| **Queue / Pub-Sub** | 간단한 메시지 큐 역할 |
| **분산 락** | 여러 서버 간의 자원 접근 제어 (setnx 기반 락) |

## 트레이드오프

| 장점 | 단점 |
| --- | --- |
| **`엄청 빠름`** (메모리 기반) | **`메모리 용량 한계`**가 있음 |
| 자료구조 다양 (List, Set, Hash 등) | 복잡한 쿼리/조인은 불가 |
| TTL로 캐시 만료 자동화 가능 | 캐시 관리 전략이 없으면 “stale data” 문제 |
| **`단일 스레드`** → race condition 없음 | CPU 활용도 낮음, **`병렬 처리 불가`** |
| Persistence 설정으로 장애 복구 가능 | 잘못 설정하면 데이터 유실 가능 |

## Redis 활용 예시

- 캐시

### Java

```java
// Java (Spring)
String key = "user:100";
String value = redisTemplate.opsForValue().get(key);
if (value == null) {
    value = userRepository.findById(100).toString();
    redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(10));
}
```

### Python

```python
# Python
r = redis.Redis(host='localhost', port=6379, db=0)
key = "user:100"
if not r.exists(key):
    r.setex(key, 600, json.dumps(get_user_from_db(100)))
print(json.loads(r.get(key)))
```

### JavaScript

```jsx
// Node.js
const redis = require('redis');
const client = redis.createClient();
await client.connect();
let data = await client.get('user:100');
if (!data) {
  data = await getUserFromDB(100);
  await client.setEx('user:100', 600, JSON.stringify(data));
}
console.log(JSON.parse(data));
```

## Redis 사용시 자주하는 실수

| 실수 | 설명 |
| --- | --- |
| **TTL 미설정** | 캐시 만료 설정 안 하면 오래된 데이터가 계속 남음 |
| **직렬화 포맷 혼용** | JSON, String, Binary 등 포맷이 섞이면 파싱 에러 발생 |
| **키 설계 부주의** | “user123” 대신 “user:123” 처럼 prefix로 구분 필요 |
| **Redis를 DB처럼 사용** | 영속 데이터까지 Redis에 넣으면 장애 시 유실 위험 |
| **단일 인스턴스만 사용** | 확장성, 장애 복구 대비 안 함 (→ Sentinel, Cluster 고려) |
| **Memory Leak** | 캐시 삭제 로직 누락으로 TTL 없는 키가 무한 증가 |

## 캐시 패턴 (Cache-Aside가 기본)

| 패턴 | 언제 | 특징 |
| --- | --- | --- |
| **Cache-Aside**(권장) | 대부분의 앱 | **읽기 시 미스** → DB 조회 → 캐시에 set(TTL). **쓰기 시 DB 변경 후 캐시 삭제**(invalidate). |
| **Write-Through** | 쓰기 빈번/일관성 중시 | 앱이 DB 대신 캐시에 먼저 쓰면, 백엔드가 DB에도 반영. 지연 증가·구현 복잡. |
| **Write-Behind** | 쓰기 폭주 완화 | 캐시에만 먼저 쓰고 DB 반영은 비동기. 장애 시 유실/순서 문제 주의. |
| **Read-Through** | 전용 라이브러리 있을 때 | 애플리케이션이 캐시만 읽어도 캐시가 DB에서 알아서 채움. |
- 쓰기 뒤엔 **invalidate**가 가장 안전(“수정”보다 “삭제”).
- **TTL + 랜덤 지터**(예: 300~360초)로 캐시 스톰 예방.
    - **`TTL이 같은 데이터가 몰려 있을 경우`** → 한번에 키가 만료됨 → **`모든 요청이 DB로 몰림`**
    - → 이 상황이 캐시 스톰
    - 그래서 TTL에 약간의 랜덤값(지터) 을 섞어준다.
    예를 들어: TTL: 300초 + (0~60초 랜덤) → 즉, 300~360초 사이
- 미스 폭주 구간에 **single-flight(요청 합치기)** 도입.
    - Single-flight (요청 합치기)
        - 10명이 동시에 같은 데이터를 요청 → 캐시 미스 → DB 10번 조회 → DB 펑!
        - 그래서 “**`한 명만 DB를 조회하고 나머지는 기다려라`**” 라는 식으로 묶음

## 자주 터지는 사고와 예방

- **TTL 없음** → 메모리 만땅 + Eviction 폭주 → **기본 TTL 정하고 예외만 예외**.
- **핫키 집중** → 특정 샤드 CPU/네트워크 핫스팟 → **샤드 증가 + 키 분산 + 로컬 캐시**.
- **대규모 만료 동시 발생** → 트래픽 급상승 → **TTL 지터 + 백필 스로틀링**.
- **Replica만 읽기 후 강한 일관성 착각** → 직후 읽기 누락 → **일관성 요구 구간은 Primary 읽기** 또는 **쓰기 후 강제 불러오기**.

## 사용 팁!

- 캐시는 “**`원본 데이터의 복제본`**”이라는 원칙을 지켜라.
    
    → 원본(DB)에 없으면 Redis에 있어도 의미 없음.
    
- TTL은 **`데이터 특성에 맞게`** 설정 (예: 사용자 세션 30분, 상품 캐시 1시간)
- 트래픽이 많을수록 **Cache Hit Ratio** 모니터링 중요
- 서버 다중화 시에는 **Redis Cluster** 또는 **ElastiCache** 사용

---

### 질문

redis에는 락이 없다면? 락을 위해서는 무조건 루아스크립트를 써야하나?

- 명시적인건지, 자동으로 되는지??

### 답변

Redis는 기본적으로 **락(lock) 기능이 내장돼 있지 않음**.

즉, 명시적으로 구현해야 하고, “자동”으로 되는 건 없음.

루아 스크립트나 Redis 트랜잭션(`MULTI/EXEC`)을 이용해서 **원자적(atomic)** 연산으로 락을 흉내낼 수 있음

# 1) 재고 차감 경쟁 → 오판매(oversell)

## ❌ 문제 상황 (락 없음)

두 요청이 동시에 재고 1개인 상품을 샀다고 해보자. 둘 다 `GET stock`으로 1을 읽고, 각각 `DECR stock`까지 치면 재고가 -1로 내려갈 수 있음.

```jsx
T1: GET stock -> 1
T2: GET stock -> 1
T1: if stock > 0 then DECR -> stock: 0
T2: if stock > 0 then DECR -> stock: -1   // 오판매 발생
```

## ✅ 해결 1A: Lua로 “검사+차감” 원자화

검사(`stock > 0`)와 차감(`DECRBY 1`)을 한 번에 실행.

```jsx
-- stock_decr.lua
-- KEYS[1] = "stock:{itemId}", ARGV[1] = "1" (수량)
local cur = tonumber(redis.call("GET", KEYS[1]) or "0")
local need = tonumber(ARGV[1])
if cur >= need then
  return redis.call("DECRBY", KEYS[1], need)  -- 성공 시 남은 재고 반환
else
  return -1  -- 재고 부족
end
```

## ✅ 해결 1B: WATCH/MULTI로 낙관적 락

watch란?

- Redis 트랜잭션(MULTI/EXEC)에서 낙관적 락을 걸때 사용하는 명령어
- “내가 본 값이 바뀌지 않았을 때만 트랜잭션을 실행해라”는 조건을 붙이는 것.

경합이 심하지 않을 때는 이 방식도 실용적(실패 시 재시도).

```jsx
while (true) {
  jedis.watch("stock:1001");
  String v = jedis.get("stock:1001");
  long cur = (v == null) ? 0 : Long.parseLong(v);
  if (cur <= 0) { jedis.unwatch(); /* 품절 */ break; }

  Transaction t = jedis.multi();
  t.decrBy("stock:1001", 1);
  if (t.exec() != null) { /* 성공 */ break; }
  // 누가 먼저 쳐서 실패 → 루프 재시도
}
```

# 2) 배치/잡 중복 실행 → 이중 과금/중복 처리

## ❌ 문제 상황 (락 없음)

두 워커가 같은 잡을 동시에 집어 처리 → 중복 과금/중복 메일 발송 같은 사고.

```jsx
W1: "report:2025-10" 작업 시작
W2: "report:2025-10" 작업도 시작  // 중복
```

## ✅ 해결 2A: “간단 락” (SET NX PX) + 안전 해제

- 시작할 때 락을 건다.
- 락 값은 **토큰**(UUID)로 저장한다.
- 작업이 끝나면 **토큰 일치 확인 + 삭제**를 Lua로 원자 처리한다.

```jsx
String lockKey = "lock:report:2025-10";
String token = UUID.randomUUID().toString();

// 1) 락 획득 (만료 필수! 예: 30초)
String ok = jedis.set(lockKey, token, SetParams.setParams().nx().px(30_000));
if (!"OK".equals(ok)) {
  // 다른 워커가 보유 중 → 스킵
  return;
}
try {
  // ... 작업 수행 ...
} finally {
  // 2) 내 토큰일 때만 해제 (원자적)
  String unlockScript =
      "if redis.call('GET', KEYS[1]) == ARGV[1] then " +
      "return redis.call('DEL', KEYS[1]) else return 0 end";
  jedis.eval(unlockScript, 1, lockKey, token);
}
```

<aside>
💡

참고: 이건 “단일 Redis 인스턴스 기준의 간단 락” 패턴. 다중 노드 환경에서 **강한 분산 잠금 보장**이 정말 필요하면, 아키텍처/실패 가정에 맞춰 별도 설계를 검토(예: 작업 파티셔닝, 큐 기반 단일 소비, DB 잠금, 혹은 충분히 검토된 분산 락 구현).

</aside>

## ✅ 해결 2B: 큐 기반 “단일 소비”로 중복 자체 방지

락 대신 작업을 **스트림/큐**에 넣고 *한 소비자만* 처리하게 설계

```jsx
# 작업 등록
XADD jobs:* MAXLEN ~10000 * type report period 2025-10

# 소비자는 소비자그룹으로 읽음 → 한 메시지는 한 소비자에게만 배정됨
XGROUP CREATE jobs:report g1 $ MKSTREAM   # 최초 1회
XREADGROUP GROUP g1 c1 COUNT 1 BLOCK 1000 STREAMS jobs:report >
```

## 한 줄 압축

경쟁 상태가 생기는 지점(검사→변경 사이)을 **Lua 원자화**나 **WATCH/MULTI 재시도**, **SET NX PX + 토큰 해제**, 또는 **큐/스트림으로 단일 소비 설계**로 막으면 된다.