# 네이버 블로그 크롤러 (naver-blog-crawl)

특정 네이버 블로그(`blog.naver.com/{blogId}`)의 전체 게시글을 크롤링해서 게시글별 Markdown 파일 + 이미지로 저장하는 도구입니다. Claude Code 스킬(`SKILL.md`)과 Codex 등 다른 코딩 에이전트(`AGENTS.md`)에서 모두 인식하도록 구성했습니다.

## ⚠️ 먼저 읽어주세요 (주의사항)

- **개인 소유 블로그 백업 또는 연구 목적**으로만 사용하세요. 특정 블로그 1개를 대상으로 하는 도구이며, 여러 블로그를 대량으로 훑거나 네이버 검색 결과를 무차별 수집하는 용도로 확장하지 마세요.
- 네이버 이용약관은 비인가 자동 수집(크롤링)을 금지하고 있습니다. 과도하게 빠른 요청을 보내면 요청자의 **IP가 일시적으로 차단되거나 캡차가 걸릴 수 있습니다.** 기본 딜레이(`--delay 0.7`)를 낮추거나 병렬로 요청하지 마세요.
- 크롤링 결과물(타인의 게시글·이미지)은 **이 저장소에 커밋하지 마세요.** `.gitignore`에 `output/`이 이미 제외되어 있습니다 — 도구만 공개하고, 실제로 긁어온 콘텐츠는 로컬에만 보관하세요.
- 본인 블로그가 아닌 콘텐츠를 재배포/재출판하면 저작권·이용약관 이슈가 생길 수 있습니다. 이 도구 자체는 문제가 없지만, **크롤링한 남의 글을 그대로 퍼가서 올리는 행위**가 위험합니다.
- 상업적 대량 수집, 서버에 부하를 주는 용도로 사용 금지.

## 설치

```bash
git clone https://github.com/dontotl/naver-blog-crawler.git
cd naver-blog-crawler
pip install -r requirements.txt
```

Claude Code 스킬로 쓰려면 이 저장소를 `~/.claude/skills/naver-blog-crawl/`에 clone하면 자동으로 스킬 목록에 나타납니다.

## 사용법

```bash
python naver_blog_crawler.py --blog-id blacklion-trading --output-dir ./output
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--blog-id` | (필수) | 크롤링할 네이버 블로그 아이디, 예: `blacklion-trading` |
| `--output-dir` | `./output` | 결과 저장 디렉토리 |
| `--delay` | `0.7` | 요청 사이 대기 시간(초). 낮추지 않기를 권장 |

실행하면:
1. 블로그의 전체 게시글 목록(logNo)을 페이지 단위로 수집
2. 게시글별로 모바일 뷰를 파싱해 제목/본문/이미지 URL 추출
3. 이미지를 `output/{logNo}/images/`에 다운로드
4. 게시글을 `output/{순번}_{logNo}_{제목}.md`로 저장 (이미지는 상대경로로 링크)

## 동작 원리

- 게시글 목록: `https://blog.naver.com/PostTitleListAsync.naver` (비공식 JSON, 네이버가 작은따옴표를 `\'`로 이스케이프하는 비표준 포맷이라 별도 보정 처리함)
- 게시글 본문: `https://m.blog.naver.com/PostView.naver` (PC뷰의 iframe 구조보다 파싱이 쉬움). 신형 에디터는 `div.se-main-container`, 구형 에디터는 `div#postViewArea`를 사용

## 제한사항 / 알려진 이슈

- 네이버가 마크업을 바꾸면 선택자(selector)가 깨질 수 있습니다. 이 경우 `naver_blog_crawler.py`의 `fetch_post_content` 함수를 실제 HTML에 맞춰 수정하세요.
- 비공식 엔드포인트를 사용하므로 예고 없이 동작이 바뀔 수 있습니다.
- 비공개(서로이웃 공개, 비밀글) 게시글은 로그인 세션이 없어 수집되지 않습니다.

## 라이선스

MIT License — [LICENSE](LICENSE) 참고. 이 라이선스는 코드에만 적용되며, 크롤링한 콘텐츠의 저작권은 원저작자에게 있습니다.
