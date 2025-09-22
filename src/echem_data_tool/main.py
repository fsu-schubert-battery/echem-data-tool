# Copyright (C) 2025 Friedrich-Schiller-Universität Jena, HIPOLE Jena
# Authors: Christian Stolze, Sebastian Witt, Felix Nagler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Main module for echem-data-tool
"""

from pycodata import constants_2022 as pc

def main():
    """Main entry point for the application."""
    print("Echem Data Tool - Data evaluation tool for electrochemical experiments")
    print("Version: 0.1.0")

    # output important constants using pycodata (CODATA 2022 - latest)
    print(f"Faraday constant (F): {pc.FARADAY_CONSTANT['value']} {pc.FARADAY_CONSTANT['unit']}")
    print(f"Gas constant (R): {pc.MOLAR_GAS_CONSTANT['value']} {pc.MOLAR_GAS_CONSTANT['unit']}")
    print(f"Avogadro constant (N_A): {pc.AVOGADRO_CONSTANT['value']} {pc.AVOGADRO_CONSTANT['unit']}")
    print(f"Elementary charge (e): {pc.ELEMENTARY_CHARGE['value']} {pc.ELEMENTARY_CHARGE['unit']}")

if __name__ == "__main__":
    main()
