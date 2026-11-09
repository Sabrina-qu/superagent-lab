#!/usr/bin/env python3
"""合并权审计：检查 main 上最近合并的 PR 是否由 agent 账号执行。

护栏（规划书 1.3 / AGENTS.md 七）：自动合并保持关闭，所有 PR 由人合并。
本脚本用 GitHub 公共 REST API（只读）拉最近合并的 PR，若 merged_by 是
agent/bot 账号（默认 Sabrina-qu-bot 及任何 `*[bot]`），判定违规并 exit 1。

用法:
    python3 org/verify/check-merge-policy.py                # 默认审计最近 20 个已合并 PR
    python3 org/verify/check-merge-policy.py --since 2026-11-09
    python3 org/verify/check-merge-policy.py --repo Sabrina-qu/superagent-lab

退出码: 0=无违规 1=发现 agent 合并 2=用法/网络错误
环境变量: GITHUB_TOKEN（可选，私有仓库或避免限流时需要）
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

DEFAULT_REPO = 'Sabrina-qu/superagent-lab'
AGENT_LOGINS = {'sabrina-qu-bot'}


def is_agent(login: str) -> bool:
    if not login:
        return False
    return login.lower() in AGENT_LOGINS or login.lower().endswith('[bot]')


def api(url: str):
    headers = {'User-Agent': 'dsh-merge-audit', 'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main(argv):
    repo = DEFAULT_REPO
    since = None
    if '--repo' in argv:
        repo = argv[argv.index('--repo') + 1]
    if '--since' in argv:
        since = datetime.fromisoformat(argv[argv.index('--since') + 1]).replace(tzinfo=timezone.utc)

    url = f'https://api.github.com/repos/{repo}/pulls?state=closed&per_page=50&sort=updated&direction=desc'
    pulls = None
    for attempt in range(3):
        try:
            pulls = api(url)
            break
        except Exception as exc:  # 网络/限流/截断
            if attempt < 2:
                print(f'列表拉取第 {attempt + 1} 次失败（{exc}），3 秒后重试')
                import time
                time.sleep(3)
            else:
                print(f'ERROR: 无法读取 PR 列表：{exc}')
                return 2

    violated, checked, unknown = [], 0, []
    for pr in pulls:
        if not pr.get('merged_at'):
            continue
        merged_at = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
        if since and merged_at < since:
            continue
        checked += 1
        # 列表接口的 merged_by 可能是 null，必须取单个 PR 详情确认合并人；
        # 单个详情拉取失败（限流/截断）不得导致整次审计崩溃 -> 计入 unknown 留人工核
        try:
            detail = api(f"https://api.github.com/repos/{repo}/pulls/{pr['number']}")
        except Exception as exc:
            print(f'注意：#{pr["number"]} 详情拉取失败（{exc}），计入 unknown')
            unknown.append((pr['number'], pr['title'], pr['merged_at']))
            continue
        login = (detail.get('merged_by') or {}).get('login')
        if not login:
            unknown.append((pr['number'], pr['title'], pr['merged_at']))
            continue
        if is_agent(login):
            violated.append((pr['number'], pr['title'], login, pr['merged_at']))

    print(f'repo={repo} 审计已合并 PR 数={checked}' + (f'（since {since.date()}）' if since else ''))
    if unknown:
        print('注意：以下 PR 取不到 merged_by，需人工确认合并人：')
        for number, title, merged_at in unknown:
            print(f'  - #{number} at={merged_at} :: {title}')
    if violated:
        print('违规：以下 PR 由 agent/bot 账号合并（应仅由人合并）：')
        for number, title, login, merged_at in violated:
            print(f'  - #{number} merged_by={login} at={merged_at} :: {title}')
        print('处理：人工复核这些改动是否仍可接受；在 GitHub 开启分支保护/限制合并权限，避免再次发生。')
        return 1
    print('通过：没有 agent 账号合并记录。')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))