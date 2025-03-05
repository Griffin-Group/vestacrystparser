import logging

logger = logging.getLogger(__name__)

def parse_token(token):
    """
    Convert a token to int or float if possible; otherwise, return it as a string.
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

def parse_line(line):
    """
    Split a line into tokens and convert each token.
    Returns a list of tokens.
    """
    tokens = line.split()
    return [parse_token(tok) for tok in tokens]

# Sections that have a blank line after them.
# (So far, I've only found this to be important for IMPORT_DENSITY,
# but if I'm doing it for one I may as well do it for all.)
sections_with_blank_line = [
    "#VESTA_FORMAT_VERSION",
    "CRYSTAL",
    "TITLE",
    "IMPORT_DENSITY",
    "HBOND",
    "SECCL",
    "TEXCL",
]

class VestaSection:
    def __init__(self, header_line):
        """
        Initialize a VESTA section from a header line.
        
        For the TITLE section:
          - Inline data is not preserved on the header, but moved to the multi-line data.
        For other sections:
          - If inline data is present on the header, it is stored (parsed) in self.inline.
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

    def to_text(self):
        """
        Convert the section back to text.
        
          - If inline data exists, it is written on the header line.
          - Then, any extra lines are written one per line.
        """
        if self.inline:
            inline_text = " ".join(str(x) for x in self.inline)
            text = f"{self.header} {inline_text}\n"
        else:
            text = f"{self.header}\n"
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


class VestaFile:
    def __init__(self, filename=None):
        """
        Initialize a VESTA file instance.
        
        Attributes:
            sections (dict): Maps section headers to VestaSection objects.
            order (list): The order in which sections appear in the file.
        """
        self.sections = {}
        self.order = []
        if filename:
            self.load(filename)
    
    def load(self, filename):
        """
        Load and parse a VESTA file.
        
        Args:
            filename (str): Path to the VESTA file.
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        current_section = None
        for raw_line in lines:
            # Remove only the newline character.
            line = raw_line.rstrip("\n")
            if line == "":
                continue  # skip blank lines

            # Use lstrip() to test for a header token.
            stripped = line.lstrip()
            tokens = stripped.split(maxsplit=1)
            if tokens and tokens[0].isupper():
                # New section.
                section = VestaSection(line)
                self.sections[section.header] = section
                self.order.append(section.header)
                current_section = section.header
            else:
                # Continuation of the current section.
                if current_section is None:
                    logger.warning("Data without section found! Line:\n"+line)
                    # Create a default section if none exists.
                    current_section = "GLOBAL"
                    section = VestaSection("GLOBAL")
                    self.sections["GLOBAL"] = section
                    self.order.append("GLOBAL")
                self.sections[current_section].add_line(line)
    
    def get_section(self, section_name) -> VestaSection|None:
        """
        Retrieve a VestaSection by its header.
        
        Args:
            section_name (str): e.g., 'TITLE', 'CELL'.
            
        Returns:
            VestaSection or None: The corresponding section object.
        """
        return self.sections.get(section_name)
    
    def __getitem__(self, name) -> VestaSection:
        return self.sections[name]

    def __len__(self) -> int:
        """Number of sections"""
        return len(self.sections)

    def save(self, filename):
        """
        Write the current VESTA data to disk.
        
        Args:
            filename (str): Output file path.
        """
        with open(filename, 'w') as f:
            f.write(str(self))
    
    def __str__(self) -> str:
        mystr = ""
        for sec_name in self.order:
            mystr += self.sections[sec_name].to_text()
        return mystr

    def summary(self) -> str:
        """
        Return a summary of the sections.
        What sections exist and how many lines they have.
        """
        summary = "VESTA file sections:\n"
        for sec_name in self.order:
            sec = self.sections[sec_name]
            typ = "Inline preserved" if sec.inline else "No inline"
            nlines = len(sec.data)
            summary += f"  {sec_name}: {nlines} additional line(s) ({typ})\n"
        return summary

    def set_site_color(self, index:int|list[int], r:int, g:int, b:int):
        """
        Set the RGB site colour for sites with index (1-based).
        
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
        atom_section = self.get_section("SITET")
        if atom_section is None:
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
    
    def add_lattice_plane(self, h:float,k:float,l:float,distance:float,
                          r:int=255,g:int=0,b:int=255,a:int=192):
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
        new_plane = [len(section.data), h,k,l,distance,r,g,b,a]
        section.data.insert(-1, new_plane)

    def delete_section_plane(self, index:int):
        """
        SPLAN

        Index (1-based)
        """
        if index == 0:
            raise ValueError("VESTA indices are 1-based; 0 is invalid index.")
        section = self["SPLAN"]
        # Process the index.
        if index < 0:
            index = len(section) + 1 + index
        if index <= 0 or index > len(section):
            raise IndexError("Index is out of range.")
        # Delete the wanted row.
        del section.data[index-1]
        # Re-index remaining entries.
        for i, line in enumerate(section.data):
            if line[0] > 0:
                line[0] = i + 1

    def delete_isosurface(self, index:int):
        """
        ISURF

        Index (1-based)
        """
        if index == 0:
            raise ValueError("VESTA indices are 1-based; 0 is invalid index.")
        section = self["ISURF"]
        # Process the index.
        if index < 0:
            index = len(section) + 1 + index
        if index <= 0 or index > len(section):
            raise IndexError("Index is out of range.")
        # Delete the wanted row.
        del section.data[index-1]
        # Re-index remaining entries.
        for i, line in enumerate(section.data):
            if line[0] > 0:
                line[0] = i + 1

    def set_section_color_scheme(self, scheme:int|str):
        """
        Sets the section colour scheme, as in Properties > Sections > Sections and slices,
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
            section.inline[0] &= 8
            section.inline[0] |= ~16

    def set_section_cutoff_levels(self,
                                lattice_min:float=None,
                                lattice_max:float=None,
                                isosurface_min:float=None,
                                isosurface_max:float=None,
                                isosurface_auto:bool=None):
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

    def set_boundary(self, xmin:float=None, xmax:float=None, ymin:float=None,
                     ymax:float=None, zmin:float=None, zmax:float=None):
        """
        Sets Boundary.
        
        Unset arguments are left unchanged.

        BOUND
        """
        section = self["BOUND"]
        for i, x in enumerate([xmin, xmax, ymin, ymax, zmin, zmax]):
            if x is not None:
                section.data[0][i] = x
    
    def set_unit_cell_line_visibility(self, show:bool=None, all:bool=False) -> int:
        """
        Sets whether to show the unit cell or whether to show all cells (vs just single)

        UCOLP
        """
        # Validate input
        if (show == False) and (all == True):
            logger.warning("Cannot set both 'Do not show' and 'All unit cells'; doing 'do not show'")
            all = False
        section = self["UCOLP"]
        if show == False:
            section.data[0][1] = 0
        elif all == True:
            section.data[0][1] = 2
        elif show == True:
            section.data[0][1] = 1
        else:
            logger.warning("Unable to determine how to set unit_cell_line_visibility.")
        return section.data[0][1]
    
    def set_compass_visibility(self, show:bool, axes:bool=True) -> int:
        """
        Set compass and axes label visibility.

        COMPS
        """
        section = self["COMPS"]
        if not show:
            section.inline[0] = 0
        else:
            if axes == False:
                section.inline[0] = 2
            else:
                section.inline[0] = 1
        return section.inline[0]