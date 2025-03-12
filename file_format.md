# The .vesta file format

Herein I have manually reverse-engineered the key features of VESTA's file format.
The specification here is UNOFFICIAL, likely INCOMPLETE, and may contain INACCURACIES. Use with caution. Contributions welcome.

VESTA is a plain-text file.
The amount of whitespace between entries on the same line does not seem to matter, neither does the number of decimal places in floating-point values.

The file has sections marked in all-caps, followed by a series of space- and newline-separated values.

## #VESTA_FORMAT_VERSION

Metadata tag: version of the VESTA file format.
The files I'm working with are in version 3.5.4.

A blank line follows it.

e.g.
```
#VESTA_FORMAT_VERSION 3.5.4

```

## CRYSTAL

Superheader for each crystal Phase (Edit Data > Phases).

No data is associated with this field. However, it can appear multiple times. Following CRYSTAL are the sections from TITLE through to PLN2D inclusive, which contain the data specific to each crystal phase. (This means those sections are also unique either.) Additional phases begin with another CRYSTAL header.

Has a blank line before and after it.
```

CRYSTAL

```

## TITLE

Name/title of the structure.

One-line string.
Defaults to "New structure".
Has a blank line after it.

e.g.
```
TITLE
New structure

```

## IMPORT_DENSITY

**Optional section.**

Where to import volumetric density data from.

Has a flag `1` after the title (units??).
Each line is a file path (2nd item, string) and how to add it to the existing data (signed float, 1st item).

Has an empty line after it.

e.g.
```
IMPORT_DENSITY 1
+1.000000 CHGCAR

```

## GROUP

Space group; the symmetry group imposed on the crystal.

e.g.
```
GROUP
1 1 P 1
```

## SYMOP

Symmetry operations associated with GROUP.

e.g.
```
SYMOP
 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1   1
 -1.0 -1.0 -1.0  0 0 0  0 0 0  0 0 0
```

## TRANM

e.g.
```
TRANM 0
 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1
```

## LTRANSL

e.g.
```
LTRANSL
 -1
 0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
```

## LORIENT

e.g.
```
LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000
```

## LMATRIX

e.g.
```
LMATRIX
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000
```

## CELLP

Unit cell lattice parameters.
This data appears in Edit Data > Unit Cell > Lattice parameters.

Two lines of 6 floats each.
The first line is a, b, c, alpha, beta, gamma.
The second line is the s.u.: entries.

e.g.
```
CELLP
  2.530000   2.530000   2.530000  60.000000  60.000000  60.000000
  0.000000   0.000000   0.000000   0.000000   0.000000   0.000000
```

## STRUC

Structure parameters.

Editable via Edit > Edit Data > Structure Parameters.

Has an entry for each (symmetrically-distinct) atom.
Each atom gets two lines.

- Row 1, item 1: No. / index (integer). Increments from 1. Not manually set.
- Row 1, item 2: Elemental symbol (string)
- Row 1, item 3: Site label (string)
- Row 1, item 4: Occupation (default `1.0000`).
- Row 1, items 5-7: x,y,z coordinates (fractional)
- Row 1, item 8: Wyckoff position/site? (default `1a`)
- Row 1, item 9: ? (default `1`)
- Row 2, items 1-3 (beneath row 1 items 5-7): x,y,z standard uncertainties (s.u.)
- Row 2, item 4 (beneath row 1 item 8): Charge (default `0.00`)

Block ends with seven `0`'s.

e.g.
```
STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0
```

## THERI

Isotropic U/B in Structure Parameters. (Isotropic thermal?)

In-line with the header is an integer flag defining whether we are using units of U or B.
`0` if B, `1` if U. Default `1`.

One row for each site in STRUC.

- Item 1: Site number/index.
- Item 2: Site label.
- Item 3: U or B value (float).

Block ends with three `0`'s.

N.B. if THERM is non-zero, it changes the value here.

e.g.
```
THERI 1
  1         Cu  0.050000
  0 0 0
```

## THERT

**Optional section.**

Anisotropic thermal type.

Appears when Structure Parameters > Anisotropic is not None.

Single integer flag. `0` if units of U, `1` if units of beta.

e.g.
```
THERT 0
```

## THERM

**Optional section.**

Appears when Structure Parameters > Anisotropic is not None.

One row for each site.

- Item 1: Site index.
- Item 2: Site label.
- Items 3-8: U11, U22, U33, U12, U13, U23.

Ends in eight `0`'s.

Overwrites THERI if non-zero.

e.g.
```
THERM
  1        Cu1    0.11000    0.22000    0.33000    0.12000    0.13000    0.23000
  2         Cu    0.00000    0.00000    0.00000    0.00000    0.00000    0.00000
  0 0 0 0 0 0 0 0
```

## SHAPE

e.g.
```
SHAPE
  0       0       0       0   0.000000  0   192   192   192   192
```

## BOUND

Boundary.

- 1st item: x min
- 2nd item: x max
- 3rd item: y min
- 4th item: y max
- 5th item: z min
- 6th item: z max

Block ends with five `0`'s.

e.g.
```
BOUND
       0        1         0        1         0        1
  0   0   0   0  0
```

## SBOND

e.g.
```
SBOND
  0 0 0 0
```

## SITET

Site-specific appearances.

Each row:
- 1st item: Site index (see STRUC)
- 2nd item: Site label (see STRUC).
- 3rd item: Atomic radius (Objects > Properties > Atoms > Radius and color)
- 4-6th item: RGB of atom colour (Objects > Properties > Atoms > Radius and color)
- 7-9th item: Default atom colour (RGB)?
- 10th item: ?
- 11th item: ?

Ends with a row of 6 zero's.

See ATOMT for global atomic properties. SITET overrides appearances set by ATOMT. New sites inherit from ATOMT.

e.g.
```
SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  0 0 0 0 0 0
```

## VECTR

Vectors to draw on the atoms.

Each vector has a block of entries. The first row is the vector.
It has an index, which is the vector's index (because multiple atoms can
share a vector, so VESTA indexes vectors separately), followed by the
Cartesian coordinates of the vector, followed by a 0 for axial vectors or
1 for polar vectors.
After the vector entry is the atoms entry. It starts with the atomic index,
followed by some 4 integers (which should be 0 in our cases, but may be
non-zero if you are selecting an individual atom instead of a
crystallographic site).
There may be multiple atoms entries; each entry receives the same vector.
Each entry is terminated by a row of 5 zeroes.
The block is terminated by 5 more zeroes.

Files lacking vectors have an empty VECTR block with just ` 0 0 0 0 0`.

e.g.
```
VECTR
    1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
    0 0 0 0 0
    2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
    0 0 0 0 0
    3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
    0 0 0 0 0
    4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
    0 0 0 0 0
    0 0 0 0 0
```

## VECTT

Vector formatting.

- 1st item: vector index (see VECTR).
- 2nd item: Radius (0.5 is default)
- 3-5 items: RGB (0-255). (255 0 0 is default)
- 6th item: +1 if vector penetrates atom (end goes out both sides); +2 if we add
    atom radius to vector length. 1 is default.

e.g.
```
VECTT
   1  0.350 255   0   0 1
   2  0.350 255   0   0 1
   3  0.350 255   0   0 1
   4  0.350 255   0   0 1
 0 0 0 0 0
```

## SPLAN

Section planes of volumetric data.

Edit Data > Lattice Planes > Add lattice planes

For each row,
- 1st item: Number/index?
- 2-4th items: hkl Miller indices
- 5th item: Distance from origin (Angstrom)
- 6-9th items: Color (RGBA).

Section ends with four `0`'s.

e.g.
```
SPLAN
  1 1.509013E+00 -1.000000E+00 1.014961E+02 5.35356 255   0 255 192
  0   0   0   0
```

## LBLAT

e.g.
```
LBLAT
 -1
```

## LBLSP

e.g.
```
LBLSP
 -1
```

## DLATM
e.g.
```
DLATM
 -1
```
## DLBND
e.g.
```
DLBND
 -1
```
## DLPLY
e.g.
```
DLPLY
 -1
```
## PLN2D
e.g.
```
PLN2D
  0   0   0   0
```

## ATOMT

Atomic/elemental appearance information.

Each row:
- 1st item: Index/number of element.
- 2nd item: Element symbol (see STRUC).
- 3rd item: Atomic radius (Objects > Properties > Atoms > Radius and color)
- 4-6th item: RGB of atom colour (Objects > Properties > Atoms > Radius and color)
- 7-9th item: RGB of something else? Default atom colour?
- 10th item: ?

Ends with a row of 6 zero's.

See SITET. New sites inherit from ATOMT, although SITET overrides the appearance of individual sites.

e.g.
```
ATOMT
  1         Cu  1.2800  34  71 220  34  71 220 204
  0 0 0 0 0 0
```

Default values are derived from `elements.ini`.
- Column 1: atomic number
- Column 2: Elemental symbol
- Column 3: Atomic radius
- Column 4: van der Waals radius
- Column 5: Ionic radius
- Columns 6-8: RGB colour (0-1)
Which radius is used is based on the atomic radii type within ATOMS. Changing this setting through the UI overwrites all existing radii with the appropriate default values.

## SCENE

View of the structure.

This parameter is modified by the view control bar at the top of the GUI window.

- First 4 lines: affine matrix describing the camera angle. Only the first 3x3 elements seem to be used; no translation component appears to be added here via the GUI.
- 5th line: Horizontal and vertical displacement, in units of half the screen width. Default `0.000 0.000`.
- 6th line: Zero. `0.000`.
- 7th line: Zoom, as a multiplier (default `1.000`). (Can also be set indirectly through View > Overall Appearance > Scale.)

e.g.
```
SCENE
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 1.000000  0.000000  0.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.000
```

## HBOND
e.g.
```
HBOND 0 2
```

## STYLE

A newline precedes this section.
No data is directly connected to the STYLE header. However, it appears to serve as a top-level header for various style-related tags.
```

STYLE
```
### DISPF

Miscellaneous display flags, as binary bits.

- +2: "Show models" is true.
- +2048: "Hide non-bonding atoms" is true (Properties > Atoms > Atom style)
- +4096: Enable depth-cueing (View > Overall Appearance > Depth-cueing)
- +8192: Isosurface render from front-to-back (Properties > Isosurfaces).
- +66536: "Show dot surface" is true.
- +131072: "Show as displacement ellispoids" instead of "Show as balls" (Properties > Atoms > Atom style)
- +2097152: Perspective projection (View > Overall Appearance > Projection)
- +33554432: "Scale isotropic atoms by Uiso" (Properties > Atoms > Atom style)

e.g.
```
DISPF 37753794
```
### MODEL

Structural model settings.

- 1st item: Style (integer flag)
  - 0: Ball-and-stick
  - 1: Space-filling
  - 2: Polyhedral
  - 3: Wireframe
  - 4: Stick
- 2nd item: 1 if Show models, 0 if not.
- 3rd item: 1 if Show dot surface, 0 if not.

e.g.
```
MODEL   0  1  0
```
### SURFS
e.g.
```
SURFS   0  1  1
```
### SECTS

Flags for display of sections.

Properties > Sections.

- 1st item: Binary flag of properties. Default `32`.
  - +1 if using "Absolute values" in Sections and slices.
  - +2 if using "Assign colors recursively" in Sections and slices.
  - +8 if SECCL is Y-M-C or C-M-Y.
  - +16 if SECCL is gray scale or rainbow+ or cyclic.
  - +128 if isosurfaces' sections is set to Manual instead of Auto.
- 2nd item: ? Default `1`.

e.g.
```
SECTS  32  1
```
### FORMS
e.g.
```
FORMS   0  1
```
### ATOMS

Atom display settings.

Properties > Atoms > Atom style

- 1st item: Atom radii type. Default 0.
  - 0: Atomic (default)
  - 1: Ionic
  - 2: van der Waals
- 2nd item: 0 if "Show as balls". 1 if "Show as displacement ellipsoids".
- 3rd item: 1: "Scale isotropic atoms by Uiso". 0: "Set radii of isotropic atoms as specified below".

e.g.
```
ATOMS   0  0  1
```
### BONDS
e.g.
```
BONDS   1
```
### POLYS
e.g.
```
POLYS   1
```
### VECTS

Global scaling factor for vectors.

e.g.
```
VECTS 1.000000
```
### FORMP
e.g.
```
FORMP
  1  1.0   0   0   0
```
### ATOMP

Atom style properties.

Properties > Atoms > Atom style.

- 3rd item: True/false 1/0 flag. "Show principal ellipses."
- 4th item: Displacement ellipsoids probability.
- 5th item: Outline width (of principal ellipses).
- 6th item: True/false 1/0 flag. "Hide non-bonding atoms".

e.g.
```
ATOMP
 24  24   0  50  2.0   0
```
### BONDP
e.g.
```
BONDP
  1  16  0.250  2.000 127 127 127
```
### POLYP
e.g.
```
POLYP
 204 1  1.000 180 180 180
```
### ISURF

Isosurfaces.

From Properties > Isosurfaces > Isosurfaces, the table there.

Each row is an isosurface.

- 1st item: index/number?
- 2nd item: mode flag?
- 3rd item: isosurface level.
- 4-6th item: RGB colour of isosurface.
- 7th item: Opacity 1 (0-255)
- 8th item: Opacity 2 (0-255)

e.g.
```
ISURF
1   1    0.55903 255 255   0 127 255
  0   0   0   0
```
### TEX3P
e.g.
```
TEX3P
  1  0.00000E+00  1.00000E+00
```
### SECTP

Section planes, properties.

Objects > Properties > Sections

- 1st item: Whether colour scale is forwards (`1`) or inverted (`-1`) (depends on SECCL).
- 2nd item: Saturation levels minimum
- 3rd item: Saturation levels maximum
- 4th item: Cutoff level, for lattice planes, minimum
- 5th item: Cutoff level, for lattice planes, maximum
- 6th item: Cutoff level, for isosurfaces's sections, minimum
- 7th item: Cutoff level, for isosurfaces's sections, maximum

Reversed colour scales are: R-G-B, Y-M-C, cyclic R-G-B-R, and scales labelled as inverted.

e.g.
```
SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
```
### CONTR
e.g.
```
CONTR
 0.1 -1 1 1 10 -1 2 5
 2 1 2 1
   0   0   0
   0   0   0
   0   0   0
   0   0   0
```
### HKLPP
e.g.
```
HKLPP
 192 1  1.000 255   0 255
```
### UCOLP

Unit cell line properties.

Properties > General > Unit cell

- 1st item: Line style flag. `0` if solid lines (default). `1` if dotted lines. `2` if dashed lines.
- 2nd item: Line visibility flag. `0` if do not show. `1` single unit cell (default). `2` if show all.
- 3rd item: Line width (float), default 1.000.
- 4-6th item: RGB line colour.

e.g.
```
UCOLP
   0   1  1.000   0   0   0
```
### COMPS

Compass settings.

Properties > General > Axes.

Single integer flag.

- 0 : Do not show compass.
- 1 : Show compass and show axes. (Default)
- 2 : Show compass, do not show axes.

e.g.
```
COMPS 1
```
### LABEL
e.g.
```
LABEL 1    12  1.000 0
```
### PROJT

Projection.

View > Overall Appearance > Projection

- 1st item: Flag. 0: Parallel. 1: Perspective. See also DISPF.
- 2nd item: Viewpoint (for perspective). Ranges from 0.5 (far) to 2.0 (close).

e.g.
```
PROJT 0  0.962
```
### BKGRC

Background colour.

View > Overall Appearance > Background Color

R G B

e.g.
```
BKGRC
 255 255 255
```
### DPTHQ

Depth cueing.

View > Overall Appearance > Depth-cueing

- 1st item: 1/0 true/false, Enable depth-cueing. (See DISPF.)
- 2nd item: Starting depth (float, Angstrom).
- 3rd item: Ending depth (float, Angstrom).

e.g.
```
DPTHQ 1 -0.5000  3.5000
```
### LIGHT0

Lighting.

View > Overall Appearance > Light

- LIGHT0 line: true/false 1/0 "Enable lighting".
- 1st-4th lines: Affine rotation matrix for direction of incident light. Identity matrix (default) is from direction of view.
- 5th line: ? Default 0 0 20 0
- 6th line: ? Default 0 0 -1
- 7th line: Ambient, X X X 255, where X is converted from percent to 0-255, rounded to integer.
- 8th line: Diffuse, X X X 255, where X is converted from percent to 0-255, rounded to integer.
- 9th line: 255 255 255 255.

e.g.
```
LIGHT0 1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
  26  26  26 255
 179 179 179 255
 255 255 255 255
```
### LIGHT1
e.g.
```
LIGHT1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
   0   0   0   0
   0   0   0   0
   0   0   0   0
```
### LIGHT2
e.g.
```
LIGHT2
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
   0   0   0   0
   0   0   0   0
   0   0   0   0
```
### LIGHT3
e.g.
```
LIGHT3
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
   0   0   0   0
   0   0   0   0
   0   0   0   0
```
### SECCL

Section colour scheme.

Objects > Properties > Sections > Sections and slices.

Integer flag indicating option.
- 0 : B-G-R
- 1 : R-G-B
- 2 : C-M-Y
- 3 : Y-M-C
- 4 : Gray scale
- 5 : Inverted gray scale
- 6 : Rainbow+
- 7 : Inverted Rainbow+
- 8 : Cyclic: B-G-R-B
- 9 : Cyclic: R-G-B-R
- 10 : Cyclic: Ostwald
- 11 : Cyclic: Inverted Ostwald
- 12 : Cyclic: W-R-K-B-W
- 13 : Cyclic: K-R-W-B-K

e.g.
```
SECCL 0
```

## TEXCL

A blank line precedes and follows this section.

e.g.
```

TEXCL 0

```

## ATOMM

Atom material.

Properties > Atoms > Material

- 1st line: R, G, B, A(? Doesn't change from 255.)
- 2nd line: Shininess, float, percentage x 1.28. (So on scale from 1.280 to 128.000.)

e.g.
```
ATOMM
 204 204 204 255
  25.600
```
## BONDM
e.g.
```
BONDM
 255 255 255 255
 128.000
```
## POLYM
e.g.
```
POLYM
 255 255 255 255
 128.000
```
## SURFM
e.g.
```
SURFM
   0   0   0 255
 128.000
```
## FORMM
e.g.
```
FORMM
 255 255 255 255
 128.000
```
## HKLPM
e.g.
```
HKLPM
 255 255 255 255
 128.000
```