"""Re-run the section-dependent notebooks twice: verbatim, and with the shared $I section function.

The notebook's own range-based mapper (`classify_folio` / `folio_to_section`) is replaced by a
one-line wrapper around sections.section_of, and literal `SECTIONS = [...]` lists by SECTIONS_I;
nothing else changes. Notebooks run in work/ (copies of corpus/ and resultados/), never in the
public repo.

Usage: python rerun_sections.py [41 43 76 77]   -> out/<nb>_{orig,I}.ipynb
"""
import ast
import shutil
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

HERE = Path(__file__).parent
REPO = Path(__file__).resolve().parents[2]
WORK, OUT = HERE / 'work', HERE / 'out'
NOTEBOOKS = {'41': '41_structural_decoding.ipynb', '43': '43_intra_folio_analysis.ipynb',
             '76': '76_role_grammar_and_sections.ipynb', '77': '77_minimal_dictionary.ipynb'}
MAPPERS = ('classify_folio', 'folio_to_section')
HEADER = f"import sys; sys.path.insert(0, {str(HERE)!r})\nfrom sections import section_of as _section_of, SECTIONS_I\n"


def patch_source(src):
    """Swap mapper defs and literal SECTIONS lists; returns (new_src, n_changes)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src, 0
    lines = src.splitlines(keepends=True)
    edits = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in MAPPERS:
            arg = node.args.args[0].arg
            edits.append((node, f"def {node.name}({arg}):\n    return _section_of({arg})  # R1: STA1 $I\n"))
        elif (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SECTIONS' for t in node.targets)
              and isinstance(node.value, ast.List)):
            edits.append((node, "SECTIONS = list(SECTIONS_I)  # R1: STA1 $I\n"))
        elif (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Name) and node.targets[0].id.endswith('colors')
              and any(isinstance(k, ast.Constant) and k.value == 'herbal' for k in node.value.keys)):
            name = node.targets[0].id  # plotting palette only: add a colour for the new section
            edits.append((node, ast.get_source_segment(src, node) + f"\n{name}.setdefault('cosmo', '#607D8B')\n"))
    for node, new in sorted(edits, key=lambda e: -e[0].lineno):
        start = node.lineno - 1 - len(getattr(node, 'decorator_list', []))
        lines[start:node.end_lineno] = [new]
    return ''.join(lines), len(edits)


def prepare_work():
    if not WORK.exists():
        WORK.mkdir()
        shutil.copytree(REPO / 'corpus', WORK / 'corpus')
        shutil.copytree(REPO / 'resultados', WORK / 'resultados')
        (WORK / 'images').mkdir()
        for f in REPO.glob('*.json'):
            shutil.copy(f, WORK)


def run(key, variant):
    nb = nbformat.read(REPO / NOTEBOOKS[key], as_version=4)
    n = 0
    if variant == 'I':
        for c in nb.cells:
            if c.cell_type == 'code':
                c.source, k = patch_source(c.source)
                n += k
        nb.cells.insert(0, nbformat.v4.new_code_cell(HEADER))
    for c in nb.cells:
        if c.cell_type == 'code':
            c.outputs, c.execution_count = [], None
    NotebookClient(nb, timeout=3600, kernel_name='python3', allow_errors=True,
                   resources={'metadata': {'path': str(WORK)}}).execute()
    out = OUT / f'{NOTEBOOKS[key][:-6]}_{variant}.ipynb'
    nbformat.write(nb, out)
    errs = [o for c in nb.cells if c.cell_type == 'code' for o in c.outputs if o.output_type == 'error']
    print(f'{key} {variant}: {n} patches, {len(errs)} errors -> {out.name}', flush=True)
    for e in errs[:3]:
        print(f"   {e['ename']}: {e['evalue'][:200]}")


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    prepare_work()
    for key in sys.argv[1:] or NOTEBOOKS:
        for variant in (('I',) if (OUT / f'{NOTEBOOKS[key][:-6]}_orig.ipynb').exists() else ('orig', 'I')):
            run(key, variant)
