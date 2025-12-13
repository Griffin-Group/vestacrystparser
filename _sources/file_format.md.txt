# The .vesta file format

Herein I have manually reverse-engineered the key features of VESTA's file format.
The specification here is UNOFFICIAL, likely INCOMPLETE, and may contain INACCURACIES. Use with caution. Contributions welcome.

VESTA is a plain-text file.
The amount of whitespace between entries on the same line does not seem to matter, neither does the number of decimal places in floating-point values.

The file has sections marked in all-caps, followed by a series of space- and newline-separated values.

(VESTA_FORMAT_VERSION)=
## #VESTA_FORMAT_VERSION

Metadata tag: version of the VESTA file format.
The files I'm working with are in version 3.5.4.

A blank line follows it.

e.g.
```
#VESTA_FORMAT_VERSION 3.5.4

```

(CRYSTAL)=
## CRYSTAL

Superheader for each crystal Phase (Edit Data > Phases).

No data is associated with this field. However, it can appear multiple times. Following CRYSTAL are the sections from TITLE through to PLN2D inclusive, which contain the data specific to each crystal phase. (This means those sections are not unique.) Additional phases begin with another CRYSTAL header.

Has a blank line before and after it.
```

CRYSTAL

```

(TITLE)=
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

(IMPORT_DENSITY)=
## IMPORT_DENSITY

**Optional section.**

Where to import volumetric density data from.

Edit Data > Volumetric Data > Isosurfaces.

Has an integer after the title, the Interpolation Factor (default 1).

Each line is a relative file path (2nd item, string) and how to add it to the existing data (signed float, 1st item).
If it is prefixed by `x`, it is to multiply the data.
If it is prefixed by `/`, it is to divide the preceding data.

Has an empty line after it.

Angstrom^3 to Bohr^3 has a factor of 0.148185.

Bohr^3 to Angstrom^3 has a factor of 6.748334.

Importing new volumetric data through VESTA resets the isosurface configuration (ISURF).

e.g.
```
IMPORT_DENSITY 1
+1.000000 CHGCAR

```

(GROUP)=
## GROUP

Space group; the symmetry group imposed on the crystal.

e.g.
```
GROUP
1 1 P 1
```

(SYMOP)=
## SYMOP

Symmetry operations associated with GROUP.

e.g.
```
SYMOP
 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1   1
 -1.0 -1.0 -1.0  0 0 0  0 0 0  0 0 0
```

(TRANM)=
## TRANM

e.g.
```
TRANM 0
 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1
```

(LTRANSL)=
## LTRANSL

Translation of this phase with respect to another.

Edit Data > Phase > Positioning

Vesta Manual Section 7.1.

- 1st row: Reference phase (0-indexed). The number in "Place (x,y,z) of this layer at (x,y,z) of layer..." minus 1. If `-1`, is the global coordinate system.
The reference phase must be lower than the current phase.
- 2nd row: x,y,z of this layer; x,y,z of reference layer.
For layers (not global coordinates), the coordinates are in fractional coordinates.

e.g.
```
LTRANSL
 -1
 0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
```

(LORIENT)=
## LORIENT

Relative orientation of this phase with respect to another.

Edit Data > Phase > Orientation

Vesta Manual Section 7.2 (although it's not very clear).

- 1st row:
- - 1st element: Reference phase (0-indexed). If `-1`, is the global coordinate system.
- - 2nd element: This layer's first vector is 0: `[u v w]`, 1: `(h k l)`.
- - 3rd element: Reference layer's first vector is 0: `[u v w]`, 1: `(h k l)`.
- - 4th and 5th element: ??? Maybe parallel vs perpendicular?
- 2nd row: Value of 1st vectors of this and reference layer.
- 3rd row: Value of 2nd vectors of this and reference layer.

If the 2nd vector is not perpendicular to the 1st vector, as given by
`hu + kv + lw = 0`, then the 2nd vector is altered to be perpendicular
before being passed to LMATRIX.
The precise procedure for this is unclear and does not appear to be uniform.
For non-equal vectors, I believe we first normalise the sign then subtract off
the component parallel to the 1st vector.
For parallel vectors, I haven't figured out any consistent pattern.

If a zero vector is provided, then LMATRIX become `nan` in the first 3 columns of all rows.

e.g.
```
LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000
```

(LMATRIX)=
## LMATRIX

Transformation matrix of this phase's coordinate system.

- 1st-4th rows: Affine transformation matrix for the orientation of the phase.
Only the linear component is used.
- 5th row: 3 floats, translation. Is the (x,y,z) of the global coordinates minus the (x,y,z) of this phase, as specified in `LTRANSL`, in global Cartesian coordinates.
The default orientation of a phase is set so that [1 0 0] axis is parallel to x and the [0 1 0] axis is in the x-y plane.

For orientation, transform to Cartesian (?), normalise all vectors, construct the third vector from the cross product of 1st and 2nd, then
`LMATRIX = {v1, v2, v1xv2}_global @ {v1, v2, v1xv2}_local^-1`
(TODO: Test with non-cubic cell.)

For translation, (x,y,z)_global - CELL @ (x,y,z)_local.
(TODO: Check with non-trivial orientation.)

e.g.
```
LMATRIX
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000
```

(CELLP)=
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

(STRUC)=
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

(THERI)=
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

(THERT)=
## THERT

**Optional section.**

Anisotropic thermal type.

Appears when Structure Parameters > Anisotropic is not None.

Single integer flag. `0` if units of U, `1` if units of beta.

e.g.
```
THERT 0
```

(THERM)=
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

(SHAPE)=
## SHAPE

e.g.
```
SHAPE
  0       0       0       0   0.000000  0   192   192   192   192
```

(BOUND)=
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

(SBOND)=
## SBOND

Bonding information.
Lists pairs of elements and specifications for when and how to draw bonds between them.

Geometry edited in Edit > Bonds.

Appearance edited in Properties > Bonds > Radius and color. Edits all existing bonds at once, but not any new ones strangely enough.

Also Objects > Bonds.

Search mode:
1. Search A2 bonded to A1 (boundary mode defaults to 2)
2. Search atoms bonded to A1 (sets A2 to `XX`) (boundary mode defaults to 2)
3. Search molecules (sets A1 and A2 to `XX`) (boundary mode defaults to 3)

Boundary mode:
1. Do not search atoms beyond the boundary.
2. Search additional atoms if A1 is included in the boundary.
3. Search additional atoms recursively if either A1 or A2 is visible.

Style:
1. Unicolor cylinder
2. Bicolor cylinder (default for standard bonds)
3. Color line
4. Gradient line
5. Dotted line
6. Dashed line (default for hydrogen bonds)

Each row:
- 1st item: Index.
- 2nd item: A1 (Atom 1).
- 3rd item: A2 (Atom 2).
- 4th item: Minimum length.
- 5th item: Maximum length.
- 6th item: Search mode - 1.
- 7th item: Boundary mode - 1.
- 8th item: Show polyhedra, 0/1.
- 9th item: Search by label, 0/1. If 1, A1 and A2 are site labels rather than element symbols.
- 10th item: Style - 1.
- 11th item: Radius (cylinder). Default `0.250`.
- 12th item: Width (line). Default `2.000`. Units px.
- 13th-15th items: Bond color (RGB) (may be overridden by atom colours depending on bond style). (Default `127 127 127`, but can be edited individually in Objects > Bonds.)

Block ends with four `0`'s.

e.g.
```
SBOND
  1     B     N    0.00000    1.93846  0  1  1  0  1  0.250  2.000 127 127 127
  0 0 0 0
```

(SITET)=
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

(VECTR)=
## VECTR

Vectors to draw on the atoms.

There are multiple blocks, one for each vector specification, which may be attached to multiple atoms. Each block is terminated by five `0`'s.
The whole section is terminated by another row of five `0`'s.

In each block:
- 1st row:
  - 1st item: vector index.
  - 2nd-4th items: vector coordinates, modulus along crystallographic axes (i.e. a basis of unit vectors parallel to the lattice vectors). (default 0 0 c-axis-length)
  - 5th item: 0/1 axial/polar vector. (default 0)
- 2nd+ rows (optional):
  - 1st item: site index to attach this vector to.
  - 2nd item: 0 if crystallographic site, 1+ if individual site (default 0). Values >1 occur for symmetric images under symmetry group transformation (e.g. If you have P2, and a site with structure parameter (0.2,0,0), then you have an image at (-0.2,0,0); that site would have a value of 2 here.).
  - 3rd-5th items: Number of unit cells/lattice vectors away from the original site, in x, y, and z directions (default 0,0,0).

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

(VECTT)=
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

(SPLAN)=
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

(LBLAT)=
## LBLAT

e.g.
```
LBLAT
 -1
```

(LBLSP)=
## LBLSP

e.g.
```
LBLSP
 -1
```

(DLATM)=
## DLATM

Delete/hides the specified atoms. Objects > Atoms.

However, the atoms are not indexed by the expected indices. Instead, they are indexed by an internal index, which has a unique 0-based index for every single atom, including those in adjacent unit cells.
It seems to be sorted by site. So first the index exhausts all atoms of the first site type, then the second, and so on. So a single site has a continuous set of indices.

Format: a list of integers (indices), terminated with a `-1`.

e.g.
```
DLATM
 1 2 3  -1
```
(DLBND)=
## DLBND

Deletes/hides the specified bonds. Objects > Bonds.

However, as for DLATM, the indices are different to the usual indices, instead with each drawn object being given a different 0-based index.

Format: a list of integers (indices), terminated with a `-1`.

e.g.
```
DLBND
 -1
```
(DLPLY)=
## DLPLY
e.g.
```
DLPLY
 -1
```
(PLN2D)=
## PLN2D
e.g.
```
PLN2D
  0   0   0   0
```

(ATOMT)=
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

(SCENE)=
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

(HBOND)=
## HBOND
e.g.
```
HBOND 0 2
```

(STYLE)=
## STYLE

A newline precedes this section.
No data is directly connected to the STYLE header. However, it appears to serve as a top-level header for various style-related tags.
```

STYLE
```
(DISPF)=
## DISPF

Miscellaneous display flags, as binary bits.

- +2: "Show models" is true.
- +2048: "Hide non-bonding atoms" is true (Properties > Atoms > Atom style)
- +4096: Enable depth-cueing (View > Overall Appearance > Depth-cueing)
- +8192: Isosurface render from front-to-back (Properties > Isosurfaces).
When true, isosurfaces in front occlude those behind. Default false.
- +66536: "Show dot surface" is true.
- +131072: "Show as displacement ellispoids" instead of "Show as balls" (Properties > Atoms > Atom style)
- +2097152: Perspective projection (View > Overall Appearance > Projection)
- +33554432: "Scale isotropic atoms by Uiso" (Properties > Atoms > Atom style)

e.g.
```
DISPF 37753794
```
(MODEL)=
## MODEL

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
(SURFS)=
## SURFS
e.g.
```
SURFS   0  1  1
```
(SECTS)=
## SECTS

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
(FORMS)=
## FORMS
e.g.
```
FORMS   0  1
```
(ATOMS)=
## ATOMS

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
(BONDS)=
## BONDS
e.g.
```
BONDS   1
```
(POLYS)=
## POLYS
e.g.
```
POLYS   1
```
(VECTS)=
## VECTS

Global scaling factor for vectors.

Edit > Vectors > Scale factor for modulus

e.g.
```
VECTS 1.000000
```
(FORMP)=
## FORMP
e.g.
```
FORMP
  1  1.0   0   0   0
```
(ATOMP)=
## ATOMP

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
(BONDP)=
## BONDP

Bond style properties.

Properties > Bonds > Resolution

Properties > Bonds > Radius and color

Strangely, the radius and color data seem to be ignored when creating new bonds in favour of the defaults in style.ini.

- 1st item: Resolution > Stacks
- 2nd item: Resolution > Slices
- 3rd item: Radius and color > Radius (cylinder)
- 4th item: Radius and color > Width (line)
- 5-7th items: Radius and color > Color; RGB.

e.g.
```
BONDP
  1  16  0.250  2.000 127 127 127
```
(POLYP)=
## POLYP
e.g.
```
POLYP
 204 1  1.000 180 180 180
```
(ISURF)=
## ISURF

Isosurfaces.

From Properties > Isosurfaces > Isosurfaces, the table there.

Each row is an isosurface.

- 1st item: Index.
- 2nd item: Mode flag. 0: Positive and negative; 1: Positive; 2: Negative
- 3rd item: Isosurface level.
- 4-6th item: RGB colour of isosurface.
- 7th item: Opacity 1 (0-255), of polygons parallel to the screen.
- 8th item: Opacity 2 (0-255), of polygons perpendicular to the screen.

Terminates with four 0's.

e.g.
```
ISURF
1   1    0.55903 255 255   0 127 255
  0   0   0   0
```
(TEX3P)=
## TEX3P
e.g.
```
TEX3P
  1  0.00000E+00  1.00000E+00
```
(SECTP)=
## SECTP

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
(CONTR)=
## CONTR
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
(HKLPP)=
## HKLPP
e.g.
```
HKLPP
 192 1  1.000 255   0 255
```
(UCOLP)=
## UCOLP

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
(COMPS)=
## COMPS

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
(LABEL)=
## LABEL
e.g.
```
LABEL 1    12  1.000 0
```
(PROJT)=
## PROJT

Projection.

View > Overall Appearance > Projection

- 1st item: Flag. 0: Parallel. 1: Perspective. See also DISPF.
- 2nd item: Viewpoint (for perspective). Ranges from 0.5 (far) to 2.0 (close).

e.g.
```
PROJT 0  0.962
```
(BKGRC)=
## BKGRC

Background colour.

View > Overall Appearance > Background Color

R G B

e.g.
```
BKGRC
 255 255 255
```
(DPTHQ)=
## DPTHQ

Depth cueing.

View > Overall Appearance > Depth-cueing

- 1st item: 1/0 true/false, Enable depth-cueing. (See DISPF.)
- 2nd item: Starting depth (float, Angstrom).
- 3rd item: Ending depth (float, Angstrom).

e.g.
```
DPTHQ 1 -0.5000  3.5000
```
(LIGHT0)=
## LIGHT0

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
(LIGHT1)=
## LIGHT1
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
(LIGHT2)=
## LIGHT2
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
(LIGHT3)=
## LIGHT3
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
(SECCL)=
## SECCL

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

(TEXCL)=
## TEXCL

A blank line precedes and follows this section.

e.g.
```

TEXCL 0

```

(ATOMM)=
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
(BONDM)=
## BONDM
e.g.
```
BONDM
 255 255 255 255
 128.000
```
(POLYM)=
## POLYM
e.g.
```
POLYM
 255 255 255 255
 128.000
```
(SURFM)=
## SURFM
e.g.
```
SURFM
   0   0   0 255
 128.000
```
(FORMM)=
## FORMM
e.g.
```
FORMM
 255 255 255 255
 128.000
```
(HKLPM)=
## HKLPM
e.g.
```
HKLPM
 255 255 255 255
 128.000
```