import sys
from pathlib import Path
import fitz
root = Path(__file__).parent
doc = fitz.open(root.parent / 'Source PDFs' / sys.argv[1])
for page in map(int, sys.argv[2:]):
    dest = root / ('batch1_' + Path(sys.argv[1]).stem + '_p' + str(page) + '.png')
    doc[page-1].get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(dest)
    print(dest)
