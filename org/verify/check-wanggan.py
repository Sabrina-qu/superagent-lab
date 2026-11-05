#!/usr/bin/env python3
"""网感静态检查（硬约束层）：对一篇稿件输出平台腔硬指标。

用法: python3 check-wanggan.py <稿件文件.md>
退出码: 0=全部通过 1=有硬指标不过

阈值说明: 主平台阈值在 Week 1 用 50 篇 case 校准后写入下方常量。
当前为初始保守值，校准前只做参考、不做门禁。
"""
import re, sys, unicodedata

# —— 主平台阈值（Week 1 校准时修订） ——
THRESH = {
    'douyin':  dict(max_avg_sentence=28, min_emoji_per_100=0.5, max_emoji_per_100=8.0, max_paragraphs=18, hook_required=True),
    'bilibili':dict(max_avg_sentence=35, min_emoji_per_100=0.0, max_emoji_per_100=4.0, max_paragraphs=25, hook_required=True),
    'xhs':     dict(max_avg_sentence=22, min_emoji_per_100=1.0, max_emoji_per_100=12.0, max_paragraphs=12, hook_required=True),
}
DEFAULT_PLATFORM = 'douyin'

def count_emoji(text: str) -> int:
    return sum(1 for ch in text if unicodedata.category(ch) == 'So' or 0x1F000 <= ord(ch) <= 0x1FAFF)

def split_sentences(text: str) -> list:
    parts = re.split(r'[。！？!?\n]+', text)
    return [p.strip() for p in parts if p.strip()]

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__); return 2
    text = open(sys.argv[1], encoding='utf-8').read()
    platform = DEFAULT_PLATFORM
    body_lines = [l for l in text.splitlines() if l.strip()]
    paragraphs = len(body_lines)
    sentences = split_sentences(text)
    hanzi = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    avg_sentence = round(hanzi / max(len(sentences), 1), 1)
    emoji = count_emoji(text)
    emoji_per_100 = round(emoji / max(hanzi, 1) * 100, 2)
    hook = '结论：有钩子' if re.search(r'^(你|我|为什么|怎么|千万别|救命|谁懂|家人们|听劝|离谱|破防)', body_lines[0] if body_lines else '') else '结论：未检出钩子句式'

    t = THRESH[platform]
    problems = []
    if avg_sentence > t['max_avg_sentence']: problems.append(f'平均句长 {avg_sentence} 字 > 阈值 {t["max_avg_sentence"]}')
    if not (t['min_emoji_per_100'] <= emoji_per_100 <= t['max_emoji_per_100']): problems.append(f'emoji 密度 {emoji_per_100}/百字 不在 [{t["min_emoji_per_100"]}, {t["max_emoji_per_100"]}]')
    if paragraphs > t['max_paragraphs']: problems.append(f'分段数 {paragraphs} > 阈值 {t["max_paragraphs"]}')
    if t['hook_required'] and hook.startswith('结论：未检出'): problems.append('前3秒/首段未检出钩子句式')

    print(f'平台={platform} 字数={hanzi} 句数={len(sentences)} 平均句长={avg_sentence}字 '
          f'emoji={emoji}({emoji_per_100}/百字) 分段={paragraphs} {hook}')
    if problems:
        print('不过项：'); [print(f'  - {p}') for p in problems]; return 1
    print('全部通过（硬指标层；品味层仍由 rubric 人工评分）')
    return 0

if __name__ == '__main__':
    sys.exit(main())
