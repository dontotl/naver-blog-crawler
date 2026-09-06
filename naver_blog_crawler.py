#!/usr/bin/env python3
"""Crawl every post from a Naver blog and save each as a Markdown file with images."""

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import unquote_plus

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
LIST_URL = "https://blog.naver.com/PostTitleListAsync.naver"
POST_URL = "https://m.blog.naver.com/PostView.naver"


def fetch_post_list(blog_id, count_per_page=30, delay=0.5):
    posts = []
    page = 1
    while True:
        params = {
            "blogId": blog_id,
            "currentPage": page,
            "categoryNo": 0,
            "parentCategoryNo": "",
            "countPerPage": count_per_page,
        }
        resp = requests.get(LIST_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        # Naver escapes single quotes as \' inside its JSON, which is not valid JSON.
        data = json.loads(resp.text.replace("\\'", "'"))
        batch = data.get("postList", [])
        if not batch:
            break
        for item in batch:
            posts.append(
                {
                    "logNo": item["logNo"],
                    "title": unquote_plus(item["title"]),
                    "addDate": item.get("addDate", ""),
                    "category": unquote_plus(item.get("categoryName", "") or ""),
                }
            )
        total_count = int(data.get("totalCount", 0))
        if len(posts) >= total_count:
            break
        page += 1
        time.sleep(delay)
    return posts


def fetch_post_content(blog_id, log_no):
    params = {"blogId": blog_id, "logNo": log_no}
    resp = requests.get(POST_URL, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.select_one('meta[property="og:title"]')
    title = title_tag["content"] if title_tag else None

    container = soup.select_one("div.se-main-container") or soup.select_one("div#postViewArea")

    image_urls = []
    if container:
        for img in container.select("img"):
            src = img.get("data-lazy-src") or img.get("src")
            if not src or not src.startswith("http"):
                continue
            image_urls.append(src)
            img["src"] = src
            if img.has_attr("data-lazy-src"):
                del img["data-lazy-src"]

    return {
        "title": title,
        "html": str(container) if container else "",
        "image_urls": image_urls,
    }


def download_images(image_urls, save_dir, referer):
    save_dir.mkdir(parents=True, exist_ok=True)
    url_to_path = {}
    headers = {**HEADERS, "Referer": referer}
    for i, url in enumerate(image_urls, start=1):
        ext = re.search(r"\.(jpg|jpeg|png|gif|bmp)", url, re.IGNORECASE)
        ext = ext.group(1).lower() if ext else "jpg"
        filename = f"{i:03d}.{ext}"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            (save_dir / filename).write_bytes(resp.content)
            url_to_path[url] = filename
        except requests.RequestException as exc:
            print(f"    이미지 다운로드 실패: {url} ({exc})")
    return url_to_path


def safe_filename(name, max_len=80):
    name = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    return name[:max_len] if name else "untitled"


def save_post_markdown(index, post, content, url_to_path, output_dir):
    images_rel_dir = f"{post['logNo']}/images"
    md_body = markdownify(content["html"], heading_style="ATX").strip()
    for url, filename in url_to_path.items():
        md_body = md_body.replace(url, f"{images_rel_dir}/{filename}")

    title = content["title"] or post["title"]
    md_text = (
        f"# {title}\n\n"
        f"- 날짜: {post['addDate']}\n"
        f"- 카테고리: {post['category']}\n"
        f"- 원문: https://blog.naver.com/{post['blog_id']}/{post['logNo']}\n\n"
        "---\n\n"
        f"{md_body}\n"
    )

    filename = f"{index:04d}_{post['logNo']}_{safe_filename(title)}.md"
    (output_dir / filename).write_text(md_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="네이버 블로그 전체 글 크롤러")
    parser.add_argument("--blog-id", required=True, help="네이버 블로그 아이디 (예: blacklion-trading)")
    parser.add_argument("--output-dir", default="./output", help="저장할 디렉토리")
    parser.add_argument("--delay", type=float, default=0.7, help="요청 사이 대기 시간(초)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/2] {args.blog_id} 게시글 목록 수집 중...")
    posts = fetch_post_list(args.blog_id, delay=args.delay)
    print(f"  총 {len(posts)}개 게시글 발견")

    print("[2/2] 게시글 본문/이미지 수집 중...")
    for i, post in enumerate(posts, start=1):
        post["blog_id"] = args.blog_id
        print(f"  ({i}/{len(posts)}) {post['title']}")
        content = fetch_post_content(args.blog_id, post["logNo"])
        referer = f"https://m.blog.naver.com/PostView.naver?blogId={args.blog_id}&logNo={post['logNo']}"
        images_dir = output_dir / post["logNo"] / "images"
        url_to_path = download_images(content["image_urls"], images_dir, referer)
        save_post_markdown(i, post, content, url_to_path, output_dir)
        time.sleep(args.delay)

    print(f"완료: {output_dir} 에 {len(posts)}개 게시글 저장됨")


if __name__ == "__main__":
    main()
