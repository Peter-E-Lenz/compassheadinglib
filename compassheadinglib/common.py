import math
from numbers import Number

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
    def __init__(self, name, abbr, azimuth, order, langs={},parent=None):
        self.name=name
        self.abbr=abbr
        self.azimuth=float(azimuth)
        self.order=order
        self.langs=langs
        self.parent=parent

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
            return self.azimuth == azimuthB.azimuth
        else:
            return self.azimuth == azimuthB
        
    def __gt__(self, azimuthB):
        azimuthB = float(azimuthB)
        diff = (azimuthB - self.azimuth) % 360
        if diff <= 180:
            return False  # azimuthB is ahead (clockwise) by <= 180°
        else:
            return True   # azimuthB is behind (counter-clockwise) by > 180°

    def __lt__(self, azimuthB):
        azimuthB = float(azimuthB)
        diff = (azimuthB - self.azimuth) % 360
        if diff <= 180:
            return True   # azimuthB is ahead (clockwise) by <= 180°
        else:
            return False  # azimuthB is behind (counter-clockwise) by > 180°

    def __ge__(self, azimuthB):
        azimuthB = float(azimuthB)
        if self.azimuth == azimuthB:
            return True
        diff = (azimuthB - self.azimuth) % 360
        if diff <= 180:
            return False  # azimuthB is ahead (clockwise) by <= 180°
        else:
            return True   # azimuthB is behind (counter-clockwise) by > 180°

    def __le__(self, azimuthB):
        azimuthB = float(azimuthB)
        if self.azimuth == azimuthB:
            return True
        diff = (azimuthB - self.azimuth) % 360
        if diff <= 180:
            return True   # azimuthB is ahead (clockwise) by <= 180°
        else:
            return False  # azimuthB is behind (counter-clockwise) by > 180°
    
    def rotate(self, degrees):
        new_azimuth = (self.azimuth + degrees) % 360
        return self.parent(new_azimuth)

    def port(self, degrees):
        assert degrees >= 0
        new_azimuth = (self.azimuth - degrees) % 360
        return self.parent(new_azimuth)

    def starboard(self, degrees):
        assert degrees >= 0
        new_azimuth = (self.azimuth + degrees) % 360
        return self.parent(new_azimuth)

    def left(self,degrees):
        return self.port(degrees)

    def right(self,degrees):
        return self.starboard(degrees)
    
    def __add__(self, other):
        # Return NotImplemented for Sector to allow Sector.__radd__ to handle it
        if type(other).__name__ == 'Sector':
            return NotImplemented
        if isinstance(other, Heading):
            new_azimuth = (self.azimuth + other.azimuth) % 360
        else:
            new_azimuth = (self.azimuth + float(other)) % 360
        return self.parent(new_azimuth)

    def __sub__(self, other):
        # Return NotImplemented for Sector to allow Sector.__rsub__ to handle it
        if type(other).__name__ == 'Sector':
            return NotImplemented
        if isinstance(other, Heading):
            new_azimuth = (self.azimuth - other.azimuth) % 360
        else:
            new_azimuth = (self.azimuth - float(other)) % 360
        return self.parent(new_azimuth)

    def __radd__(self, other):
        # For when a number is added to a heading (number + heading)
        new_azimuth = (float(other) + self.azimuth) % 360
        return self.parent(new_azimuth)

    def __rsub__(self, other):
        # For when a heading is subtracted from a number (number - heading)
        new_azimuth = (float(other) - self.azimuth) % 360
        return self.parent(new_azimuth)
    
    def asDict(self):
        return {i:self.__dict__[i] for i in self.__dict__ if i not in ('langs','parent')}

    def translate(self,lang):
        new_lang=self.langs[lang.upper()]
        return Heading(
            new_lang['Heading'],
            new_lang['Abbreviation'],
            self.azimuth,
            self.order,
            self.langs,
            self.parent
        )

    def withBearing__(self,azimuth):
        return Heading(
            self.name,
            self.abbr,
            azimuth,
            self.order,
            self.langs,
            self.parent
        )
    
class Sector(list):
    #collection of Heading objects representing a sector of the compass
    def __init__(self, headings=None, parent=None):
        super().__init__()
        self.parent = parent
        if headings:
            for h in headings:
                self.append(h)
    
    def append(self, item):
        if isinstance(item, Heading):
            super().append(item)
        elif isinstance(item, (int, float)):
            # Convert numeric value to a proper Heading object using parent
            if self.parent is None:
                raise ValueError(
                    "Cannot append numeric values to a Sector without a parent Compass. "
                    "Create Sectors using Compass.sector() instead."
                )
            # Use parent's findHeading to get a proper Heading with the right parent
            heading = self.parent.findHeading(float(item), order=4)
            super().append(heading)
        else:
            raise TypeError(
                f"Item must be a Heading or numeric type. Got {type(item)}"
            )
        
    def sort(self, key=None, reverse=False):
        # Sort headings clockwise from the min heading
        if not self or len(self) == 1:
            return
        
        if key is not None:
            # If user provides a custom key, use standard sort
            super().sort(key=key, reverse=reverse)
            return
        
        min_heading = self.min()
        min_az = float(min_heading)
        
        # Sort by relative bearing (clockwise offset from min)
        def relative_key(h):
            az = float(h)
            return (az - min_az) % 360
        
        super().sort(key=relative_key, reverse=reverse)
    
    def __add__(self, other):
        if isinstance(other, Sector):
            # Merge two Sectors (list concatenation)
            result = Sector(self, parent=self.parent)
            result.extend(other)
            return result
        elif isinstance(other, (Heading, int, float)):
            # Rotate all headings in the Sector
            result = Sector(parent=self.parent)
            for h in self:
                result.append(h + other)
            return result
        else:
            return super().__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, (Heading, int, float)):
            # Rotate all headings in the Sector
            result = Sector(parent=self.parent)
            for h in self:
                result.append(h - other)
            return result
        else:
            raise TypeError('Cannot subtract {} from Sector'.format(type(other)))
    
    def __radd__(self, other):
        if isinstance(other, Heading):
            result = Sector(parent=self.parent)
            for h in self:
                result.append(other + h)
            return result
        elif isinstance(other, (int, float)):
            result = Sector(parent=self.parent)
            for h in self:
                result.append(other + h)
            return result
        return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, Heading):
            result = Sector(parent=self.parent)
            for h in self:
                result.append(other - h)
            return result
        elif isinstance(other, (int, float)):
            result = Sector(parent=self.parent)
            for h in self:
                result.append(other - h)
            return result
        return NotImplemented

    def port(self, degrees):
        # Shift all headings port (left/counter-clockwise)
        result = Sector(parent=self.parent)
        for h in self:
            result.append(h.port(degrees))
        return result
    
    def starboard(self, degrees):
        # Shift all headings starboard (right/clockwise)
        result = Sector(parent=self.parent)
        for h in self:
            result.append(h.starboard(degrees))
        return result
    
    def left(self, degrees):
        # Shift all headings left (port)
        return self.port(degrees)
    
    def right(self, degrees):
        # Shift all headings right (starboard)
        return self.starboard(degrees)
    
    def translate(self, lang):
        # Translate all headings to the specified language
        result = Sector(parent=self.parent)
        for h in self:
            result.append(h.translate(lang))
        return result
    
    def _angular_distance(self, h1, h2):
        # Returns the smaller arc distance between two headings (0-180)
        az1 = float(h1)
        az2 = float(h2)
        diff = abs(az2 - az1)
        if diff > 180:
            diff = 360 - diff
        return diff
    
    def min(self):
        if not self:
            raise ValueError('Cannot find min of empty Sector')
        
        if len(self) == 1:
            return self[0]
        
        # Find the heading that minimizes the maximum clockwise distance to any other heading
        # This is the "start" of the smallest arc containing all headings
        min_heading = None
        min_max_distance = float('inf')
        
        for candidate in self:
            # Calculate max clockwise distance from this candidate to all others
            max_distance = 0
            for h in self:
                if h != candidate:
                    az_candidate = float(candidate)
                    az_h = float(h)
                    # Clockwise distance from candidate to h
                    distance = (az_h - az_candidate) % 360
                    max_distance = max(max_distance, distance)
            
            # Choose the candidate with smallest max distance
            if max_distance < min_max_distance:
                min_max_distance = max_distance
                min_heading = candidate
            elif max_distance == min_max_distance and float(candidate) < float(min_heading):
                # Tie-breaker: prefer smaller azimuth
                min_heading = candidate
        
        return min_heading
    
    def max(self):
        if not self:
            raise ValueError('Cannot find max of empty Sector')
        
        if len(self) == 1:
            return self[0]
        
        min_heading = self.min()
        min_az = float(min_heading)
        
        # Find heading with maximum clockwise distance from min
        max_heading = min_heading
        max_distance = 0
        
        for h in self:
            az = float(h)
            # Calculate clockwise distance from min to h
            distance = (az - min_az) % 360
            if distance > max_distance:
                max_distance = distance
                max_heading = h
        
        return max_heading
    
    def relative_bearings(self):
        if not self:
            return []
        
        min_heading = self.min()
        min_az = float(min_heading)
        
        result = []
        for h in self:
            az = float(h)
            # Calculate clockwise offset from min
            offset = (az - min_az) % 360
            result.append(offset)
        
        return result
    
    def mean(self):
        
        if not self:
            raise ValueError('Cannot find mean of empty Sector')
        
        # Use circular mean: average of sine and cosine components
        sin_sum = 0
        cos_sum = 0
        
        for h in self:
            az_rad = math.radians(float(h))
            sin_sum += math.sin(az_rad)
            cos_sum += math.cos(az_rad)
        
        mean_sin = sin_sum / len(self)
        mean_cos = cos_sum / len(self)
        
        # Convert back to degrees
        mean_rad = math.atan2(mean_sin, mean_cos)
        mean_deg = math.degrees(mean_rad)
        
        # Normalize to 0-360
        if mean_deg < 0:
            mean_deg += 360
        
        return mean_deg
    
    def median(self):
        if not self:
            raise ValueError('Cannot find median of empty Sector')
        
        if len(self) == 1:
            return float(self[0])
        
        # Get relative bearings from min
        min_heading = self.min()
        min_az = float(min_heading)
        
        # Calculate all relative bearings
        relatives = []
        for h in self:
            az = float(h)
            offset = (az - min_az) % 360
            relatives.append(offset)
        
        # Sort and find median
        relatives.sort()
        n = len(relatives)
        
        if n % 2 == 1:
            median_offset = relatives[n // 2]
        else:
            median_offset = (relatives[n // 2 - 1] + relatives[n // 2]) / 2
        
        # Convert back to absolute bearing
        median_bearing = (min_az + median_offset) % 360
        
        return median_bearing

class _Headings(dict):
    #host object for a collection of headings (i.e. the Compass object)
    def __init__(self,c):
        self.iterlist__=[]
        for i in c:
            h=Heading(
                i['Heading'],
                i['Abbreviation'],
                i['Azimuth'],
                i['Order'],
                i['Lang'],
                self
            )
            if i['Heading'] not in c:
                self[i['Heading'].lower().replace(' ','-')]=h
            self.iterlist__.append(h)

    def __getitem__(self, key):
        if isinstance(key,str):
            return super().__getitem__(key)
        else:
            return self.iterlist__[key]

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
    
    def sector(self, headings=None):
        """Create a Sector with this Compass as the parent"""
        return Sector(headings, parent=self)
    
    def asList(self):
        return [i.asDict() for i in self]

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
                    return out.withBearing__(bearing)
        return out.withBearing__(bearing)
