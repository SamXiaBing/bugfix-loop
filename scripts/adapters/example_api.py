#!/usr/bin/env python3
"""参考适配器。把缺陷系统的接口接成主清单能吃的 feed。

这是样板，不是能直接跑的成品。你的缺陷系统不一样，照着改四个地方就行。
演示模式 --demo 不需要任何凭证，直接出一份示例 feed，用来自测。

用法
  python adapters/example_api.py --demo
  python adapters/example_api.py --url https://issues.example.com --query filter=backlog --token-env TRACKER_TOKEN
"""

import argparse
import json
import os
import sys
import urllib.request


def demo_feed():
    return {
        "issues": [
            {"key": "BUG-101", "title": "订单列表页在窄屏下按钮错位"},
            {"key": "BUG-102", "title": "点击导出偶尔没反应"},
            {"key": "BUG-103", "title": "支付结果页偶发白屏"},
        ]
    }


def fetch(base_url, query, token):
    url = f"{base_url.rstrip('/')}/rest/issues?query={query}"
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description="缺陷源适配器样板")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--url", default=None)
    ap.add_argument("--query", default=None)
    ap.add_argument("--token-env", default=None)
    args = ap.parse_args()

    if args.demo:
        json.dump(demo_feed(), sys.stdout, ensure_ascii=False)
        print()
        return

    if not args.url or not args.query:
        print("要 --url 和 --query，或者 --demo", file=sys.stderr)
        sys.exit(1)

    token = os.environ.get(args.token_env or "") or None
    json.dump(fetch(args.url, args.query, token), sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
