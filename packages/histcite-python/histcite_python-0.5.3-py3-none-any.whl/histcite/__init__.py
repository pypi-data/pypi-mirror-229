"""
## What is histcite-python?
histcite-python is a Python package for parsing scientific papers' references and recognizing citation relathiship between them. 

It's originated from the [HistCite project](https://support.clarivate.com/ScientificandAcademicResearch/s/article/HistCite-No-longer-in-active-development-or-officially-supported),
which is no longer maintained by `Clarivate` for some years. 
With pandas 2.0 and Graphviz, `histcite-python` implements the core functions of HistCite and extends some new features.

- Supported OS system
    - `Windows`, `Linux` and `macOS`
- Supported abstract database
    - `Web of Science`, `Scopus` and `CSSCI`

histcite-python is an open source project under MIT license, you can find the source code on [GitHub](https://github.com/doublessay/histcite-python).
If you have any questions or suggestions, please submit issues on GitHub. 
"""

__version__ = "0.5.3"

from .compute_metrics import ComputeMetrics
from .network_graph import GraphViz
from .parse_reference import ParseReference
from .process_file import ProcessFile
from .read_file import ReadFile
from .recognize_reference import RecognizeReference

__all__ = [
    "ComputeMetrics",
    "GraphViz",
    "ParseReference",
    "ProcessFile",
    "ReadFile",
    "RecognizeReference",
]
