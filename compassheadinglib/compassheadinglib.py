#  compassheadingslib
#  A pure python, dependency-free library for describing compass headings
#  Originally intended to be a part of mgrslib but now broken out
#  version 0.0.1 
#  alpha status
#
#  http://www.pelenz.com/mgrslib
#  http://www.github.com/peter-e-lenz/mgrslib
#
#  Copyright 2017-2021 (c) Peter E Lenz [pelenz@pelenz.com]
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
#

def _instanceTypeCheck(inst,typeof):
    #tests if inst is of type typeof (or if typeof is a list any of the types in typeof) otherwise throws an error
    if not isinstance(typeof,list):
        typeof=[typeof]

    matchesAny = False

    for i in typeof:
        if isinstance(inst,i):
            matchesAny = True
            break

    if not matchesAny:
        acceptable = ', '.join([str(i) for i in typeof])
        
        isMultMsg=''
        if len(typeof)>1:
            isMultMsg='one of '
        
        raise TypeError('Variable type must be {}{}. Input was type {}.'.format(isMultMsg,acceptable,type(inst)))


class Heading(object):
    #host object for a single heading
    def __init__(self, name, abbr, azimuth, order):
        self.name=name
        self.abbr=abbr
        self.azimuth=float(azimuth)
        self.order=order

    def __repr__(self):
        return self.name
    
    def __float__(self):
        return self.azimuth

    def __str__(self):
        return self.name

    def __abs__(self):
        return abs(self.azimuth)

    def __eq__(self,azimuthB):
        if isinstance(azimuthB,Heading):
            return self.__dict__ == azimuthB.__dict__
        else:
            return self.azimuth == azimuthB

    def __ne__(self,azimuthB):
        if isinstance(azimuthB,Heading):
            return self.__dict__ != azimuthB.__dict__
        else:
            return self.azimuth != azimuthB

    def __gt__(self,azimuthB):
        return float(azimuthB)<self.azimuth
    
    def __lt__(self,azimuthB):
        return float(azimuthB)>self.azimuth

    def __ge__(self,azimuthB):
        return float(azimuthB)<=self.azimuth

    def __le__(self,azimuthB):
        return float(azimuthB)>=self.azimuth

    #def next(self) 

class _Headings(dict):
    #host object for a collection of headings (i.e. the Compass object)
    def __init__(self,c):
        self.iterlist__=[]
        for i in c:
            h=Heading(i['name'],i['abbr'],i['azimuth'],i['order'])
            if i['name'] not in c:
                self[i['name'].lower().replace(' ','-')]=h
            self.iterlist__.append(h)

    def __getattr__(self, name):
        return self[name.lower()]

    def __setattr__(self, name, value):
        if '__' not in name:
            _instanceTypeCheck(value,Heading)
            self[name.lower()]=value
        else:
            self[name]=value

    def __delattr__(self, name):
        del self[name]

    def __iter__(self):
        return iter(self.iterlist__)

    def __repr__(self):
        return '< Headings {} >'.format(repr(self.keys()))

    def __call__(self,bearing,order=3):
        return self.findHeading(bearing,order)

    def findHeading(self,bearing,order=3):
        #returns the nearest heading of order or below to the bearing entered
        s=361
        out=None

        for i in self.iterlist__:
            if i.order<=order:
                d=max(bearing,i.azimuth)-min(bearing,i.azimuth)
                if d < s:
                    s = d
                    out = i
                else:
                    return out
        return out

#source data for the Compass object
_compass = [
    {
        'name':'North',
        'abbr':'N',
        'azimuth':0,
        'order':1
    },
    {
        'name':'North by East',
        'abbr':'NbE',
        'azimuth':11.25,
        'order':4
    },
    {
        'name':'North-Northeast',
        'abbr':'NNE',
        'azimuth':22.5,
        'order':3
    },
    {
        'name':'Northeast by North',
        'abbr':'NEbN',
        'azimuth':33.75,
        'order':4
    },
    {
        'name':'Northeast',
        'abbr':'NE',
        'azimuth':45,
        'order':2
    },
    {
        'name':'Northeast by East',
        'abbr':'NEbE',
        'azimuth':56.25,
        'order':4
    },
    {
        'name':'East-Northeast',
        'abbr':'ENE',
        'azimuth':67.5,
        'order':3
    },
    {
        'name':'East by North',
        'abbr':'EbN',
        'azimuth':78.75,
        'order':4
    },
    {
        'name':'East',
        'abbr':'E',
        'azimuth':90,
        'order':1
    },
    {
        'name':'East by South',
        'abbr':'EbS',
        'azimuth':101.25,
        'order':4
    },
    {
        'name':'East-Southeast',
        'abbr':'ESE',
        'azimuth':112.5,
        'order':3
    },
    {
        'name':'Southeast by East',
        'abbr':'SEbE',
        'azimuth':123.75,
        'order':4
    },
    {
        'name':'Southeast',
        'abbr':'SE',
        'azimuth':135,
        'order':2
    },
    {
        'name':'Southeast by South',
        'abbr':'SEbS',
        'azimuth':146.25,
        'order':4
    },
    {
        'name':'South-Southeast',
        'abbr':'SSE',
        'azimuth':157.5,
        'order':3
    },
    {
        'name':'South by East',
        'abbr':'SbE',
        'azimuth':168.75,
        'order':4
    },
    {
        'name':'South',
        'abbr':'S',
        'azimuth':180,
        'order':1
    },
    {
        'name':'South by West',
        'abbr':'SbW',
        'azimuth':191.25,
        'order':4
    },
    {
        'name':'South-Southwest',
        'abbr':'SSW',
        'azimuth':202.5,
        'order':3
    },
    {
        'name':'Southwest by South',
        'abbr':'SWbS',
        'azimuth':213.75,
        'order':4
    },
    {
        'name':'Southwest',
        'abbr':'SW',
        'azimuth':225,
        'order':2
    },
    {
        'name':'Southwest by West',
        'abbr':'SWbW',
        'azimuth':236.25,
        'order':4
    },
    {
        'name':'West-Southwest',
        'abbr':'WSW',
        'azimuth':247.5,
        'order':3
    },
    {
        'name':'West by South',
        'abbr':'WbS',
        'azimuth':258.75,
        'order':4
    },
    {
        'name':'West',
        'abbr':'W',
        'azimuth':270,
        'order':1
    },
    {
        'name':'West by North',
        'abbr':'WbN',
        'azimuth':281.25,
        'order':4
    },
    {
        'name':'West-Northwest',
        'abbr':'WNW',
        'azimuth':292.5,
        'order':3
    },
    {
        'name':'Northwest by West',
        'abbr':'NWbW',
        'azimuth':303.75,
        'order':4
    },
    {
        'name':'Northwest',
        'abbr':'NW',
        'azimuth':315,
        'order':2
    },
    {
        'name':'Northwest by North',
        'abbr':'NWbN',
        'azimuth':326.25,
        'order':4
    },
    {
        'name':'North-Northwest',
        'abbr':'NNW',
        'azimuth':337.5,
        'order':3
    },
    {
        'name':'North by West',
        'abbr':'NbW',
        'azimuth':348.75,
        'order':4
    },
    {
        'name':'North',
        'abbr':'N',
        'azimuth':360,
        'order':1
    }
]


#create the Compass object it self
Compass = _Headings(_compass)