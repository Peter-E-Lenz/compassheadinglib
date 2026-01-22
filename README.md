# CompassHeadingLib

<span style="font-variant: small-caps">CompassHeadingLib</span> is a small, dependency-free, pure python library for working with compass headings in terms of comparison and transformation between decimal degree and natural language space. While it originally only supported English, it now supports multiple languages.

<span style="font-variant: small-caps">CompassHeadingLib</span> follows the [worse is better](https://en.wikipedia.org/wiki/Worse_is_better) design philosophy; it's better to have a slower less featureful implementation than no implementation at all. Optimizations will be executed when we have to.

## License

<span style="font-variant: small-caps">CompassHeadingLib</span> is licensed under the MIT License and offered as is without warranty of any kind, express or implied. 

## Installation

### From PyPi
`pip install -u compassheadinglib`

### From Git
`pip install pip@git+https://github.com/Peter-E-Lenz/compassheadinglib/`

## Usage

## Basic Usage

### Importing the Library

```python
# Import with default English language support
from compassheadinglib import Compass

# Or import with specific language support
from compassheadinglib.fr import Compass  # French
from compassheadinglib.de import Compass  # German
from compassheadinglib.es import Compass  # Spanish
```

### Creating a Compass Object

```python
compass = Compass()
```

## Finding Headings from Bearings

### Basic Heading Lookup

```python
# Find the closest heading for a given bearing (in decimal degrees)
heading = compass.findHeading(45.0)
print(heading.name)        # "Northeast"
print(heading.abbr)        # "NE" 
print(heading.azimuth)     # 45.0
print(heading.order)       # 2

# You can also call the compass object directly
heading = compass(45.0)    # Same as compass.findHeading(45.0)
```

### Specifying Heading Precision with Order

```python
bearing = 80.0

# Order 1: Cardinal directions only (N, E, S, W)
heading_order1 = compass.findHeading(bearing, order=1)
print(heading_order1.name)  # "East"

# Order 2: Half-winds (NE, SE, SW, NW)
heading_order2 = compass.findHeading(bearing, order=2)
print(heading_order2.name)  # "East"

# Order 3: Quarter-winds (default)
heading_order3 = compass.findHeading(bearing, order=3)
print(heading_order3.name)  # "East-Northeast"

# Order 4: Eighth-winds (most precise)
heading_order4 = compass.findHeading(bearing, order=4)
print(heading_order4.name)  # "East by North"
```

## Rotating Headings

### Basic Rotation with Wraparound

```python
# Start with a North heading
north = compass.findHeading(0.0)
print(north.name)  # "North"

# Rotate 45 degrees clockwise
northeast = north.rotate(45)
print(northeast.name)  # "Northeast"

# Rotate 90 degrees counter-clockwise
west = north.rotate(-90)
print(west.name)  # "West"

# Rotation automatically wraps around
north_by_west = north.rotate(-30)
print(north_by_west.name)      # "North by West"
print(north_by_west.azimuth)   # 330.0 (wraps from -30 to 330)

# Large rotations also wrap
east_northeast = north.rotate(405)  # 405° = 45° after wrapping
print(east_northeast.name)     # "Northeast"
```

### Using Nautical Terminology

```python
# Start with an East heading
east = compass.findHeading(90.0)

# Turn to starboard (right/clockwise)
southeast = east.starboard(45)
print(southeast.name)  # "Southeast"

# Turn to port (left/counter-clockwise)
northeast = east.port(45)
print(northeast.name)  # "Northeast"

# Wraparound examples
north = compass.findHeading(0.0)
northwest = north.port(45)      # 0° - 45° = 315° (wraps around)
print(northwest.name)           # "Northwest"

west = compass.findHeading(270.0)
northeast = west.starboard(135)  # 270° + 135° = 405° → 45° (wraps around)
print(northeast.name)           # "Northeast"
```

### Using Land-based Terminology

```python
# Same functionality with familiar left/right terms
east = compass.findHeading(90.0)

# Turn right (clockwise)
southeast = east.right(45)
print(southeast.name)  # "Southeast"

# Turn left (counter-clockwise)
northeast = east.left(45)
print(northeast.name)  # "Northeast"
```

## Arithmetic Operations

### Adding and Subtracting Headings

```python
compass = Compass()

# Create some headings
north = compass(0)      # 0°
east = compass(90)      # 90°
south = compass(180)    # 180°
west = compass(270)     # 270°

# Add headings (adds their azimuth values)
result1 = north + east  # 0° + 90° = 90°
print(result1.name)     # "East"

# Add degrees to headings
northeast = north + 45  # 0° + 45° = 45°
print(northeast.name)   # "Northeast"

# Reverse addition works too
northeast2 = 45 + north # Same as above
print(northeast2.name)  # "Northeast"

# Subtract headings
result2 = east - north  # 90° - 0° = 90°
print(result2.name)     # "East"

# Subtract degrees from headings
northwest = north - 45  # 0° - 45° = 315° (wraps around)
print(northwest.name)   # "Northwest"

# Reverse subtraction
result3 = 360 - east    # 360° - 90° = 270°
print(result3.name)     # "West"

# Wraparound examples
west_by_north = west + 45   # 270° + 45° = 315°
print(west_by_north.name)   # "Northwest"

south_by_east = south - 45  # 180° - 45° = 135°
print(south_by_east.name)   # "Southeast"
```

## Comparing Headings with Circular Logic

Heading objects support comparison operators (`<`, `>`, `<=`, `>=`, `==`, `!=`) that understand circular/compass logic. Unlike standard numeric comparisons, these operators recognize that compass headings wrap around at 360°/0°.

### How Circular Comparisons Work

The comparison logic determines which heading comes "first" when moving clockwise around the compass:

- `heading_a < heading_b` is True if heading_b is less than or equal to 180° clockwise from heading_a
- `heading_a > heading_b` is True if heading_b is more than 180° clockwise (i.e., counter-clockwise is shorter)

```python
compass = Compass()

# Simple case: both in same quadrant
north = compass(0)
east = compass(90)
print(north < east)     # True (90° is 90° clockwise from 0°)
print(east > north)     # True (same comparison, reversed)

# Wraparound case: comparing across 0°/360° boundary
northwest = compass(350)
northeast = compass(10)
print(northwest < northeast)  # True (10° is 20° clockwise from 350°)
print(northeast > northwest)  # True

# The "wrong way" around is False
print(northeast < northwest)  # False (would be 340° clockwise)

# Edge case: exactly 180° apart
north = compass(0)
south = compass(180)
print(north < south)    # True (180° is exactly 180° clockwise)
print(south < north)    # True (0° is exactly 180° clockwise from 180°)
# Both are "less than" each other at exactly 180° separation!

# Equality works as expected
north1 = compass(0)
north2 = compass(0)
print(north1 == north2)  # True
print(north1 <= north2)  # True
print(north1 >= north2)  # True
```

### Practical Uses for Circular Comparisons

```python
compass = Compass()

# Determining if a turn is "ahead" or "behind"
current_heading = compass(350)
target_heading = compass(10)

if current_heading < target_heading:
    print("Target is clockwise - turn right/starboard")
else:
    print("Target is counter-clockwise - turn left/port")

# Finding which of two headings is further clockwise
heading_a = compass(350)
heading_b = compass(340)
heading_c = compass(10)

if heading_b > heading_a:
    print("B is counter-clockwise from A")
if heading_c > heading_a:
    print("C is clockwise from A")
```

### Important Notes on Circular Comparisons

- Comparisons are **not transitive** in the usual mathematical sense due to wraparound
- At exactly 180° separation, both directions can be considered "less than" each other
- These comparisons are designed for navigation and angular relationships, not for sorting in the traditional sense
- For working with collections of headings, use the `Sector` class which handles circular sorting correctly

## Working with Multiple Headings: The Sector Class

The `Sector` class is designed for working with collections of compass headings. It provides circular-aware sorting, statistical methods, and bulk operations that properly handle the wraparound nature of compass directions.

### Creating a Sector

Sectors must be created using the `Compass.sector()` method, which ensures they have the proper parent Compass reference:

```python
compass = Compass()

# Create an empty sector
sector = compass.sector()

# Create a sector with initial headings
headings = [compass(0), compass(90), compass(180)]
sector = compass.sector(headings)

# Add headings to a sector
sector = compass.sector()
sector.append(compass(45))          # Append a Heading object
sector.append(135)                  # Append a numeric bearing (gets converted)
sector.append(compass.findHeading(270, order=2))  # Append specific order heading
```

### Circular-Aware Sorting

The `Sector.sort()` method sorts headings clockwise from the minimum heading, properly handling wraparound:

```python
compass = Compass()
sector = compass.sector()

# Add headings in random order
sector.append(180)
sector.append(90)
sector.append(270)
sector.append(0)

# Sort them (clockwise from minimum)
sector.sort()

# They're now in clockwise order starting from the minimum
for h in sector:
    print(f"{h.name}: {h.azimuth}°")
# Output:
# North: 0.0°
# East: 90.0°
# South: 180.0°
# West: 270.0°
```

Sorting with wraparound is handled automatically:

```python
compass = Compass()
sector = compass.sector()

# Add headings that wrap around 0°
sector.append(10)    # Just past North
sector.append(350)   # Just before North
sector.append(5)     # Very close to North

sector.sort()

# Sorted clockwise from minimum (350°)
for h in sector:
    print(f"{h.azimuth}°")
# Output (approximately):
# 348.75° (North by West - closest to 350)
# 0.0° (North - closest to 5)  
# 11.25° (North by East - closest to 10)
```

### Finding Minimum and Maximum Headings

The `min()` and `max()` methods find the start and end of the smallest arc containing all headings:

```python
compass = Compass()
sector = compass.sector([compass(90), compass(120), compass(180)])

# Minimum is the start of the smallest containing arc
min_heading = sector.min()
print(min_heading.name)  # "East" (90°)

# Maximum is the furthest heading clockwise from minimum
max_heading = sector.max()
print(max_heading.name)  # "South" (180°)

# With wraparound
sector2 = compass.sector()
sector2.append(350)
sector2.append(10)
sector2.append(30)

min_heading = sector2.min()  # Start of arc (≈350°)
max_heading = sector2.max()  # End of arc (≈30°)
print(f"Arc from {min_heading.azimuth}° to {max_heading.azimuth}°")
```

### Arithmetic Operations on Sectors

Sectors support arithmetic operations that apply to all headings in the collection:

```python
compass = Compass()

# Create a sector with several headings
sector = compass.sector([compass(0), compass(90), compass(180)])

# Add degrees to all headings (rotate all clockwise)
rotated = sector + 45
for h in rotated:
    print(f"{h.azimuth}°")  # 45°, 135°, 225°

# Subtract degrees (rotate all counter-clockwise)
counter_rotated = sector - 45
for h in counter_rotated:
    print(f"{h.azimuth}°")  # 315°, 45°, 135°

# Add a heading to all headings in the sector
northeast = compass(45)
result = sector + northeast
for h in result:
    print(f"{h.azimuth}°")  # 45°, 135°, 225°

# Reverse operations also work
result2 = 90 + sector  # Add 90° to each heading
result3 = 360 - sector  # Subtract each heading from 360°

# Concatenate two sectors
sector1 = compass.sector([compass(0), compass(90)])
sector2 = compass.sector([compass(180), compass(270)])
combined = sector1 + sector2
print(len(combined))  # 4 headings
```

### Navigation Methods for Sectors

Apply nautical/land-based turns to all headings at once:

```python
compass = Compass()
sector = compass.sector([compass(0), compass(90), compass(180)])

# Turn all headings to port (left/counter-clockwise)
port_sector = sector.port(45)
for h in port_sector:
    print(f"{h.name}: {h.azimuth}°")
# Northwest: 315°, Northeast: 45°, Southeast: 135°

# Turn all headings to starboard (right/clockwise)
starboard_sector = sector.starboard(45)
for h in starboard_sector:
    print(f"{h.name}: {h.azimuth}°")
# Northeast: 45°, Southeast: 135°, Southwest: 225°

# Aliases
left_sector = sector.left(30)     # Same as port
right_sector = sector.right(30)   # Same as starboard
```

### Statistical Methods

Sectors provide circular statistics for analyzing heading distributions:

```python
compass = Compass()
sector = compass.sector()
sector.append(0)
sector.append(90)
sector.append(180)
sector.append(270)

# Circular mean (average direction)
mean_heading = sector.mean()
print(f"Mean heading: {mean_heading}°")

# Circular median
median_heading = sector.median()
print(f"Median heading: {median_heading}°")

# Relative bearings from minimum
relatives = sector.relative_bearings()
print(f"Relative bearings: {relatives}")
# Shows clockwise offset of each heading from the minimum
```

The circular mean is especially useful for averaging headings that might wrap around:

```python
compass = Compass()

# Average of headings near North (wraps around 0°/360°)
sector = compass.sector([compass(350), compass(10)])
mean = sector.mean()
print(f"Mean of 350° and 10°: {mean}°")  # Approximately 0° (North)

# This is different from arithmetic mean which would give 180°!
arithmetic_mean = (350 + 10) / 2  # 180° - wrong!
print(f"Arithmetic mean (incorrect): {arithmetic_mean}°")
```

### Translating Sectors

Translate all headings in a sector to another language:

```python
compass = Compass()
sector_en = compass.sector([compass(0), compass(90), compass(180)])

# Translate entire sector to French
sector_fr = sector_en.translate('FR')
for h in sector_fr:
    print(h.name)
# Nord, Est, Sud

# Translate to German
sector_de = sector_en.translate('DE')
for h in sector_de:
    print(h.name)
# Nord, Ost, Süd
```

### Practical Examples with Sectors

#### Analyzing a Set of Observed Bearings

```python
compass = Compass()

# Collection of observed bearings to a landmark
observations = [355, 2, 358, 5, 1, 359]
sector = compass.sector()
for bearing in observations:
    sector.append(bearing)

# Get statistics
mean_bearing = sector.mean()
print(f"Mean bearing: {mean_bearing:.1f}°")

# Sort to see the spread
sector.sort()
min_obs = sector.min()
max_obs = sector.max()
print(f"Observations span from {min_obs.azimuth}° to {max_obs.azimuth}°")
```

#### Planning a Route with Multiple Waypoints

```python
compass = Compass()

# Initial course headings for each leg
route = compass.sector([compass(45), compass(90), compass(135)])

# Apply a constant wind correction to all legs
wind_correction = -10  # 10° to port
corrected_route = route + wind_correction

print("Corrected headings:")
for i, heading in enumerate(corrected_route):
    print(f"Leg {i+1}: {heading.name} ({heading.azimuth}°)")

# Find the mean heading of the route
average_heading = corrected_route.mean()
print(f"Average course: {average_heading:.1f}°")
```

#### Working with a Search Pattern

```python
compass = Compass()

# Define a search pattern (8 radial directions)
pattern = compass.sector()
for angle in range(0, 360, 45):
    pattern.append(angle)

# Rotate the entire pattern by 22.5° for better coverage
rotated_pattern = pattern + 22.5

# Sort to get clockwise search order
rotated_pattern.sort()

print("Search pattern (clockwise):")
for heading in rotated_pattern:
    print(f"- {heading.name} ({heading.azimuth}°)")
```

## Working with Multiple Languages

### Translating Headings

```python
# Start with English compass
from compassheadinglib import Compass
compass = Compass()

# Get a heading in English
north_en = compass.findHeading(0.0)
print(north_en.name)  # "North"

# Translate to other languages
north_fr = north_en.translate('FR')
print(north_fr.name)  # "Nord" (French)

north_de = north_en.translate('DE')  
print(north_de.name)  # "Nord" (German)

north_es = north_en.translate('ES')
print(north_es.name)  # "Norte" (Spanish)
```

### Using Language-Specific Compasses

```python
# Create compass objects for different languages
from compassheadinglib.fr import Compass as CompassFR
from compassheadinglib.de import Compass as CompassDE

compass_fr = CompassFR()
compass_de = CompassDE()

# Get headings directly in different languages
heading_fr = compass_fr.findHeading(45.0)
print(heading_fr.name)  # "Nord-Est" (French)

heading_de = compass_de.findHeading(45.0)
print(heading_de.name)  # "Nordost" (German)
```

### Language Support

To use a specific language import the library as import compassheadinglib.<language-two-letter-code>, i.e. to have Korean language support use `from compassheadinglib.kr import Compass` or to use Portuguese use `from compassheadinglib.pt import Compass`. Because the library was originally available with only English language support `from compassheadinglib import Compass` is equivalent to `from  compassheadinglib.en import Compass`.

| Language | Two letter code |
| ---- | ------- |
| ar | Arabic |
| cn | Chinese |
| de | German |
| en | English |
| es | Spanish |
| fr | French |
| hi | Hindi |
| jp | Japanese |
| kr | Korean |
| pt | Portuguese |

Unfortunately the developer of this library is an English monoglot. Translations were achieved via machine. The developer apologizes for any mistakes in those translations - corrections are graciously accepted.

## Dependencies

<span style="font-variant: small-caps">CompassHeadingLib</span> has only dependencies from Python's standard library.
It was originally written to run on Python 2.7 but is now only tested on Python 3.7+. 

# API Reference

## Compass Object

The primary interface for working with compass headings.

### Compass(Float *heading*, Int *order* = 3)
### Compass.findHeading(Float *heading*, Int *order* = 3)

| Type | Returns |
| ---- | ------- |
| Object(based on Dict)| Heading |

These functions take a heading between two points as a float (i.e. in decimal degrees) and returns the best matching heading with `order` degree of specificity. `Order` is a 1-indexed description of how specific the natural language heading should be. The higher the order the more specific the heading. At an `order` of 1 the decimal degree heading of 80.0 will return a heading object of 'East' while at an `order` of 4 it would return 'East by North' heading object. 

Internally, calling the Compass object directly will silently call its `findHeading` method.

### Compass.sector(List *headings* = None)

| Type | Returns |
| ---- | ------- |
| Sector | Sector object |

Creates and returns a new Sector object with this Compass as its parent. The optional `headings` parameter can be a list of Heading objects to initialize the sector. This is the proper way to create Sector objects, as they require a parent Compass reference for proper functionality.

Example:
```python
# Create empty sector
sector = compass.sector()

# Create sector with initial headings
sector = compass.sector([compass(0), compass(90), compass(180)])
```

## Heading Object

Heading objects are returned by Compass objects and are not intended to be created by end users.

| Type | Returns |
| ---- | ------- |
| Object| N/A|

Heading objects are containers for information about headings that are designed to be comparable to each other (and other python objects) using built-in methods. There are four pieces of information for each heading, each a method of the object: `name`, `abbr`, `azimuth`, and `order`. The various built-in comparisons look to different methods (and thus different pieces of the information) as appropriate. For the most part you can safely ignore all this background stuff.

### Heading.name

| Type | Returns |
| ---- | ------- |
| string| string|

The full name of this heading, along the lines of 'North' or 'South by East'.
Note: despite what the festival has told you there is no such heading as 'South by Southwest'.

### Heading.abbr

| Type | Returns |
| ---- | ------- |
| string| string|

The abbreviated name of this heading, along the lines of 'N' or 'SbE'

### Heading.azimuth

| Type | Returns |
| ---- | ------- |
| float| float|

The decimal degree value of this heading. For example; 'West' is 270.0 while 'North-Northeast' is 22.5

### Heading.order

| Type | Returns |
| ---- | ------- |
| integer| integer|

Order defines how specific the heading is. The cardinal directions ('North', 'East', 'South' & 'West') are of order 1 while 'South by East' is order 4. The Compass Headings Reference chart at the end of this document will be more illustrative of this difference.

Put another way: order 1 headings are 90° apart, order 2 headings are 45° apart, order 3 headings are 22.5° apart, and order 4 headings are 11.25° apart. By default this library uses order 3 wherever that value can be specified. Each order includes the headings of that order and all headings of any lower valued orders. Hence order 2 includes all headings labeled order 2 and order 1.

When treated as a string the Heading object returns the value for the `name` method.
When treated as a numeric (regardless of int or float) it will return the value for the `azimuth` method.

### Arithmetic Operations

Heading objects support addition and subtraction operations that work with their azimuth values:

- **Adding headings**: `heading1 + heading2` adds their azimuth values
- **Adding degrees**: `heading + 45` or `45 + heading` adds degrees to the heading
- **Subtracting headings**: `heading1 - heading2` subtracts their azimuth values  
- **Subtracting degrees**: `heading - 30` subtracts degrees from the heading
- **Reverse subtraction**: `360 - heading` subtracts the heading's azimuth from a number

All arithmetic operations automatically wrap around to keep results within 0-360°.

Examples:
```python
north = compass(0)      # 0°
east = compass(90)      # 90°

northeast = north + east    # 0° + 90° = 90° (East)
southeast = east + 45       # 90° + 45° = 135° (Southeast)
northwest = north - 45      # 0° - 45° = 315° (Northwest, wraps around)
```

### Comparison Operators

Heading objects support circular comparison operators (`<`, `>`, `<=`, `>=`, `==`, `!=`) that understand wraparound:

- `heading_a < heading_b`: True if heading_b is ≤180° clockwise from heading_a
- `heading_a > heading_b`: True if heading_b is >180° clockwise from heading_a (counter-clockwise is shorter)
- `heading_a == heading_b`: True if both headings have the same azimuth

See the "Comparing Headings with Circular Logic" section for detailed examples.

### Heading.translate(String *lang*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Returns a new Heading object with the name and abbreviation translated to the specified language. The language parameter should be the two-letter language code (e.g., 'EN', 'FR', 'DE'). The azimuth, order, and other properties remain unchanged. This method allows you to get the same compass heading in different languages while maintaining all the mathematical properties.

Example: `north_heading.translate('FR')` would return a Heading object with French names for the same compass direction.

### Heading.rotate(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading by the specified number of degrees and returns a new Heading object for the resulting direction. Positive degrees rotate clockwise, negative degrees rotate counter-clockwise. The resulting azimuth automatically wraps around to stay within 0-360°. This method calls the parent Compass object to find the appropriate heading for the new azimuth.

Example: `north_heading.rotate(45)` would return a Northeast heading. `north_heading.rotate(-30)` would return a heading at 330° (North-Northwest).

### Heading.starboard(Float *degrees*)
### Heading.right(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading to starboard (right/clockwise) by the specified number of degrees. The degrees parameter must be non-negative (>= 0). The resulting azimuth automatically wraps around to stay within 0-360°. Returns a new Heading object for the resulting direction. `right()` is an alias for `starboard()` for those more familiar with land-based terminology.

Example: `north_heading.starboard(90)` would return an East heading. `west_heading.starboard(135)` would return a Northeast heading (270° + 135° = 405°, wraps to 45°).

### Heading.port(Float *degrees*)
### Heading.left(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading to port (left/counter-clockwise) by the specified number of degrees. The degrees parameter must be non-negative (>= 0). The resulting azimuth automatically wraps around to stay within 0-360°. Returns a new Heading object for the resulting direction. `left()` is an alias for `port()` for those more familiar with land-based terminology.

Example: `east_heading.port(45)` would return a Northeast heading. `north_heading.port(30)` would return a heading at 330° (0° - 30°, wraps to 330°).

### Heading.asDict()

| Type | Returns |
| ---- | ------- |
| dict| dictionary|

Returns a dictionary representation of the Heading object containing the core properties (name, abbr, azimuth, order) but excluding the langs and parent references. This is useful for serialization or when you need a simple data structure representation of the heading.

## Sector Object

A Sector is a collection of Heading objects that provides circular-aware operations and statistics. Sectors extend Python's list class and must be created using `Compass.sector()`.

### Creating Sectors

Sectors should always be created via the Compass object:

```python
sector = compass.sector()                    # Empty sector
sector = compass.sector([heading1, heading2]) # With initial headings
```

### Sector.append(Heading or Number *item*)

| Type | Returns |
| ---- | ------- |
| None | None |

Appends a heading to the sector. Accepts either a Heading object or a numeric bearing (which will be converted to a Heading using the parent Compass). Raises TypeError if the item is neither a Heading nor a numeric type.

Example:
```python
sector.append(compass(45))   # Append Heading object
sector.append(90)            # Append numeric bearing
```

### Sector.sort(Function *key* = None, Boolean *reverse* = False)

| Type | Returns |
| ---- | ------- |
| None | None |

Sorts the headings in the sector clockwise from the minimum heading, properly handling wraparound. If a custom `key` function is provided, uses standard list sorting. The `reverse` parameter reverses the sort order.

Example:
```python
sector = compass.sector([compass(350), compass(10), compass(180)])
sector.sort()  # Headings now in clockwise order from minimum
```

### Sector.min()

| Type | Returns |
| ---- | ------- |
| Heading | Heading object |

Returns the heading that starts the smallest arc containing all headings in the sector. This is the circular-aware minimum. Raises ValueError if the sector is empty.

### Sector.max()

| Type | Returns |
| ---- | ------- |
| Heading | Heading object |

Returns the heading with the maximum clockwise distance from the minimum heading. This is the circular-aware maximum. Raises ValueError if the sector is empty.

### Sector.mean()

| Type | Returns |
| ---- | ------- |
| Float | degrees (0-360) |

Returns the circular mean (average direction) of all headings in the sector using trigonometric circular statistics. Properly handles wraparound.

### Sector.percentile(Float *pct*)

| Type | Returns |
| ---- | ------- |
| Float | degrees (0-360) |

Returns the bearing at the specified percentile of all headings in the sector. The percentile is specified as a decimal between 0.0 and 1.0 (e.g., 0.25 for 25th percentile, 0.5 for median, 0.75 for 75th percentile). Uses linear interpolation between values when the percentile falls between two headings. Properly handles wraparound by calculating percentiles based on relative bearings from the minimum heading. Raises ValueError if the sector is empty or if pct is outside the range [0.0, 1.0].

Example:
```python
sector = compass.sector([compass(0), compass(90), compass(180), compass(270)])
p25 = sector.percentile(0.25)   # 25th percentile
p50 = sector.percentile(0.5)    # 50th percentile (median)
p75 = sector.percentile(0.75)   # 75th percentile
```

### Sector.median()

| Type | Returns |
| ---- | ------- |
| Float | degrees (0-360) |

Returns the circular median of all headings in the sector. This is equivalent to calling `percentile(0.5)`. The median represents the middle value when headings are sorted clockwise from the minimum heading. Raises ValueError if the sector is empty.

Example:
```python
sector = compass.sector([compass(90), compass(120), compass(150)])
median = sector.median()  # Returns 120.0
```