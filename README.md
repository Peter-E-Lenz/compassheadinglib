
<span style="font-variant: small-caps">CompassHeadingLib</span> is a small, dependency-free, pure python library for working with compass headings in terms of comparison and transformation between decimal degree and natural language space. It was originally written as a part of `mgrslib` but was separated out since there is nothing about it that is MGRS specific and because I've been dragging my feet on getting `mgrslib` fully tested and loaded to PyPi for *years*.

<span style="font-variant: small-caps">CompassHeadingLib</span> follows the [worse is better](https://en.wikipedia.org/wiki/Worse_is_better) design philosophy; it's better to have a slower less featureful implementation then no implementation at all. Optimizations will be executed when we have to.

### License

<span style="font-variant: small-caps">CompassHeadingLib</span> is licensed under the MIT License and offered as is without warranty of any kind, express or implied. 

### Installation

#### From PyPi
`pip install -u compassheadinglib`

#### From Git

### Dependencies

<span style="font-variant: small-caps">CompassHeadingLib</span> was specifically written to have no dependencies. The test suite uses the `random` library from Python's Standard Lib.
It was originally written to run on Python 2.7 but is now only tested on Python 3.7+. 

### Assumptions
<span style="font-variant: small-caps">CompassHeadingLib</span> currently assumes the English language. Translations and a scheme to specify language to return will be happily accepted as pull requests.

## Example

## Compass Object
###### Compass(Float *heading*, Int *order* = 3)
###### Compass.findHeading(Float *heading*, Int *order* = 3)

| Type | Returns |
| ---- | ------- |
| Object(based on Dict)| Heading |

  

These functions take a heading between two points as a float (i.e. in decimal degrees) and returns the best matching heading with `order` degree of specificity. `Order` is a 1-indexed description of how specific the natural language The higher the order the more specific the heading. At an `order` of 1 the decimal degree heading of 80.0 will return a heading object of 'East' while at an `order` of 4 it would return 'East by North' heading object. 

Internally, calling the Compass object directly will silently call it's `findHeading` method.

## Heading Object
Heading objects are returned by Compass objects and are not intended to be created by end users.

| Type | Returns |
| ---- | ------- |
| Object| N/A|

Heading objects are containers for information about headings that are designed to be comparable to each other (and other python objects) using built-in methods. There are four pieces of information for each heading, each a method of the object: `name`, `abbr`, `azimuth`, and `order`. The various built-in comparisons look to different methods (and thus different pieces of the information) as appropriate. For the most part you can safely ignore all this background stuff.

###### Heading.name

| Type | Returns |
| ---- | ------- |
| string| string|

The full name of this heading, along the lines of 'North' or 'South by East'.
Note: despite what the festival has told you there is no such heading as 'South by Southwest'.

###### Heading.abbr

| Type | Returns |
| ---- | ------- |
| string| string|

The abbreviated name of this heading, along the lines of 'N' or 'SbE'
###### Heading.azimuth

| Type | Returns |
| ---- | ------- |
| float| float|

The decimal degree value of this heading. For example; 'West' is 270.0 while 'North-Northeast' is 22.5

###### Heading.order

| Type | Returns |
| ---- | ------- |
| integer| integer|

Order defines how specific the heading is. The cardinal directions ('North', 'East', 'South' & 'West') are of order 1 while 'South by East' is order 4. The Compass Headings Reference chart at the end of this document will be more illustrative of this difference.
Put another way: order 1 headings are 90° apart, order 2 headings are 45° apart, order 3 headings are 22.5° apart, and order 4 headings are 11.25° apart. By default this library uses order 3 where ever that value can be specified. Each order includes the headings of that order and all headings of any lower valued orders. Hence order 2 includes all headings labeled order 2 and order 1.

When treated as a string the Heading object returns the value for the `name` method
When treated as a numeric(regardless of int or float) it will return the values for the `azimuth` method.



## Compass Headings Reference
| Heading            | Abbreviation | Azimuth| Order |
|--------------------|-----------|---------|-------|
| North              | N         | 0       | 1     |
| North by East      | NbE       | 11.25   | 4     |
| North-Northeast    | NNE       | 22.5    | 3     |
| Northeast by North | NEbN      | 33.75   | 4     |
| Northeast          | NE        | 45      | 2     |
| Northeast by East  | NEbE      | 56.25   | 4     |
| East-Northeast     | ENE       | 67.5    | 3     |
| East by North      | EbN       | 78.75   | 4     |
| East               | E         | 90      | 1     |
| East by South      | EbS       | 101.25  | 4     |
| East-Southeast     | ESE       | 112.5   | 3     |
| Southeast by East  | SEbE      | 123.75  | 4     |
| Southeast          | SE        | 135     | 2     |
| Southeast by South | SEbS      | 146.25  | 4     |
| South-Southeast    | SSE       | 157.5   | 3     |
| South by East      | SbE       | 168.75  | 4     |
| South              | S         | 180     | 1     |
| South by West      | SbW       | 191.25  | 4     |
| South-Southwest    | SSW       | 202.5   | 3     |
| Southwest by South | SWbS      | 213.75  | 4     |
| Southwest          | SW        | 225     | 2     |
| Southwest by West  | SWbW      | 236.25  | 4     |
| West-Southwest     | WSW       | 247.5   | 3     |
| West by South      | WbS       | 258.75  | 4     |
| West               | W         | 270     | 1     |
| West by North      | WbN       | 281.25  | 4     |
| West-Northwest     | WNW       | 292.5   | 3     |
| Northwest by West  | NWbW      | 303.75  | 4     |
| Northwest          | NW        | 315     | 2     |
| Northwest by North | NWbN      | 326.25  | 4     |
| North-Northwest    | NNW       | 337.5   | 3     |
| North by West      | NbW       | 348.75  | 4     |

