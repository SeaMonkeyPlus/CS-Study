# ✅ Git은 “파일 변경 기록”이 아니라 “스냅샷 저장소”

보통 사람들은 Git을

> “변경(diff)을 저장하는 도구”
> 라고 생각하지만 ❌

**Git은 ‘매 버전의 전체 스냅샷’을 저장한다.** ⭕️

단,
같은 내용의 파일은 이전 버전과 **중복 저장 안 하고 공유**함 → 그래서 빠르고 용량 효율 좋음.

---

# ✅ Git 내부 저장 구조 – 객체(Object) 3개만 알면 끝

Git 저장소 내부 `.git/objects`에 3가지 객체만 저장됨

---

## 1️⃣ Blob (파일 내용)

- 파일 내용 자체
- 이름, 권한 정보 없음
- 그냥 내용 덩어리

```
hello.txt  → Blob
```

---

## 2️⃣ Tree (디렉토리 구조)

- 폴더 구조 + 파일 이름 + 권한 + blob 연결

```
Tree
 ├── hello.txt → Blob
 └── src/ → Tree
```

---

## 3️⃣ Commit

- 어떤 Tree를 가리키는지
- 부모 Commit
- 작성자 / 메시지

```
Commit
 ├─ Tree (스냅샷 전체)
 ├─ Parent Commit
 └─ Message
```

---

# 🔥 중요한 특징

모든 객체는 **내용 기반 SHA-1 해시값으로 저장됨**
→ 내용이 바뀌면 다른 객체
→ 내용 같으면 같은 객체 재사용

그래서:

- 데이터 위조 거의 불가
- 안정적
- 빠름

---

# ✅ Branch는 “특별한 것”이 아니다

많이 오해하는데:

> 브랜치는 “복사본” ❌
> 브랜치는 “포인터” ⭕️

단지,

```
master → commit A
feature → commit B
```

처럼 **커밋 하나를 가리키는 이름(label)**일 뿐.

---

# ✅ HEAD는 “현재 내가 보고 있는 커밋 포인터”

보통

```
HEAD → branch → commit
```

checkout 하면?
👉 HEAD 가 다른 커밋/브랜치를 가리키는 것뿐

---

# ✅ Staging Area(= Index)는 “커밋 후보 공간”

Git 구조 3개만 기억하면 됨

```
Working Directory  : 실제 파일
Staging Area       : 이번 커밋에 넣을 것
Repository         : 완성된 Commit
```

`git add` → Staging에 올림
`git commit` → Staging 상태를 Snapshot으로 저장

---

# ✅ Reset / Revert 이해도 내부 원리로 해결됨

### 🔹 reset

> “브랜치 포인터를 움직인다”

```
branch pointer ← 옮김
```

### 🔹 revert

> “이전 상태를 되돌리는 **새 커밋**을 만든다”

```
새 Commit 하나 더 추가
```

그래서 reset은 위험하고
revert는 안전함.

---

# 🎯 한 줄 정리 (스터디/면접용)

```
Git은 변경(diff)이 아니라 스냅샷을 저장하는 분산 버전 관리 시스템입니다.
파일은 Blob, 디렉토리는 Tree, 버전은 Commit 객체로 관리되고,
각 객체는 SHA-1 해시로 식별되는 불변 구조입니다.
Branch는 단순히 Commit을 가리키는 포인터이고,
HEAD는 현재 참조 위치를 의미합니다.
```

---

# 질문

- Git을 사용할 때 충돌이 나는데, 어떤 상황일 때 충돌이 발생하냐?
  - 답은 Git이 원래 자동으로 병합해주는 기능이 있는데, Commit을 했을 때, 이전 버전과 자동으로 병합이 안될 때 충돌이 일어난다.
