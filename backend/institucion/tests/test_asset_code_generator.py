"""
Unit tests for AssetCodeGenerator service.

Tests all functionality of the AssetCodeGenerator service including:
- Asset code generation with pattern validation
- Code evolution algorithm for warehouse transfers
- Code parsing functionality to extract movement history
- Support for multiple transfer chains
- Validation of code formats
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from .services import AssetCodeGenerator, AssetCodeValidator, AssetCodeInfo


class TestAssetCodeGenerator(TestCase):
    """Test cases for AssetCodeGenerator service"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_warehouse = 'ZUL'
        self.valid_asset_type = 'BOMBA'
        self.current_year = timezone.now().year
    
    def test_generate_asset_code_basic(self):
        """Test basic asset code generation"""
        code = AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=self.valid_warehouse,
            asset_type=self.valid_asset_type
        )
        
        # Should follow pattern: ZUL-BOMBA-XXXXXX-YYYY
        self.assertTrue(code.startswith(f"{self.valid_warehouse}-{self.valid_asset_type}-"))
        self.assertTrue(code.endswith(f"-{self.current_year}"))
        self.assertEqual(len(code.split('-')), 4)
    
    def test_generate_asset_code_with_year(self):
        """Test asset code generation with specific year"""
        test_year = 2023
        code = AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=self.valid_warehouse,
            asset_type=self.valid_asset_type,
            year=test_year
        )
        
        self.assertTrue(code.endswith(f"-{test_year}"))
    
    def test_generate_asset_code_invalid_warehouse(self):
        """Test asset code generation with invalid warehouse prefix"""
        with self.assertRaises(ValidationError) as context:
            AssetCodeGenerator.generate_asset_code(
                warehouse_prefix='INVALID',
                asset_type=self.valid_asset_type
            )
        
        self.assertIn('Invalid warehouse prefix', str(context.exception))
    
    def test_generate_asset_code_invalid_asset_type(self):
        """Test asset code generation with invalid asset type"""
        with self.assertRaises(ValidationError) as context:
            AssetCodeGenerator.generate_asset_code(
                warehouse_prefix=self.valid_warehouse,
                asset_type='INVALID_TYPE'
            )
        
        self.assertIn('Invalid asset type', str(context.exception))
    
    def test_evolve_asset_code_basic(self):
        """Test basic asset code evolution"""
        original_code = "ZUL-BOMBA-000001-2024"
        new_warehouse = "CAR"
        
        evolved_code = AssetCodeGenerator.evolve_asset_code(
            current_code=original_code,
            new_warehouse_prefix=new_warehouse
        )
        
        expected = f"{new_warehouse}-{original_code}"
        self.assertEqual(evolved_code, expected)
    
    def test_evolve_asset_code_multiple_transfers(self):
        """Test asset code evolution through multiple transfers"""
        # Start with original code
        code1 = "ZUL-BOMBA-000001-2024"
        
        # First transfer: ZUL -> CAR
        code2 = AssetCodeGenerator.evolve_asset_code(code1, "CAR")
        self.assertEqual(code2, "CAR-ZUL-BOMBA-000001-2024")
        
        # Second transfer: CAR -> MIR
        code3 = AssetCodeGenerator.evolve_asset_code(code2, "MIR")
        self.assertEqual(code3, "MIR-CAR-ZUL-BOMBA-000001-2024")
        
        # Third transfer: MIR -> ARA
        code4 = AssetCodeGenerator.evolve_asset_code(code3, "ARA")
        self.assertEqual(code4, "ARA-MIR-CAR-ZUL-BOMBA-000001-2024")
    
    def test_evolve_asset_code_same_warehouse(self):
        """Test asset code evolution to same warehouse (should fail)"""
        original_code = "ZUL-BOMBA-000001-2024"
        
        with self.assertRaises(ValidationError) as context:
            AssetCodeGenerator.evolve_asset_code(
                current_code=original_code,
                new_warehouse_prefix="ZUL"
            )
        
        self.assertIn('already at warehouse', str(context.exception))
    
    def test_evolve_asset_code_invalid_current_code(self):
        """Test asset code evolution with invalid current code"""
        with self.assertRaises(ValidationError) as context:
            AssetCodeGenerator.evolve_asset_code(
                current_code="INVALID-CODE",
                new_warehouse_prefix="CAR"
            )
        
        self.assertIn('invalid format', str(context.exception))
    
    def test_parse_asset_code_original(self):
        """Test parsing original asset code"""
        code = "ZUL-BOMBA-000001-2024"
        info = AssetCodeGenerator.parse_asset_code(code)
        
        self.assertIsInstance(info, AssetCodeInfo)
        self.assertEqual(info.current_warehouse, "ZUL")
        self.assertEqual(info.movement_history, [])
        self.assertEqual(info.asset_type, "BOMBA")
        self.assertEqual(info.sequence, "000001")
        self.assertEqual(info.year, "2024")
        self.assertEqual(info.original_code, "ZUL-BOMBA-000001-2024")
        self.assertFalse(info.is_evolved)
        self.assertEqual(info.transfer_count, 0)
    
    def test_parse_asset_code_evolved_once(self):
        """Test parsing asset code evolved once"""
        code = "CAR-ZUL-BOMBA-000001-2024"
        info = AssetCodeGenerator.parse_asset_code(code)
        
        self.assertIsInstance(info, AssetCodeInfo)
        self.assertEqual(info.current_warehouse, "CAR")
        self.assertEqual(info.movement_history, ["ZUL"])
        self.assertEqual(info.asset_type, "BOMBA")
        self.assertEqual(info.sequence, "000001")
        self.assertEqual(info.year, "2024")
        self.assertEqual(info.original_code, "ZUL-BOMBA-000001-2024")
        self.assertTrue(info.is_evolved)
        self.assertEqual(info.transfer_count, 1)
    
    def test_parse_asset_code_evolved_multiple(self):
        """Test parsing asset code evolved multiple times"""
        code = "ARA-MIR-CAR-ZUL-BOMBA-000001-2024"
        info = AssetCodeGenerator.parse_asset_code(code)
        
        self.assertIsInstance(info, AssetCodeInfo)
        self.assertEqual(info.current_warehouse, "ARA")
        self.assertEqual(info.movement_history, ["MIR", "CAR", "ZUL"])
        self.assertEqual(info.asset_type, "BOMBA")
        self.assertEqual(info.sequence, "000001")
        self.assertEqual(info.year, "2024")
        self.assertEqual(info.original_code, "ZUL-BOMBA-000001-2024")
        self.assertTrue(info.is_evolved)
        self.assertEqual(info.transfer_count, 3)
    
    def test_parse_asset_code_invalid(self):
        """Test parsing invalid asset codes"""
        invalid_codes = [
            "",
            "INVALID",
            "ZUL-BOMBA",
            "ZUL-BOMBA-001",
            "ZUL-BOMBA-001-24",  # Year too short
            "ZUL-BOMBA-1-2024",  # Sequence too short
            "XX-BOMBA-000001-2024",  # Invalid warehouse prefix
        ]
        
        for code in invalid_codes:
            with self.subTest(code=code):
                info = AssetCodeGenerator.parse_asset_code(code)
                self.assertIsNone(info)
    
    def test_validate_asset_code_format_valid_codes(self):
        """Test validation of valid asset codes"""
        valid_codes = [
            "ZUL-BOMBA-000001-2024",
            "CAR-ZUL-BOMBA-000001-2024",
            "MIR-CAR-ZUL-BOMBA-000001-2024",
            "ARA-MIR-CAR-ZUL-BOMBA-000001-2024",
            "LAR-TUBERIA-999999-2023",
            "TAC-QUIMICO-000001-2025",
        ]
        
        for code in valid_codes:
            with self.subTest(code=code):
                self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code))
    
    def test_validate_asset_code_format_invalid_codes(self):
        """Test validation of invalid asset codes"""
        invalid_codes = [
            "",
            None,
            "INVALID",
            "ZUL-BOMBA",
            "ZUL-BOMBA-001-24",
            "XX-BOMBA-000001-2024",  # Invalid warehouse
            "ZUL-INVALID-000001-2024",  # Invalid asset type
            "ZUL-BOMBA-1-2024",  # Invalid sequence
            "ZUL-BOMBA-000001-24",  # Invalid year
        ]
        
        for code in invalid_codes:
            with self.subTest(code=code):
                self.assertFalse(AssetCodeGenerator.validate_asset_code_format(code))
    
    def test_validate_code_evolution_chain_valid(self):
        """Test validation of valid evolution chains"""
        chains = [
            ["ZUL-BOMBA-000001-2024"],  # Single code
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-ZUL-BOMBA-000001-2024"
            ],
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-ZUL-BOMBA-000001-2024",
                "MIR-CAR-ZUL-BOMBA-000001-2024"
            ]
        ]
        
        for chain in chains:
            with self.subTest(chain=chain):
                self.assertTrue(AssetCodeGenerator.validate_code_evolution_chain(chain))
    
    def test_validate_code_evolution_chain_invalid(self):
        """Test validation of invalid evolution chains"""
        invalid_chains = [
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-ZUL-BOMBA-000002-2024"  # Different sequence
            ],
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-ZUL-MOTOR-000001-2024"  # Different asset type
            ],
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-ZUL-BOMBA-000001-2023"  # Different year
            ],
            [
                "ZUL-BOMBA-000001-2024",
                "CAR-MIR-BOMBA-000001-2024"  # Invalid evolution
            ]
        ]
        
        for chain in invalid_chains:
            with self.subTest(chain=chain):
                self.assertFalse(AssetCodeGenerator.validate_code_evolution_chain(chain))
    
    def test_get_movement_history_from_code(self):
        """Test extracting movement history from codes"""
        test_cases = [
            ("ZUL-BOMBA-000001-2024", ["ZUL"]),
            ("CAR-ZUL-BOMBA-000001-2024", ["ZUL", "CAR"]),
            ("MIR-CAR-ZUL-BOMBA-000001-2024", ["ZUL", "CAR", "MIR"]),
            ("ARA-MIR-CAR-ZUL-BOMBA-000001-2024", ["ZUL", "CAR", "MIR", "ARA"])
        ]
        
        for code, expected_history in test_cases:
            with self.subTest(code=code):
                history = AssetCodeGenerator.get_movement_history_from_code(code)
                self.assertEqual(history, expected_history)
    
    def test_get_original_code_from_evolved(self):
        """Test extracting original code from evolved codes"""
        test_cases = [
            ("ZUL-BOMBA-000001-2024", "ZUL-BOMBA-000001-2024"),
            ("CAR-ZUL-BOMBA-000001-2024", "ZUL-BOMBA-000001-2024"),
            ("MIR-CAR-ZUL-BOMBA-000001-2024", "ZUL-BOMBA-000001-2024"),
            ("ARA-MIR-CAR-ZUL-BOMBA-000001-2024", "ZUL-BOMBA-000001-2024")
        ]
        
        for evolved_code, expected_original in test_cases:
            with self.subTest(code=evolved_code):
                original = AssetCodeGenerator.get_original_code_from_evolved(evolved_code)
                self.assertEqual(original, expected_original)
    
    def test_is_code_evolved(self):
        """Test checking if code has been evolved"""
        test_cases = [
            ("ZUL-BOMBA-000001-2024", False),
            ("CAR-ZUL-BOMBA-000001-2024", True),
            ("MIR-CAR-ZUL-BOMBA-000001-2024", True),
        ]
        
        for code, expected_evolved in test_cases:
            with self.subTest(code=code):
                is_evolved = AssetCodeGenerator.is_code_evolved(code)
                self.assertEqual(is_evolved, expected_evolved)
    
    def test_get_transfer_count(self):
        """Test getting transfer count from codes"""
        test_cases = [
            ("ZUL-BOMBA-000001-2024", 0),
            ("CAR-ZUL-BOMBA-000001-2024", 1),
            ("MIR-CAR-ZUL-BOMBA-000001-2024", 2),
            ("ARA-MIR-CAR-ZUL-BOMBA-000001-2024", 3),
        ]
        
        for code, expected_count in test_cases:
            with self.subTest(code=code):
                count = AssetCodeGenerator.get_transfer_count(code)
                self.assertEqual(count, expected_count)
    
    def test_validate_transfer_compatibility(self):
        """Test transfer compatibility validation"""
        # Valid transfers
        self.assertTrue(AssetCodeGenerator.validate_transfer_compatibility(
            current_code="ZUL-BOMBA-000001-2024",
            origin_warehouse="ZUL",
            destination_warehouse="CAR"
        ))
        
        self.assertTrue(AssetCodeGenerator.validate_transfer_compatibility(
            current_code="CAR-ZUL-BOMBA-000001-2024",
            origin_warehouse="CAR",
            destination_warehouse="MIR"
        ))
        
        # Invalid transfers
        # Wrong origin warehouse
        self.assertFalse(AssetCodeGenerator.validate_transfer_compatibility(
            current_code="ZUL-BOMBA-000001-2024",
            origin_warehouse="CAR",
            destination_warehouse="MIR"
        ))
        
        # Same origin and destination
        self.assertFalse(AssetCodeGenerator.validate_transfer_compatibility(
            current_code="ZUL-BOMBA-000001-2024",
            origin_warehouse="ZUL",
            destination_warehouse="ZUL"
        ))
        
        # Invalid warehouse prefixes
        self.assertFalse(AssetCodeGenerator.validate_transfer_compatibility(
            current_code="ZUL-BOMBA-000001-2024",
            origin_warehouse="INVALID",
            destination_warehouse="CAR"
        ))
    
    def test_generate_batch_codes(self):
        """Test batch code generation"""
        codes = AssetCodeGenerator.generate_batch_codes(
            warehouse_prefix="ZUL",
            asset_type="BOMBA",
            count=5
        )
        
        self.assertEqual(len(codes), 5)
        
        # All codes should be unique
        self.assertEqual(len(set(codes)), 5)
        
        # All codes should be valid
        for code in codes:
            self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code))
    
    def test_generate_batch_codes_invalid_count(self):
        """Test batch code generation with invalid count"""
        with self.assertRaises(ValidationError):
            AssetCodeGenerator.generate_batch_codes(
                warehouse_prefix="ZUL",
                asset_type="BOMBA",
                count=0
            )
        
        with self.assertRaises(ValidationError):
            AssetCodeGenerator.generate_batch_codes(
                warehouse_prefix="ZUL",
                asset_type="BOMBA",
                count=1001  # Too many
            )
    
    def test_get_code_statistics(self):
        """Test code statistics generation"""
        codes = [
            "ZUL-BOMBA-000001-2024",
            "CAR-ZUL-BOMBA-000002-2024",
            "MIR-CAR-ZUL-BOMBA-000003-2024",
            "INVALID-CODE",
            "LAR-TUBERIA-000001-2023"
        ]
        
        stats = AssetCodeGenerator.get_code_statistics(codes)
        
        self.assertEqual(stats['total_codes'], 5)
        self.assertEqual(stats['valid_codes'], 4)
        self.assertEqual(stats['invalid_codes'], 1)
        self.assertEqual(stats['evolved_codes'], 2)
        self.assertEqual(stats['original_codes'], 2)
        self.assertIn('ZUL', stats['warehouses'])
        self.assertIn('CAR', stats['warehouses'])
        self.assertIn('MIR', stats['warehouses'])
        self.assertIn('LAR', stats['warehouses'])
        self.assertIn('BOMBA', stats['asset_types'])
        self.assertIn('TUBERIA', stats['asset_types'])
        self.assertIn('2024', stats['years'])
        self.assertIn('2023', stats['years'])
        self.assertEqual(stats['max_transfers'], 2)
    
    def test_get_code_statistics_empty(self):
        """Test code statistics with empty list"""
        stats = AssetCodeGenerator.get_code_statistics([])
        
        self.assertEqual(stats['total_codes'], 0)
        self.assertEqual(stats['valid_codes'], 0)
        self.assertEqual(stats['invalid_codes'], 0)
        self.assertEqual(stats['evolved_codes'], 0)
        self.assertEqual(stats['original_codes'], 0)
        self.assertEqual(stats['warehouses'], [])
        self.assertEqual(stats['asset_types'], [])
        self.assertEqual(stats['years'], [])
        self.assertEqual(stats['max_transfers'], 0)
        self.assertEqual(stats['avg_transfers'], 0.0)


class TestAssetCodeValidator(TestCase):
    """Test cases for AssetCodeValidator"""
    
    def test_validate_code_with_details_valid(self):
        """Test detailed validation of valid codes"""
        valid_codes = [
            "ZUL-BOMBA-000001-2024",
            "CAR-ZUL-BOMBA-000001-2024",
        ]
        
        for code in valid_codes:
            with self.subTest(code=code):
                is_valid, errors = AssetCodeValidator.validate_code_with_details(code)
                self.assertTrue(is_valid)
                self.assertEqual(errors, [])
    
    def test_validate_code_with_details_invalid(self):
        """Test detailed validation of invalid codes"""
        invalid_cases = [
            ("", ["Asset code cannot be empty"]),
            ("INVALID", ["Asset code does not match required pattern"]),
            ("XX-BOMBA-000001-2024", ["Invalid warehouse prefix: XX"]),
            ("ZUL-INVALID-000001-2024", ["Invalid asset type: INVALID"]),
            ("ZUL-BOMBA-000001-1999", ["Invalid year: 1999"]),
            ("ZUL-BOMBA-0-2024", ["Invalid sequence format: 0"]),
        ]
        
        for code, expected_error_substrings in invalid_cases:
            with self.subTest(code=code):
                is_valid, errors = AssetCodeValidator.validate_code_with_details(code)
                self.assertFalse(is_valid)
                self.assertTrue(len(errors) > 0)
                
                # Check that expected error substrings are present
                error_text = ' '.join(errors)
                for expected_substring in expected_error_substrings:
                    self.assertIn(expected_substring, error_text)
    
    def test_validate_evolution_step_valid(self):
        """Test validation of valid evolution steps"""
        valid_steps = [
            ("ZUL-BOMBA-000001-2024", "CAR-ZUL-BOMBA-000001-2024"),
            ("CAR-ZUL-BOMBA-000001-2024", "MIR-CAR-ZUL-BOMBA-000001-2024"),
        ]
        
        for old_code, new_code in valid_steps:
            with self.subTest(old_code=old_code, new_code=new_code):
                is_valid, errors = AssetCodeValidator.validate_evolution_step(old_code, new_code)
                self.assertTrue(is_valid)
                self.assertEqual(errors, [])
    
    def test_validate_evolution_step_invalid(self):
        """Test validation of invalid evolution steps"""
        invalid_steps = [
            ("ZUL-BOMBA-000001-2024", "CAR-ZUL-BOMBA-000002-2024"),  # Different sequence
            ("ZUL-BOMBA-000001-2024", "CAR-ZUL-MOTOR-000001-2024"),  # Different asset type
            ("ZUL-BOMBA-000001-2024", "CAR-MIR-BOMBA-000001-2024"),  # Invalid evolution
        ]
        
        for old_code, new_code in invalid_steps:
            with self.subTest(old_code=old_code, new_code=new_code):
                is_valid, errors = AssetCodeValidator.validate_evolution_step(old_code, new_code)
                self.assertFalse(is_valid)
                self.assertTrue(len(errors) > 0)


class TestAssetCodeInfo(TestCase):
    """Test cases for AssetCodeInfo dataclass"""
    
    def test_asset_code_info_creation(self):
        """Test AssetCodeInfo dataclass creation"""
        info = AssetCodeInfo(
            current_warehouse="CAR",
            movement_history=["ZUL"],
            asset_type="BOMBA",
            sequence="000001",
            year="2024",
            original_code="ZUL-BOMBA-000001-2024",
            is_evolved=True,
            transfer_count=1
        )
        
        self.assertEqual(info.current_warehouse, "CAR")
        self.assertEqual(info.movement_history, ["ZUL"])
        self.assertEqual(info.asset_type, "BOMBA")
        self.assertEqual(info.sequence, "000001")
        self.assertEqual(info.year, "2024")
        self.assertEqual(info.original_code, "ZUL-BOMBA-000001-2024")
        self.assertTrue(info.is_evolved)
        self.assertEqual(info.transfer_count, 1)


class TestAssetCodeGeneratorIntegration(TestCase):
    """Integration tests for AssetCodeGenerator with realistic scenarios"""
    
    def test_complete_asset_lifecycle(self):
        """Test complete asset lifecycle with multiple transfers"""
        # Generate initial code
        code1 = AssetCodeGenerator.generate_asset_code("ZUL", "BOMBA")
        self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code1))
        
        # First transfer: ZUL -> CAR
        code2 = AssetCodeGenerator.evolve_asset_code(code1, "CAR")
        self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code2))
        
        # Second transfer: CAR -> MIR
        code3 = AssetCodeGenerator.evolve_asset_code(code2, "MIR")
        self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code3))
        
        # Third transfer: MIR -> ARA
        code4 = AssetCodeGenerator.evolve_asset_code(code3, "ARA")
        self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code4))
        
        # Validate evolution chain
        codes = [code1, code2, code3, code4]
        self.assertTrue(AssetCodeGenerator.validate_code_evolution_chain(codes))
        
        # Check movement history
        history = AssetCodeGenerator.get_movement_history_from_code(code4)
        expected_history = ["ZUL", "CAR", "MIR", "ARA"]
        self.assertEqual(history, expected_history)
        
        # Check transfer count
        transfer_count = AssetCodeGenerator.get_transfer_count(code4)
        self.assertEqual(transfer_count, 3)
        
        # Check original code extraction
        original = AssetCodeGenerator.get_original_code_from_evolved(code4)
        self.assertEqual(original, code1)
    
    def test_multiple_assets_same_warehouse(self):
        """Test generating multiple assets for the same warehouse"""
        # Use batch generation which handles uniqueness properly
        codes = AssetCodeGenerator.generate_batch_codes("ZUL", "BOMBA", 10)
        
        # All codes should be unique
        self.assertEqual(len(set(codes)), 10)
        
        # All codes should be valid
        for code in codes:
            self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code))
    
    def test_cross_warehouse_transfers(self):
        """Test transfers between different warehouses"""
        # Create assets in different warehouses
        zul_asset = AssetCodeGenerator.generate_asset_code("ZUL", "BOMBA")
        car_asset = AssetCodeGenerator.generate_asset_code("CAR", "MOTOR")
        mir_asset = AssetCodeGenerator.generate_asset_code("MIR", "TUBERIA")
        
        # Transfer ZUL asset to CAR
        zul_to_car = AssetCodeGenerator.evolve_asset_code(zul_asset, "CAR")
        
        # Transfer CAR asset to MIR
        car_to_mir = AssetCodeGenerator.evolve_asset_code(car_asset, "MIR")
        
        # Transfer MIR asset to ZUL
        mir_to_zul = AssetCodeGenerator.evolve_asset_code(mir_asset, "ZUL")
        
        # All evolved codes should be valid
        evolved_codes = [zul_to_car, car_to_mir, mir_to_zul]
        for code in evolved_codes:
            self.assertTrue(AssetCodeGenerator.validate_asset_code_format(code))
        
        # Check that each asset maintains its original identity
        self.assertEqual(
            AssetCodeGenerator.get_original_code_from_evolved(zul_to_car),
            zul_asset
        )
        self.assertEqual(
            AssetCodeGenerator.get_original_code_from_evolved(car_to_mir),
            car_asset
        )
        self.assertEqual(
            AssetCodeGenerator.get_original_code_from_evolved(mir_to_zul),
            mir_asset
        )


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    # Configure Django settings if not already configured
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'institucion',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()
    
    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])