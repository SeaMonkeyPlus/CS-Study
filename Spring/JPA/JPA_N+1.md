# JPA / N+1

## ORM (개념/패러다임)

- 자바의 객체와 DB의 테이블을 자동으로 서로 변환/매핑 해주는 기술
- 개발자는 `User`라는 **객체**만 다루고, SQL(`SELECT/INSERT`)은 프레임워크가 만들어줌.

## JPA (표준/인터페이스)

- ORM을 위해 자바에서 제공하는 API

### JPA 사용이유 / 장점

- **객체 중심으로 코드를 짜면**, **SQL은 JPA가 대신 생성**해줘서 개발이 빠르고 유지보수가 쉬워진다.
    - `sava(entity)`, `find()` 처럼 CRUD 대부분 SQL을 직접 안쓰게됨
    - 엔티티, 연관관계를 그대로 코드에 작성
    - 변경감지(더티체킹) → 필드만 바꿔도 커밋시 UPDATE 자동 생성 → 비즈니스 로직에 집중가능
    - 캐시/동일성 보장 → 같은 트랜잭션 내 1차 캐시로 중복 조회 줄어듬, 동일 객체(==) 보장
    - 구현체 교체가 유연함 (hibernate → ibatis)
- 비즈니스 로직에 집중하고 객체중심의 개발을 할 수 있게 된다.
- 메소드 호출만으로도 쿼리를 수행해서 생산성이 향상되고 유지보수 비용이 줄어든다.
- 특정 DB에 의존하지 않게된다.

### JPA 단점

- 직접 SQL을 호출하는것보다 느리다.
- 복잡한 쿼리는 메소드로 처리가 어렵다
- 러닝커브 있음
    - 영속성 컨텍스트, 지연로딩(LAZY), flush 타이밍 이해 필요.
- N+1 문제 발생 가능
    - **해결**: `fetch join`, `@EntityGraph`, `default_batch_fetch_size`, DTO 쿼리.

## Hibernate (프레임워크/ JPA의 구현체)

- **자바 ORM 프레임워크**.
- **JPA 표준 명세의 대표 구현체**이자, JPA 바깥의 **자체 API**(Session 등)도 제공
- 실제 DB 쿼리 요청은 Hibernate가

### Hibernate의 핵심 동작/기능

1. **영속성 컨텍스트 & 1차 캐시**
    - 같은 트랜잭션 내 동일 엔티티는 동일 객체(==) 보장, 중복 조회 감소.
    - 예시코드
        
        ```java
        @Transactional
        public void firstLevelCache(EntityManager em) {
            Member a = em.find(Member.class, 1L); // ← DB HIT (캐시에 적재)
            Member b = em.find(Member.class, 1L); // ← 1차 캐시 HIT (DB 쿼리 없음)
            assert a == b; // true : 동일 객체 보장
        }
        ```
        
2. **더티 체킹(변경 감지)**
    - 엔티티 필드만 바꿔도 **flush 시 UPDATE 자동 생성**.
    - 예시코드
        
        ```java
        @Transactional
        public void dirtyChecking(EntityManager em) {
            Member m = em.find(Member.class, 1L); // 영속 상태
            m.setName("changed");                 // 필드만 변경
        } // 트랜잭션 커밋 직전 flush → UPDATE 자동 생성
        
        ```
        
3. **지연 로딩(LAZY) / 프록시 → 이친구 때문에 N+1 문제 발생함**
    - 연관 엔티티는 접근 시점에 쿼리. 불필요한 로딩 줄여 성능 보호.
    - 예시코드
        
        ```java
        // 엔티티
        @Entity
        class Order {
          @Id @GeneratedValue Long id;
          @ManyToOne(fetch = FetchType.LAZY) // 프록시로 들고 있다가
          private Member member;             // 접근 시 쿼리
        }
        
        // N+1 발생 코드(목록 + 루프 내 연관 접근)
        @Transactional(readOnly = true)
        public void nPlusOne(OrderRepository repo) {
            List<Order> list = repo.findAll();     // select * from orders
            for (Order o : list) o.getMember().getName(); // 각 row마다 member 조회(N번)
        }
        
        // 개선1: fetch join로 단건/명확한 케이스 해결
        @Query("select o from Order o join fetch o.member where o.id=:id")
        Optional<Order> findWithMember(@Param("id") Long id);
        
        // 개선2(목록+페이징): ID 2단계 페이징 or batch fetch size 활용
        
        ```
        
    - 프록시란?
        - JPA가 연관 객체를 실제로 로딩하지 않고 ‘가짜 객체(대리인)’를 만들어 두는것
        - 필요할 때 진짜 DB에서 데이터를 가져오도록 하는 일종의 “지연로딩 장치”
        
        ```java
        Order order = orderRepository.findById(1L).get();
        Member member = order.getMember();  // 아직 DB에 접근 안함
        System.out.println(member.getName());  // 이 시점에 DB 조회 발생!
        ```
        
        - `Member member = order.getMember();`  이부분은 Member의 프록시 객체가 들어가있음
        - `System.out.println(member.getName());`  실제 쿼리가 실행됨
4. **매핑 다양성 (연관관계 / 상속 / 값 타입)**
    - 연관관계(단/양방향), 상속 매핑(SINGLE_TABLE/JOINED/TPCC), 값 타입(Embeddable).

## 영속성

- 데이터가 **프로그램이 끝나도** 살아있게(디스크/DB에) 보존되는 성질

## 영속성 컨텍스트

- JPA가 트랜잭션 동안 엔티티를 **보관·관리**하는 **작업 메모(1차 캐시)**.
- **효과**:
    - 같은 엔티티는 **동일 객체(==)** 보장
    - **더티 체킹**(변경 감지)으로 UPDATE 자동 생성
    - **쓰기 지연**으로 커밋/쿼리 실행 전까지 SQL 모아두기

<aside>
💡

- `find()` → **DB 조회** 후 **영속성 컨텍스트**에 저장(1차 캐시).
- 엔티티 값 변경 → **더티 체킹 후보**로 표시(아직 DB 미반영).
- `flush`(커밋/JPQL 직전) → 변경 사항을 **SQL로 보내기**.
- `commit` → 트랜잭션 **확정**(롤백되면 flush도 무효).
</aside>

## LAZY(지연로딩)

- **필요할 때까지 DB에서 안 가져오고**(프록시만 들고 있다가) **접근하는 순간 쿼리** 날리는 로딩 방식.

```java
@Entity
class Order {
  @ManyToOne(fetch = FetchType.LAZY)  // 지연 로딩
  private Member member;
}

Order o = orderRepo.findById(1L).get(); // 이때 member는 아직 안 가져옴(프록시)
o.getMember().getName();                // 이 순간 쿼리 실행 → member 로딩
```

- 불필요한 쿼리/데이터 로딩 방지
- N+1 문제 발생가능

## N+1 문제

- 부모 N건 조회 후, 각 행마다 자식 연관을 접근할 때 **추가 쿼리 N번** 더 나가는 현상.
- 왜생기느냐?
    - JPA/Hibernate의 **지연 로딩(LAZY) 프록시**를 `루프`에서 접근할 때 주로 발생.
- `@ManyToOne`, `@OneToMany` 연관을 가진 리스트 화면 + 루프 내 `getXXX()` 등에서 발생

### N+1 문제 발생 예

```java
@Transactional(readOnly = true)
public void nPlusOneDemo(OrderRepository repo) {
    var orders = repo.findAll();               // 1번: select * from orders
    for (var o : orders) o.getMember().getName(); // N번: 각 주문마다 member 조회
}
```

```java
1️⃣ select * from orders;     // 전체 주문 조회 (→ N개의 주문)
2️⃣ 각 주문마다 member 조회:
    select * from member where id = ?;   // N번 반복
```

- `Order.member`가 지연로딩(LAZY) 프록시이기 때문
- `order.getMember()`가 호출될 때마다 DB에 따로 쿼리가 날아감

### N+1 문제 해결방법 5가지

1. **Fetch Join** – “이번 쿼리에서 같이 가져와” (Spring Data JPA + JPQL 사용)
    
    ```java
    @Query("select o from Order o join fetch o.member where o.id=:id")
    Optional<Order> findWithMember(@Param("id") Long id);
    ```
    
    - 쿼리결과
    
    ```sql
    select o.*, m.*
    from orders o
    join member m on o.member_id = m.id;
    
    ```
    
    ✅ 왜 해결되나?
    처음 쿼리에서 `Order`와 `Member`를 한 번에 조인해서 가져오니까
    프록시로 인한 추가 쿼리가 발생하지 않음.
    
2. **EntityGraph** – 선언적으로 필요한 연관만 로딩 (Spring Data JPA + JPQL 사용)
    
    ```java
    @EntityGraph(attributePaths = {"member"})
    @Query("select o from Order o")
    List<Order> findAllWithMember();
    ```
    
    - `EntityGraph`는 “특정 연관 필드를 미리 패치해” 라는 **선언적 fetch join**
    
    ✅ 왜 해결되나?
    **지연로딩 프록**시가 생성되지 않으니, 나중에 접근해도 추가 쿼리가 없음.
    → 즉, Fetch Join의 **선언적 버전**이라 보면 됨.
    
3. **배치 페치** – LAZY 프록시들을 **IN 쿼리로 묶음** (설정파일 yml의 `default_batch_fetch_size`)
    
    ```java
    //application.yml
    // 코드 변경 없이도, 프록시 접근 시 Hibernate가 select ... where id in (...)로 묶어 가져옴
    spring:
      jpa:
        properties:
          hibernate.default_batch_fetch_size: 100
    ```
    
    ✅ 왜 해결되나?
    지연로딩은 그대로 두되, 여러 프록시를 한꺼번에 불러올 때
    **Hibernate**가 자동으로 “**`묶어서 IN 쿼리`**”로 날림:
    
    `select * from member where id in (1, 2, 3, ..., 100);`
    
    ```sql
    (기존)
    Order1 → Member(id=1)   → select ... where id=1
    Order2 → Member(id=2)   → select ... where id=2
    ...
    ⛔ N번
    
    (배치페치)
    Order(1~100) → Members(ids 1~100)
    ✅ select ... where id in (1,...,100)
    ```
    
4. **ID 2단계 페이징** – “ID로 자르고, 본문은 IN으로”
    
    ```java
    // 1) ID만 페이징
    @Query("select o.id from Order o where o.status=:s order by o.id desc")
    Page<Long> pageIds(@Param("s") Status s, Pageable pageable);
    
    // 2) 본문 로딩 (연관은 배치 페치/EntityGraph 활용)
    List<Order> findByIdIn(List<Long> ids);
    ```
    
    1️⃣ ID만 먼저 페이징
    
    ```sql
    select o.id
    from orders o
    where o.status = 'READY'
    order by o.id desc
    limit 20 offset 0;
    ```
    
    2️⃣ 그 ID들만 다시 조회 (+ fetch join or batch fetch)
    
    ```sql
    select o.*, m.*
    from orders o
    join member m on o.member_id = m.id
    where o.id in (1, 2, ..., 20);
    ```
    
    ✅ 왜 해결되나?
    페이징 효율을 유지하면서도 필요한 연관 데이터를 한 번에 불러옴.
    지연로딩 시 N+1이 아니라, “2쿼리로 모든 데이터”를 가져오게 됨.
    
    ```sql
    단계1: ID 리스트만
     [1,2,3,...,20]
    단계2: IN으로 조인
     select * from order join member where id in (1,...,20)
    ✅ 총 2쿼리
    ```
    
5. DTO 프로젝션 
    
    ```java
    @Query("""
     select new com.sample.api.OrderSummaryDto(o.id, o.createdAt, m.name)
     from Order o
     join o.member m
     where o.status = :status
    """)
    List<OrderSummaryDto> findSummaries(@Param("status") Status status);
    ```
    
    - 화면/API에 **딱 필요한 칼럼만** 가져오니 가장 가볍고 빠름.
    - 리포트, 목록 화면엔 거의 항상 DTO가 베스트.

## 🎯 정리 요약

| 방법 | 핵심 아이디어 | 쿼리 수 | 단점 |
| --- | --- | --- | --- |
| Fetch Join | 한 번의 조인으로 모두 로딩 | 1 | 페이징 불가, 중복 가능 |
| EntityGraph | 선언적 Fetch Join | 1 | 복잡한 조인엔 한계 |
| Batch Fetch | 프록시 접근 시 IN으로 묶음 | ⌈N/batch⌉ | 즉시로딩은 적용X |
| ID 2단계 | ID만 먼저, 본문은 IN으로 | 2 | 코드 복잡도 증가 |

---

### 질문

Fetch 타입을 Lazy가 아니라 즉시Eager로 하면 order_1 과 관련된 모두 즉시 불러오는것으로 알고 있는데 연관테이블 모두

→ 그럼 N+1 문제가 해결 되는게 아닌가??

→ 즉시 로딩을 지양 하는 이유는? 불필요 데이터까지 불러 와서?

→ eager 로 했을 때 ??

```mathematica
@Transactional(readOnly = true)
public void nPlusOneDemo(OrderRepository repo) {
    var orders = repo.findAll();               // 1번: select * from orders
    for (var o : orders) o.getMember().getName(); // N번: 각 주문마다 member 조회
}
```

### 답변

- **EAGER를 안 쓰는 이유:** 필요한 데이터만 써도 모든 연관 엔티티를 한꺼번에 불러 불필요한 쿼리와 중복 데이터를 낳기 때문.
- **EAGER가 N+1의 근본 해결이 아닌 이유:** 일부 연관만 줄일 뿐, 다른 관계나 컬렉션에선 여전히 N+1이 발생하고 쿼리 제어권이 사라지기 때문.
- **LAZY를 실무에서 많이 쓰는 이유:** 언제·무엇을 조회할지 명시적으로 통제할 수 있어 성능과 유지보수 모두 예측 가능하기 때문.