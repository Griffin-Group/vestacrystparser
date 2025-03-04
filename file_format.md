# The .vesta file format

Herein I have manually reverse-engineered the key features of VESTA's file format.
The specification here is UNOFFICIAL, likely INCOMPLETE, and may contain INACCURACIES. Use with caution. Contributions welcome.

VESTA is a plain-text file.
The amount of whitespace between entries on the same line does not seem to matter, neither does the number of decimal places in floating-point values.

The file has sections marked in all-caps, followed by a series of space- and newline-separated values.

## #VESTA_FORMAT_VERSION

Metadata tag: version of the VESTA file format.
The files I'm working with are in version 3.5.4.

e.g.
```
#VESTA_FORMAT_VERSION 3.5.4
```

## CRYSTAL

No data is associated with this field. It appears to be a super-header.
Has a blank line after it.
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

e.g.
```
SPLAN
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
- 1st item: ?
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

## SCENE

View of the structure.

This parameter is modified by the view control bar at the top of the GUI window.

- First 4 lines: affine matrix describing the camera angle. Only the first 3x3 elements seem to be used; no translation component appears to be added here via the GUI.
- 5th line: Horizontal and vertical displacement, in units of half the screen width. Default `0.000 0.000`.
- 6th line: Zero. `0.000`.
- 7th line: Zoom, as a multiplier (default `1.000`).

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
e.g.
```
DISPF 37753794
```
### MODEL
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
e.g.
```
ISURF
  0   0   0   0
```
### TEX3P
e.g.
```
TEX3P
  1  0.00000E+00  1.00000E+00
```
### SECTP
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
e.g.
```
UCOLP
   0   1  1.000   0   0   0
```
### COMPS
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
e.g.
```
PROJT 0  0.962
```
### BKGRC
e.g.
```
BKGRC
 255 255 255
```
### DPTHQ
e.g.
```
DPTHQ 1 -0.5000  3.5000
```
### LIGHT0
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