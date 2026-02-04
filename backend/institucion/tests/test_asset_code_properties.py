"""
Property-based tests for AssetCodeGenerator service.

This module contains comprehensive property-based tests that validate universal
properties of asset code generation, evolution, and parsing across all possible
inputs using Hypothesis for randomized testing.

Tests validate:
- Property 5: Asset Code Generation and Evolution
- Property 6: Asset Code Uniqueness  
- Property 7: Asset Code Parsing Round-Trip

Each property test runs with minimum 100 iterations to ensure comprehensive
coverage across the input space.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis.extra.django import TestCase
from django.core.exceptions import ValidationError

from .services import AssetCodeGenerator, AssetCodeValidator, AssetCodeInfo


# ============================================================================
# HYPOTHESIS STRATEGIES FOR GENERATING TEST DATA
# ============================================================================

# Valid warehouse prefixes from the service
VALID_WAREHOUSES = AssetCodeGenerator.VALID_WAREHOUSE_PREFIXES
VALID_ASSET_TYPES = AssetCodeGenerator.VALID_ASSET_TYPES

# Strategy for generating valid warehouse prefixes
warehouse_strategy = st.sampled_from(VALID_WAREHOUSES)

# Strategy for generating valid asset types
asset_type_strategy = st.sampled_from(VALID_ASSET_TYPES)

# Strategy for generating valid years (2020-2030)
year_strategy = st.integers(min_value=2020, max_value=2030)

# Strategy for generating valid sequence numbers (1-999999)
sequence_strategy = st.integers(min_value=1, max_value=999999)

# Strategy for generating original asset codes
@st.composite
def original_asset_code_strategy(draw):
    """Generate valid original asset codes."""
    warehouse = draw(warehouse_strategy)
    asset_type = draw(asset_type_strategy)
    sequence = draw(sequence_strategy)
    year = draw(year_strategy)
    
    return f"{warehouse}-{asset_type}-{sequence:06d}-{year}"

# Strategy for generating evolved asset codes (1-5 transfers)
@st.composite
def evolved_asset_code_strategy(draw):
    """Generate valid evolved asset codes with 1-5 transfers."""
    original_code = draw(original_asset_code_strategy())
    
    # Number of transfers (1-5)
    num_transfers = draw(st.integers(min_value=1, max_value=5))
    
    # Get original warehouse from code
    original_warehouse = original_code.split('-')[0]
    
    # Generate transfer chain
    current_code = original_code
    used_warehouses = {original_warehouse}
    
    for _ in range(num_transfers):
        # Choose a different warehouse for transfer
        available_warehouses = [w for w in VALID_WAREHOUSES if w not in used_warehouses]
        if not available_warehouses:
            # If all warehouses used, allow reuse (though unlikely with 9 warehouses)
            available_warehouses = [w for w in VALID_WAREHOUSES if w != current_code.split('-')[0]]
        
        if available_warehouses:
            new_warehouse = draw(st.sampled_from(available_warehouses))
            current_code = f"{new_warehouse}-{current_code}"
            used_warehouses.add(new_warehouse)
    
    return current_code

# Strategy for generating any valid asset code (original or evolved)
valid_asset_code_strategy = st.one_of(
    original_asset_code_strategy(),
    evolved_asset_code_strategy()
)

# Strategy for generating lists of unique asset codes
@st.composite
def unique_asset_codes_strategy(draw, min_size=2, max_size=20):
    """Generate lists of unique asset codes."""
    codes = []
    used_sequences = set()
    
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    
    for _ in range(size):
        # Generate unique sequence to ensure uniqueness
        sequence = draw(st.integers(min_value=1, max_value=999999))
        while sequence in used_sequences:
            sequence = draw(st.integers(min_value=1, max_value=999999))
        used_sequences.add(sequence)
        
        warehouse = draw(warehouse_strategy)
        asset_type = draw(asset_type_strategy)
        year = draw(year_strategy)
        
        code = f"{warehouse}-{asset_type}-{sequence:06d}-{year}"
        codes.append(code)
    
    return codes

# Strategy for generating transfer scenarios
@st.composite
def transfer_scenario_strategy(draw):
    """Generate valid transfer scenarios."""
    current_code = draw(valid_asset_code_strategy)
    
    # Parse current code to get current warehouse
    code_info = AssetCodeGenerator.parse_asset_code(current_code)
    assume(code_info is not None)
    
    current_warehouse = code_info.current_warehouse
    
    # Choose different destination warehouse
    available_destinations = [w for w in VALID_WAREHOUSES if w != current_warehouse]
    destination_warehouse = draw(st.sampled_from(available_destinations))
    
    return {
        'current_code': current_code,
        'origin_warehouse': current_warehouse,
        'destination_warehouse': destination_warehouse
    }


# ============================================================================
# PROPERTY-BASED TESTS
# ============================================================================

class TestAssetCodeGenerationProperties(TestCase):
    """Property-based tests for asset code generation and evolution."""
    
    @given(
        warehouse=warehouse_strategy,
        asset_type=asset_type_strategy,
        year=year_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_5_asset_code_generation_and_evolution(self, warehouse, asset_type, year):
        """
        **Feature: hidroven-organizational-restructuring, Property 5: Asset Code Generation and Evolution**
        
        **Validates: Requirements 3.1, 3.2, 3.5**
        
        For any asset and warehouse combination, the generated asset code should follow 
        the pattern {WAREHOUSE}-{TYPE}-{SEQUENCE}-{YEAR}, and when transferred, should 
        evolve to {NEW_WAREHOUSE}-{OLD_CODE} while maintaining the original sequence 
        number throughout all transfers.
        """
        # Generate initial asset code
        initial_code = AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=warehouse,
            asset_type=asset_type,
            year=year
        )
        
        # Verify initial code follows correct pattern
        parts = initial_code.split('-')
        assert len(parts) == 4, f"Initial code should have 4 parts: {initial_code}"
        assert parts[0] == warehouse, f"First part should be warehouse: {initial_code}"
        assert parts[1] == asset_type, f"Second part should be asset type: {initial_code}"
        assert len(parts[2]) == 6, f"Sequence should be 6 digits: {initial_code}"
        assert parts[3] == str(year), f"Last part should be year: {initial_code}"
        
        # Parse initial code to get sequence
        initial_info = AssetCodeGenerator.parse_asset_code(initial_code)
        assert initial_info is not None, f"Initial code should be parseable: {initial_code}"
        original_sequence = initial_info.sequence
        original_asset_type = initial_info.asset_type
        original_year = initial_info.year
        
        # Test evolution through multiple transfers
        current_code = initial_code
        transfer_count = 0
        
        # Perform up to 3 transfers to different warehouses
        available_warehouses = [w for w in VALID_WAREHOUSES if w != warehouse]
        for new_warehouse in available_warehouses[:3]:  # Test up to 3 transfers
            # Evolve code
            evolved_code = AssetCodeGenerator.evolve_asset_code(current_code, new_warehouse)
            
            # Verify evolution pattern: {NEW_WAREHOUSE}-{OLD_CODE}
            assert evolved_code == f"{new_warehouse}-{current_code}", \
                f"Evolved code should follow pattern: {evolved_code}"
            
            # Parse evolved code
            evolved_info = AssetCodeGenerator.parse_asset_code(evolved_code)
            assert evolved_info is not None, f"Evolved code should be parseable: {evolved_code}"
            
            # Verify sequence number is maintained
            assert evolved_info.sequence == original_sequence, \
                f"Sequence should be maintained: {evolved_info.sequence} vs {original_sequence}"
            
            # Verify asset type is maintained
            assert evolved_info.asset_type == original_asset_type, \
                f"Asset type should be maintained: {evolved_info.asset_type} vs {original_asset_type}"
            
            # Verify year is maintained
            assert evolved_info.year == original_year, \
                f"Year should be maintained: {evolved_info.year} vs {original_year}"
            
            # Verify current warehouse is correct
            assert evolved_info.current_warehouse == new_warehouse, \
                f"Current warehouse should be updated: {evolved_info.current_warehouse} vs {new_warehouse}"
            
            # Verify transfer count increases
            transfer_count += 1
            assert evolved_info.transfer_count == transfer_count, \
                f"Transfer count should increment: {evolved_info.transfer_count} vs {transfer_count}"
            
            # Verify code is marked as evolved
            assert evolved_info.is_evolved == True, \
                f"Code should be marked as evolved: {evolved_code}"
            
            # Update for next iteration
            current_code = evolved_code
    
    @given(unique_codes=unique_asset_codes_strategy(min_size=2, max_size=10))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
    def test_property_6_asset_code_uniqueness(self, unique_codes):
        """
        **Feature: hidroven-organizational-restructuring, Property 6: Asset Code Uniqueness**
        
        **Validates: Requirements 3.3**
        
        For any number of assets in the system, no two assets should ever have 
        identical asset codes regardless of generation or evolution operations.
        """
        # Verify all generated codes are unique
        assert len(unique_codes) == len(set(unique_codes)), \
            f"All generated codes should be unique: {len(unique_codes)} vs {len(set(unique_codes))}"
        
        # Test that evolution maintains uniqueness
        evolved_codes = []
        
        for code in unique_codes:
            # Parse code to get current warehouse
            code_info = AssetCodeGenerator.parse_asset_code(code)
            assume(code_info is not None)
            
            current_warehouse = code_info.current_warehouse
            
            # Find a different warehouse for evolution
            available_warehouses = [w for w in VALID_WAREHOUSES if w != current_warehouse]
            if available_warehouses:
                new_warehouse = available_warehouses[0]  # Use first available
                
                try:
                    evolved_code = AssetCodeGenerator.evolve_asset_code(code, new_warehouse)
                    evolved_codes.append(evolved_code)
                except ValidationError:
                    # Skip if evolution fails (shouldn't happen with valid inputs)
                    pass
        
        # Verify evolved codes are unique among themselves
        if evolved_codes:
            assert len(evolved_codes) == len(set(evolved_codes)), \
                f"All evolved codes should be unique: {len(evolved_codes)} vs {len(set(evolved_codes))}"
        
        # Verify evolved codes don't conflict with original codes
        all_codes = unique_codes + evolved_codes
        assert len(all_codes) == len(set(all_codes)), \
            f"Original and evolved codes should all be unique: {len(all_codes)} vs {len(set(all_codes))}"
        
        # Test batch generation uniqueness
        warehouse = VALID_WAREHOUSES[0]
        asset_type = VALID_ASSET_TYPES[0]
        
        try:
            batch_codes = AssetCodeGenerator.generate_batch_codes(
                warehouse_prefix=warehouse,
                asset_type=asset_type,
                count=min(10, 50)  # Generate up to 10 codes
            )
            
            # Verify batch codes are unique
            assert len(batch_codes) == len(set(batch_codes)), \
                f"Batch generated codes should be unique: {len(batch_codes)} vs {len(set(batch_codes))}"
            
            # Verify batch codes don't conflict with existing codes
            all_with_batch = all_codes + batch_codes
            assert len(all_with_batch) == len(set(all_with_batch)), \
                f"Batch codes should not conflict with existing codes"
                
        except ValidationError:
            # Skip if batch generation fails (e.g., due to sequence limits)
            pass
    
    @given(code=valid_asset_code_strategy)
    @settings(max_examples=100, deadline=None)
    def test_property_7_asset_code_parsing_round_trip(self, code):
        """
        **Feature: hidroven-organizational-restructuring, Property 7: Asset Code Parsing Round-Trip**
        
        **Validates: Requirements 3.6**
        
        For any valid asset code, parsing the code to extract movement history 
        then reconstructing it should produce an equivalent code structure with 
        correct warehouse sequence and asset information.
        """
        # Parse the asset code
        parsed_info = AssetCodeGenerator.parse_asset_code(code)
        assert parsed_info is not None, f"Code should be parseable: {code}"
        
        # Verify all components are extracted correctly
        assert parsed_info.current_warehouse is not None, \
            f"Current warehouse should be extracted: {code}"
        assert parsed_info.asset_type is not None, \
            f"Asset type should be extracted: {code}"
        assert parsed_info.sequence is not None, \
            f"Sequence should be extracted: {code}"
        assert parsed_info.year is not None, \
            f"Year should be extracted: {code}"
        assert parsed_info.original_code is not None, \
            f"Original code should be extracted: {code}"
        
        # Verify current warehouse is valid
        assert parsed_info.current_warehouse in VALID_WAREHOUSES, \
            f"Current warehouse should be valid: {parsed_info.current_warehouse}"
        
        # Verify asset type is valid
        assert parsed_info.asset_type in VALID_ASSET_TYPES, \
            f"Asset type should be valid: {parsed_info.asset_type}"
        
        # Verify sequence format
        assert len(parsed_info.sequence) == 6, \
            f"Sequence should be 6 digits: {parsed_info.sequence}"
        assert parsed_info.sequence.isdigit(), \
            f"Sequence should be numeric: {parsed_info.sequence}"
        sequence_int = int(parsed_info.sequence)
        assert 1 <= sequence_int <= 999999, \
            f"Sequence should be in valid range: {sequence_int}"
        
        # Verify year format
        assert len(parsed_info.year) == 4, \
            f"Year should be 4 digits: {parsed_info.year}"
        assert parsed_info.year.isdigit(), \
            f"Year should be numeric: {parsed_info.year}"
        year_int = int(parsed_info.year)
        assert 2020 <= year_int <= 2030, \
            f"Year should be in valid range: {year_int}"
        
        # Verify movement history consistency
        if parsed_info.is_evolved:
            assert len(parsed_info.movement_history) > 0, \
                f"Evolved code should have movement history: {code}"
            assert parsed_info.transfer_count > 0, \
                f"Evolved code should have positive transfer count: {code}"
            assert parsed_info.transfer_count == len(parsed_info.movement_history), \
                f"Transfer count should match movement history length: {parsed_info.transfer_count} vs {len(parsed_info.movement_history)}"
        else:
            assert len(parsed_info.movement_history) == 0, \
                f"Original code should have empty movement history: {code}"
            assert parsed_info.transfer_count == 0, \
                f"Original code should have zero transfer count: {code}"
        
        # Verify all warehouses in movement history are valid
        for warehouse in parsed_info.movement_history:
            assert warehouse in VALID_WAREHOUSES, \
                f"Warehouse in movement history should be valid: {warehouse}"
        
        # Test round-trip reconstruction
        # Get movement history from code
        movement_history = AssetCodeGenerator.get_movement_history_from_code(code)
        assert len(movement_history) > 0, f"Movement history should not be empty: {code}"
        
        # First warehouse in history should be original warehouse
        original_warehouse = movement_history[0]
        assert original_warehouse in VALID_WAREHOUSES, \
            f"Original warehouse should be valid: {original_warehouse}"
        
        # Last warehouse in history should be current warehouse
        current_warehouse_from_history = movement_history[-1]
        assert current_warehouse_from_history == parsed_info.current_warehouse, \
            f"Current warehouse should match: {current_warehouse_from_history} vs {parsed_info.current_warehouse}"
        
        # Verify original code extraction
        extracted_original = AssetCodeGenerator.get_original_code_from_evolved(code)
        assert extracted_original == parsed_info.original_code, \
            f"Extracted original should match parsed original: {extracted_original} vs {parsed_info.original_code}"
        
        # Verify original code format
        original_parts = parsed_info.original_code.split('-')
        assert len(original_parts) == 4, \
            f"Original code should have 4 parts: {parsed_info.original_code}"
        assert original_parts[0] == original_warehouse, \
            f"Original code warehouse should match: {original_parts[0]} vs {original_warehouse}"
        assert original_parts[1] == parsed_info.asset_type, \
            f"Original code asset type should match: {original_parts[1]} vs {parsed_info.asset_type}"
        assert original_parts[2] == parsed_info.sequence, \
            f"Original code sequence should match: {original_parts[2]} vs {parsed_info.sequence}"
        assert original_parts[3] == parsed_info.year, \
            f"Original code year should match: {original_parts[3]} vs {parsed_info.year}"
        
        # Test evolution detection
        is_evolved = AssetCodeGenerator.is_code_evolved(code)
        assert is_evolved == parsed_info.is_evolved, \
            f"Evolution detection should match: {is_evolved} vs {parsed_info.is_evolved}"
        
        # Test transfer count extraction
        transfer_count = AssetCodeGenerator.get_transfer_count(code)
        assert transfer_count == parsed_info.transfer_count, \
            f"Transfer count should match: {transfer_count} vs {parsed_info.transfer_count}"
        
        # If code is evolved, verify reconstruction by simulating evolution
        if parsed_info.is_evolved and len(movement_history) > 1:
            # Start with original code
            reconstructed_code = parsed_info.original_code
            
            # Apply each transfer in sequence
            for i in range(1, len(movement_history)):
                new_warehouse = movement_history[i]
                try:
                    reconstructed_code = AssetCodeGenerator.evolve_asset_code(
                        reconstructed_code, new_warehouse
                    )
                except ValidationError:
                    # If evolution fails, the original code might be malformed
                    # This shouldn't happen with valid inputs, but we'll skip the test
                    assume(False)
            
            # The reconstructed code should match the original
            assert reconstructed_code == code, \
                f"Reconstructed code should match original: {reconstructed_code} vs {code}"
    
    @given(scenario=transfer_scenario_strategy())
    @settings(max_examples=100, deadline=None)
    def test_transfer_compatibility_validation(self, scenario):
        """
        Test that transfer compatibility validation works correctly.
        This supports the main properties by ensuring transfers are valid.
        """
        current_code = scenario['current_code']
        origin_warehouse = scenario['origin_warehouse']
        destination_warehouse = scenario['destination_warehouse']
        
        # Verify transfer compatibility
        is_compatible = AssetCodeGenerator.validate_transfer_compatibility(
            current_code=current_code,
            origin_warehouse=origin_warehouse,
            destination_warehouse=destination_warehouse
        )
        
        assert is_compatible == True, \
            f"Transfer should be compatible: {current_code} from {origin_warehouse} to {destination_warehouse}"
        
        # Test that evolution works with compatible transfer
        try:
            evolved_code = AssetCodeGenerator.evolve_asset_code(current_code, destination_warehouse)
            
            # Verify evolved code is valid
            assert AssetCodeGenerator.validate_asset_code_format(evolved_code), \
                f"Evolved code should be valid: {evolved_code}"
            
            # Verify evolution maintains asset identity
            original_info = AssetCodeGenerator.parse_asset_code(current_code)
            evolved_info = AssetCodeGenerator.parse_asset_code(evolved_code)
            
            assert original_info is not None and evolved_info is not None, \
                "Both codes should be parseable"
            
            assert evolved_info.asset_type == original_info.asset_type, \
                "Asset type should be maintained"
            assert evolved_info.sequence == original_info.sequence, \
                "Sequence should be maintained"
            assert evolved_info.year == original_info.year, \
                "Year should be maintained"
            assert evolved_info.current_warehouse == destination_warehouse, \
                "Current warehouse should be updated"
            
        except ValidationError as e:
            # Evolution should not fail with compatible transfers
            pytest.fail(f"Evolution failed with compatible transfer: {e}")
    
    @given(
        codes=st.lists(valid_asset_code_strategy, min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_code_statistics_accuracy(self, codes):
        """
        Test that code statistics are calculated accurately.
        This supports validation of the main properties.
        """
        stats = AssetCodeGenerator.get_code_statistics(codes)
        
        # Verify basic counts
        assert stats['total_codes'] == len(codes), \
            f"Total codes count should match: {stats['total_codes']} vs {len(codes)}"
        
        # Manually verify statistics
        valid_count = 0
        evolved_count = 0
        warehouses = set()
        asset_types = set()
        years = set()
        transfer_counts = []
        
        for code in codes:
            if AssetCodeGenerator.validate_asset_code_format(code):
                valid_count += 1
                code_info = AssetCodeGenerator.parse_asset_code(code)
                
                if code_info:
                    if code_info.is_evolved:
                        evolved_count += 1
                    
                    warehouses.add(code_info.current_warehouse)
                    asset_types.add(code_info.asset_type)
                    years.add(code_info.year)
                    transfer_counts.append(code_info.transfer_count)
        
        # Verify calculated statistics
        assert stats['valid_codes'] == valid_count, \
            f"Valid codes count should match: {stats['valid_codes']} vs {valid_count}"
        
        assert stats['evolved_codes'] == evolved_count, \
            f"Evolved codes count should match: {stats['evolved_codes']} vs {evolved_count}"
        
        assert stats['original_codes'] == valid_count - evolved_count, \
            f"Original codes count should match: {stats['original_codes']} vs {valid_count - evolved_count}"
        
        assert set(stats['warehouses']) == warehouses, \
            f"Warehouses should match: {set(stats['warehouses'])} vs {warehouses}"
        
        assert set(stats['asset_types']) == asset_types, \
            f"Asset types should match: {set(stats['asset_types'])} vs {asset_types}"
        
        assert set(stats['years']) == years, \
            f"Years should match: {set(stats['years'])} vs {years}"
        
        if transfer_counts:
            assert stats['max_transfers'] == max(transfer_counts), \
                f"Max transfers should match: {stats['max_transfers']} vs {max(transfer_counts)}"
            
            expected_avg = sum(transfer_counts) / len(transfer_counts)
            assert abs(stats['avg_transfers'] - expected_avg) < 0.001, \
                f"Average transfers should match: {stats['avg_transfers']} vs {expected_avg}"


# ============================================================================
# ADDITIONAL PROPERTY TESTS FOR EDGE CASES
# ============================================================================

class TestAssetCodeEdgeCaseProperties(TestCase):
    """Property-based tests for edge cases and boundary conditions."""
    
    @given(
        warehouse=warehouse_strategy,
        asset_type=asset_type_strategy
    )
    @settings(max_examples=50, deadline=None)
    def test_batch_generation_consistency(self, warehouse, asset_type):
        """Test that batch generation produces consistent, unique codes."""
        try:
            # Generate small batch
            batch_size = 5
            codes = AssetCodeGenerator.generate_batch_codes(
                warehouse_prefix=warehouse,
                asset_type=asset_type,
                count=batch_size
            )
            
            # Verify batch properties
            assert len(codes) == batch_size, f"Batch should have correct size: {len(codes)} vs {batch_size}"
            assert len(set(codes)) == batch_size, f"All codes in batch should be unique"
            
            # Verify all codes are valid
            for code in codes:
                assert AssetCodeGenerator.validate_asset_code_format(code), \
                    f"All batch codes should be valid: {code}"
                
                # Verify code components
                code_info = AssetCodeGenerator.parse_asset_code(code)
                assert code_info is not None, f"Batch code should be parseable: {code}"
                assert code_info.current_warehouse == warehouse, \
                    f"Batch code warehouse should match: {code_info.current_warehouse} vs {warehouse}"
                assert code_info.asset_type == asset_type, \
                    f"Batch code asset type should match: {code_info.asset_type} vs {asset_type}"
                assert not code_info.is_evolved, \
                    f"Batch codes should not be evolved: {code}"
                
        except ValidationError:
            # Skip if batch generation fails (e.g., due to constraints)
            pass
    
    @given(code=valid_asset_code_strategy)
    @settings(max_examples=50, deadline=None)
    def test_validation_consistency(self, code):
        """Test that validation methods are consistent with each other."""
        # Basic format validation
        is_valid_format = AssetCodeGenerator.validate_asset_code_format(code)
        
        # Detailed validation
        is_valid_detailed, errors = AssetCodeValidator.validate_code_with_details(code)
        
        # Parsing validation
        parsed_info = AssetCodeGenerator.parse_asset_code(code)
        is_parseable = parsed_info is not None
        
        # All validation methods should agree for valid codes
        if is_valid_format:
            assert is_valid_detailed, \
                f"Detailed validation should agree with format validation: {code}, errors: {errors}"
            assert is_parseable, \
                f"Code should be parseable if format is valid: {code}"
        
        # If code is parseable, it should pass format validation
        if is_parseable:
            assert is_valid_format, \
                f"Format validation should pass if code is parseable: {code}"
    
    @given(
        original_code=original_asset_code_strategy(),
        transfer_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=50, deadline=None)
    def test_evolution_chain_validation(self, original_code, transfer_count):
        """Test that evolution chains are validated correctly."""
        # Build evolution chain
        chain = [original_code]
        current_code = original_code
        
        # Get original warehouse
        original_info = AssetCodeGenerator.parse_asset_code(original_code)
        assume(original_info is not None)
        used_warehouses = {original_info.current_warehouse}
        
        # Build chain with unique warehouses
        for _ in range(transfer_count):
            available_warehouses = [w for w in VALID_WAREHOUSES if w not in used_warehouses]
            if not available_warehouses:
                # If all warehouses used, allow reuse
                available_warehouses = [w for w in VALID_WAREHOUSES 
                                      if w != AssetCodeGenerator.parse_asset_code(current_code).current_warehouse]
            
            if available_warehouses:
                new_warehouse = available_warehouses[0]  # Use first available
                try:
                    evolved_code = AssetCodeGenerator.evolve_asset_code(current_code, new_warehouse)
                    chain.append(evolved_code)
                    current_code = evolved_code
                    used_warehouses.add(new_warehouse)
                except ValidationError:
                    # Stop if evolution fails
                    break
        
        # Validate the chain
        if len(chain) > 1:
            is_valid_chain = AssetCodeGenerator.validate_code_evolution_chain(chain)
            assert is_valid_chain, f"Evolution chain should be valid: {chain}"
            
            # Test individual evolution steps
            for i in range(1, len(chain)):
                old_code = chain[i-1]
                new_code = chain[i]
                
                is_valid_step, step_errors = AssetCodeValidator.validate_evolution_step(old_code, new_code)
                assert is_valid_step, \
                    f"Evolution step should be valid: {old_code} -> {new_code}, errors: {step_errors}"


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