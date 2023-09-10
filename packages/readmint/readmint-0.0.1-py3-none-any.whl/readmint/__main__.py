# SPDX-FileCopyrightText: 2023-present Alvaro Leiva Geisse <aleivag@gmail.com>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == "__main__":
    from readmint.cli import readmint

    sys.exit(readmint(standalone=False))
