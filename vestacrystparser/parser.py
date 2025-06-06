import logging
import math
from typing import Union, Iterator
import importlib.resources

import vestacrystparser.resources

logger = logging.getLogger(__name__)


def parse_token(token: str) -> Union[int, float, str]:
    """
    Convert a token to int or float if possible.
    Otherwise, return it as a string.
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def parse_line(line: str) -> list[Union[int, float, str]]:
    """
    Split a line into tokens and convert each token.
    Returns a list of tokens.
    """
    tokens = line.split()
    return [parse_token(tok) for tok in tokens]


def invert_matrix(mat: list[list[float]]) -> list[list[float]]:
    """Inverts a 3x3 matrix"""
    # Implementation using raw Python; importing numpy is overkill.
    # https://mathworld.wolfram.com/MatrixInverse.html
    assert len(mat) == 3, "mat must be 3x3"
    assert len(mat[0]) == 3, "mat must be 3x3"
    # Determinant of full matrix
    detfull = mat[0][0] * (mat[1][1]*mat[2][2] - mat[2][1]*mat[1][2]) \
        - mat[0][1] * (mat[1][0]*mat[2][2] - mat[1][2]*mat[2][0]) \
        + mat[0][2] * (mat[1][0]*mat[2][1] - mat[1][1]*mat[2][0])
    if detfull == 0:
        raise ValueError("Singular matrix")
    # Make determinants for each element.
    # Initialise
    inverse = [[None, None, None] for _ in range(3)]
    for i in range(3):
        # Grab the co-factor coordinates
        if i == 0:
            x1, x2 = 1, 2
        elif i == 1:
            x1, x2 = 2, 0
        else:
            x1, x2 = 0, 1
        for j in range(3):
            if j == 0:
                y1, y2 = 1, 2
            elif j == 1:
                y1, y2 = 2, 0
            else:
                y1, y2 = 0, 1
            # Each term is built from the co-factor, i.e. determinant of the
            # rest of the matrix.
            # But also, transpose the terms
            inverse[j][i] = (mat[x1][y1] * mat[x2][y2] -
                             mat[x1][y2] * mat[x2][y1]) / detfull
    return inverse


def load_elements_data(element: Union[int, str]) -> \
        list[int, str, float, float, float, int, int, int]:
    fn = importlib.resources.files(vestacrystparser.resources) / "elements.ini"
    with open(fn, 'r') as f:
        for line in f.readlines():
            tokens = parse_line(line)
            if tokens[0] == element or tokens[1] == element:
                # Convert float RGB to int RGB
                for i in [5, 6, 7]:
                    tokens[i] = int(tokens[i]*255)
                return tokens
    # For other elements, load the default.
    if element != 'XX':
        logger.info(f"Element {element} not in elements.ini. Using defaults.")
        try:
            tokens = load_elements_data('XX')
        except ValueError:
            # Return a more useful error message.
            raise ValueError(
                f"Element {element} not in elements.ini and unable to load \
                    default! (This shouldn't happen.)")
        # Change the atomic symbol to the one provided.
        if isinstance(element, str):
            tokens[1] = element
        return tokens
    else:
        # 'XX' is not in elements.ini. Break before we hit an infinite loop.
        # This shouldn't happen.
        raise ValueError("Unable to load default element from elements.ini.")


def load_default_bond_style(A1: str, A2: str, hbond: bool = False) \
      -> Union[list[int, str, str, float, float, int, int, int, int, int], None]:
    """
    Loads default bond style for a pair of elements (if present).

    hbond - if True, grab the hydrogen bond, if present.
    This is the second matching entry in style.ini

    returns: [index (ignore),
              A1,
              A2,
              minimum length,
              maximum length,
              search mode,
              boundary mode,
              show polyhedra,
              0 (search by label = False),
              normal (1) or H-bond (5)]

    May be None. Not every element pair has default bonds in style.ini.
    (N.B. If adding bonds manually, VESTA GUI defaults to 1.6.)
    """
    # Load style.ini file.
    fn = importlib.resources.files(vestacrystparser.resources) / "style.ini"
    first = True
    with open(fn, 'r') as f:
        # Find and parse the SBOND block.
        in_sbond = False
        for line in f.readlines():
            if not in_sbond:
                if line.strip() == "SBOND":
                    in_sbond = True
            else:
                if line.split() == ["0"]*4:
                    # End of SBOND section
                    # No match found.
                    return None
                # Parse line
                tokens = parse_line(line)
                if ((tokens[1] == A1 and tokens[2] == A2) or
                        (tokens[1] == A2 and tokens[2] == A1)):
                    # A1 and A2 are interchangeable.
                    # We've found our match.
                    if not hbond or (hbond and not first):
                        return tokens
                    else:
                        first = False
    # We shouldn't have gotten here.
    if in_sbond:
        raise RuntimeError("SBOND section in style.ini not properly terminated!"
                           "(Your installation's resources are broken.)")
    else:
        raise RuntimeError("SBOND section missing from style.ini!"
                           "(Your installation's resources are broken.)")


def load_default_bond_length(A1: str, A2: str) -> Union[float, None]:
    """
    Loads default maximum bond length for a pair of elements (if present).

    May be None. Not every element pair has default bonds in style.ini.
    (N.B. If adding bonds manually, VESTA GUI defaults to 1.6.)
    """
    tokens = load_default_bond_style(A1, A2)
    if tokens is None:
        return None
    else:
        return tokens[4]

# Sections that have a blank line after them.
# (So far, I've only found this to be important for IMPORT_DENSITY,
# but if I'm doing it for one I may as well do it for all.)
sections_with_blank_line = [
    "#VESTA_FORMAT_VERSION",
    "CRYSTAL",
    "TITLE",
    "IMPORT_DENSITY",
    "SECCL",
    "TEXCL",
]
sections_with_blank_line_before = [
    "CRYSTAL",
    "STYLE",
]
# We also need to take note of what sections are in specific phases
# and what sections are outside the phases.
sections_that_are_global = [
    "ATOMT",
    "SCENE",
    "HBOND",
    "STYLE",
    "DISPF",
    "MODEL",
    "SURFS",
    "SECTS",
    "FORMS",
    "ATOMS",
    "BONDS",
    "POLYS",
    "VECTS",
    "FORMP",
    "ATOMP",
    "BONDP",
    "POLYP",
    "ISURF",
    "TEX3P",
    "SECTP",
    "CONTR",
    "HKLPP",
    "UCOLP",
    "COMPS",
    "LABEL",
    "PROJT",
    "BKGRC",
    "DPTHQ",
    "LIGHT0",
    "LIGHT1",
    "LIGHT2",
    "LIGHT3",
    "SECCL",
    "TEXCL",
    "ATOMM",
    "BONDM",
    "POLYM",
    "SURFM",
    "FORMM",
    "HKLPM",
]


class VestaSection:
    def __init__(self, header_line):
        """
        Initialize a VESTA section from a header line.

        For the TITLE section:
          - Inline data is not preserved on the header, but moved to the
            multi-line data.
        For other sections:
          - If inline data is present on the header, it is stored (parsed) in
            self.inline.
          - Subsequent lines are stored in self.data.

        Args:
            header_line (str): The complete header line (with any inline data).
        """
        # Remove only the newline character.
        line = header_line.rstrip("\n")
        # Save the original header line (for potential formatting).
        self.raw_header = line

        # Use lstrip to parse the header and inline text.
        stripped = line.lstrip()
        tokens = stripped.split(maxsplit=1)
        self.header = tokens[0]  # e.g., TITLE, CELL, TRANM, etc.

        inline_text = tokens[1] if len(tokens) > 1 else ""
        # Tokenize inline data.
        self.inline = parse_line(inline_text) if inline_text else []
        self.data = []  # Extra lines will be stored here.

    def add_line(self, line):
        """
        Add a continuation line to the section.

        For TITLE, store the entire line as a string.
        For other sections, split the line into tokens and convert them.
        """
        if self.header == "TITLE":
            self.data.append([line])
        else:
            self.data.append(parse_line(line))

    def __str__(self) -> str:
        """
        Convert the section back to text.

          - If inline data exists, it is written on the header line.
          - Then, any extra lines are written one per line.
        """
        text = ""
        if self.header in sections_with_blank_line_before:
            text += "\n"
        if self.inline:
            inline_text = " ".join(str(x) for x in self.inline)
            text += f"{self.header} {inline_text}\n"
        else:
            text += f"{self.header}\n"
        for line in self.data:
            if self.header == "IMPORT_DENSITY":
                # IMPORT_DENSITY requires a *signed* float.
                text += "{:+.6f} {}\n".format(*line)
            else:
                text += " ".join(str(x) for x in line) + "\n"
        # Add a blank line if required.
        if self.header in sections_with_blank_line:
            text += "\n"
        return text

    def __len__(self) -> int:
        """Number of lines (besides the header line)"""
        return len(self.data)


class VestaPhase:
    """A collection of uniquely-named VestaSection's"""

    def __init__(self):
        self._sections = {}
        self._order = []

    def __getitem__(self, name: str) -> VestaSection:
        return self._sections[name]

    def __contains__(self, item: str) -> bool:
        return item in self._sections

    def append(self, section: VestaSection):
        header = section.header
        if header in self:
            raise KeyError(
                f"{header} is already in this VestaPhase! Cannot append.")
        else:
            # Intentionally not copying, as we want to update the
            # VestaSection as we construct it.
            self._sections[header] = section
            self._order.append(header)

    def __len__(self) -> int:
        return len(self._sections)

    def __iter__(self) -> Iterator[VestaSection]:
        for header in self._order:
            yield self._sections[header]

    @property
    def title(self) -> str:
        return self["TITLE"].data[0][0]

    @property
    def nsites(self) -> int:
        """Number of sites (read-only)"""
        return len(self["SITET"].data) - 1


class VestaFile:
    def __init__(self, filename: Union[str, None] = None):
        """
        Initialize a VESTA file instance.

        Attributes:
            sections (dict): Maps section headers to VestaSection objects.
            order (list): The order in which sections appear in the file.
        """
        self._phases = []
        self._globalsections = VestaPhase()
        self.current_phase = 0
        self._vesta_format_version = None
        if filename:
            self.load(filename)
        else:
            # Initialise the empty VESTA file.
            filename = importlib.resources.files(
                vestacrystparser.resources) / "default.vesta"
            self.load(filename)

    def load(self, filename):
        """
        Load and parse a VESTA file.

        Args:
            filename (str): Path to the VESTA file.
        """
        with open(filename, 'r') as f:
            lines = f.readlines()

        section = None
        for raw_line in lines:
            # Remove only the newline character.
            line = raw_line.rstrip("\n")
            if line == "":
                continue  # skip blank lines

            # Use lstrip() to test for a header token.
            stripped = line.lstrip()
            tokens = stripped.split(maxsplit=1)
            # If we are in the line immediately after TITLE, record it
            # The title might be uppercase, and that's allowed.
            if section is not None and section.header == "TITLE" \
                    and len(section.data) == 0:
                section.add_line(line)
            # Otherwise, an all-uppercase word is a section header.
            elif tokens and tokens[0].isupper():
                # New section.
                section = VestaSection(line)
                # Identify where we are to put this section.
                if section.header == "#VESTA_FORMAT_VERSION":
                    self._vesta_format_version = section
                elif section.header == "CRYSTAL":
                    # New phase.
                    self._phases.append(VestaPhase())
                    self._phases[-1].append(section)
                elif section.header in sections_that_are_global:
                    # This section belongs outside the phase information
                    self._globalsections.append(section)
                else:
                    # This section belongs in the currently active phase
                    self._phases[-1].append(section)
            else:
                # Continuation of the current section.
                if section is None:
                    # This shouldn't happen. We probably have malformed data.
                    raise ValueError(
                        "Data without section header found! Line:\n"+line)
                section.add_line(line)

    def __getitem__(self, name: Union[str, tuple[str, int]]) \
            -> VestaSection:
        """
        Gets the section with the given name, from the given or current phase

        self[name]
        self[name, phase]

        phase defaults to self.current_phase
        """
        # Parse a multi-argument call, because getitem is special.
        if isinstance(name, tuple):
            phase = name[1]
            name = name[0]
        else:
            phase = None
        # Read the requested name, look for where we should grab the section
        if name == "#VESTA_FORMAT_VERSION":
            return self._vesta_format_version
        elif name in sections_that_are_global:
            return self._globalsections[name]
        elif phase is None:
            return self._phases[self.current_phase][name]
        else:
            return self._phases[phase][name]

    def __contains__(self, name: Union[str, tuple[str, int]]) -> bool:
        """
        name
        (name, phase)

        phase defaults to self.current_phase
        """
        try:
            # Why copy the __getitem__ logic when I can just do this?
            self[name]
        except (KeyError, IndexError):
            return False
        else:
            return True

    def __len__(self) -> int:
        """Number of sections"""
        length = 0
        if self._vesta_format_version is not None:
            length += 1
        for phase in self._phases:
            length += len(phase)
        length += len(self._globalsections)
        return length

    def __iter__(self) -> Iterator[VestaSection]:
        """Iterate over the sections"""
        yield self._vesta_format_version
        for phase in self._phases:
            yield from phase
        yield from self._globalsections

    def save(self, filename):
        """
        Write the current VESTA data to disk.

        Args:
            filename (str): Output file path.
        """
        with open(filename, 'w') as f:
            f.write(str(self))

    def __str__(self) -> str:
        """Entire VestaFile as multi-line string"""
        mystr = ""
        for section in self:
            mystr += str(section)
        return mystr

    def set_current_phase(self, phase: int):
        """
        Sets the currently active phase by 0-based index.

        __getitem__ calls, along with all set and get functions, will default
        to this phase.

        Accepts negative indices in the Pythonic manner, but it is recorded as a
        positive index.
        """
        if not isinstance(phase, int):
            raise TypeError(f"phase must be an integer, not {type(phase)}.")
        if phase < 0:
            phase += len(self._phases)
        if phase < 0 or phase >= len(self._phases):
            raise IndexError(
                f"Index {phase} is out of range of a list of length {len(self._phases)}")
        self.current_phase = phase

    def __repr__(self) -> str:
        """
        Compact representation. Titles and number of sites of each phase.
        """
        mystr = "<VestaFile: "
        data = []
        for phase in self._phases:
            data.append(
                f"{phase.title} [{phase.nsites} site{'s' if phase.nsites == 0 else ''}]")
        return mystr + '; '.join(data) + ">"

    # Properties
    @property
    def title(self) -> str:
        """Title of the current phase (settable)"""
        return self["TITLE"].data[0][0]

    @title.setter
    def title(self, value):
        self.set_title(value)

    @property
    def nphases(self) -> int:
        """Number of phases (read-only)"""
        return len(self._phases)

    @property
    def nsites(self) -> int:
        """Number of sites in the current phase (read-only)"""
        return len(self["SITET"].data) - 1

    @property
    def nvectors(self) -> int:
        """Number of vector types in the current phase (read-only)"""
        return len(self["VECTT"].data) - 1

    # Methods for modifying the system.
    def set_site_color(self, index: Union[int, list[int]],
                       r: int, g: int, b: int):
        """
        Set the RGB site colour for sites with index (1-based).
        Supports setting multiple sites at once.

        Args:
            index : indices or list of indices
            r (int): Red value (0-255).
            g (int): Green value (0-255).
            b (int): Blue value (0-255).
        """
        changed = False
        # Convert single-index to list.
        if isinstance(index, int):
            index = [index]
        if 0 in index:
            raise IndexError(
                "Illegal site index 0 given! Remember VESTA is 1-based.")
        atom_section = self["SITET"]
        if atom_section is None:
            # TODO: Custom Error type for improper format?
            raise TypeError("No SITET section found!")
        for i, line in enumerate(atom_section.data):
            if isinstance(line, list) and len(line) >= 6:
                # Check for matching index:
                if line[0] in index:
                    changed = True
                    # Update the color tokens.
                    line[3] = r
                    line[4] = g
                    line[5] = b
            else:
                raise TypeError(f"Unexpected format in SITET line {i}: {line}")
        # Issue a warning to the user if no atoms were changed,
        # which can happen if you specify invalid indices.
        if not changed:
            logger.warning(f"No sites with indices {index} found.")

    def set_atom_color(self, element: Union[str, int], r: int, g: int, b: int,
                       overwrite_site_colors: bool = True):
        """
        Sets the colour of all atoms of an element.

        ATOMT, SITET
        """
        section = self["ATOMT"]
        # Are we matching by index or symbol?
        if isinstance(element, str):
            col = 1
        elif isinstance(element, int):
            col = 0
        else:
            raise TypeError(
                "Expected element to be int or str, got " + str(type(element)))
        if element == 0:
            raise IndexError(
                "Illegal site index 0 given! Remember VESTA is 1-based.")
        # Find the row with the matching element
        found = False
        for row in section.data:
            if row[col] == element:
                found = True
                break
        if not found:
            logger.warning(f"No elements of type {element} found!")
            return
        # Set the colour
        row[3:6] = r, g, b
        # If required, find the sites with this element and edit them too.
        if overwrite_site_colors:
            # Grab the element symbol
            element = row[1]
            # Search through the structure
            section = self["STRUC"]
            # Grab the site indices of entries with a matching element symbol.
            for row in section.data:
                if row[1] == element:
                    # Found a matching element. Edit the site colour
                    self.set_site_color(row[0], r, g, b)

    def add_lattice_plane(self, h: float, k: float, l: float, distance: float,
                          r: int = 255, g: int = 0, b: int = 255,
                          a: int = 192):
        """
        Adds a lattice plane, sectioning the volumetric data.

        Sets SPLAN.
        Mimics Edit Data > Lattice Planes > Add lattice planes.

        Args:
            h,k,l - Miller indices of the plane.
            distance - distance from origin (Angstrom)
            r,g,b,a - colour (0-255) of section. Default is magenta.
        """
        section = self["SPLAN"]
        new_plane = [len(section.data), h, k, l, distance, r, g, b, a]
        section.data.insert(-1, new_plane)

    def delete_lattice_plane(self, index: int):
        """
        SPLAN

        Index (1-based).
        Accepts negative indices, counting from the end.
        """
        if index == 0:
            raise IndexError("VESTA indices are 1-based; 0 is invalid index.")
        section = self["SPLAN"]
        # Process the index.
        if index < 0:
            # Note that length of section includes the empty 0-line.
            index = len(section) + index
        if index <= 0 or index >= len(section):
            raise IndexError("Index is out of range.")
        # Delete the wanted row.
        del section.data[index-1]
        # Re-index remaining entries.
        for i, line in enumerate(section.data):
            if line[0] > 0:
                line[0] = i + 1

    def delete_isosurface(self, index: int):
        """
        ISURF

        Index (1-based)
        """
        if index == 0:
            raise IndexError("VESTA indices are 1-based; 0 is invalid index.")
        section = self["ISURF"]
        # Process the index.
        if index < 0:
            # len(section) includes the empty 0-line
            index = len(section) + index
        if index <= 0 or index >= len(section):
            raise IndexError("Index is out of range.")
        # Delete the wanted row.
        del section.data[index-1]
        # Re-index remaining entries.
        for i, line in enumerate(section.data):
            if line[0] > 0:
                line[0] = i + 1

    def set_section_color_scheme(self, scheme: Union[int, str]):
        """
        Sets the section colour scheme, as in
        Properties > Sections > Sections and slices,
        from the drop-down menu.

        scheme - either a string with the exact name of the colour scheme, or
            an integer (0-based) indexing the item's position in the list.

        SECCL, SECTP, SECTS
        """
        section_color_scheme_names = [
            "B-G-R",
            "R-G-B",
            "C-M-Y",
            "Y-M-C",
            "Gray scale",
            "Inverted gray scale",
            "Rainbow+",
            "Inverted Rainbow+",
            "Cyclic: B-G-R-B",
            "Cyclic: R-G-B-R",
            "Cyclic: Ostwald",
            "Cyclic: Inverted Ostwald",
            "Cyclic: W-R-K-B-W",
            "Cyclic: K-R-W-B-K",
        ]
        # Convert string-name to index name.
        if isinstance(scheme, str):
            scheme = section_color_scheme_names.index(scheme)
        # Is it an inverted colour scheme?
        # The colour schemes alternate between regular and inverted.
        invert = scheme % 2 == 1
        # First, we set SECCL.
        section = self["SECCL"]
        section.inline[0] = scheme
        # Now, let us set the follow-on data.
        # SECTP records whether the colour map is forwards or inverted.
        section = self["SECTP"]
        if invert:
            section.data[0][0] = -1
        else:
            section.data[0][0] = 1
        # Finally, set appropriate flags in SECTS.
        section = self["SECTS"]
        if scheme <= 1:
            # RGB, unset bits 3 and 4.
            section.inline[0] &= ~(8+16)
        elif scheme <= 3:
            # CMY, unset bit 4, set bit 3.
            section.inline[0] |= 8
            section.inline[0] &= ~16
        else:
            # Set bit 4, unset bit 3.
            section.inline[0] &= ~8
            section.inline[0] |= 16

    def set_section_cutoff_levels(self,
                                  lattice_min: float = None,
                                  lattice_max: float = None,
                                  isosurface_min: float = None,
                                  isosurface_max: float = None,
                                  isosurface_auto: bool = None):
        """
        Sets cutoff levels for sections (Properties > Sections > Cutoff levels)

        Unset keyword arguments are left unchanged.

        SECTP, SECTS
        """
        section = self["SECTP"]
        # Set cut-off levels.
        if lattice_min is not None:
            section.data[0][3] = lattice_min
        if lattice_max is not None:
            section.data[0][4] = lattice_max
        if isosurface_min is not None:
            section.data[0][5] = isosurface_min
        if isosurface_max is not None:
            section.data[0][6] = isosurface_max
        # Set the auto flag.
        if isosurface_auto is not None:
            section = self["SECTS"]
            if isosurface_auto:
                # Unset the Manual bit
                section.inline[0] &= ~128
            else:
                # Set the Manual bit
                section.inline[0] |= 128

    def unhide_atoms(self):
        """Unhides all hidden atoms (DLATM)"""
        self["DLATM"].data = [[-1]]
    
    def unhide_bonds(self):
        """Unhides all hidden bonds (DLBND)"""
        self["DLBND"].data = [[-1]]
    
    def unhide_polyhedra(self):
        """Unhides all hidden polyhedra (DLPLY)"""
        self["DLPLY"].data = [[-1]]

    def _reset_hidden(self):
        """
        Handles DLATM, DLBND, and DLPLY, reverting them to null if not null.
        You should call this when your function potentially changes the number
        of visible atoms or bonds or polyhedra, because I don't support 
        modifying those via this API yet.
        Although, you're probably safe if you just add atoms and they don't
        add bonds that can connect to older atoms.
        """
        if self["DLATM"].data != [[-1]]:
            logger.warning(
                "Reseting atom visibility (computing hidden atoms not supported).")
            self.unhide_atoms()
        if self["DLBND"].data != [[-1]]:
            logger.warning(
                "Reseting bond visibility (computing hidden bonds not supported).")
            self.unhide_bonds()
        if self["DLPLY"].data != [[-1]]:
            logger.warning(
                "Reseting polyhedra visibility (computing hidden polyhedra not supported).")
            self.unhide_polyhedra()

    def set_boundary(self, xmin: float = None, xmax: float = None,
                     ymin: float = None, ymax: float = None,
                     zmin: float = None, zmax: float = None):
        """
        Sets Boundary.

        Unset arguments are left unchanged.

        BOUND
        """
        section = self["BOUND"]
        for i, x in enumerate([xmin, xmax, ymin, ymax, zmin, zmax]):
            if x is not None:
                section.data[0][i] = x
        # Reset the hidden atoms, bonds, polyhedra.
        self._reset_hidden()

    def set_unit_cell_line_visibility(self, show: bool = None,
                                      all: bool = False) -> int:
        """
        Sets whether to show the unit cell or whether to show all cells
        (vs just single)

        Returns the value of the flag that was set.

        Avoid setting both at once. But currently, if you do,
        show=False takes precedent over all=True, but don't count on it.
        Note also that setting all=False without setting show
        is undefined (and leaves it unchanged).

        UCOLP
        """
        # Validate input
        if (show is False) and (all is True):
            logger.warning("Cannot set both 'Do not show' and 'All unit cells';\
                           doing 'do not show'")
            all = False
        section = self["UCOLP"]
        if show is False:
            section.data[0][1] = 0
        elif all is True:
            section.data[0][1] = 2
        elif show is True:
            section.data[0][1] = 1
        else:
            logger.warning(
                "Unable to determine how to set unit_cell_line_visibility.")
        return section.data[0][1]

    def set_compass_visibility(self, show: bool, axes: bool = True) -> int:
        """
        Set compass and axes label visibility.

        Returns the value of the flag that was set.

        COMPS
        """
        section = self["COMPS"]
        if not show:
            section.inline[0] = 0
        else:
            if axes is False:
                section.inline[0] = 2
            else:
                section.inline[0] = 1
        return section.inline[0]

    def set_scene_view_matrix(self, matrix):
        """
        Set the 3x3 rotation matrix describing viewing angle.

        SCENE
        """
        if (len(matrix) != 3 or len(matrix[0]) != 3 or len(matrix[1]) != 3
                or len(matrix[2]) != 3):
            raise ValueError("matrix must be 3x3")
        section = self["SCENE"]
        for i in range(3):
            for j in range(3):
                section.data[i][j] = matrix[i][j]

    def set_scene_view_direction(self, view: str) -> list[list[float]]:
        """
        Set view direction to a preset viewing direction.

        Valid presets: "c"

        Returns the matrix that was set.

        SCENE
        """
        # Get the unit cell parameters
        a, b, c, alpha, beta, gamma = self.get_cell()
        alpha = math.radians(alpha)
        beta = math.radians(beta)
        gamma = math.radians(gamma)
        # Get the viewing angle matrix
        if view == "a":
            raise NotImplementedError
        elif view == "b":
            raise NotImplementedError
        elif view == "c":
            # c_x = c cos β,
            # c_y = c (cos α – cos β cos γ)/ sin γ,
            # c_z = c V with V = √[1 – cos²β – ((cos α – cos β cos γ)/ sin γ)²].
            # cos θ = c_z/|c|   and  φ = arctan2(c_y, cₓ).
            # We rotate by Rz(-phi), then Ry(-theta) (which gets c to (0,0,1)),
            # then Rz(asin(sin(phi)/sqrt(1-sin(theta)**2*cos(phi)**2)))
            # to bring a_y to 0.
            cx = math.cos(beta)
            cy = (math.cos(alpha) - math.cos(beta)
                  * math.cos(gamma))/math.sin(gamma)
            ct = math.sqrt(1 - cx**2 - cy**2)  # cos theta, also cz.
            theta = math.acos(ct)
            phi = math.atan2(cy, cx)
            cp = math.cos(phi)  # cos phi
            st = math.sin(theta)  # sin theta
            sp = math.sin(phi)  # sin phi
            # cosine of angle needed for a
            ca = ct * cp / math.sqrt(1 - st**2 * cp**2)
            # sine of angle needed for a
            sa = sp / math.sqrt(1 - st**2 * cp**2)
            matrix = [[ct*cp*ca + sp*sa, ct*sp*ca - cp*sa, -st*ca],
                      [ct*cp*sa - sp*ca, ct*sp*sa + cp*ca, -st*sa],
                      [st*cp, st*sp, ct]]
        elif view == "a*":
            raise NotImplementedError
        elif view == "b*":
            raise NotImplementedError
        elif view == "c*":
            raise NotImplementedError
        elif view == "1":
            matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            raise ValueError("Do not recognise view: "+str(view))
        self.set_scene_view_matrix(matrix)
        return matrix

    def set_scene_zoom(self, zoom: float):
        """
        Set zoom of the view. (1 is VESTA default)

        SCENE
        """
        section = self["SCENE"]
        section.data[6] = [zoom]

    def set_cell(self,
                 a: float = None,
                 b: float = None,
                 c: float = None,
                 alpha: float = None,
                 beta: float = None,
                 gamma: float = None):
        """
        Set unit cell parameters

        Unset values left unchanged.

        CELLP
        """
        section = self["CELLP"]
        for i, x in enumerate([a, b, c, alpha, beta, gamma]):
            if x is not None:
                section.data[0][i] = x

    def add_site(self, symbol: str, label: str, x: float, y: float, z: float,
                 dx: float = 0.0, dy: float = 0.0, dz: float = 0.0,
                 occupation: float = 1.0, charge: float = 0.0, U: float = 0.0,
                 add_bonds: bool = False):
        """
        Adds a new site.

        If requested, will create new bonds if this is a new element.
        While not the default behaviour in VESTA, this is provided as a
        convenience function.

        STRUC, THERI, THERM, ATOMT, SITET, (ATOMS)
        """
        # Add to structure parameters.
        section = self["STRUC"]
        new_idx = (len(section.data) - 1) // 2 + 1
        section.data.insert(-1, [new_idx, symbol, label,
                            occupation, x, y, z, '1a', 1])
        section.data.insert(-1, [dx, dy, dz, charge])
        # Add the uncertainty entry
        section = self["THERI"]
        section.data.insert(-1, [new_idx, label, U])
        # If applicable, add anisotropic uncertainty entry
        if "THERM" in self:
            section = self["THERM"]
            section.data.insert(-1, [new_idx, label] + [0.0]*6)
        # Add new element if applicable.
        # Otherwise find defaults
        section = self["ATOMT"]
        found = False
        for element in section.data:
            if element[1] == symbol:
                found = True
                break
        if not found:
            # Create a new element
            # Load data from elements.ini
            element_data = load_elements_data(symbol)
            # Figure out which radius to use
            radii_type = self["ATOMS"].inline[0]
            # 0=atomic, 1=ionic, 2=vdW.
            # elements_data has 2=atomic, 3=vdW, 4=ionic.
            radii_type = {0: 2, 1: 4, 2: 3}[radii_type]
            element = [len(section.data), symbol, element_data[radii_type]] + \
                element_data[5:] + element_data[5:] + [204]
            section.data.insert(-1, element)
            # If requested, create new bonds.
            if add_bonds:
                # Get the atomic symbols of the other elements.
                # Read from ATOMT
                other_symbols = [section.data[i][1]
                                 for i in range(len(section.data)-2)]
                for A2 in other_symbols:
                    # TODO: It turns out, when VESTA loads a POSCAR, it only
                    # adds bonds that could be drawn. If no atoms satisfy the
                    # length requirements, it does not add the bond.
                    
                    # If there is a bond length, add a new bond.
                    bond = load_default_bond_style(symbol, A2)
                    # If there is a hydrogen bond, load it.
                    if symbol == "H" or A2 == "H":
                        hbond = load_default_bond_style(symbol, A2, hbond=True)
                    else:
                        hbond = None
                    if bond is not None:
                        self.add_bond(bond[1], bond[2],
                                      min_length=bond[3],
                                      max_length=bond[4],
                                      search_mode=bond[5]+1,
                                      boundary_mode=bond[6]+1,
                                      show_polyhedra=bool(bond[7]),
                                      search_by_label=bool(bond[8]),
                                      style=bond[9]+1,
                        )
                    if hbond is not None:
                        self.add_bond(hbond[1], hbond[2],
                                    min_length=hbond[3],
                                    max_length=hbond[4],
                                    search_mode=hbond[5]+1,
                                    boundary_mode=hbond[6]+1,
                                    show_polyhedra=bool(hbond[7]),
                                    search_by_label=bool(hbond[8]),
                                    style=hbond[9]+1,
                        )
        # Use found data to set-up a new site
        params = element[2:10]  # Radius, RGB, RGB, 204
        section = self["SITET"]
        section.data.insert(-1, [new_idx, label] + params + [0])
        # Correct the hidden atoms, bonds, polyhedra if required.
        # If this site might bond to other sites outside the boundary, we
        # need to reset. Or if it might draw new bonds from older bonds,
        # we'd also need to reset.
        # (Really, we're doing better than VESTA, because VESTA doesn't
        # even track this.)
        bonds = self.get_bonds()
        for bond in bonds:
            # Check if we have matching elements.
            if bond["A1"] == "XX" or bond["A2"] == "XX":
                self._reset_hidden()
                break
            elif bond["search_by_label"] and (bond["A1"] == label or bond["A2"] == label) or \
                 not bond["search_by_label"] and (bond["A1"] == element or bond["A2"] == element):
                self._reset_hidden()
                break

    def add_bond(self, A1: str, A2: str, min_length: float = 0.0,
                 max_length: float = 1.6, search_mode: int = 1,
                 boundary_mode: Union[int, None] = None, show_polyhedra: bool = True,
                 search_by_label: bool = False, style: int = 2):
        """
        Add a new bond type.

        Edit > Bonds

        search_mode:
            1 = Search A2 bonded to A1 (default)
            2 = Search atoms bonded to A1. (Overwrites A2 to be 'XX'.)
            3 = Search molecules. (Overwrites A1 and A2 to be 'XX'.)
        boundary_mode:
            1 = Do not search atoms beyond the boundary.
            2 = Search additional atoms if A1 is included in the boundary.
                (default for search_mode = 1 or 2)
            3 = Search additional atoms recursively if either A1 or A2 is
                visible. (default for search_mode = 3)
        style:
            1 = Unicolor cylinder
            2 = Bicolor cylinder (default for standard bonds)
            3 = Color line
            4 = Gradient line
            5 = Dotted line
            6 = Dashed line (default for hydrogen bonds)

        SBOND
        """
        # Validate search_mode and boundary_mode inputs
        if search_mode not in [1, 2, 3]:
            raise ValueError("search_mode must be 1, 2, or 3. Got ",
                             str(search_mode))
        if boundary_mode not in [None, 1, 2, 3]:
            raise ValueError("boundary_mode must be 1, 2, or 3. Got ",
                             str(boundary_mode))
        # Overwrite A1 and A2.
        if search_mode > 1:
            A2 = "XX"
        if search_mode == 3:
            A1 = "XX"
        # Get default boundary_mode.
        if boundary_mode is None:
            if search_mode == 3:
                boundary_mode = 3
            else:
                boundary_mode = 2
        section = self["SBOND"]
        # Construct the line we need to add.
        index = len(section.data)  # Index
        radius = 0.25  # Default radius
        width = 2.0  # Default width
        r, g, b = (127, 127, 127)  # Default colour.
        # Write the line
        tokens = [index, A1, A2, min_length, max_length, search_mode - 1, boundary_mode - 1,
                  int(show_polyhedra), int(search_by_label), style - 1,
                  radius, width, r, g, b]
        section.data.insert(-1, tokens)
        # TODO: validation that A1 and A2 are valid symbols/labels.
        # Correct the visible atoms if required.
        # Because I don't process the data, identify if any new bonds could
        # have been drawn to sites outside the boundary.
        if boundary_mode > 1:
            # I could check if A1 and A2 are actually present,
            # but they should be anyway.
            self._reset_hidden()

    def get_bonds(self) -> list[dict]:
        """
        Gets a list of what bond types exist.

        Each element is a dictionary, which can be used directly as keyword
        arguments for self.add_bond.
        
        Data is a copy.

        SBOND
        """
        section = self["SBOND"]
        bonds = []
        for row in section.data[:-1]:
            # Unpack each row, converting data type if requried.
            bonds.append(dict(
                A1 = row[1],
                A2 = row[2],
                min_length = row[3],
                max_length = row[4],
                search_mode = row[5] + 1,
                boundary_mode = row[6] + 1,
                show_polyhedra = bool(row[7]),
                search_by_label = bool(row[8]),
                style = row[9] + 1,
            ))
        return bonds

    def get_structure(self) -> list[list]:
        """
        Gets a list of the key site structure parameters
        (index, element, label, x, y, z)

        Returned data is a copy.

        STRUC
        """
        section = self["STRUC"]
        my_list = []
        for row in section.data:
            if len(row) == 9:
                my_list.append((row[0:3] + row[4:7]).copy())
        return my_list

    def get_cell(self) -> list[float, float, float, float, float, float]:
        """
        Gets the cell parameters: a,b,c,alpha,beta,gamma

        Is a copy.
        """
        section = self["CELLP"]
        return section.data[0].copy()

    def get_cell_matrix(self) -> list[list[float]]:
        """
        Gets the lattice vectors as a 3x3 matrix.

        VESTA aligns the 1st lattice vectors with the x axis, and the 2nd in
        the x-y plane.
        """
        a, b, c, alpha, beta, gamma = self.get_cell()
        alpha = math.radians(alpha)
        beta = math.radians(beta)
        gamma = math.radians(gamma)
        # a is aligned along the x-axis.
        ax, ay, az = [a, 0, 0]
        # b is in the x-y plane.
        bx = b * math.cos(gamma)
        by = b * math.sin(gamma)
        bz = 0
        # c is more free.
        cx = c * math.cos(beta)
        cy = c * (math.cos(alpha) - math.cos(beta)
                  * math.cos(gamma))/math.sin(gamma)
        cz = math.sqrt(c**2 - cx**2 - cy**2)
        return [[ax, ay, az], [bx, by, bz], [cx, cy, cz]]

    def set_atom_material(self, r: int = None, g: int = None, b: int = None,
                          shininess: float = None):
        """
        Sets the atom material for lighting purposes.

        Unset parameters are left unchanged.

        r,g,b - integers from 0 to 255.
        shininess - float from 1 to 100; percentage.

        ATOMM
        """
        section = self["ATOMM"]
        # Set the colours
        for i, x in enumerate([r, g, b]):
            if x is not None:
                section.data[0][i] = x
        # Set the shininess
        # VESTA converts from a 0-100 scale to a 0-128 scale.
        if shininess is not None:
            section.data[1][0] = 1.28 * shininess

    def set_background_color(self, r: int, g: int, b: int):
        """
        Sets the background colour (RGB).

        BKGRC
        """
        section = self["BKGRC"]
        section.data[0] = [r, g, b]

    def set_enable_lighting(self, enable: bool):
        """
        Sets whether or not to Enable Lighting.

        LIGHT0
        """
        section = self["LIGHT0"]
        section.inline[0] = int(enable)

    def set_lighting_angle(self, matrix: list):
        """
        Sets the angle for lighting, using a 3x3 rotation matrix.

        LIGHT0
        """
        section = self["LIGHT0"]
        for i in range(3):
            for j in range(3):
                section.data[i][j] = matrix[i][j]

    def reset_lighting_angle(self):
        """
        Resets the lighting angle to directly overhead.

        LIGHT0
        """
        self.set_lighting_angle([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def set_lighting(self, ambient: int = None, diffuse: int = None):
        """
        Sets the ambient and diffuse character of lighting, in percent.

        Unset properties are left unchanged.

        LIGHT0
        """
        section = self["LIGHT0"]
        # N.B. VESTA internally converts the percentages to 0-255 scale.
        if ambient is not None:
            x = int(ambient / 100 * 255)
            section.data[6] = [x, x, x, 255]
        if diffuse is not None:
            x = int(diffuse / 100 * 255)
            section.data[7] = [x, x, x, 255]

    def set_depth_cueing(self, enable: bool = None, start: float = None,
                         end: float = None):
        """
        Sets depth cueing settings.

        Unset properties are left unchanged.

        DPTHQ
        """
        section = self["DPTHQ"]
        if enable is not None:
            section.inline[0] = int(enable)
        if start is not None:
            section.inline[1] = start
        if end is not None:
            section.inline[2] = end

    def find_sites(self, elements: Union[list[str], str, None] = None,
                   xmin: float = 0, xmax: float = 1,
                   ymin: float = 0, ymax: float = 1,
                   zmin: float = 0, zmax: float = 1) -> list[int]:
        """
        Obtains the site indices (1-based) matching the provided list of
        elements (if applicable) and with (fractional) coordinates within
        the specified bounding box.

        Fractional coordinates are probably in the interval [0,1).
        """
        stru = self.get_structure()  # List of (index, element, label, x, y, z)
        # Configure the elements list.
        if elements is not None:
            if isinstance(elements, str):
                elements = [elements]
        # Search
        indices = []
        for site in stru:
            # If no element specified or element symbol matches.
            if elements is None or site[1] in elements:
                # If coordinates are within range
                if xmin <= site[3] <= xmax and \
                   ymin <= site[4] <= ymax and \
                   zmin <= site[5] <= zmax:
                    # Record the index.
                    indices.append(site[0])
        return indices

    def set_title(self, title: str):
        """Sets the TITLE field. No newlines allowed."""
        # Verify that title is one line.
        lines = title.splitlines()  # This also strips off any trailing newlines
        if len(lines) > 1:
            raise ValueError("Title not allowed to include line breaks!")
        # Set the title
        section = self["TITLE"]
        section.data[0][0] = lines[0]

    def _convert_vector_coords(self, x: float, y: float, z: float,
                               coord_type: str) -> tuple[float, float, float]:
        """
        Converts x, y, z in coord_type coordinates to modulus.
        """
        if coord_type == "modulus":
            # This is the internal representation. No change needed.
            pass
        elif coord_type == "uvw":
            # To get to modulus, multiply by length of lattice vectors
            va, vb, vc, _, _, _ = self.get_cell()
            x *= va
            y *= vb
            z *= vc
        elif coord_type == "xyz":
            # Get lattice vector directions
            a, b, c, _, _, _ = self.get_cell()
            mat = self.get_cell_matrix()
            # Convert lattice vectors to unit vectors
            for i, length in enumerate((a, b, c)):
                for j in range(3):
                    mat[i][j] /= length
            # Obtain inverse matrix
            imat = invert_matrix(mat)
            # (x',y',z') = (x,y,z) * imat (row vectors)
            # Copy
            cart = [x, y, z]
            x = sum(imat[i][0] * cart[i] for i in range(3))
            y = sum(imat[i][1] * cart[i] for i in range(3))
            z = sum(imat[i][2] * cart[i] for i in range(3))
        else:
            raise ValueError(
                "coord_type must be modulus, uvw, or xyz, but got ", coord_type)
        return x, y, z

    def add_vector_type(self, x: float, y: float, z: float,
                        polar: bool = False, radius: float = 0.5,
                        r: int = 255, g: int = 0, b: int = 0,
                        penetrate_atoms: bool = True,
                        add_atom_radius: bool = False,
                        coord_type: str = "xyz"):
        """
        Create a new type of vector (Edit > Vectors > New)

        Arguments:
            - x, y, z: floats, coordinates of vector.
            - polar: bool, whether this is a polar vector (rather than axial).
                Default False.
            - radius: float (positive), radius of rendered arrow. Default 0.5.
            - r, g, b: int (0-255). RGB colour of vector. Default 255, 0, 0.
            - penetrate_atoms: bool. Whether the vector penetrates the atom,
                such that it sticks out on both sides. Default True.
            - add_atom_radius: bool. Whether to add the atomic radius to the
                length of the vector. Default False.
            - coord_type: {"xyz", "uvw", "modulus"}. Coordinate basis for
                x, y, z arguments.
                - "xyz": Cartesian vector notation. (Default)
                - "uvw": Lattice vector notation.
                - "modulus": Modulus along crystallographic axes. (This is the
                    internal representation.)

        VECTR, VECTT.
        """
        # Convert input coordinates.
        x, y, z = self._convert_vector_coords(x, y, z, coord_type)
        # Add vector formatting.
        # (I do this first because it's easier to get the index from here.)
        section = self["VECTT"]
        # Index of the new vector.
        idx = len(section.data)
        # Exploit Python converting bools to ints. True = 1.
        flag = penetrate_atoms + 2 * add_atom_radius
        section.data.insert(-1, [idx, radius, r, g, b, flag])
        # Add the new vector block
        section = self["VECTR"]
        section.data.insert(-1, [idx, x, y, z, int(polar)])
        section.data.insert(-1, [0, 0, 0, 0, 0])  # Block termination.

    def edit_vector_type(self,
                         index: int,
                         x: float = None,
                         y: float = None,
                         z: float = None,
                         polar: bool = None,
                         radius: float = None,
                         r: int = None,
                         g: int = None,
                         b: int = None,
                         penetrate_atoms: bool = None,
                         add_atom_radius: bool = None,
                         coord_type: str = "xyz"):
        """
        Edits an existing type of vector (Edit > Vectors > Edit)

        Accepts negative indices, counting from the end.

        All arguments after index are optional. Unset arguments are left 
        unchanged.
        If x, y, or z are provided, all of x, y, and z need to be provided.

        Arguments:
            - index: int, index (1-based) of the vector.
            - x, y, z: floats, coordinates of vector.
            - polar: bool, whether this is a polar vector (rather than axial).
            - radius: float (positive), radius of rendered arrow.
            - r, g, b: int (0-255). RGB colour of vector.
            - penetrate_atoms: bool. Whether the vector penetrates the atom,
                such that it sticks out on both sides.
            - add_atom_radius: bool. Whether to add the atomic radius to the
                length of the vector.
            - coord_type: {"xyz", "uvw", "modulus"}. Coordinate basis for
                x, y, z arguments.
                - "xyz": Cartesian vector notation.
                - "uvw": Lattice vector notation.
                - "modulus": Modulus along crystallographic axes. (This is the
                    internal representation.)

        VECTR, VECTT.
        """
        if index == 0:
            raise IndexError("VESTA indices are 1-based; 0 is invalid index.")
        section = self["VECTT"]
        # Process the index.
        if index < 0:
            # Note that length of section includes the empty 0-line.
            index = len(section) + index
        if index <= 0 or index >= len(section):
            raise IndexError("Index is out of range.")
        # Process the vector coordinates if provided.
        if x is not None:
            if y is None or z is None:
                raise TypeError("x, y, and z must be specified together.")
            else:
                x, y, z = self._convert_vector_coords(x, y, z, coord_type)
        else:
            if y is not None or z is not None:
                raise TypeError("x, y, and z must be specified together.")
        # Update values
        if radius is not None:
            section.data[index-1][1] = radius
        if r is not None:
            section.data[index-1][2] = r
        if g is not None:
            section.data[index-1][3] = g
        if b is not None:
            section.data[index-1][4] = b
        if penetrate_atoms is not None:
            # Set bit flags.
            if penetrate_atoms:
                section.data[index-1][5] |= 1
            else:
                section.data[index-1][5] &= ~1
        if add_atom_radius is not None:
            if add_atom_radius:
                section.data[index-1][5] |= 2
            else:
                section.data[index-1][5] &= ~2
        section = self["VECTR"]
        # Find the row that has the target index.
        idx = None
        for i, row in enumerate(section.data):
            if row[0] == index:
                idx = i
                break
        if idx is None:
            raise RuntimeError(
                "VECTR malformed? Could not find entry with index ", index)
        # Update data
        if x is not None:
            section.data[idx][1:4] = x, y, z
        if polar is not None:
            section.data[idx][4] = int(polar)

    def delete_vector_type(self, index: int):
        """
        Delete the given vector type

        VECTT, VECTR

        Index (1-based)
        """
        if index == 0:
            raise IndexError("VESTA indices are 1-based; 0 is invalid index.")
        # Vector styles are easier to parse number of vectors
        section = self["VECTT"]
        nvec = len(section)
        # VECTT has n+1 rows; the last row is all 0's.
        # Indexing starts at 1 in the 0'th row.
        # Process the index.
        if index < 0:
            # len(section) includes the empty 0-line
            index = nvec + index
        if index <= 0 or index >= nvec:
            raise IndexError("Index is out of range.")
        # Delete the wanted row.
        del section.data[index-1]
        # Re-index remaining entries.
        for i, line in enumerate(section.data):
            if line[0] > 0:
                line[0] = i + 1
        # Now delete the row in VECTR
        section = self["VECTR"]
        for i, line in enumerate(section.data):
            # Find the relevant row
            if line[0] == index and (i == 0 or section.data[i-1] == [0]*5):
                # We have found the matching index.
                # Now delete lines until we delete the block-end line.
                while section.data.pop(i) != [0]*5:
                    pass
                # We're done deleting things
                break
        # Re-index.
        if nvec > 1:
            idx = 1
            for i, line in enumerate(section.data):
                # Find the starting line of each block
                if (i == 0 or section.data[i-1] == [0]*5) and line != [0]*5:
                    # Re-write the index.
                    line[0] = idx
                    idx += 1

    def set_vector_to_site(self, type: int, site: int):
        """
        Attach a vector of type `type` to atomic `site`.

        Currently, we attach to all symmetrically equivalent sites based on
        the current space group.
        Also, no duplicate checking is performed.

        VECTR
        """
        # Validate inputs
        if type <= 0:
            raise IndexError("type should be positive, but got ", type)
        if site <= 0:
            raise IndexError("site should be positive, but got ", site)
        section = self["VECTR"]
        # Find the relevant block matching the type.
        idx = 0
        while idx < len(section.data):
            # Start of a block has the end of a block before it.
            if (section.data[idx][0] == type) and (idx == 0 or section.data[idx-1] == 5*[0]):
                break
            idx += 1
        if idx == len(section.data):
            raise IndexError("Vector of type ", type, " does not exist.")
        # Now that we've found the start of the block, let's go to the end of the block.
        while idx < len(section.data):
            # If I want to, check for duplicates here.
            # But I think duplicates are allowed.
            if section.data[idx] == 5*[0]:
                break
            idx += 1
        if idx == len(section.data):
            raise RuntimeError(
                "Malformed VECTR; no block termination detected.")
        # Insert
        section.data.insert(idx, [site, 0, 0, 0, 0])

    def remove_vector_from_site(self, type: int, site: int):
        """
        Removes vectors of type `type` from atomic site `site`.

        Will remove multiple matching sites if there are duplicates.

        Silent does nothing if `site` not found, but will raise an error if
        `type` is not valid.

        VECTR
        """
        # Validate inputs
        if type <= 0:
            raise IndexError("type should be positive, but got ", type)
        section = self["VECTR"]
        # Find the relevant block matching the type.
        idx = 0
        while idx < len(section.data):
            # Start of a block has the end of a block before it.
            if (section.data[idx][0] == type) and (idx == 0 or section.data[idx-1] == 5*[0]):
                break
            idx += 1
        if idx == len(section.data):
            raise IndexError("Vector of type ", type, " does not exist.")
        # Now that we've found the start of the block, let's go through the
        # block and delete matching rows.
        # Get past the first row of the block which defines the vector.
        idx += 1
        while idx < len(section.data):
            # If hit end of block, exit.
            if section.data[idx] == 5*[0]:
                break
            # If this entry matches the site, delete it.
            if section.data[idx][0] == site:
                del section.data[idx]
                # Do not increment, index, because the next row moved to us.
            else:
                idx += 1

    def set_vector_scale(self, scale: float):
        """Sets global vector scale factor (VECTS)"""
        self["VECTS"].inline = [scale]

    # This function is incomplete. I'm setting it aside for future me to deal
    # with, as it turns out to require some fairly advanced computation to
    # make work.
    # TODO: Toggle visibility of atoms, sites, etc.
    # TODO: A way to invert this function, so I can reverse out which sites are hidden
    # before I add new bonds or change the boundary, then reconstruct DLATM.
    # Actually, not even VESTA attempts to invert this. Which elements are shown or
    # hidden is tracked in the GUI session only. But if you close and open the file
    # again, then the check-boxes for visibility are all checked, and if you change
    # the boundary it resets to everything being visible.
    # def set_site_visibility(self, site: int, show: bool = None):
    #     """
    #     Toggles visibility of a specified site (by index, 1-based, as in STRUC).

    #     If `show` not set, toggle. Otherwise, set visibility to show.

    #     As in Objects visibility check-boxes.

    #     The algorithm here is non-trivial, as we have to track all visible
    #     objects. As such, we only support limited symmetry groups and bonding
    #     boundary modes.

    #     WIP!

    #     DLATM.
    #     """
    #     # (I should probably understand how GROUP is formatted a bit better...)
    #     if self["GROUP"].data != [[1, 1, "P", 1]]:
    #         raise NotImplementedError(
    #             "Unable to process site visibility for non-trivial symmetry groups.")
    #     # Validate input
    #     if site <= 0 or site > self.nsites:
    #         raise IndexError("Site ", site,
    #                          " is out of range for a structure with ",
    #                          self.nsites, " sites.")
    #     # Get the important data.
    #     structure = self.get_structure()
    #     boundary = self["BOUND"].data[0].copy()
    #     cell_mat = self.get_cell_matrix()
    #     inv_cell = invert_matrix(cell_mat)
    #     # TODO: Get cut-off planes.
    #     # Identify relevant bonds.
    #     bonds = []
    #     section = self["SBOND"]
    #     for bond in section.data:
    #         if bond[6] == 2: # Boundary mode
    #             raise NotImplementedError(
    #                 "Unable to process site visibility when bonds with "
    #                 "recursive boundary mode are present.")
    #         if bond[5] == 2 and bond[6] != 0: # Search mode
    #             raise NotImplementedError(
    #                 "Unable to process site visibility with bonds with "
    #                 "search molecules search mode that search beyond the bondary.")
    #         if bond[6] != 0 and (bond[2] == 'XX' or
    #                              (structure[site-1][1] in bond[1:3] and not bond[8]) or
    #                              (structure[site-1][2] in bond[1:3] and bond[8])):
    #             # To be relevant, search mode must stretch beyond the boundary
    #             # (bond[6] != 0), and the site must match A1 or A2 (bond[1], bond[2]),
    #             # which might be as a wild-card ('XX'), by element (if bond[8] == 0),
    #             # or by site label (if bond[8] == 1).
    #             bonds.append(bond)
    #     # Count all the visible atoms 
    #     # (N.B. "Hide non-bonding atoms" is tracked separately.)
    #     # It is the bond boundary mode which makes a difference here.
    #     natoms = 0
    #     for isite in range(1,site):
    #         # Count the number of visible atoms for each site.
    #         # First, find the coordinates of all elements within the boundary.
    #         # Next, find the bonding distances with all atoms
    #         # Finally, count the atoms of this site outside the boundary which 
    #         # would be bonded to atoms within the boundary.
    #         pass
