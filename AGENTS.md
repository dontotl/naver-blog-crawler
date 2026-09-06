# Repository purpose (for Codex / other coding agents)

This repo is a single-purpose tool: crawl every post from one Naver blog and save each as a Markdown file with its images.

Read `SKILL.md` first — it has the full when/how-to-use guidance written for an AI coding agent (Claude Code's skill format, but the content applies here too). `README.md` is the human-facing install/usage doc.

## Quick facts

- Entry point: `naver_blog_crawler.py`, CLI args `--blog-id`, `--output-dir`, `--delay`.
- Dependencies: `pip install -r requirements.txt` (requests, beautifulsoup4, markdownify).
- No auth/API key required — it uses Naver's public post-list JSON endpoint and the mobile post-view HTML page.

## Ground rules when modifying or running this tool

- Keep the default `--delay` (0.7s) conservative; do not add concurrency/threading to speed up requests — that's what gets a user's IP rate-limited or CAPTCHA-blocked by Naver.
- This tool is for crawling one named blog for personal backup / research, not for bulk-crawling many blogs or search results.
- Never commit crawled output (`output/` — other people's blog content) into this repo; it's git-ignored on purpose.
- When fixing parsing (e.g. Naver changes its HTML), verify against a live fetch (`curl`) before assuming a selector is right — see the two content containers already handled: `div.se-main-container` (new editor) and `div#postViewArea` (old editor).
