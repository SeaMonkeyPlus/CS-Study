'''   
    마크다운 자동 갱신 파이썬 파일
    Github Actions로 월수금 자정마다 실행
    갱신내용이 없는경우(ex 스터디 쉬는날) 갱신 X(캐싱 처리)
    각 폴더의 마크다운 이름을 가져와서 링크 생성
    하위 폴더를 고려해 폴더/파일 유무 이모지 추가
    Rule 수정이 필요한 경우 해당 파일에서 수정
    Github에 이름이 불분명, 스터디원 한정적으로 인해 스터디원 하드코딩

'''
import os
import re
from pathlib import Path
from urllib.parse import quote

# GitHub 레포지토리 정보
REPO_OWNER = "SeaMonkeyPlus"
REPO_NAME = "CS-Study"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main"

# 제외할 폴더/파일
EXCLUDE_DIRS = {'.git', '.github', 'image', '__pycache__', '.venv', 'node_modules', '.idea', '.vscode'}

# Rule 섹션 (고정값)
RULE_SECTION = """## ✨ Rule

- 스터디는 매주 월, 수, 금 21:00 진행
- 각자 발표할 CS 주제를 정하고 학습하기
- 학습한 CS는 마크다운으로 정리해서 스터디 시간에 발표
- 다른 참가자들로부터 질문을 받고 답변을 기록하기
- 불충분한 답변은 이후에 작성하고 다음 스터디 시간에 답변하기
- 다음에 발표할 CS 주제를 각자 Discord 스레드에 작성하여 공유하기

"""

# 스터디원 섹션 (고정값)
MEMBERS_SECTION = """## 👨‍💻 스터디원

| 이름   | GitHub                                     |
| ------ | ------------------------------------------ |
| 김정우 | [@3957ki](https://github.com/3957ki)       |
| 백승훈 | [@Shbak111](https://github.com/Shbak111)   |
| 이진호 | [@binaryarc](https://github.com/binaryarc) |
| 장현정 | [@hyunddo](https://github.com/hyunddo)     |
| 전희성 | [@Airdexx](https://github.com/Airdexx)     |
| 최영환 | [@dlsxj101](https://github.com/dlsxj101)   |
"""

def get_categories():
    """루트 디렉토리의 폴더를 카테고리로 자동 인식 (알파벳 순)"""
    categories = []
    root = Path('.')
    
    for item in root.iterdir():
        # 폴더만 선택, 제외 목록에 없고, 숨김 폴더 아닌 것
        if item.is_dir() and item.name not in EXCLUDE_DIRS and not item.name.startswith('.'):
            categories.append(item.name)
    
    # 알파벳 순 정렬
    categories.sort(key=str.lower)
    return categories

def get_md_files(category_path):
    """특정 카테고리의 .md 파일 목록 가져오기 (알파벳 순 정렬)"""
    md_files = []
    
    if not category_path.exists():
        return md_files
    
    for item in category_path.rglob("*.md"):
        # image 폴더 제외
        if "image" in item.parts:
            continue
        
        relative_path = item.relative_to(category_path.parent)
        md_files.append(relative_path)
    
    # 알파벳 순 정렬
    md_files.sort(key=lambda x: str(x).lower())
    return md_files

def create_github_link(file_path):
    """파일 경로를 GitHub 링크로 변환"""
    # URL 인코딩
    encoded_path = quote(str(file_path).replace('\\', '/'))
    return f"{REPO_URL}/{encoded_path}"

def get_file_title(file_path):
    """파일명에서 제목 추출 (.md 제거)"""
    return file_path.stem

def generate_category_section(category):
    """카테고리별 섹션 생성"""
    lines = [f"## ✏️ {category}\n"]
    
    category_path = Path(category)
    md_files = get_md_files(category_path)
    
    if not md_files:
        lines.append("\n")
        return "".join(lines)
    
    # 하위 폴더별로 그룹화
    current_subfolder = None
    
    for file_path in md_files:
        parts = file_path.parts
        
        # 하위 폴더가 있는 경우
        if len(parts) > 2:  # Category/Subfolder/file.md
            subfolder = parts[1]
            if subfolder != current_subfolder:
                lines.append(f"\n- 📁 **{subfolder}**\n")
                current_subfolder = subfolder
            indent = "  "
        else:
            indent = ""
            current_subfolder = None
        
        title = get_file_title(file_path)
        link = create_github_link(file_path)
        lines.append(f"{indent}- 📄 [{title}]({link})\n")
    
    lines.append("\n")
    return "".join(lines)

def generate_readme():
    """README.md 생성"""
    readme_path = Path("README.md")
    
    # 새 README 생성
    new_content = "# CS-Study\n\n"
    
    # Rule 섹션 추가 (고정값)
    new_content += RULE_SECTION
    
    # 동적으로 감지한 카테고리별 섹션 생성
    categories = get_categories()
    print(f"📁 Found {len(categories)} categories: {', '.join(categories)}")
    
    for category in categories:
        new_content += generate_category_section(category)
    
    # 스터디원 섹션 추가 (고정값)
    new_content += MEMBERS_SECTION
    
    # 캐시 기능: 내용이 같으면 저장하지 않음
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            if f.read() == new_content:
                print("✅ README.md is already up to date. No changes needed.")
                return False
    
    # README.md 저장
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ README.md has been updated successfully!")
    return True

if __name__ == "__main__":
    generate_readme()