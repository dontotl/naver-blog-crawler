---
name: naver-blog-crawl
description: Crawl every post from a specific Naver blog (blog.naver.com/{blogId}) and save each as a Markdown file with downloaded images. Use this when the user asks to crawl, scrape, archive, or back up a Naver blog ("네이버 블로그 크롤링", "네이버 블로그 백업", "crawl naver blog"). Requires the target blog id/URL and only supports personal-backup / research use, never mass or commercial scraping.
compatibility: Requires Python 3 with requests, beautifulsoup4, markdownify (see requirements.txt). No API key needed.
---

# Naver Blog Crawler

Crawls all posts from one Naver blog (`blog.naver.com/{blogId}`) via Naver's public (unofficial) post-list and mobile post-view endpoints, and saves each post as a standalone Markdown file with its images downloaded locally.

## When to use

- The user names a specific `blog.naver.com/{id}` (or `m.blog.naver.com/{id}`) and asks to crawl / scrape / archive / back up its posts.
- Do NOT use this for: crawling arbitrary non-Naver sites, bulk-crawling many blogs at once, or any request framed around mass/commercial scraping — decline and explain the risk instead (see Cautions).

## Before running

1. Confirm the target blog id (or URL) with the user if not given.
2. Confirm the output directory and whether they want images included (default: yes).
3. Remind the user of the caution points below once, briefly, before the first run in a session.

## How to run

```bash
pip install -r requirements.txt
python naver_blog_crawler.py --blog-id {blogId} --output-dir ./output --delay 0.7
```

- `--blog-id`: required, the Naver blog id (e.g. `blacklion-trading`)
- `--output-dir`: default `./output`
- `--delay`: seconds between requests, default `0.7` — do not lower this for a user; if they ask to speed it up, explain that faster crawling raises the chance of a temporary Naver IP block

Script does two phases:
1. Paginates `PostTitleListAsync.naver` to collect every `logNo` (handles Naver's non-standard `\'`-escaped JSON).
2. For each `logNo`, fetches the mobile post view (`m.blog.naver.com/PostView.naver`), extracts title/body/images from `div.se-main-container` (falls back to `div#postViewArea` for old-editor posts), downloads images, and writes `output/{index}_{logNo}_{title}.md` plus `output/{logNo}/images/`.

## After running

Verify before reporting success:
- Count of generated `.md` files matches the `totalCount` the script printed.
- Spot-check 1-2 files: title/date/body render correctly and image links resolve to files that actually exist in `{logNo}/images/`.

## Cautions (always mention before/around first run)

- **Personal-backup / research use only.** This targets a specific blog the user names — never suggest expanding scope to scrape many blogs or Naver search results in bulk.
- Naver's terms of service prohibit unauthorized automated collection; aggressive request rates can get the requester's IP temporarily blocked or CAPTCHA-walled. Keep the default delay; never parallelize requests.
- Don't commit crawled output (other people's blog content) into a git repo — it belongs in `.gitignore`. This skill's own repo excludes `output/` for that reason.
- If the target blog is not the user's own, remind them that redistributing the scraped content may raise copyright/ToS concerns — the tool is fine, republishing someone else's posts is the risky part.
