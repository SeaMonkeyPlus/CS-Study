# DB

## RDBMS, NoSQL

**RDBMS vs NoSQL 차이점은?**

- RDBMS: **정형 데이터**, 스키마 고정, 관계 기반(SQL).
- NoSQL: **비정형/대용량 데이터**, 스키마 유연, 수평 확장(JSON).
- 실무 예: **사용자 정보**는 RDB, **로그/세션**은 NoSQL.

## 트랜잭션 / ACID

- 트랜잭션의 정의
    - 여러 쿼리를 **하나의 논리 단위**로 묶어 전부 성공/전부 실패하게 하는 것. `BEGIN/COMMIT/ROLLBACK`.

**ACID 요약**

- **A(원자성)**: 전부 성공 또는 전부 실패
- **C(일관성)**: 제약조건(FK/UNIQUE/CHECK)이 항상 유효.
- **I(격리성)**: 동시에 실행돼도 **순차 실행과 동일한 결과를**(수준에 따라 보장 범위 다름)보장 하는것.
- **D(지속성)**: COMMIT 후엔 장애가 나도 데이터 보존(로그/리두)

## 제약조건

| 종류 | 역할 | 예시 |
| --- | --- | --- |
| NOT NULL | 필수 입력 | `name VARCHAR(50) NOT NULL` |
| UNIQUE | 중복 방지 | `email UNIQUE` |
| CHECK | 값 범위 제한 | `CHECK(age >= 0)` |
| DEFAULT | 기본값 설정 | `created_at DEFAULT NOW()`  |

## PK, FK, 식별/비식별 관계

- **PK(Primary Key)**
    - 각 행의 유일 식별자.
    - 짧고 불변한 정수형(BIGINT AUTO_INCREMENT) 선호.
    - InnoDB에선 **클러스터드 인덱스**로 저장.
- **FK(Foreign Key)**
    - 참조 무결성 보장 (부모 삭제 시 자식 처리).
    - 정책: `CASCADE`, `SET NULL`, `RESTRICT`
    - 실무: 외래키 사용 시 삭제 정책 명확히 정의, 데이터 정합성 보장.

**꼬리질문 예시**

- Q. FK 제약은 항상 걸어야 하나요?
    - A. “규모 큰 시스템에선 FK 대신 애플리케이션 레벨에서 제어하기도 합니다. 하지만 무결성을 보장할 구조는 반드시 필요합니다.”

| 구분 | 설명 | PK 구조 | 예시 |
| --- | --- | --- | --- |
| 식별 | 자식 PK가 부모 PK를 포함 | 복합 PK | `order_item(order_id, line_no)` |
| 비식별 | 자식 PK는 독립 (부모 FK 참조) | 단일 PK | `review(id, order_id FK)` |

## 카디널리티(1:1 / 1:N / N:M) + 선택성(필수/선택)

| 관계 | 설명 | 예시 |
| --- | --- | --- |
| 1:1 | 희소 정보 분리 / 세부 테이블 | `user - user_detail` |
| 1:N | 가장 일반적, FK로 연결 | `user - order` |
| N:M | 교차 테이블로 분리 | `product - tag → product_tag` |

**면접 포인트**

> “N:M 관계는 반드시 중간 테이블로 풀어야 합니다.
> 
> 
> 예를 들어 `product_tag(product_id, tag_id)`처럼 복합 PK와 인덱스 설정을 합니다.”
> 
> A(1) ─── N (조인 테이블) N ─── (1) B / 조인 테이블로 풀기
> 

# 정규화: 1NF → 2NF → 3NF

## 1정규화(1NF) — 원자성/반복열 제거

- **원칙**: 각 칼럼은 더 쪼갤 수 없는 **원자값 1개**만 가진다. 반복 그룹/배열 금지.
- **안티패턴**: `order(items='A, B, C')` / `phone1, phone2, phone3`
- **수정**: 반복을 **행**으로 내린다 → 별도 테이블로 분해.

```sql
-- BEFORE
-- orders(id, customer_id, items_csv)
-- AFTER
CREATE TABLE orders (id BIGINT PK, customer_id BIGINT NOT NULL, created_at DATETIME NOT NULL);
CREATE TABLE order_item (
  order_id BIGINT NOT NULL,
  line_no INT NOT NULL,
  product_id BIGINT NOT NULL,
  qty INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  PRIMARY KEY(order_id, line_no),
  FOREIGN KEY(order_id) REFERENCES orders(id)
);
```

- **이득**: 쿼리/인덱스가 쉬워지고 데이터 정합성이 올라감.

## 2정규화(2NF) — 부분함수 종속 제거(복합 PK일 때만)

- **원칙**: **복합 기본키**의 일부에만 의존하는 속성 제거.
- **안티패턴**: `order_item(order_id, product_id, qty, product_name, product_price)`
    
    → `product_name/price`는 `(order_id, product_id)` 중 `product_id`에만 의존.
    
- **수정**: 제품 속성은 **product** 테이블로.

```sql
CREATE TABLE product (
  id BIGINT PK,
  name VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL
);
-- order_item에선 제품 스냅샷 저장 필요하면 별도 칼럼로 '복사' (비정규화, 아래 참고)
```

- **포인트**: “복합키일 때만” 의미가 있다. 단일키면 2NF는 자동 충족.

## 3정규화(3NF) — 이행적 종속 제거

- **원칙**: 키가 아닌 속성이 **다른 키가 아닌 속성**에 의존하면 안 됨.
- **안티패턴**: `customer(id, zip, city, state)` → `city/state`는 `zip`에 의존(이행 종속).
- **수정**: `zipcode(zip PK, city, state)`로 분리하고 `customer.zip → zipcode.zip` FK.

```sql
CREATE TABLE zipcode (zip CHAR(5) PRIMARY KEY, city VARCHAR(60), state CHAR(2));
ALTER TABLE customer ADD CONSTRAINT fk_customer_zip FOREIGN KEY(zip) REFERENCES zipcode(zip);
```

- **면접 한 줄**: “1NF는 원자화, 2NF는 복합키 부분 의존 제거, 3NF는 비키→비키 의존 제거.”

> 실무 팁
> 
> - 기본은 3NF. **읽기 병목**(핫 조인)이 명확하면, **의도적 비정규화(스냅샷/캐시 칼럼)** 적용 + 정합성 유지 로직/트리거/배치로 보완.

## 인덱스

**B-Tree**(일반): 정렬된 키로 탐색/범위 효율.

**선행열(Leftmost Prefix Rule)**: 복합 인덱스 `(a,b,c)`는 `a`, `(a,b)`, `(a,b,c)` 조건엔 효율적이지만 `b=…`만으론 못 탄다.

**선택도(Selectivity)**: 값 다양성이 높을수록(카디널리티 큼) 인덱스 효율 ↑.

- 예) `gender`(M/F) 단독 인덱스는 도움 적음. `(country, user_id)` 등 조합으로 선택도↑.

### 인덱스 설계

- **조인/WHERE에 자주 쓰는 컬럼**에 우선.
- 복합 인덱스의 **첫 컬럼은 = 조건이 많은 고선택도** 컬럼.
- **정렬/범위**가 필요하면 그 순서까지 포함. (= 조건 → 범위/정렬 순)
- 너무 많은 인덱스는 **쓰기 성능/메모리**를 소모. 꼭 필요한 것만.

### 인덱스 안타는 경우

- 선행열 아닌경우
- 함수/연산 적용: `WHERE DATE(created_at)=...` → 범위로 바꾸기 `created_at >= ? AND < ?`
- 타입/Collation 불일치, 앞 와일드카드 `LIKE '%abc'`, OR 남발(엔진/버전에 따라)
- 통계 노후 → `ANALYZE TABLE`/자동 통계 갱신 켜기

> InnoDB 특성
> 
> - PK는 **클러스터드**. 보조 인덱스의 리프는 **PK를 포함** → PK가 길면 보조 인덱스도 비대.
>     
>     ⇒ **숫자 대리키 PK**를 권장하는 이유.
>     

## Join

- **INNER JOIN**: 교집합
- **LEFT/RIGHT JOIN**: 한쪽은 전부 + 다른 쪽은 매칭만
- **FULL OUTER**: MySQL은 직접 미지원(UNION으로 흉내)
- **CROSS JOIN**: 데카르트곱(조건 없으면 폭발)

**조인 알고리즘(엔진이 선택)**

- **Nested Loop**(MySQL 기본): 드라이빙 테이블의 각 행마다 상대 테이블 탐색(인덱스 중요)
- **Hash Join**(MySQL 8 일부 상황): 큰 집합에 유리
- **Merge Join**(정렬된 입력 필요, 엔진 의존)

**성능 요령(중요도 순)**

1. **드라이빙 테이블에서 행 수를 최대한 줄여라**(선택도 높은 WHERE + 인덱스)
2. **조인 키 양쪽에 인덱스**(특히 대용량 테이블의 FK)
3. **필요 칼럼만 SELECT**(I/O 절감, 커버링 유도)
4. 조인 조건은 **ON**에, 행 필터링은 **WHERE**에 명확히
5. 큰↔큰 조인이면 **중간 집계/임시 테이블** 고려

## 실행계획

```java
EXPLAIN FORMAT=JSON
SELECT ...
```

**type**: 접근 방식(좋음→나쁨)

- `system` > `const` > `eq_ref` > `ref` > `range` > `index` > **ALL(풀스캔)**

**key**: 실제 사용 인덱스

**rows**: **추정 스캔 행 수**(크면 위험 신호)

**Extra**:

- `Using index`(커버링),
- `Using where`(필터 적용),
- `Using temporary`(임시 테이블 사용),
- `Using filesort`(정렬 단계—인덱스로 커버 못함),
- `Using index condition`(ICP) 등

**실전 튜닝 순서**

1. 슬로우 쿼리 캡쳐(로그/성능 스키마)
2. `EXPLAIN`으로 **rows/type/key/Extra** 확인
3. WHERE/JOIN/ORDER BY에 맞춰 **복합 인덱스**(=조건→범위/정렬 순서)
4. 비SARG 조건 제거(함수, 변환)
5. 큰↔큰 조인은 **중간 집계/파티셔닝/매테리얼라이즈** 검토
6. 통계 갱신 & 실행 재확인

## DB 로그

### **Redo Log (재실행 로그)**

- **역할**: 커밋된 트랜잭션을 **디스크에 반영(복구)**하기 위함.
- **위치**: InnoDB의 `ib_logfile0`, `ib_logfile1` 등
- **내용**: “어떤 페이지, 어떤 레코드가 이렇게 변경됨” 이력.

### **Undo Log** (되돌리기 로그)

- **역할**: 트랜잭션 롤백 시 **이전 상태로 복구**.
- **내용**: “수정 전 데이터 값”.

### 일반 로그들

| 로그 종류 | 설명 | 사용 목적 |
| --- | --- | --- |
| **General Log** | 실행된 모든 SQL 기록 | 디버깅용 (주의: 부하 큼) |
| **Slow Query Log** | 일정 시간 이상 걸린 쿼리 | 쿼리 튜닝, 인덱스 최적화 |
| **Error Log** | 서버 오류, 시작/중단, 경고 | 운영 모니터링 |
| **Audit Log** (엔터프라이즈) | 사용자·쿼리·시간 등 상세 행위 | 보안·감사 추적 |

### 로그흐름

```java
→ (1) 데이터 변경 요청
→ (2) Undo 기록 생성 (되돌릴 값)
→ (3) Redo 기록 작성 (적용할 값)
→ (4) Binlog 기록 (SQL 수준 변경)
→ (5) Commit (Redo flush 후 완료)
```

질문

---

- “규모 큰 시스템에선 FK 대신 애플리케이션 레벨에서 제어하기도 합니다. 하지만 무결성을 보장할 구조는 반드시 필요합니다.” 의 조금더 구체적인 사례
    - 규모가 큰 시스템에서는 FK를 실제 DB에 설정하지 않는 경우도 많음
    이유는 단순히 “귀찮아서”가 아니라, 운영 중인 대규모 DB에서 FK 제약이 성능 병목이 되기 때문...
    
    ### 사례
    
    - 수천만 개의 주문(`orders`)이 있고, 회원(`users`)도 수백만 명 단위.
    - 이때 DB에 FK가 걸려 있으면,
        
        사용자를 삭제하거나 주문 데이터를 대량으로 마이그레이션할 때
        
        DB가 모든 참조 관계를 검증하느라 **락(lock)** 이 걸리고 처리 속도가 급격히 느려짐.
        
    - 그래서 FK 제약은 걸지 않고,
        
        대신 **애플리케이션 레벨에서 검증 로직**을 둠.
        
        예를 들어 주문을 생성할 때
        
        ```java
        if (!userRepository.existsById(userId)) {
            throw new IllegalArgumentException("존재하지 않는 사용자입니다.");
        }
        orderRepository.save(order);
        ```
        
        - 이런 식으로 DB가 아니라 비즈니스 로직에서 무결성 체크를 수행.
        - 코드 레벨에서 누락되거나 버그로 인해 관계가 깨질 수 있으므로,
            - 별도의 데이터 정합성 검증 배치(batch) 나 백엔드에서 soft delete 정책을 병행하는 식으로 보완
- CROSS JOIN
    - **크로스 조인**은 말 그대로 **모든 행을 서로 곱**하는 조인
    
    ```sql
    SELECT * 
    FROM users
    CROSS JOIN orders;
    ```
    
    - 크로스조인 결과
    
    | user_id | user_name | order_id | price |
    | --- | --- | --- | --- |
    | 1 | 홍길동 | 101 | 5000 |
    | 1 | 홍길동 | 102 | 12000 |
    | 2 | 김영희 | 101 | 5000 |
    | 2 | 김영희 | 102 | 12000 |
    | 3 | 박철수 | 101 | 5000 |
    | 3 | 박철수 | 102 | 12000 |
- 보통은 실수로 JOIN 조건(ON)을 빠뜨렸을 때 이런 결과가 나오고,
그걸 “의도치 않은 크로스 조인”이라고 함. 성능에 아주 치명적
- 하지만 분석용 데이터 조합을 만들 때
예: 모든 날짜와 모든 상품을 조합해서 판매 데이터 없는 경우도 채워넣을 때
의도적으로 CROSS JOIN을 쓰기도 함