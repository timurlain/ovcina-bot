#!/usr/bin/env python3
"""
Gamebook graph parser and structural analyzer.

Usage:
    python parse_gamebook.py <input_file> [--output <output_dir>]

Parses a gamebook manuscript (plain text or markdown) into a directed graph,
then runs structural checks: reachability, dead ends, broken references,
loops, and bottleneck analysis.

Expected input format:
    Paragraphs are numbered sections, e.g.:
        ## §1  /  ## 1  /  **§1**  /  1.
    References use Czech navigation formulas:
        "Otoč na odstavec 42"  /  "Pokračuj na 15"  /  "Jdi na §7"

Output:
    - graph.json: adjacency list with edge labels
    - analysis.json: structural issues found
    - map.mermaid: Mermaid diagram of the structure
"""

import re
import json
import sys
import os
from collections import defaultdict, deque
from pathlib import Path


def parse_paragraphs(text: str) -> dict[int, str]:
    """Extract numbered paragraphs from gamebook text."""
    # Match common paragraph heading patterns
    pattern = r'(?:^|\n)(?:##?\s*)?(?:§|\*\*§?)?\s*(\d+)\s*[.\):\-—]?\s*\*?\*?\s*\n'
    splits = list(re.finditer(pattern, text))

    paragraphs = {}
    for i, match in enumerate(splits):
        num = int(match.group(1))
        start = match.end()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        paragraphs[num] = text[start:end].strip()

    return paragraphs


def extract_references(text: str) -> list[tuple[int, str]]:
    """Extract paragraph references and their context from text."""
    refs = []
    # Czech navigation patterns
    patterns = [
        r'[Oo]toč\s+na\s+(?:odstavec\s+)?(\d+)',
        r'[Pp]okračuj\s+na\s+(?:odstavec\s+)?(\d+)',
        r'[Pp]řejdi\s+na\s+(?:odstavec\s+)?(\d+)',
        r'[Jj]di\s+na\s+(?:odstavec\s+)?(\d+)',
        r'→\s*§?(\d+)',
        r'viz\s+(?:odstavec\s+)?§?(\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            num = int(match.group(1))
            # Get surrounding context for edge label
            start = max(0, match.start() - 60)
            context = text[start:match.start()].strip()
            # Trim to last sentence/clause
            for sep in ['.', '!', '?', '\n', '—']:
                idx = context.rfind(sep)
                if idx >= 0:
                    context = context[idx+1:].strip()
                    break
            refs.append((num, context[:80] if context else ""))

    return refs


def detect_endings(text: str) -> str | None:
    """Detect if a paragraph is an ending (victory or death)."""
    death_patterns = [
        r'[Zz]emřeš', r'[Uu]mír[áa]š', r'[Kk]onec\s+(?:tvé|tvého)',
        r'[Pp]rohráváš', r'[Ss]mrt', r'[Zz]ahyneš', r'[Kk]onec\s+hry',
        r'KONEC', r'[Pp]adáš\s+(?:mrtev|bez\s+života)',
    ]
    victory_patterns = [
        r'[Vv]ítězství', r'[Vv]yhrá(?:l|váš)', r'[Uu]spěl',
        r'[Zz]achránil', r'[Šš]ťastný\s+konec', r'VÍTĚZSTVÍ',
        r'[Dd]obrodružství\s+(?:končí|je\s+u\s+konce)',
    ]

    for p in death_patterns:
        if re.search(p, text):
            return 'death'
    for p in victory_patterns:
        if re.search(p, text):
            return 'victory'
    return None


def build_graph(paragraphs: dict[int, str]) -> dict:
    """Build directed graph from paragraphs."""
    graph = {
        'nodes': {},
        'edges': [],
        'all_nums': sorted(paragraphs.keys()),
    }

    for num, text in paragraphs.items():
        ending = detect_endings(text)
        refs = extract_references(text)

        graph['nodes'][num] = {
            'type': ending or 'normal',
            'has_outgoing': len(refs) > 0 or ending is not None,
            'ref_count': len(refs),
        }

        for target, label in refs:
            is_conditional = bool(re.search(
                r'[Pp]okud|[Jj]estliže|[Mm]áš-li|[Kk]dyž|≥|>=|[Vv]lastníš',
                label
            ))
            graph['edges'].append({
                'from': num,
                'to': target,
                'label': label,
                'conditional': is_conditional,
            })

    return graph


def analyze_structure(graph: dict) -> dict:
    """Run all structural checks on the graph."""
    nodes = graph['nodes']
    edges = graph['edges']
    all_nums = set(graph['all_nums'])

    # Build adjacency list
    adj = defaultdict(list)
    for e in edges:
        adj[e['from']].append(e['to'])

    issues = {
        'orphaned': [],
        'dead_ends': [],
        'broken_refs': [],
        'loops': [],
        'bottlenecks': [],
        'no_win_path': False,
    }

    # 1. Reachability from §1
    if 1 not in all_nums:
        issues['orphaned'] = list(all_nums)
        return issues

    visited = set()
    queue = deque([1])
    visited.add(1)
    while queue:
        current = queue.popleft()
        for target in adj.get(current, []):
            if target in all_nums and target not in visited:
                visited.add(target)
                queue.append(target)

    issues['orphaned'] = sorted(all_nums - visited)

    # 2. Dead ends (no outgoing, not an ending)
    for num in all_nums:
        node = nodes.get(num, {})
        if not adj.get(num) and node.get('type') == 'normal':
            issues['dead_ends'].append(num)

    # 3. Broken references
    all_targets = {e['to'] for e in edges}
    issues['broken_refs'] = sorted(all_targets - all_nums)

    # 4. Simple cycle detection (find strongly connected components > 1 node)
    # Check if any SCC has no exit
    # Using iterative Tarjan's
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in adj.get(v, []):
            if w not in all_nums:
                continue
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], index[w])

        if lowlinks[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:
                sccs.append(sorted(scc))

    # Increase recursion limit for large gamebooks
    sys.setrecursionlimit(10000)
    for n in sorted(all_nums):
        if n not in index:
            strongconnect(n)

    # Check each SCC for exit edges
    for scc in sccs:
        scc_set = set(scc)
        has_exit = any(
            t not in scc_set
            for n in scc
            for t in adj.get(n, [])
            if t in all_nums
        )
        if not has_exit:
            issues['loops'].append({
                'paragraphs': scc,
                'has_exit': False,
                'note': 'Smyčka bez východu'
            })
        else:
            issues['loops'].append({
                'paragraphs': scc,
                'has_exit': True,
                'note': 'Smyčka s východem (pravděpodobně OK)'
            })

    # 5. Win path existence
    victory_nodes = {n for n, info in nodes.items() if info.get('type') == 'victory'}
    if not victory_nodes:
        issues['no_win_path'] = True
    else:
        # Check if any victory node is reachable
        issues['no_win_path'] = not bool(victory_nodes & visited)

    # 6. Bottleneck detection — find articulation points
    # (nodes whose removal disconnects start from any ending)
    endings = {n for n, info in nodes.items() if info.get('type') in ('victory', 'death')}
    reachable_endings = endings & visited

    if reachable_endings and len(visited) > 2:
        for candidate in visited - {1} - reachable_endings:
            # Remove candidate and check if all endings still reachable
            test_visited = set()
            q = deque([1])
            test_visited.add(1)
            while q:
                c = q.popleft()
                for t in adj.get(c, []):
                    if t != candidate and t in all_nums and t not in test_visited:
                        test_visited.add(t)
                        q.append(t)

            lost_endings = reachable_endings - test_visited
            if lost_endings:
                issues['bottlenecks'].append({
                    'paragraph': candidate,
                    'blocks_access_to': sorted(lost_endings),
                })

    return issues


def generate_mermaid(graph: dict, issues: dict) -> str:
    """Generate Mermaid diagram from graph."""
    lines = ['graph TD']
    nodes = graph['nodes']

    for num in sorted(graph['all_nums']):
        info = nodes.get(num, {})
        if info.get('type') == 'victory':
            lines.append(f'    {num}[[§{num} — VÍTĚZSTVÍ]]')
        elif info.get('type') == 'death':
            lines.append(f'    {num}((§{num} — SMRT))')
        elif num in issues.get('orphaned', []):
            lines.append(f'    {num}[§{num} ❌ osiřelý]')
        else:
            lines.append(f'    {num}[§{num}]')

    for edge in graph['edges']:
        src, tgt = edge['from'], edge['to']
        label = edge.get('label', '')
        # Truncate long labels
        if len(label) > 40:
            label = label[:37] + '...'
        # Escape quotes for Mermaid
        label = label.replace('"', "'")

        if edge.get('conditional'):
            if label:
                lines.append(f'    {src} -.-> |"{label}"| {tgt}')
            else:
                lines.append(f'    {src} -.-> {tgt}')
        else:
            if label:
                lines.append(f'    {src} --> |"{label}"| {tgt}')
            else:
                lines.append(f'    {src} --> {tgt}')

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_gamebook.py <input_file> [--output <output_dir>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = '.'
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Parsing {input_file}...")
    paragraphs = parse_paragraphs(text)
    print(f"Found {len(paragraphs)} paragraphs: §{min(paragraphs.keys(), default=0)}–§{max(paragraphs.keys(), default=0)}")

    graph = build_graph(paragraphs)
    print(f"Found {len(graph['edges'])} edges")

    issues = analyze_structure(graph)
    mermaid = generate_mermaid(graph, issues)

    # Save outputs
    with open(os.path.join(output_dir, 'graph.json'), 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, 'analysis.json'), 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, 'map.mermaid'), 'w', encoding='utf-8') as f:
        f.write(mermaid)

    # Print summary
    print(f"\n--- Structural Analysis ---")
    print(f"Orphaned paragraphs: {issues['orphaned'] or 'none'}")
    print(f"Dead ends: {issues['dead_ends'] or 'none'}")
    print(f"Broken references: {issues['broken_refs'] or 'none'}")
    print(f"Loops: {len(issues['loops'])} found ({sum(1 for l in issues['loops'] if not l['has_exit'])} without exit)")
    print(f"Bottlenecks: {len(issues['bottlenecks'])} found")
    print(f"Win path exists: {'no ❌' if issues['no_win_path'] else 'yes ✅'}")
    print(f"\nOutputs saved to {output_dir}/")


if __name__ == '__main__':
    main()
