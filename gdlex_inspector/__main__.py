"""Allow running gdlex_inspector as a module: python -m gdlex_inspector"""

import sys
from .cli import main

sys.exit(main())
