# Swagger vs Spring REST Docs

## 요약

- **Swagger(OpenAPI)**
    
    👉 “코드 기반 자동 문서화 + UI로 테스트까지 되는, 개발-친화적 도구”
    
- **Spring REST Docs**
    
    👉 “테스트 기반으로 실제 응답을 스니펫으로 뽑아내는, 정확도 최상위 문서화 도구”
    

---

# 1. Swagger (OpenAPI)

## 1-1. 개념 / 컨셉

- **코드 애노테이션 기반으로 자동으로 API 문서 생성**
- **브라우저에서 API 테스트 가능한 UI 제공** (`/swagger-ui.html`)
- 개발 시 빠르게 문서 확인/테스트에 유리

---

## 1-2. 장점

- **자동화 끝판왕**: 컨트롤러에 어노테이션 달면 문서 바로 생성
- **Swagger UI 테스트 지원**: 클라이언트 개발자 만족도 높음
- API 변경사항을 바로 UI에서 확인 가능
- 학습 난이도 낮음 → 신입이 쓰기 매우 쉬움

---

## 1-3. 단점

- **문서 정확도가 ‘개발자 의도에 따라 달라짐’ (실제 응답 기반 X)**
    
    → 실제 동작과 문서가 맞지 않는 상황 자주 발생
    
- 어노테이션이 많아져서 **컨트롤러 코드가 지저분해짐**
- API가 많아지면 문서 유지보수 부담 증가
- 보안적으로 API 전체 노출 → 실제 서비스에서는 많이 감춤

---

## 1-4. Swagger 사용 예제

### build.gradle

```
implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0'
```

### 예제 Controller

```java
@RestController
@RequestMapping("/users")
@Tag(name="User API", description="유저 정보 조회/생성 API")
public class UserController {

    @Operation(summary = "유저 조회 API")
    @GetMapping("/{id}")
    public UserResponse getUser(
            @Parameter(description="유저 ID") @PathVariable Long id) {

        return new UserResponse(id, "Jinho");
    }
}
```

---

## 1-5. Swagger 주의할 점 (실무 기준)

- **실 서비스 배포 시 Swagger UI는 보통 닫거나 인증 걸어둬야 함**
    
    → 공격자가 API 구조 다 볼 수 있음
    
- DTO 변경 시 문서 자동 업데이트 되므로 **신규/변경된 필드 반드시 확인**
- “API 문서의 진실성(정확도)”는 안 보장됨
    
    → 실제 응답과 문서 차이가 발생하기 쉬움
    

---

---

# 2. Spring REST Docs

## 2-1. 개념 / 컨셉

- **테스트 코드로 실제 API 요청·응답을 검사한 뒤, 그 결과로 문서 생성**
- 즉, **“실제 API 동작 기반”**
- 테스트 실패 시 문서가 생성되지 않음 → 문서 정확도 최고

---

## 2-2. 장점

- **문서 = 실제 API 결과**
    
    → 문서 신뢰도 100%
    
- 테스트 기반 → TDD/BDD 코드 품질 향상에 도움
- API가 커도 유지보수 수월
- 코드가 Swagger처럼 어노테이션으로 더러워지지 않음

---

## 2-3. 단점

- 학습 난이도 높음
- 문서 생성 과정이 번거롭다
- UI가 Swagger처럼 완성형이 아님
- 개발 초기에 문서 빠르게 보기가 힘듦

---

## 2-4. 사용 예제 코드

### build.gradle

```
testImplementation 'org.springframework.restdocs:spring-restdocs-mockmvc'
```

### 예제 테스트 코드

```java
// UserController만 슬라이스 테스트하는 WebMvcTest 설정
@WebMvcTest(UserController.class)
// Spring REST Docs 자동 설정 (MockMvc와 REST Docs 연동)
@AutoConfigureRestDocs
class UserApiDocsTest {

    // MockMvc: 웹 애플리케이션을 실제 서버 띄우지 않고 MVC 호출 테스트할 수 있게 해주는 객체
    @Autowired
    private MockMvc mockMvc;

    @Test
    void getUserDocs() throws Exception {
        // GET /users/1 요청을 MockMvc로 수행
        mockMvc.perform(get("/users/1"))
                // HTTP 응답 코드가 200 OK 인지 검증
                .andExpect(status().isOk())
                // 그리고 이 요청/응답을 기반으로 "get-user" 라는 이름의 문서 스니펫 생성
                .andDo(document("get-user",      
                // 스니펫이 저장될 디렉토리 이름 (identifier)

                     // pathParameters: URL 경로에 있는 {변수} 들을 문서화
                        pathParameters(
                     // {id} 라는 path variable이 있고, "유저 ID" 라는 설명을 문서에 남김
                                parameterWithName("id").description("유저 ID")
                        ),

                     // responseFields: JSON 응답 body에 포함된 필드들을 문서화
                        responseFields(
                                // JSON 응답의 "id" 필드 설명
                                fieldWithPath("id").description("유저 ID"),
                                // JSON 응답의 "name" 필드 설명
                                fieldWithPath("name").description("유저 이름")
                        )
                ));
    }
}
```

### 결과:

- `build/generated-snippets/get-user/` 폴더에
    
    `path-parameters.adoc`, `response-fields.adoc` 같은 문서 스니펫 자동 생성
    
- 폴더 구조 예시

```bash
project-root/
└── build/
    └── generated-snippets/
        └── get-user/                # document("get-user", ...) 이름과 동일한 폴더
            ├── http-request.adoc    # 요청 예시 (HTTP 요청 라인, 헤더 등)
            ├── http-response.adoc   # 응답 예시 (HTTP 상태, 헤더, body 등)
            ├── path-parameters.adoc # pathParameters() 로 정의한 내용
            ├── response-fields.adoc # responseFields() 로 정의한 내용
            └── curl-request.adoc    # curl 예시 요청
```

---

## 2-5. REST Docs 주의할 점

- 테스트 코드 없으면 문서를 만들 수 없음
- DTO 필드 변경 시 테스트 수정 안 하면 문서 실패
- 스니펫을 Asciidoctor로 합쳐야 하므로 **빌드 파이프라인 설정 필요**
- API 변경이 많고 빠른 스타트업 초기에는 Swagger보다 느릴 수 있음

---

## 스니펫과 아스키닥터

## 스니펫(snippet)

**스니펫 = 문서 조각**

- REST Docs는 **테스트를 돌릴 때**
    - `요청 예시`
    - `응답 예시`
    - `path parameter 설명`
    - `response field 설명`
- 이런 것들을 각각 `.adoc` 파일로 저장 → 이게 스니펫

이걸 왜 쪼개서 저장하냐?

- 나중에 **최종 문서를 만들 때** 이런 식으로 필요한 부분만 가져와서 include 할 수 있음

```
== Get User API

요청:

include::{snippets}/get-user/http-request.adoc[]

응답:

include::{snippets}/get-user/http-response.adoc[]

필드 설명:

include::{snippets}/get-user/response-fields.adoc[]
```

이렇게 하면:

- API 바뀌면 → 테스트 수정 → 스니펫 재생성 → 문서 자동 최신화
- 최종 문서에서는 `include`만 쓰니까 사람이 복붙할 필요가 없음

## Asciidoctor

**Asciidoctor = AsciiDoc 문서를 HTML/PDF 같은 걸로 변환해주는 엔진/툴**

- `.adoc` 확장자 = AsciiDoc 포맷 문서
    - 마크다운이랑 비슷한 마크업 언어라고 보면 됨
- Spring REST Docs가 뽑아주는 스니펫도 전부 `.adoc` 형식
- 최종적으로는
    - `src/docs/asciidoc/index.adoc` 같은 “메인 문서”를 만들고
    - 그 안에서 `include::{snippets}/...` 로 조각들을 끼워 넣고
    - Asciidoctor로 돌려서 HTML/PDF 생성

즉:

1. 테스트 → 스니펫(.adoc) 생성
2. AsciiDoc 메인 문서에서 스니펫들을 include
3. **Asciidoctor**로 최종 문서 빌드 (HTML/PDF)

---

## 왜 빌드 파이프라인 설정이 필요하냐?

“빌드 파이프라인 설정 필요”라는 말은 보통 **Gradle/Maven에서 문서 빌드가 자동으로 돌도록** 설정하라는 뜻

### 흐름을 보면:

1. `./gradlew test`
    - REST Docs 스니펫 생성 (`build/generated-snippets/...`)
2. `./gradlew asciidoctor`
    - Asciidoctor가 `src/docs/asciidoc/*.adoc` + `generated-snippets`를 합쳐서 HTML 문서 생성

그래서 보통 Gradle에 이런 식 설정을 추가

```
plugins {
    id "org.asciidoctor.jvm.convert" version "3.3.2"
}

asciidoctor {
    inputs.dir("build/generated-snippets")     // 스니펫 폴더
    dependsOn test                             // test 후에 asciidoctor 실행
}
```

이렇게 하면:

- **로컬에서 빌드할 때도**
    - `./gradlew asciidoctor` 한 번으로 테스트 + 문서 생성까지 같이
- **CI/CD 파이프라인에서도**
    - 테스트 통과해야만 문서가 생성되고,
    - 생성된 문서를 artifact로 남기거나, 정적 사이트로 배포 가능

---

# 3. Swagger vs REST Docs 차이 한눈에 정리

| 항목 | Swagger (OpenAPI) | Spring REST Docs |
| --- | --- | --- |
| 문서 생성 방식 | 코드 애노테이션 기반 자동화 | **실제 테스트 결과 기반** |
| 정확도 | 사람 실수로 틀릴 수 있음 | **테스트 기반으로 가장 정확함** |
| UI | 매우 좋음(Swagger UI) | 직접 Asciidoc/HTML 만들면 됨 |
| 학습 난이도 | 쉬움 | 어려움 |
| 코드 오염 여부 | 어노테이션 증가로 코드 더러워짐 | 코드 깔끔 |
| 변경 대응 | 자동 변경 → 빠름 | 테스트 수정 필요 |
| 적합한 환경 | 빠른 개발, 협업 많은 팀 | 안정 제품, 공공/금융, 문서 품질 중요한 팀 |

---

---

# 4. 어떤 상황에서 무엇을 쓰면 좋나?

### Swagger 추천 케이스

- 스타트업/초기 프로젝트
- 백엔드/프론트/모바일 팀 협업 많은 조직
- 빠르게 UI로 API 테스트해야 하는 경우
- 클라이언트 개발자 많아서 문서 UI가 중요한 경우

### REST Docs 추천 케이스

- 금융/공공/의료 등 **문서 정확도**가 최우선인 서비스
- 대규모 백엔드 API 프로젝트
- TDD/BDD 기반 개발 문화
- API 문서를 표준 문서로 외부 제공해야 하는 경우