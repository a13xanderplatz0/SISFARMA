from pathlib import Path

for fname in ['app.py', 'src/views/templates/ventas.html']:
    p = Path(fname)
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    dups = []
    for size in (5, 10):
        seen = {}
        for i in range(len(lines) - size + 1):
            block = '\n'.join(lines[i:i+size]).strip()
            if block in seen:
                seen[block].append(i)
            else:
                seen[block] = [i]
        for block, idxs in seen.items():
            if len(idxs) > 1:
                dups.append((size, len(idxs), idxs[:5], block.splitlines()[0] if block else ''))

    print('FILE', fname)
    if not dups:
        print('  no exact duplicated blocks found')
    else:
        for size, count, idxs, head in sorted(dups, key=lambda x:(x[0], -x[1]))[:20]:
            print(f'  size={size} count={count} idxs={idxs} head="{head}"')
