# clamming.src.claminfo.py
#
# This file is part of Clamming tool.
# (C) 2023 Brigitte Bigi, Laboratoire Parole et Langage,
# Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Public License, version 3.
#
# Clamming is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Clamming is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Clamming. If not, see <http://www.gnu.org/licenses/>.
#
# This banner notice must not be removed.
# ---------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass

# -----------------------------------------------------------------------


@dataclass
class ClamInfo:
    """The information extracted for a function in the documented class.

    Public members are:

    - name (str)
    - args (list of str)
    - source (str)
    - docstring (str or None)

    """
    name: str
    args: list[str]
    source: str
    docstring: str | None
