#!/usr/bin/env python3
"""
AI 文风痕迹检测工具

检测中文小说叙述文本中的 AI 典型写作痕迹。所有规则仅检查非对话叙述部分。

使用方式：
    python tools/ai_pattern_checker.py <正文文件路径> [--json] [--fix]

    --json    以 JSON 格式输出结果
    --fix     输出修复建议

退出码：
    0 — 全部通过
    1 — 存在 AI 痕迹
    2 — 文件错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ── 规则定义 ──────────────────────────────────────────────────────────

# 叙述中破折号最大允许次数
EM_DASH_MAX = 1

# 负面排比：3+ 个并列否定短语
NEG_PARALLEL_RE = re.compile(
    r'(?:不|没有|不再|不会|无法)[^，。！？]{1,8}，'
    r'(?:不|没有|不再|不会|无法)[^，。！？]{1,8}，'
    r'(?:不|没有|不再|不会|无法)'
)

# 纠偏句式
CORRECTIVE_PATTERNS = [
    (re.compile(r'不是[^，。]{1,30}而是'), '不是…而是…'),
    (re.compile(r'并非[^，。]{1,30}(?:只是|而是)'), '并非…只是/而是…'),
    (re.compile(r'与其说[^，。]{1,30}不如说'), '与其说…不如说…'),
    (re.compile(r'不在于[^，。]{1,30}而在于'), '不在于…而在于…'),
    (re.compile(r'恰恰相反'), '恰恰相反'),
    (re.compile(r'相反，'), '相反，'),
]

# 虚假升华
FALSE_ELEVATION_KEYWORDS = ['象征着', '昭示着', '映照出', '命运转折', '时代缩影', '格局改写']
FALSE_ELEVATION_PATTERNS = [
    (re.compile(r'这不仅是[^，。]{1,30}更是'), '这不仅是…更是…'),
]

# 交流残留
COMMUNICATION_RESIDUE_KEYWORDS = [
    '让我们看看',
    '下面来看看',
    '这里可以看出',
    '如果你愿意',
    '值得注意的是',
    '需要指出的是',
]

# 形容词+冒号
ADJ_COLON_RE = re.compile(r'(?:的是|之处|之处在于|很简单|很明确|很清晰)：')

# 段首过渡词
PARAGRAPH_START_WORDS = [
    '最终',
    '总之',
    '综上所述',
    '由此可见',
    '显而易见',
]

# 否定词开头的句子（在 。！？ 或行首之后）
NEGATION_SENTENCE_RE = re.compile(r'(?:^|[。！？\n])(\s*(?:没有|不是|不会|不能|不再|并非|从未))')

# 中文小说高频 AI 腔禁用词与模板动作（Rule 9）
AI_FICTION_CLICHE_PATTERNS = [
    (re.compile(r'攥'), '高频AI动词「攥」'),
    (re.compile(r'眼眸|眸子|眸光|眸色|垂眸|抬眸|凝眸'), '高频AI词「眼眸/眸」'),
    (re.compile(r'(?:声音|语气|嗓音)很轻|轻声(?:开口|道|说|问|笑)|声音轻得'), '高频AI语态「声音很轻/轻声」'),
    (re.compile(r'(?:唇角|唇边|嘴角)[^，。！？]{0,14}(?:弧度|上扬|微扬|勾起|弯起|抽搐)'), '高频AI微表情「唇角/嘴角弧度」'),
    (re.compile(r'近乎'), '高频AI修饰「近乎」'),
    (re.compile(r'(?:背脊|脊背)发(?:凉|寒|僵)|毛骨悚然'), '高频AI情绪词「背脊发凉」'),
    (re.compile(r'(?:掠过|闪过|划过)一(?:丝|瞬|抹)'), '高频AI眼神特效「掠过/闪过一丝/一瞬」'),
    (re.compile(r'一眨不眨|锁在[^，。！？]{0,8}脸上'), '高频AI凝视套话'),
    (re.compile(r'指节泛白|喉结(?:滚动|微动)|瞳孔(?:骤缩|一缩|微缩)'), '高频AI身体模板'),
    (re.compile(r'肉眼可见地|微微(?:偏头|抬起|挑眉|眯起|一顿|一滞)'), '高频AI动作修饰'),
    (re.compile(r'微不可察|不知何时|空气(?:里|中)弥漫|毫不留情地宣告|死寂|腥甜|深吸一口气|低笑一声|嗤笑一声'), '高频AI叙述套词'),
]

# 高频弱修饰词单章上限（Rule 10）
WEAK_MODIFIER_RE = re.compile(r'半分|半点|一丝|一抹')
WEAK_MODIFIER_MAX = 2

# 日轻防串味：中式古装/武侠/明清市井禁用词（Rule 11，全文含对话一并检查）
WUXIA_ARCHAIC_RE = re.compile(
    r'时辰|半刻钟|一炷香|[一二三四五六七八九十百半两数几]息|'
    r'[一二三四五六七八九十两半数几]丈|[一二三四五六七八九十两半数几]尺|'
    r'客栈|掌柜|店小二|二老爷|老爵爷|大老爷|官道|驿馆|茅厕|'
    r'泼皮|盘缠|行头|银两|碎银|护驾|候驾|用膳|罪该万死|血债血偿|'
    r'留具全尸|留个全尸|手刀|寸劲|丹田|内力|斗气|仁至义尽|事了拂衣去|打抱不平|江湖'
)


# ── 核心函数 ──────────────────────────────────────────────────────────

def strip_dialogue(text: str) -> str:
    """移除对话内容，只保留叙述文本。"""
    return re.sub(r'[""「][^""」]+[""」]', '', text)


def _context(text: str, pos: int, width: int = 20) -> str:
    """截取 pos 位置前后各 width 个字符作为上下文。"""
    start = max(0, pos - width)
    end = min(len(text), pos + width)
    snippet = text[start:end]
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet = snippet + '...'
    return snippet


def check(text: str, threshold_config: Optional[dict] = None) -> list[dict]:
    """
    运行全部 AI 痕迹检查，返回违规列表。

    每条违规: {"rule": 规则名, "count": 违规次数, "items": [{"position": int, "context": str}]}
    无违规则返回空列表。
    """
    violations = []
    narrative = strip_dialogue(text)

    # 1. 破折号
    em_dashes = list(re.finditer(r'——', narrative))
    if len(em_dashes) > EM_DASH_MAX:
        items = []
        for m in em_dashes:
            items.append({'position': m.start(), 'context': _context(narrative, m.start())})
        violations.append({
            'rule': '破折号',
            'count': len(em_dashes),
            'items': items,
        })

    # 2. 负面排比
    neg_matches = list(NEG_PARALLEL_RE.finditer(narrative))
    if neg_matches:
        items = []
        for m in neg_matches:
            items.append({'position': m.start(), 'context': _context(narrative, m.start())})
        violations.append({
            'rule': '负面排比',
            'count': len(neg_matches),
            'items': items,
        })

    # 3. 纠偏句式
    corrective_items = []
    for pat, label in CORRECTIVE_PATTERNS:
        for m in pat.finditer(narrative):
            corrective_items.append({
                'position': m.start(),
                'context': _context(narrative, m.start()) + f'  [{label}]',
            })
    if corrective_items:
        violations.append({
            'rule': '纠偏句式',
            'count': len(corrective_items),
            'items': corrective_items,
        })

    # 4. 虚假升华
    elevation_items = []
    for kw in FALSE_ELEVATION_KEYWORDS:
        for m in re.finditer(re.escape(kw), narrative):
            elevation_items.append({
                'position': m.start(),
                'context': _context(narrative, m.start()) + f'  [{kw}]',
            })
    for pat, label in FALSE_ELEVATION_PATTERNS:
        for m in pat.finditer(narrative):
            elevation_items.append({
                'position': m.start(),
                'context': _context(narrative, m.start()) + f'  [{label}]',
            })
    if elevation_items:
        violations.append({
            'rule': '虚假升华',
            'count': len(elevation_items),
            'items': elevation_items,
        })

    # 5. 交流残留
    residue_items = []
    for kw in COMMUNICATION_RESIDUE_KEYWORDS:
        for m in re.finditer(re.escape(kw), narrative):
            residue_items.append({
                'position': m.start(),
                'context': _context(narrative, m.start()),
            })
    if residue_items:
        violations.append({
            'rule': '交流残留',
            'count': len(residue_items),
            'items': residue_items,
        })

    # 6. 形容词+冒号
    adj_matches = list(ADJ_COLON_RE.finditer(narrative))
    if adj_matches:
        items = []
        for m in adj_matches:
            items.append({'position': m.start(), 'context': _context(narrative, m.start())})
        violations.append({
            'rule': '形容词+冒号',
            'count': len(adj_matches),
            'items': items,
        })

    # 7. 段首过渡词
    paragraphs = re.split(r'\n\n+', text)
    para_items = []
    for para in paragraphs:
        stripped = para.lstrip()
        if not stripped:
            continue
        for word in PARAGRAPH_START_WORDS:
            if stripped.startswith(word):
                para_items.append({
                    'position': text.find(para),
                    'context': stripped[:40],
                })
                break
    if para_items:
        violations.append({
            'rule': '段首过渡词',
            'count': len(para_items),
            'items': para_items,
        })

    # 8. 否定词开头的句子
    neg_sent_matches = list(NEGATION_SENTENCE_RE.finditer(narrative))
    if neg_sent_matches:
        items = []
        for m in neg_sent_matches:
            items.append({'position': m.start(), 'context': _context(narrative, m.start())})
        violations.append({
            'rule': '否定词开头',
            'count': len(neg_sent_matches),
            'items': items,
        })

    # 9. 中文小说高频 AI 腔禁用词与模板动作
    cliche_items = []
    for pat, label in AI_FICTION_CLICHE_PATTERNS:
        for m in pat.finditer(narrative):
            cliche_items.append({
                'position': m.start(),
                'context': _context(narrative, m.start()) + f'  [{label}]',
            })
    if cliche_items:
        violations.append({
            'rule': '小说高频AI腔',
            'count': len(cliche_items),
            'items': cliche_items,
        })

    # 10. 高频弱修饰词密度（半分/半点/一丝/一抹）
    weak_matches = list(WEAK_MODIFIER_RE.finditer(narrative))
    if len(weak_matches) > WEAK_MODIFIER_MAX:
        items = []
        for m in weak_matches:
            items.append({'position': m.start(), 'context': _context(narrative, m.start())})
        violations.append({
            'rule': f'弱修饰词过密(>{WEAK_MODIFIER_MAX})',
            'count': len(weak_matches),
            'items': items,
        })

    # 11. 日式轻小说防串味检查（全文含对话禁中式古装/武侠词）
    wuxia_matches = list(WUXIA_ARCHAIC_RE.finditer(text))
    if wuxia_matches:
        items = []
        for m in wuxia_matches:
            items.append({
                'position': m.start(),
                'context': _context(text, m.start()) + f'  [{m.group(0)}]',
            })
        violations.append({
            'rule': '中式古装/武侠串味词',
            'count': len(wuxia_matches),
            'items': items,
        })

    return violations


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='AI 文风痕迹检测工具')
    parser.add_argument('file', help='正文文件路径')
    parser.add_argument('--json', action='store_true', dest='json_output',
                        help='以 JSON 格式输出结果')
    parser.add_argument('--fix', action='store_true',
                        help='输出修复建议')
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f'文件不存在: {path}', file=sys.stderr)
        sys.exit(2)

    try:
        text = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f'读取文件失败: {e}', file=sys.stderr)
        sys.exit(2)

    violations = check(text)

    if args.json_output:
        result = {
            'passed': len(violations) == 0,
            'violations': violations,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not violations:
            print('✓ AI 文风痕迹检测通过')
            sys.exit(0)

        total = sum(v['count'] for v in violations)
        print(f'✗ 发现 {total} 处 AI 文风痕迹（{len(violations)} 条规则）:')
        for v in violations:
            print(f'\n  【{v["rule"]}】 ×{v["count"]}')
            for item in v['items']:
                print(f'      位置 {item["position"]}: {item["context"]}')

    if args.fix:
        print('\n修复建议: 针对每项违规，联系前后句整句重写，不做局部换词。')

    sys.exit(0 if not violations else 1)


if __name__ == '__main__':
    main()
