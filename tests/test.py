#  compassheadingslib
#  A pure python, dependency-free library for describing compass headings
#  Originally intended to be a part of mgrslib but now broken out
#  version 0.0.1 
#  alpha status
#
#  http://www.pelenz.com/mgrslib
#  http://www.github.com/peter-e-lenz/mgrslib
#
#  Copyright 2017 (c) Peter E Lenz [pelenz@pelenz.com]
#  All rights reserved. 
#
#  MIT License
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this
#  software and associated documentation files (the "Software"), to deal in the Software 
#  without restriction, including without limitation the rights to use, copy, modify, merge,
#  publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
#  to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or
#  substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.


from compassheadinglib import _compass,Compass,Heading
from random import uniform


#wrap around test
assert _compass[0]['name'] == _compass[-1]['name']
assert _compass[0]['abbr'] == _compass[-1]['abbr']
assert _compass[0]['order'] == _compass[-1]['order']
assert _compass[0]['azimuth'] < _compass[-1]['azimuth']

#monotonic range increase tests
last=-1
items_monotocicity=[]
for i in _compass:
	items_monotocicity.append(last < i['azimuth'])
	last=i['azimuth']
assert all(items_monotocicity)

#check that data contains only order 1-4
number_of_heading_levels=4
assert set(range(1,number_of_heading_levels+1)) == set([i['order'] for i in _compass])

#count how entrys there are for each order
#remember that order 1 has 5 values because 'North' get repeated as the first and last elements of the Compass object
assert len([i for i in _compass if i['order']==1]) == 5
assert len([i for i in _compass if i['order']==2]) == 4
assert len([i for i in _compass if i['order']==3]) == 8
assert len([i for i in _compass if i['order']==4]) == 16


#manual range selection tests
manual_range_test_azimuth=57
manul_range_test_names=['East','Northeast','East-Northeast','Northeast by East']
for i in zip(range(0,number_of_heading_levels),manul_range_test_names):
	assert str(Compass.findHeading(1,i[0]+1)) == 'North'
	assert str(Compass.findHeading(manual_range_test_azimuth,i[0]+1)) == i[1]

#randomized range selection test
#for each direction in a level (remember that a level also countains any items on any lower 
#numbered level) do FUZZ_IN_TEST_COUNT tests iside it's range (i.e. the range is say 10-20 
#and the test value is 14) return the correct item and do FUZZ_OUT_TEST_COUNT tests outside
# it's range (i.e. the range is say 1 0-20 and the test value is 42). Test values are randomly
#selected each run. This test implicity also tests the Heading and _Headings object.

number_of_random_range_selections=10000

slice_angle=11.25
parent_angles=[0,90,180,270]

angle_list=[uniform(0.0, 360.0) for i in range(0,number_of_random_range_selections)]

for angle in angle_list:
	res=int(angle//slice_angle)
	#this test can be off by one since it's simpler then the real logic, but as long as one or one-off by +1 matches across 
	#a large random set we're good
	assert Heading(**_compass[res])==Compass.findHeading(angle,4) or Heading(**_compass[res+1])==Compass.findHeading(angle,4)

#manual spot tests of relativity tests (greater than, less than, etc.)
#also tests that calling a Headings object directly is functionally the same as calling the findHeading method
assert Compass(0,1)==Compass.findHeading(12,1)
assert Compass(0,1)==Compass.findHeading(12,2)
assert Compass(0,1)<Compass.findHeading(12,3)
assert Compass(0,1)<Compass.findHeading(12,4)
assert Compass(12,3)>Compass.findHeading(0,1)
assert Compass(12,4)>Compass.findHeading(0,1)

#randomized test of relativity tests (greater than, less than, etc.)

number_of_random_relativity_tests=10000

for relative_a,relative_b in [(uniform(0,360),uniform(0,360)) for i in range(0,number_of_random_relativity_tests)]:
	#print(relative_a,relative_b,relative_a//slice_angle,relative_b//slice_angle,abs(relative_a-relative_b),Compass.findHeading(relative_a),Compass.findHeading(relative_b))

	if (relative_a//slice_angle) == (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=3) == Compass.findHeading(relative_b,order=3)
	
	elif  ((relative_a//slice_angle) < (relative_b//slice_angle)) and abs(relative_a-relative_b)<slice_angle:
		assert Compass.findHeading(relative_a,order=4) <= Compass.findHeading(relative_b,order=4)
	elif  ((relative_a//slice_angle) > (relative_b//slice_angle)) and abs(relative_a-relative_b)<slice_angle:
		assert Compass.findHeading(relative_a,order=4) >= Compass.findHeading(relative_b,order=4)

	elif  (relative_a//slice_angle) < (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=4) < Compass.findHeading(relative_b,order=4)
	elif  (relative_a//slice_angle) > (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=4) > Compass.findHeading(relative_b,order=4)

	else:
		print('Impossible relationship: {},{}'.format(relative_a,relative_b))
		assert False
print('All tests have passed')
 
