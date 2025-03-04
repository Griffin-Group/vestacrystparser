# The .vesta file format

Herein I have manually reverse-engineered the key features of VESTA's file format.
VESTA is a plain-text file.
The amount of whitespace between entries on the same line does not seem to matter, neither does the number of decimal places in floating-point values.

The file has sections marked in all-caps, followed by a series of space- and newline-separated values.
The sections appear to be the same between all files, even when nominally unused.

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

e.g.
```
STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0
```

## THERI

e.g.
```
THERI 1
  1         Cu  0.050000
  0 0 0
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

e.g.
```
SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  0 0 0 0 0 0
```

## VECTR

## VECTT

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

e.g.
```
ATOMT
  1         Cu  1.2800  34  71 220  34  71 220 204
  0 0 0 0 0 0
```

## SCENE
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