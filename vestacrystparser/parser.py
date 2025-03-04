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
        
        # Determine special behavior.
        self.is_title = (self.header == "TITLE")
        
        inline_text = tokens[1] if len(tokens) > 1 else ""
        if self.is_title:
            # For TITLE, store inline text in data (as a string) and leave inline empty.
            self.inline = []
            self.data = [inline_text] if inline_text else []
        else:
            # For non-TITLE sections, tokenize inline data.
            self.inline = parse_line(inline_text) if inline_text else []
            self.data = []  # Extra lines will be stored here.

    def add_line(self, line):
        """
        Add a continuation line to the section.
        
        For TITLE, store the entire line as a string.
        For other sections, split the line into tokens and convert them.
        """
        if self.is_title:
            self.data.append(line)
        else:
            self.data.append(parse_line(line))

    def to_text(self):
        """
        Convert the section back to text.
        
        For TITLE:
          - The header is written alone.
          - Each line of data (stored as strings) is written on its own line.
        For non-TITLE sections:
          - If inline data exists, it is written on the header line.
          - Then, any extra lines are written one per line.
        """
        if self.is_title:
            # For TITLE, output header on its own then each data line as-is.
            text = f"{self.header}\n"
            for line in self.data:
                text += f"{line}\n"
            return text
        else:
            if self.inline:
                inline_text = " ".join(str(x) for x in self.inline)
                text = f"{self.header} {inline_text}\n"
            else:
                text = f"{self.header}\n"
            for line in self.data:
                text += " ".join(str(x) for x in line) + "\n"
            return text

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
                    # Create a default section if none exists.
                    current_section = "GLOBAL"
                    section = VestaSection("GLOBAL")
                    self.sections["GLOBAL"] = section
                    self.order.append("GLOBAL")
                self.sections[current_section].add_line(line)
    
    def get_section(self, section_name):
        """
        Retrieve a VestaSection by its header.
        
        Args:
            section_name (str): e.g., 'TITLE', 'CELL'.
            
        Returns:
            VestaSection or None: The corresponding section object.
        """
        return self.sections.get(section_name)
    
    def save(self, filename):
        """
        Write the current VESTA data to disk.
        
        Args:
            filename (str): Output file path.
        """
        with open(filename, 'w') as f:
            for sec_name in self.order:
                section = self.sections[sec_name]
                f.write(section.to_text())
    
    def __str__(self):
        """
        Return a summary of the sections.
        """
        summary = "VESTA file sections:\n"
        for sec_name in self.order:
            sec = self.sections[sec_name]
            if sec.is_title:
                typ = "TITLE (multi-line)"
                nlines = len(sec.data)
            else:
                typ = "Inline preserved" if sec.inline else "No inline"
                nlines = len(sec.data)
            summary += f"  {sec_name}: {nlines} additional line(s) ({typ})\n"
        return summary

    def set_atom_color(self, r, g, b):
        """
        Set the RGB atom color for all atoms in the ATOM section.
        
        Assumes that each line in the ATOMT section has its tokens as:
          [flag, element, number, R, G, B, R, G, B, A?]
        and that the RGB values are at positions 5, 6, and 7.
        
        Args:
            r (int): Red value (0-255).
            g (int): Green value (0-255).
            b (int): Blue value (0-255).
        """
        atom_section = self.get_section("SITET")
        if atom_section is None:
            print("No ATOMT section found.")
            return
        for i, line in enumerate(atom_section.data):
            if isinstance(line, list) and len(line) >= 8:
                # Update the color tokens.
                line[3] = r
                line[4] = g
                line[5] = b
                line[6] = r
                line[7] = g
                line[8] = b
            else:
                print(f"Warning: Unexpected format in ATOMT line {i}: {line}")

