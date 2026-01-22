"""
Complete pytest test suite for compassheadinglib
Combines original tests with additional coverage for untested functionality
"""

import pytest
import math
from compassheadinglib import Compass
from compassheadinglib.common import Heading, Sector, _instanceTypeCheck
from random import uniform
from json import load
from pathlib import Path
from itertools import chain
from collections import Counter


class TestBasicFunctionality:
    """Test basic compass functionality and data integrity"""
    
    def test_wrap_around(self):
        """Test that first and last compass entries wrap around correctly"""
        assert Compass[0].name == Compass[-1].name
        assert Compass[0].abbr == Compass[-1].abbr
        assert Compass[0].order == Compass[-1].order
        assert Compass[0].azimuth < Compass[-1].azimuth

    def test_monotonic_range_increase(self):
        """Test that azimuth values increase monotonically"""
        last = -1
        items_monotonicity = []
        for i in Compass:
            items_monotonicity.append(last < i.azimuth)
            last = i.azimuth
        assert all(items_monotonicity)

    def test_heading_orders(self):
        """Test that data contains only order 1-4 and correct counts"""
        number_of_heading_levels = 4
        assert set(range(1, number_of_heading_levels + 1)) == set([i.order for i in Compass])
        
        # Count entries for each order
        # Order 1 has 5 values because 'North' gets repeated as first and last elements
        assert len([i for i in Compass if i.order == 1]) == 5
        assert len([i for i in Compass if i.order == 2]) == 4
        assert len([i for i in Compass if i.order == 3]) == 8
        assert len([i for i in Compass if i.order == 4]) == 16

class TestRandomizedRangeSelection:
    """Test randomized range selection with fuzzing"""
    
    def test_randomized_range_selection(self):
        """Test randomized range selection against expected results"""
        number_of_random_range_selections = 1000  # Reduced for faster testing
        slice_angle = 11.25
        
        _compass = Compass.asList()
        angle_list = [uniform(0.0, 360.0) for _ in range(number_of_random_range_selections)]
        
        for angle in angle_list:
            res = int(angle // slice_angle)
            # Test can be off by one since it's simpler than the real logic
            expected_heading = Heading(**_compass[res])
            expected_heading_plus_one = Heading(**_compass[res + 1]) if res + 1 < len(_compass) else Heading(**_compass[0])
            actual_heading = Compass.findHeading(angle, 4)
            
            assert (expected_heading.name == actual_heading.name or 
                   expected_heading_plus_one.name == actual_heading.name)


class TestRelativityOperators:
    """Test heading comparison operators with circular logic"""
    
    def test_manual_relativity_tests(self):
        """Test manual spot tests of relativity operators"""
        # Basic same-heading tests
        assert Compass(0, 1).name == Compass.findHeading(12, 1).name
        assert Compass(0, 1).name == Compass.findHeading(12, 2).name
        
        # These comparisons now need to account for circular logic
        # 12° is clockwise from 0° by 12°, so 0 < 12
        assert Compass(0, 1) < Compass.findHeading(12, 3)
        assert Compass(0, 1) < Compass.findHeading(12, 4)
        assert Compass(12, 3) > Compass.findHeading(0, 1)
        assert Compass(12, 4) > Compass.findHeading(0, 1)
        
    def test_circular_wraparound_comparisons(self):
        """Test that circular comparisons work correctly across 0°/360° boundary"""
        # 350° < 10° because 10° is only 20° clockwise from 350°
        assert Compass.findHeading(350, 4) < Compass.findHeading(10, 4)
        assert Compass.findHeading(10, 4) > Compass.findHeading(350, 4)
        
        # 350° <= 10° 
        assert Compass.findHeading(350, 4) <= Compass.findHeading(10, 4)
        assert Compass.findHeading(10, 4) >= Compass.findHeading(350, 4)
        
        # 10° < 350° is False (would require 340° clockwise)
        assert not (Compass.findHeading(10, 4) < Compass.findHeading(350, 4))
        
        # More wraparound tests
        assert Compass.findHeading(355, 4) < Compass.findHeading(5, 4)
        assert Compass.findHeading(0, 4) < Compass.findHeading(180, 4)
        assert Compass.findHeading(180, 4) < Compass.findHeading(0, 4)  # 0° is 180° clockwise from 180°

    def test_equality_comparisons(self):
        """Test equality and near-equality comparisons"""
        # Exact equality
        assert Compass.findHeading(90, 4) == Compass.findHeading(90, 4)
        assert Compass.findHeading(90, 4) <= Compass.findHeading(90, 4)
        assert Compass.findHeading(90, 4) >= Compass.findHeading(90, 4)
        
        # Not equal
        assert Compass.findHeading(90, 4) != Compass.findHeading(91, 4)

    def test_opposite_headings(self):
        """Test comparisons at exactly 180° apart"""
        # At exactly 180°, the comparison uses the 'less than or equal to 180' rule
        # So 0° < 180° (180° is exactly 180° clockwise)
        assert Compass.findHeading(0, 4) < Compass.findHeading(180, 4)
        
        # But 180° < 0° is also true (0° is exactly 180° clockwise from 180°)
        assert Compass.findHeading(180, 4) < Compass.findHeading(0, 4)
        
        # This means both directions are "less than" at 180° separation
        # This is a known edge case in circular comparisons

    def test_randomized_relativity_tests(self):
        """Test randomized relativity comparisons with circular logic"""
        number_of_random_relativity_tests = 1000
        
        for _ in range(number_of_random_relativity_tests):
            relative_a = uniform(0, 360)
            relative_b = uniform(0, 360)
            
            heading_a = Compass.findHeading(relative_a, order=4)
            heading_b = Compass.findHeading(relative_b, order=4)
            
            # Calculate circular distance from a to b (clockwise)
            diff = (relative_b - relative_a) % 360
            
            if abs(relative_a - relative_b) < 0.01 or abs(diff - 360) < 0.01:
                # Essentially equal
                assert heading_a == heading_b or heading_a <= heading_b or heading_a >= heading_b
            elif diff < 180:
                # b is clockwise from a by less than 180°, so a < b
                assert heading_a < heading_b
                assert heading_a <= heading_b
                assert heading_b > heading_a
                assert heading_b >= heading_a
            elif diff > 180:
                # b is clockwise from a by more than 180° (counter-clockwise is shorter), so a > b
                assert heading_a > heading_b
                assert heading_a >= heading_b
                assert heading_b < heading_a
                assert heading_b <= heading_a
            else:
                # Exactly 180° apart - edge case where both can be considered "less than"
                # Just verify the operations don't crash
                _ = heading_a < heading_b
                _ = heading_a > heading_b

class TestArithmeticOperations:
    """Test arithmetic operations on headings"""
    
    def test_heading_addition(self):
        """Test Heading + Heading and Heading + number"""
        north = Compass.findHeading(0, 1)  # North
        east = Compass.findHeading(90, 1)  # East
        
        # Test Heading + Heading
        result = north + east
        assert result.azimuth == 90.0
        
        # Test Heading + number
        result = north + 45
        assert result.azimuth == 45.0

    def test_reverse_addition(self):
        """Test number + Heading (__radd__)"""
        north = Compass.findHeading(0, 1)
        result = 45 + north
        assert result.azimuth == 45.0

    def test_heading_subtraction(self):
        """Test Heading - Heading and Heading - number"""
        north = Compass.findHeading(0, 1)
        east = Compass.findHeading(90, 1)
        
        # Test Heading - Heading
        result = east - north
        assert result.azimuth == 90.0
        
        # Test Heading - number
        result = east - 45
        assert result.azimuth == 45.0

    def test_reverse_subtraction(self):
        """Test number - Heading (__rsub__)"""
        north = Compass.findHeading(0, 1)
        result = 180 - north
        assert result.azimuth == 180.0

    def test_arithmetic_wraparound(self):
        """Test wraparound in arithmetic operations"""
        north = Compass.findHeading(0, 1)
        
        # Test negative wraparound
        result = north - 45  # 0 - 45 should wrap to 315
        assert result.azimuth == 315.0
        
        # Test positive wraparound
        result = Compass.findHeading(350, 1) + 20  # 350 + 20 should wrap to 10
        assert result.azimuth == 10.0

    def test_random_arithmetic_operations(self):
        """Test random arithmetic operations for consistency"""
        number_of_tests = 100  # Reduced for faster testing
        
        for _ in range(number_of_tests):
            bearing1 = uniform(0, 360)
            operation_value = uniform(-720, 720)
            
            heading1 = Compass.findHeading(bearing1, 4)
            
            # Test addition with modulo consistency
            add_result = heading1 + operation_value
            expected_add = (bearing1 + operation_value) % 360
            assert abs(add_result.azimuth - expected_add) < 0.001
            
            # Test subtraction with modulo consistency
            sub_result = heading1 - operation_value
            expected_sub = (bearing1 - operation_value) % 360
            assert abs(sub_result.azimuth - expected_sub) < 0.001


class TestNavigationMethods:
    """Test navigation methods (port, starboard, left, right, rotate)"""
    
    def test_port_starboard(self):
        """Test port (left turn) and starboard (right turn)"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        # Test port (left turn)
        port_result = heading_90.port(30)
        assert port_result.azimuth == 60.0
        
        # Test starboard (right turn)
        starboard_result = heading_90.starboard(30)
        assert starboard_result.azimuth == 120.0

    def test_left_right_aliases(self):
        """Test left and right as aliases for port and starboard"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        # Test left (alias for port)
        left_result = heading_90.left(30)
        assert left_result.azimuth == 60.0
        
        # Test right (alias for starboard)
        right_result = heading_90.right(30)
        assert right_result.azimuth == 120.0

    def test_rotate(self):
        """Test rotate method (positive and negative)"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        rotate_result = heading_90.rotate(45)
        assert rotate_result.azimuth == 135.0
        
        rotate_result = heading_90.rotate(-45)
        assert rotate_result.azimuth == 45.0

    def test_navigation_wraparound(self):
        """Test wraparound in navigation methods"""
        heading_10 = Compass.findHeading(10, 1)
        port_wrap = heading_10.port(20)  # 10 - 20 should wrap to 350
        assert port_wrap.azimuth == 350.0
        
        heading_350 = Compass.findHeading(350, 1)
        starboard_wrap = heading_350.starboard(20)  # 350 + 20 should wrap to 10
        assert starboard_wrap.azimuth == 10.0

    def test_negative_degrees_assertion(self):
        """Test assertion in port and starboard methods for negative degrees"""
        heading_90 = Compass.findHeading(90, 1)
        
        with pytest.raises(AssertionError):
            heading_90.port(-10)
        
        with pytest.raises(AssertionError):
            heading_90.starboard(-10)


class TestMagicMethods:
    """Test magic methods (__abs__, __float__, __str__, __repr__)"""
    
    def test_abs_float_methods(self):
        """Test __abs__ and __float__ methods"""
        heading = Compass.findHeading(270, 1)
        
        # Test __abs__
        abs_result = abs(heading)
        assert abs_result == 270.0
        
        # Test __float__
        float_result = float(heading)
        assert float_result == 270.0

    def test_str_repr_methods(self):
        """Test __str__ and __repr__ methods"""
        heading = Compass.findHeading(270, 1)
        
        # Test __str__
        str_result = str(heading)
        assert isinstance(str_result, str)
        assert str_result == heading.name
        
        # Test __repr__
        repr_result = repr(heading)
        assert isinstance(repr_result, str)
        assert repr_result == heading.name


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_as_dict_method(self):
        """Test asDict method"""
        heading = Compass.findHeading(45, 4)
        dict_result = heading.asDict()
        
        assert isinstance(dict_result, dict)
        assert 'name' in dict_result
        assert 'abbr' in dict_result
        assert 'azimuth' in dict_result
        assert 'order' in dict_result
        
        # Ensure langs and parent are excluded
        assert 'langs' not in dict_result
        assert 'parent' not in dict_result

    def test_withBearing_method(self):
        """Test withBearing method"""
        original_heading = Compass.findHeading(45, 3)
        new_bearing_heading = original_heading.withBearing__(120)
        
        # Should have same name, abbr, order, but different azimuth
        assert new_bearing_heading.name == original_heading.name
        assert new_bearing_heading.abbr == original_heading.abbr
        assert new_bearing_heading.order == original_heading.order
        assert new_bearing_heading.azimuth == 120.0


class TestHeadingsClass:
    """Test _Headings class methods"""
    
    def test_getattr_method(self):
        """Test __getattr__ method for attribute-style access"""
        north_attr = Compass.north
        assert north_attr.name == "North"

    def test_setattr_delattr_methods(self):
        """Test __setattr__ and __delattr__ methods"""
        # Create a test heading
        test_heading = Heading("Test", "T", 999, 5, {}, Compass)
        
        # Test setting attribute
        Compass.test_heading = test_heading
        assert Compass.test_heading == test_heading
        
        # Test deleting attribute
        del Compass.test_heading
        with pytest.raises((KeyError, AttributeError)):
            _ = Compass.test_heading


class TestErrorHandling:
    """Test error handling"""
    
    def test_instance_type_check(self):
        """Test _instanceTypeCheck error handling"""
        # Test with correct type
        _instanceTypeCheck("test", str)  # Should not raise
        
        # Test with list of types
        _instanceTypeCheck(5, [int, float])  # Should not raise
        
        # Test with incorrect type
        with pytest.raises(TypeError) as excinfo:
            _instanceTypeCheck("test", int)
        assert "Variable type must be" in str(excinfo.value)
        
        # Test with list of incorrect types
        with pytest.raises(TypeError) as excinfo:
            _instanceTypeCheck("test", [int, float])
        assert "Variable type must be one of" in str(excinfo.value)


class TestEdgeCases:
    """Test edge cases"""
    
    def test_exact_360_operations(self):
        """Test exact 360-degree operations"""
        heading_0 = Compass.findHeading(0, 1)
        
        result_360 = heading_0 + 360
        assert result_360.azimuth == 0.0
        
        result_720 = heading_0 + 720
        assert result_720.azimuth == 0.0
        
        # Test negative wraparound
        result_neg = heading_0 - 90
        assert result_neg.azimuth == 270.0


class TestSectorBasics:
    """Test basic Sector functionality"""
    
    def test_sector_creation_empty(self):
        """Test creating an empty Sector"""
        sector = Compass.sector()
        assert len(sector) == 0
        assert isinstance(sector, list)
    
    def test_sector_creation_with_headings(self):
        """Test creating a Sector with headings"""
        headings = [Compass.findHeading(0, 1), Compass.findHeading(90, 1)]
        sector = Compass.sector(headings)
        assert len(sector) == 2
        assert float(sector[0]) == 0
        assert float(sector[1]) == 90
    
    def test_sector_append_heading(self):
        """Test appending Heading objects"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(45, 1))
        assert len(sector) == 1
        assert float(sector[0]) == 45
    
    def test_sector_append_numeric(self):
        """Test appending numeric values"""
        sector = Compass.sector()
        sector.append(45.5)
        sector.append(90)
        assert len(sector) == 2
        assert abs(float(sector[0]) - 45.5) < 1  # May snap to nearest heading
        assert float(sector[1]) == 90.0
    
    def test_sector_append_invalid_type(self):
        """Test that appending invalid types raises proper error"""
        sector = Compass.sector()
        
        with pytest.raises(TypeError) as excinfo:
            sector.append("invalid")
        
        assert "must be a Heading or numeric type" in str(excinfo.value)


class TestSectorSorting:
    """Test Sector sorting functionality"""
    
    def test_sort_clockwise_from_min(self):
        """Test that sort arranges headings clockwise from min"""
        sector = Compass.sector()
        sector.append(180)
        sector.append(90)
        sector.append(120)
        
        sector.sort()
        
        # After sorting, should be in clockwise order from min (90)
        assert float(sector[0]) == 90
        assert float(sector[1]) == 120
        assert float(sector[2]) == 180
    
    def test_sort_with_wraparound(self):
        """Test sorting with wraparound across 0°"""
        sector = Compass.sector()
        sector.append(350)
        sector.append(10)
        sector.append(5)
        
        sector.sort()
        
        # Min should be 350, then clockwise to 5, then 10
        # Note: values may snap to nearest compass heading
        assert float(sector[0]) >= 348  # ~350
        assert float(sector[1]) <= 7    # ~5
        assert float(sector[2]) <= 12   # ~10


class TestSectorArithmetic:
    """Test arithmetic operations on Sectors"""
    
    def test_sector_add_sector(self):
        """Test Sector + Sector (concatenation)"""
        sector1 = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        sector2 = Compass.sector([Compass.findHeading(180, 1), Compass.findHeading(270, 1)])
        
        result = sector1 + sector2
        assert len(result) == 4
        assert float(result[0]) == 0
        assert float(result[3]) == 270
    
    def test_sector_add_heading(self):
        """Test Sector + Heading (rotation)"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        heading = Compass.findHeading(45, 1)
        
        result = sector + heading
        assert len(result) == 2
        assert float(result[0]) == 45
        assert float(result[1]) == 135
    
    def test_sector_add_number(self):
        """Test Sector + number (rotation)"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        
        result = sector + 45
        assert len(result) == 2
        assert float(result[0]) == 45
        assert float(result[1]) == 135
    
    def test_sector_sub_heading(self):
        """Test Sector - Heading"""
        sector = Compass.sector([Compass.findHeading(90, 1), Compass.findHeading(180, 1)])
        heading = Compass.findHeading(45, 1)
        
        result = sector - heading
        assert len(result) == 2
        assert float(result[0]) == 45
        assert float(result[1]) == 135
    
    def test_sector_sub_number(self):
        """Test Sector - number"""
        sector = Compass.sector([Compass.findHeading(90, 1), Compass.findHeading(180, 1)])
        
        result = sector - 45
        assert len(result) == 2
        assert float(result[0]) == 45
        assert float(result[1]) == 135
    
    def test_sector_radd_heading(self):
        """Test Heading + Sector"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        heading = Compass.findHeading(45, 1)
        
        # This should work via Sector.__radd__
        result = heading + sector
        assert isinstance(result, Sector)
        assert len(result) == 2
        # heading + sector means add heading to each element
        assert float(result[0]) == 45  # 45 + 0
        assert float(result[1]) == 135  # 45 + 90
    
    def test_sector_radd_number(self):
        """Test number + Sector"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        
        result = 45 + sector
        assert isinstance(result, Sector)
        assert len(result) == 2
        assert float(result[0]) == 45
        assert float(result[1]) == 135
    
    def test_sector_rsub_heading(self):
        """Test Heading - Sector"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        heading = Compass.findHeading(180, 1)
        
        # heading - sector means subtract each element from heading
        result = heading - sector
        assert isinstance(result, Sector)
        assert len(result) == 2
        assert float(result[0]) == 180  # 180 - 0
        assert float(result[1]) == 90   # 180 - 90
    
    def test_sector_rsub_number(self):
        """Test number - Sector"""
        sector = Compass.sector([Compass.findHeading(45, 1), Compass.findHeading(90, 1)])
        
        result = 180 - sector
        assert isinstance(result, Sector)
        assert len(result) == 2
        assert float(result[0]) == 135  # 180 - 45
        assert float(result[1]) == 90   # 180 - 90


class TestSectorNavigation:
    """Test Sector navigation methods"""
    
    def test_sector_port(self):
        """Test port (left turn) on all headings in Sector"""
        sector = Compass.sector([Compass.findHeading(90, 1), Compass.findHeading(180, 1)])
        
        result = sector.port(30)
        assert len(result) == 2
        assert float(result[0]) == 60
        assert float(result[1]) == 150
    
    def test_sector_starboard(self):
        """Test starboard (right turn) on all headings in Sector"""
        sector = Compass.sector([Compass.findHeading(90, 1), Compass.findHeading(180, 1)])
        
        result = sector.starboard(30)
        assert len(result) == 2
        assert float(result[0]) == 120
        assert float(result[1]) == 210
    
    def test_sector_left_right(self):
        """Test left and right aliases"""
        sector = Compass.sector([Compass.findHeading(90, 1)])
        
        left_result = sector.left(30)
        assert float(left_result[0]) == 60
        
        right_result = sector.right(30)
        assert float(right_result[0]) == 120


class TestSectorMinMax:
    """Test Sector min/max functionality"""
    
    def test_min_single_heading(self):
        """Test min with single heading"""
        sector = Compass.sector([Compass.findHeading(90, 1)])
        assert float(sector.min()) == 90
    
    def test_max_single_heading(self):
        """Test max with single heading"""
        sector = Compass.sector([Compass.findHeading(90, 1)])
        assert float(sector.max()) == 90
    
    def test_min_no_wraparound(self):
        """Test min when all headings are in one quadrant"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(90, 1))   # East
        sector.append(Compass.findHeading(120, 1))
        sector.append(Compass.findHeading(180, 1))  # South
        
        min_heading = sector.min()
        # Min should be the start of the smallest arc containing all headings
        # From 90°, the arc to 180° is 90° clockwise
        # This is the smallest containing arc, so min should be 90°
        assert float(min_heading) == 90
    
    def test_max_no_wraparound(self):
        """Test max when all headings are in one quadrant"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(90, 1))
        sector.append(Compass.findHeading(120, 1))
        sector.append(Compass.findHeading(180, 1))
        
        max_heading = sector.max()
        # Max should be furthest clockwise from min (90°), which is 180°
        assert float(max_heading) == 180
    
    def test_min_with_wraparound(self):
        """Test min with wraparound across 0°"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(350, 1))
        sector.append(Compass.findHeading(10, 1))
        sector.append(Compass.findHeading(20, 1))
        
        min_heading = sector.min()
        # Smallest arc is from 350° clockwise to 20°, so min is 350°
        assert float(min_heading) >= 337.5  # May snap to NNW at 337.5
    
    def test_min_max_opposite_headings(self):
        """Test min/max with headings at opposite ends"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(0, 1))    # North
        sector.append(Compass.findHeading(180, 1))  # South
        
        min_heading = sector.min()
        max_heading = sector.max()
        
        # With two headings 180° apart, min should be the one with smallest max clockwise distance
        # Both have max distance of 180°, so tiebreaker chooses smaller azimuth = 0°
        assert float(min_heading) == 0
        # Max should be the heading with maximum clockwise distance from min (0°)
        # 180° is 180° clockwise from 0°, so max is 180°
        assert float(max_heading) == 180
    
    def test_min_empty_sector(self):
        """Test that min raises error on empty Sector"""
        sector = Compass.sector()
        with pytest.raises(ValueError):
            sector.min()
    
    def test_max_empty_sector(self):
        """Test that max raises error on empty Sector"""
        sector = Compass.sector()
        with pytest.raises(ValueError):
            sector.max()


class TestSectorStatistics:
    """Test Sector statistical methods"""
    
    def test_relative_bearings(self):
        """Test relative bearings calculation"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(350, 1))
        sector.append(Compass.findHeading(10, 1))
        sector.append(Compass.findHeading(30, 1))
        
        relatives = sector.relative_bearings()
        # Min may snap to nearest heading, so be flexible
        assert len(relatives) == 3
        # First should be 0 (it's the min)
        assert relatives[0] == 0
    
    def test_mean_simple(self):
        """Test circular mean with simple case"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(0, 1))
        sector.append(Compass.findHeading(90, 1))
        
        mean = sector.mean()
        # Mean of 0° and 90° should be around 45°
        assert abs(mean - 45) < 1
    
    def test_mean_wraparound(self):
        """Test circular mean with wraparound"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(350, 1))
        sector.append(Compass.findHeading(10, 1))
        
        mean = sector.mean()
        # Mean of 350° and 10° should be around 0°
        assert mean < 5 or mean > 355
    
    def test_median_odd_count(self):
        """Test median with odd number of headings"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(90, 1))
        sector.append(Compass.findHeading(120, 1))
        sector.append(Compass.findHeading(150, 1))
        
        median = sector.median()
        # Median should be 120°
        assert abs(median - 120) < 1
    
    def test_median_even_count(self):
        """Test median with even number of headings"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(90, 1))
        sector.append(Compass.findHeading(180, 1))
        
        median = sector.median()
        # Median should be 135° (average of 90 and 180)
        assert abs(median - 135) < 1


class TestSectorIntegration:
    """Integration tests for Sector functionality"""
    
    def test_sector_workflow(self):
        """Test a complete workflow with Sector"""
        # Create sector
        sector = Compass.sector()
        sector.append(0)
        sector.append(90)
        sector.append(180)
        
        # Rotate
        rotated = sector + 45
        assert float(rotated[0]) == 45
        
        # Sort
        rotated.sort()
        assert float(rotated[0]) == 45
        
        # Statistics
        mean = rotated.mean()
        assert mean > 0  # Should have a valid mean
        
        # Min/Max
        min_h = rotated.min()
        max_h = rotated.max()
        assert float(min_h) <= float(max_h) or (float(min_h) > 180 and float(max_h) < 180)


class TestMultiLanguageSupport:
    """Test multi-language support functionality"""
    
    @pytest.fixture(scope="class")
    def compass_data(self):
        """Load compass data from JSON file"""
        try:
            # Try to find the data file relative to the test
            data_file_path = Path(__file__).parent / '../compassheadinglib/compass_data.json'
            if not data_file_path.exists():
                # Alternative path
                data_file_path = Path('compassheadinglib/compass_data.json')
            
            if data_file_path.exists():
                with open(data_file_path, 'rt') as f:
                    return load(f)
            else:
                pytest.skip("compass_data.json not found - skipping multilanguage tests")
        except Exception as e:
            pytest.skip(f"Could not load compass data: {e}")

    def flatten(self, x):
        """Helper function to flatten nested lists"""
        return list(chain.from_iterable(x))

    def test_language_structure(self, compass_data):
        """Test that all languages have proper structure"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        # Get all unique language codes in the dataset
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for heading in compass_data:
            for lang in all_langs:
                # All languages must be present in all headings
                assert lang in heading['Lang'], f'{lang} missing from {heading["Azimuth"]}'
                
                # Check that structure is well formed
                assert 'Heading' in heading['Lang'][lang]
                assert 'Abbreviation' in heading['Lang'][lang]

    def test_unique_translations(self, compass_data):
        """Test that translations are unique within each language"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for lang in all_langs:
            lang_compass = [i['Lang'][lang] | i for i in compass_data]
            
            # No duplicate heading names (except for North wraparound)
            heading_names = [i['Heading'] for i in lang_compass]
            heading_counter = Counter(heading_names)
            
            for name, count in heading_counter.items():
                if count > 1:
                    # Check if this is the expected North wraparound
                    azimuths = [i['Azimuth'] for i in lang_compass if i['Heading'] == name]
                    if not (len(azimuths) == 2 and 0 in azimuths and 360 in azimuths):
                        pytest.fail(f"Duplicate heading name '{name}' in language '{lang}' at azimuths {azimuths}")
            
            # No duplicate abbreviations (except for North wraparound)
            abbr_names = [i['Abbreviation'] for i in lang_compass]
            abbr_counter = Counter(abbr_names)
            
            for abbr, count in abbr_counter.items():
                if count > 1:
                    # Check if this is the expected North wraparound
                    azimuths = [i['Azimuth'] for i in lang_compass if i['Abbreviation'] == abbr]
                    if not (len(azimuths) == 2 and 0 in azimuths and 360 in azimuths):
                        pytest.fail(f"Duplicate abbreviation '{abbr}' in language '{lang}' at azimuths {azimuths}")

    def test_language_wraparound(self, compass_data):
        """Test wraparound for each language"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for lang in all_langs:
            lang_compass = [i['Lang'][lang] | i for i in compass_data]
            
            # Wrap around test, per language
            assert lang_compass[0]['Heading'] == lang_compass[-1]['Heading'], f'Wrap around test fail: Heading for {lang}'
            assert lang_compass[0]['Abbreviation'] == lang_compass[-1]['Abbreviation'], f'Wrap around test fail: Abbreviation for {lang}'
            assert lang_compass[0]['Order'] == lang_compass[-1]['Order'], f'Wrap around test fail: Order for {lang}'
            assert lang_compass[0]['Azimuth'] < lang_compass[-1]['Azimuth'], f'Wrap around test fail: Azimuth for {lang}'

    
class TestSectorPercentile:
    """Test Sector percentile and median methods"""

    def test_percentile_single_heading(self):
        """Test percentile with single heading"""
        sector = Compass.sector([Compass.findHeading(90, 1)])
        assert sector.percentile(0.5) == 90.0
        assert sector.percentile(0.0) == 90.0
        assert sector.percentile(1.0) == 90.0
    
    def test_percentile_two_headings(self):
        """Test percentile with two headings"""
        sector = Compass.sector([Compass.findHeading(0, 1), Compass.findHeading(90, 1)])
        
        # 0th percentile should be 0°
        assert sector.percentile(0.0) == 0.0
        
        # 100th percentile should be 90°
        assert sector.percentile(1.0) == 90.0
        
        # 50th percentile (median) should be 45°
        assert sector.percentile(0.5) == 45.0
    
    def test_percentile_odd_count(self):
        """Test percentile with odd number of headings"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(0, 1))
        sector.append(Compass.findHeading(90, 1))
        sector.append(Compass.findHeading(180, 1))
        
        # 0th percentile
        p0 = sector.percentile(0.0)
        assert p0 == 0.0
        
        # 50th percentile (median) - should be middle value
        p50 = sector.percentile(0.5)
        assert p50 == 90.0
        
        # 100th percentile
        p100 = sector.percentile(1.0)
        assert p100 == 180.0
    
    def test_percentile_even_count(self):
        """Test percentile with even number of headings"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(0, 1))
        sector.append(Compass.findHeading(60, 1))
        sector.append(Compass.findHeading(120, 1))
        sector.append(Compass.findHeading(180, 1))
        
        # 25th percentile - position 0.75, interpolating between indices 0 and 1
        # 75% of way from 0° to 60° = 45°
        p25 = sector.percentile(0.25)
        assert abs(p25 - 45.0) < 1
        
        # 50th percentile - position 1.5, interpolating between indices 1 and 2
        # 50% of way from 60° to 120° = 90°
        p50 = sector.percentile(0.5)
        assert abs(p50 - 90.0) < 1
        
        # 75th percentile - position 2.25, interpolating between indices 2 and 3
        # 25% of way from 120° to 180° = 135°
        p75 = sector.percentile(0.75)
        assert abs(p75 - 135.0) < 1
    
    def test_percentile_with_wraparound(self):
        """Test percentile with wraparound across 0°"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(350, 1))
        sector.append(Compass.findHeading(0, 1))
        sector.append(Compass.findHeading(10, 1))
        
        # Median should be near 0°
        median = sector.percentile(0.5)
        assert median < 5 or median > 355
    
    def test_percentile_invalid_range(self):
        """Test that percentile raises error for out-of-range values"""
        sector = Compass.sector([Compass.findHeading(90, 1)])
        
        with pytest.raises(ValueError) as excinfo:
            sector.percentile(-0.1)
        assert "must be between 0.0 and 1.0" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            sector.percentile(1.5)
        assert "must be between 0.0 and 1.0" in str(excinfo.value)
    
    def test_percentile_empty_sector(self):
        """Test that percentile raises error on empty sector"""
        sector = Compass.sector()
        
        with pytest.raises(ValueError) as excinfo:
            sector.percentile(0.5)
        assert "Cannot find percentile of empty Sector" in str(excinfo.value)
    
    def test_median_wrapper(self):
        """Test that median() properly wraps percentile(0.5)"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(90, 1))
        sector.append(Compass.findHeading(120, 1))
        sector.append(Compass.findHeading(150, 1))
        
        median = sector.median()
        p50 = sector.percentile(0.5)
        
        assert median == p50
        assert abs(median - 120) < 1
    
    def test_percentile_interpolation(self):
        """Test that percentile properly interpolates between values"""
        sector = Compass.sector()
        sector.append(Compass.findHeading(0, 1))
        sector.append(Compass.findHeading(100, 1))
        
        # At 25%, should be 25% of the way from 0 to 100
        p25 = sector.percentile(0.25)
        assert abs(p25 - 25.0) < 1
        
        # At 75%, should be 75% of the way from 0 to 100
        p75 = sector.percentile(0.75)
        assert abs(p75 - 75.0) < 1

if __name__ == "__main__":
    # Run tests with pytest when script is executed directly
    pytest.main([__file__, "-v"])