#!/usr/bin/env python3

import os

from vestacrystparser.parser import VestaFile

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# Example usage:
if __name__ == "__main__":
    vesta_path = os.path.join(TEST_DIR, 'data', 'Cu_primitive_plain.vesta')  # input file
    output_path = os.path.join(TEST_DIR,'data', 'cu_modified.vesta')         # output file
    try:
        vfile = VestaFile(vesta_path)
        print(vfile.summary())
        
        # Example: inspect TITLE and TRANM sections.
        title_sec = vfile["TITLE"]
        if title_sec:
            print("TITLE data:", title_sec.data)
        tranm_sec = vfile.get_section("TRANM")
        if tranm_sec:
            print("TRANM inline data:", tranm_sec.inline)
            print("TRANM extra data:", tranm_sec.data)
        
        print("Number of sections: ", len(vfile))

        # Update the atom colors to a new RGB value, e.g., 255 0 0 (red).
        vfile.set_site_color(1, 255, 0, 0)
        
        vfile.save(output_path)
        print(f"Modified VESTA file saved to '{output_path}'")
    except FileNotFoundError:
        print(f"File '{vesta_path}' not found.")
