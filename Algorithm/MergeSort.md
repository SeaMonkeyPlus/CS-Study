# 병합 정렬 (Merge Sort)

---

분할 정복(Divide and Conquer) 전략을 사용하는 대표적인 정렬 알고리즘에 대한 내용이다

## 정의

**배열을 반으로 나누어 정렬한 후 병합하는 알고리즘**

- 배열을 더 이상 나눌 수 없을 때까지 반으로 분할
- 분할된 작은 배열들을 정렬하면서 병합
- 안정 정렬(Stable Sort) 알고리즘
- 분할 정복의 대표적인 예시

참고 영상: https://www.youtube.com/shorts/9Koa-hWoMes

## 왜 병합 정렬인가?

**예측 가능한 성능**

- 최선, 평균, 최악의 경우 모두 O(n log n) 보장
- 입력 데이터 상태에 관계없이 일정한 성능
- 퀵 정렬과 달리 최악의 경우에도 O(n²)로 떨어지지 않음

**안정 정렬의 장점**

- 같은 값을 가진 원소들의 상대적 순서 유지
- 복합 정렬 기준이 필요한 경우 유용
- 데이터베이스나 정렬 체인에서 중요

**분할 정복의 학습**

- 재귀적 사고방식 훈련에 최적
- 복잡한 문제를 작은 문제로 나누는 전략 이해
- 많은 알고리즘의 기초가 되는 패러다임

## 작동 원리

### 1단계: 분할 (Divide)

**배열을 절반씩 나누어 단일 원소가 될 때까지 분할**

```
[38, 27, 43, 3, 9, 82, 10]
      ↓ 분할
[38, 27, 43, 3] | [9, 82, 10]
      ↓ 분할
[38, 27] [43, 3] | [9, 82] [10]
      ↓ 분할
[38] [27] [43] [3] | [9] [82] [10]
```

### 2단계: 정복 및 병합 (Conquer & Combine)

**정렬된 부분 배열들을 병합하면서 정렬**

```
[38] [27] [43] [3] | [9] [82] [10]
      ↓ 병합
[27, 38] [3, 43] | [9, 82] [10]
      ↓ 병합
[3, 27, 38, 43] | [9, 10, 82]
      ↓ 병합
[3, 9, 10, 27, 38, 43, 82]
```

### 병합 과정의 핵심

**두 개의 정렬된 배열을 하나의 정렬된 배열로 합치기**

1. 각 배열의 첫 번째 원소를 비교
2. 더 작은 원소를 결과 배열에 추가
3. 선택된 원소의 다음 원소와 비교 반복
4. 한쪽 배열이 끝나면 나머지를 모두 추가

## 구현

### 기본 구현 (Python)

```python
def merge_sort(arr):
    """
    병합 정렬 메인 함수
    
    Args:
        arr: 정렬할 배열
    
    Returns:
        정렬된 배열
    """
    # 기저 조건: 배열의 크기가 1 이하면 이미 정렬됨
    if len(arr) <= 1:
        return arr
    
    # 분할 단계: 배열을 반으로 나눔
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    
    # 재귀적으로 각 부분을 정렬
    left = merge_sort(left)
    right = merge_sort(right)
    
    # 정렬된 부분들을 병합
    return merge(left, right)


def merge(left, right):
    """
    두 정렬된 배열을 병합
    
    Args:
        left: 정렬된 왼쪽 배열
        right: 정렬된 오른쪽 배열
    
    Returns:
        병합된 정렬 배열
    """
    result = []
    i = j = 0
    
    # 두 배열을 비교하며 작은 원소부터 추가
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= 사용으로 안정 정렬 보장
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 남은 원소들 추가
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result
```

### In-place 병합 정렬 (공간 최적화)

```python
def merge_sort_inplace(arr, left=0, right=None):
    """
    제자리 병합 정렬 (추가 공간 최소화)
    
    Args:
        arr: 정렬할 배열
        left: 정렬 시작 인덱스
        right: 정렬 끝 인덱스
    """
    if right is None:
        right = len(arr) - 1
    
    if left < right:
        mid = (left + right) // 2
        
        # 재귀적으로 분할 정렬
        merge_sort_inplace(arr, left, mid)
        merge_sort_inplace(arr, mid + 1, right)
        
        # 병합
        merge_inplace(arr, left, mid, right)


def merge_inplace(arr, left, mid, right):
    """
    제자리 병합 (임시 배열 사용)
    """
    # 임시 배열 생성
    temp = []
    i = left
    j = mid + 1
    
    # 병합 과정
    while i <= mid and j <= right:
        if arr[i] <= arr[j]:
            temp.append(arr[i])
            i += 1
        else:
            temp.append(arr[j])
            j += 1
    
    # 남은 원소들 추가
    while i <= mid:
        temp.append(arr[i])
        i += 1
    
    while j <= right:
        temp.append(arr[j])
        j += 1
    
    # 원본 배열에 복사
    for i in range(len(temp)):
        arr[left + i] = temp[i]
```

### 사용 예제

```python
# 기본 사용
arr = [38, 27, 43, 3, 9, 82, 10]
sorted_arr = merge_sort(arr)
print(f"정렬 결과: {sorted_arr}")
# 출력: 정렬 결과: [3, 9, 10, 27, 38, 43, 82]

# In-place 정렬
arr2 = [64, 34, 25, 12, 22, 11, 90]
merge_sort_inplace(arr2)
print(f"In-place 정렬 결과: {arr2}")
# 출력: In-place 정렬 결과: [11, 12, 22, 25, 34, 64, 90]

# 안정 정렬 확인 (같은 값의 순서 유지)
students = [
    ('Alice', 85),
    ('Bob', 75),
    ('Charlie', 85),
    ('David', 75)
]

# 점수로 정렬 (이름 순서는 유지됨)
sorted_students = merge_sort(students)
print(f"정렬된 학생들: {sorted_students}")
```

## 시간 복잡도 분석

### 분석

**모든 경우 O(n log n)**

```
분할 단계: log n 번 (트리의 높이)
각 단계의 병합: n 번 (모든 원소 처리)
→ 총 시간: O(n log n)
```

| 경우 | 시간 복잡도 | 설명 |
|------|------------|------|
| 최선 | O(n log n) | 이미 정렬된 경우도 동일 |
| 평균 | O(n log n) | 항상 절반씩 분할 |
| 최악 | O(n log n) | 입력 상태 무관 |

### 공간 복잡도

**O(n)의 추가 공간 필요**

- 병합 과정에서 임시 배열 필요
- 재귀 호출 스택: O(log n)
- 총 공간: O(n)

## 다른 정렬과의 비교

### 퀵 정렬과 비교

| 특징 | 병합 정렬 | 퀵 정렬 |
|------|----------|---------|
| 최악 시간 | O(n log n) | O(n²) |
| 평균 시간 | O(n log n) | O(n log n) |
| 공간 복잡도 | O(n) | O(log n) |
| 안정성 | 안정 | 불안정 |
| 캐시 효율 | 낮음 | 높음 |

**선택 기준**
- 안정 정렬이 필요하거나 최악 성능이 중요하면 → 병합 정렬
- 메모리가 제한적이거나 평균 속도가 중요하면 → 퀵 정렬

## 어디에 사용될까?

### 실전 활용

**대용량 데이터 정렬**
- 외부 정렬(External Sort): 메모리보다 큰 파일 정렬
- 데이터베이스 정렬 연산
- 파일 시스템 정렬

**안정성이 필요한 경우**
- 다중 키 정렬 (예: 나이순 → 이름순)
- 타임스탬프 유지가 중요한 로그 데이터
- UI 정렬에서 사용자 경험 유지

**병렬 처리**
- 각 부분을 독립적으로 정렬 가능
- 멀티코어 환경에서 효율적
- 분산 시스템에서 활용 (MapReduce)

### 알고리즘 문제

**역순 쌍 개수 세기 (Inversion Count)**
- 배열에서 i < j이지만 arr[i] > arr[j]인 쌍의 개수
- 병합 과정에서 O(n log n)에 계산 가능

**구간 합 문제**
- 분할 정복을 이용한 최적화
- 세그먼트 트리의 기초

### 병합 전 정렬 여부 확인

```python
def smart_merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = smart_merge_sort(arr[:mid])
    right = smart_merge_sort(arr[mid:])
    
    # 이미 정렬되어 있다면 병합 생략
    if left[-1] <= right[0]:
        return left + right
    
    return merge(left, right)
```

## 주의사항

- 메모리 사용량  많음
- 연속된 메모리 접근이 아니어서 캐시 효율이 낮음
- Timsort라는 상위호환 존재(Python의 sorted())
---