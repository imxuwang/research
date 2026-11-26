#!/usr/bin/env python3
"""Master builder for the entire 9-page Retirement Spending interactive static suite."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_ch2 import build_ch2
from build_ch3 import build_ch3
from build_ch4 import build_ch4
from build_ch5a import build_ch5a
from build_ch5b import build_ch5b
from build_ch6 import build_ch6
from build_ch7 import build_ch7
from build_ch8_9 import build_ch8_9
from build_hub import build_hub


def main():
    build_hub()
    build_ch2()
    build_ch3()
    build_ch4()
    build_ch5a()
    build_ch5b()
    build_ch6()
    build_ch7()
    build_ch8_9()
    print("Successfully built all 9 self-contained HTML pages under docs/retirement-spending/.")


if __name__ == "__main__":
    main()
