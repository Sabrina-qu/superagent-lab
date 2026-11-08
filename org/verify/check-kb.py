#!/usr/bin/env python3
"""kb-ingest 门禁（硬约束层）：校验 case 卡是否按收料要求入库。

用法:
    python3 org/verify/check-kb.py <case卡.md> [--root <仓库根>]
    python3 org/verify/check-kb.py --self-test

退出码: 0=全部通过 1=有门禁不过 2=用法/解析错误

检查项（对应规划书 Phase 2「格式/词表/门禁」验收）:
  1. front-matter 必填字段齐全（kb_version/source_*/title/枚举字段）
  2. 枚举值全部来自 kb-inbox/vocabulary.yml 受控词表
  3. 原料存在，且原料登记的平台/账号/链接/抓取日期与 case 卡一致
  4. 禁改原则：每个 `原句:` 摘录必须逐字出现在原料里（允许空白差异，不允许改字、省略号跨段）
  5. 必填小节齐全且非空；评论区热门梗 ≥3 条
  6. 结构标记的数字与按原料重算的硬指标一致（句长 ±1 字、emoji ±0.5/百字、分段数完全一致）
  7. meme_refs 引用的梗必须在 meme-bank 里存在且未标灰

依赖: PyYAML（WSL/Windows 均已装好）
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - 环境缺依赖时给明确提示
    print('ERROR: 需要 PyYAML（pip install pyyaml）')
    sys.exit(2)

# Windows 控制台默认 GBK，直接 print 中文/符号会崩；统一按 UTF-8 输出。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:  # pragma: no cover - 老版本 Python 没有 reconfigure
        pass

ELLIPSIS = ('…', '...', '⋯')

REQUIRED_ENTRY_FIELDS = [
    'kb_version', 'source_raw', 'source_platform', 'source_account', 'source_url',
    'captured_at', 'title', 'hook_type', 'emotion_arc', 'cta_type', 'golden_line_position',
]
REQUIRED_RAW_FIELDS = ['source_platform', 'source_account', 'source_url', 'captured_at', 'title']


def split_front_matter(text):
    """返回 (front_matter_dict, body_text, parse_error)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, text, '缺少 YAML front-matter（文件第一行必须是 ---）'
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return None, text, 'front-matter 没有结束的 ---'
    try:
        meta = yaml.safe_load('\n'.join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        return None, text, f'front-matter 不是合法 YAML：{exc}'
    return meta, '\n'.join(lines[end + 1:]), None


def norm(s):
    """折叠空白，用于逐字比对（不做任何标点/文字替换）。"""
    return ''.join(s.split())


def count_emoji(text):
    import unicodedata
    return sum(1 for ch in text if unicodedata.category(ch) == 'So' or 0x1F000 <= ord(ch) <= 0x1FAFF)


def count_hanzi(text):
    return sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')


def split_sentences(text):
    import re
    return [p.strip() for p in re.split(r'[。！？!?\n]+', text) if p.strip()]


def parse_raw_body(body):
    """把原料正文拆成 (正文, 评论区原文)；评论区以「评论区」开头的行为界。"""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('评论区'):
            return '\n'.join(lines[:i]), '\n'.join(lines[i + 1:])
    return body, ''


def metrics_of(raw_body):
    hanzi = count_hanzi(raw_body)
    sentences = split_sentences(raw_body)
    lines = [l for l in raw_body.splitlines() if l.strip()]
    emoji = count_emoji(raw_body)
    return {
        'avg_sentence': round(hanzi / max(len(sentences), 1), 1),
        'emoji_per_100': round(emoji / max(hanzi, 1) * 100, 2),
        'paragraphs': len(lines),
        'hanzi': hanzi,
        'sentences': len(sentences),
        'emoji': emoji,
    }


def heading_sections(body):
    """把正文按 ## 标题切开，返回 {标题: 内容}。"""
    sections, current, buf = {}, None, []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            if current is not None:
                sections[current] = '\n'.join(buf)
            current, buf = stripped[3:].strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = '\n'.join(buf)
    return sections


def find_section(sections, name):
    for title, content in sections.items():
        if title == name or title.startswith(name):
            return content
    return None


def extract_quotes(body):
    quotes = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith('- '):
            line = line[2:].strip()
        if not line.startswith('原句:'):
            continue
        value = line[len('原句:'):].strip()
        for wrapper in ('"', "'", '“', '”', '「', '」'):
            if value.startswith(wrapper):
                value = value[len(wrapper):]
            if value.endswith(wrapper):
                value = value[:-len(wrapper)]
        quotes.append(value.strip())
    return quotes


def load_meme_bank(root):
    path = root / 'org' / 'skills' / 'meme-bank.md'
    if not path.exists():
        return None
    names = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or cells[0] in ('梗', '') or set(cells[0]) <= set('-: '):
            continue
        names[cells[0].strip('`')] = line
    return names


def parse_metric_line(section_text, label):
    import re
    for line in section_text.splitlines():
        line = line.strip().lstrip('- ').strip()
        if label in line:
            m = re.search(r'([-+]?\d+(?:\.\d+)?)', line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1])
            if m:
                return float(m.group(1))
    return None


class Report:
    def __init__(self):
        self.failures = []
        self.passes = 0

    def ok(self, msg):
        self.passes += 1
        print(f'  [OK]   {msg}')

    def fail(self, msg):
        self.failures.append(msg)
        print(f'  [FAIL] {msg}')


def check_entry(entry_path, root, vocab, report, quiet=False):
    entry_path = Path(entry_path)
    if not entry_path.exists():
        report.fail(f'case 卡不存在：{entry_path}')
        return None

    text = entry_path.read_text(encoding='utf-8')
    meta, body, err = split_front_matter(text)
    if err:
        report.fail(err)
        return None

    # 1. 必填字段
    missing = [k for k in REQUIRED_ENTRY_FIELDS if k not in meta or meta[k] in (None, '')]
    if missing:
        report.fail(f'front-matter 缺必填字段：{", ".join(missing)}')
        return None
    report.ok('front-matter 必填字段齐全')

    # 2. 枚举
    enum_checks = [
        ('source_platform', 'platform'),
        ('hook_type', 'hook_type'),
        ('emotion_arc', 'emotion_arc'),
        ('cta_type', 'cta_type'),
        ('golden_line_position', 'golden_line_position'),
    ]
    bad = []
    for field, vocab_key in enum_checks:
        allowed = vocab.get(vocab_key) or []
        if meta[field] not in allowed:
            bad.append(f'{field}={meta[field]!r} 不在受控词表 {vocab_key} 里（可选：{"/".join(map(str, allowed))}）')
    if bad:
        for b in bad:
            report.fail(b)
    else:
        report.ok('枚举字段全部命中受控词表')

    # 3. 原料
    raw_rel = str(meta['source_raw'])
    raw_path = (root / raw_rel).resolve()
    if not raw_path.exists():
        report.fail(f'原料不存在：{raw_rel}（先落 kb-inbox/raw/，再写 case 卡）')
        return None
    raw_meta, raw_body, raw_err = split_front_matter(raw_path.read_text(encoding='utf-8'))
    if raw_err:
        report.fail(f'原料 front-matter 有问题：{raw_err}')
        return None
    raw_missing = [k for k in REQUIRED_RAW_FIELDS if k not in raw_meta]
    if raw_missing:
        report.fail(f'原料缺登记字段：{", ".join(raw_missing)}')
    else:
        mismatched = [k for k in REQUIRED_RAW_FIELDS if str(meta.get(k)) != str(raw_meta.get(k))]
        if mismatched:
            report.fail(f'case 卡与原料登记不一致：{", ".join(mismatched)}（禁改原料登记，照抄原料值）')
        else:
            report.ok('原料存在且登记信息一致')

    raw_text, raw_comments = parse_raw_body(raw_body)

    # 4. 禁改：逐字摘录
    quotes = extract_quotes(body)
    vocab_fidelity = vocab.get('fidelity') or {}
    min_quotes = int(vocab_fidelity.get('min_quotes', 2))
    if len(quotes) < min_quotes:
        report.fail(f'逐字摘录不足：{len(quotes)} 条 < 门槛 {min_quotes} 条（钩子与金句都必须摘原句）')
    else:
        haystack = norm(raw_text + '\n' + raw_comments)
        bad_quotes = []
        for q in quotes:
            if any(tok in q for tok in ELLIPSIS):
                bad_quotes.append(f'「{q}」用了省略号——禁改原则不允许跨句拼接')
                continue
            if not q or norm(q) not in haystack:
                bad_quotes.append(f'「{q}」在原料里找不到逐字对应（不许改写/补字/改标点）')
        if bad_quotes:
            for b in bad_quotes:
                report.fail(b)
        else:
            report.ok(f'逐字摘录 {len(quotes)} 条全部在原料中命中（禁改通过）')

    # 5. 小节
    sections = heading_sections(body)
    missing_sections, empty_sections = [], []
    for name in vocab.get('required_sections') or []:
        content = find_section(sections, name)
        if content is None:
            missing_sections.append(name)
        elif not content.strip():
            empty_sections.append(name)
    if missing_sections:
        report.fail(f'缺必填小节：{"、".join(missing_sections)}')
    if empty_sections:
        report.fail(f'必填小节为空：{"、".join(empty_sections)}')
    if not missing_sections and not empty_sections:
        report.ok('必填小节齐全且非空')

    top3 = find_section(sections, '评论区热门梗') or ''
    items = [l for l in top3.splitlines() if l.strip().startswith(('1.', '2.', '3.'))]
    if len(items) < 3:
        report.fail(f'评论区热门梗不足 3 条（当前 {len(items)} 条）')
    else:
        report.ok('评论区热门梗 Top3 已填')

    # 6. 结构指标
    metric_section = find_section(sections, '结构标记') or ''
    computed = metrics_of(raw_text)
    pairs = [
        ('平均句长（字）', 'avg_sentence', 1.0, f"{computed['avg_sentence']}"),
        ('emoji 密度（个/百字）', 'emoji_per_100', 0.5, f"{computed['emoji_per_100']}"),
        ('分段数', 'paragraphs', 0, f"{computed['paragraphs']}"),
    ]
    metric_bad = []
    for label, key, tol, expect in pairs:
        got = parse_metric_line(metric_section, label)
        if got is None:
            metric_bad.append(f'{label} 没填数字')
            continue
        if abs(got - computed[key]) > tol:
            metric_bad.append(f'{label} 填了 {got:g}，按原料重算是 {expect}')
    if metric_bad:
        for b in metric_bad:
            report.fail(b)
    else:
        report.ok(f'结构指标与原料一致（句长 {computed["avg_sentence"]} 字 / emoji {computed["emoji_per_100"]}/百字 / {computed["paragraphs"]} 段）')

    # 7. 梗引用
    meme_refs = meta.get('meme_refs') or []
    if meme_refs:
        bank = load_meme_bank(root)
        if bank is None:
            report.fail('引用了梗但找不到 org/skills/meme-bank.md')
        else:
            unknown = [m for m in meme_refs if str(m).strip('`') not in bank]
            grey = [m for m in meme_refs if str(m).strip('`') in bank and '⚪' in bank[str(m).strip('`')]]
            if unknown:
                report.fail(f'meme_refs 里的梗不在梗库：{"、".join(map(str, unknown))}')
            if grey:
                report.fail(f'meme_refs 用了已标灰（过期）的梗：{"、".join(map(str, grey))}')
            if not unknown and not grey:
                report.ok('meme_refs 全部在梗库且未过期')
    else:
        report.ok('未引用梗（允许）')

    return computed


def default_root():
    return Path(__file__).resolve().parents[2]


def load_vocab(root):
    path = root / 'kb-inbox' / 'vocabulary.yml'
    if not path.exists():
        print(f'ERROR: 找不到受控词表 {path}')
        sys.exit(2)
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def self_test(root, vocab):
    samples = root / 'kb-inbox' / 'samples'
    good = samples / 'entry-sample-good.md'
    bad = samples / 'entry-sample-bad.md'
    if not good.exists() or not bad.exists():
        print(f'ERROR: 自测样例缺失（{samples}）')
        return 2
    print(f'[self-test] 合规样例：{good.relative_to(root)}')
    rep = Report()
    check_entry(good, root, vocab, rep)
    if rep.failures:
        print(f'[self-test] 失败：合规样例应通过，却报 {len(rep.failures)} 项问题')
        return 1
    print('[self-test] 合规样例通过 [OK]')
    print(f'[self-test] 违规样例：{bad.relative_to(root)}（应被拦截）')
    rep2 = Report()
    check_entry(bad, root, vocab, rep2)
    if len(rep2.failures) < 3:
        print(f'[self-test] 失败：违规样例只报 {len(rep2.failures)} 项，门禁不够敏感')
        return 1
    print(f'[self-test] 违规样例被拦截（{len(rep2.failures)} 项问题）[OK]')
    print('[self-test] 全部通过')
    return 0


def main(argv):
    root = default_root()
    args = [a for a in argv[1:] if not a.startswith('--')]
    if '--root' in argv:
        idx = argv.index('--root')
        if idx + 1 >= len(argv):
            print(__doc__)
            return 2
        root = Path(argv[idx + 1]).resolve()
    vocab = load_vocab(root)
    if '--self-test' in argv:
        return self_test(root, vocab)
    if len(args) != 1:
        print(__doc__)
        return 2
    entry = Path(args[0])
    if not entry.is_absolute():
        entry = (Path.cwd() / entry).resolve()
    print(f'kb-check: {entry}')
    rep = Report()
    check_entry(entry, root, vocab, rep)
    print()
    if rep.failures:
        print(f'结论：不过（{len(rep.failures)} 项问题，{rep.passes} 项通过）')
        print('修复后重跑本命令，把输出原样贴进 PR 描述；没过门禁 = 不算交付。')
        return 1
    print(f'结论：全部通过（{rep.passes} 项）')
    print('硬指标层已过；品味层（网感 rubric）仍由人工评分。')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))