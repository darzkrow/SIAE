# ============================================================================
# ASSET CODE GENERATION AND EVOLUTION SERVICES
# ============================================================================

import re
from typing import Dict, List, Optional, Tuple, Any
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Max
from dataclasses import dataclass


@dataclass
class AssetCodeInfo:
    """
    Data class to hold parsed asset code information.
    Contains all components extracted from an asset code.
    """
    current_warehouse: Optional[str]
    movement_history: List[str]
    asset_type: str
    sequence: str
    year: str
    original_code: str
    is_evolved: bool
    transfer_count: int


class AssetCodeGenerator:
    """
    Service class for asset code generation, evolution, and parsing.
    
    Handles all asset code operations according to the requirements:
    - Pattern validation for asset codes
    - Code evolution algorithm for warehouse transfers
    - Code parsing to extract movement history
    - Support for multiple transfer chains
    - Validation of code formats
    
    Asset Code Patterns:
    - Initial: {WAREHOUSE_PREFIX}-{ASSET_TYPE}-{SEQUENCE}-{YEAR}
    - After transfer: {NEW_WAREHOUSE}-{PREVIOUS_CODE}
    - Multi-transfer: {WAREHOUSE3}-{WAREHOUSE2}-{WAREHOUSE1}-{ASSET_TYPE}-{SEQUENCE}-{YEAR}
    
    Examples:
    - Original: ZUL-BOMBA-000001-2024
    - After 1 transfer: CAR-ZUL-BOMBA-000001-2024
    - After 2 transfers: MIR-CAR-ZUL-BOMBA-000001-2024
    """
    
    # Valid warehouse prefixes as per requirements
    VALID_WAREHOUSE_PREFIXES = [
        'ZUL',  # Zulia
        'CAR',  # Carabobo
        'MIR',  # Miranda
        'ARA',  # Aragua
        'LAR',  # Lara
        'TAC',  # Táchira
        'BOL',  # Bolívar
        'ANZ',  # Anzoátegui
        'MON',  # Monagas
    ]
    
    # Valid asset types for code generation
    VALID_ASSET_TYPES = [
        'BOMBA',
        'MOTOR',
        'TUBERIA',
        'QUIMICO',
        'ACCESORIO',
        'EQUIPO',
        'VALVULA',
        'MEDIDOR',
    ]
    
    # Regex patterns for code validation
    ORIGINAL_CODE_PATTERN = r'^([A-Z]{3})-([A-Z_]+)-(\d{6})-(\d{4})$'
    EVOLVED_CODE_PATTERN = r'^([A-Z]{3})-(.+)$'
    FULL_CODE_PATTERN = r'^([A-Z]{3}-)*[A-Z]{3}-[A-Z_]+-\d{6}-\d{4}$'
    
    @classmethod
    def generate_asset_code(cls, warehouse_prefix: str, asset_type: str, 
                          year: Optional[int] = None) -> str:
        """
        Generate a new unique asset code following the pattern:
        {WAREHOUSE_PREFIX}-{ASSET_TYPE}-{SEQUENCE}-{YEAR}
        
        Args:
            warehouse_prefix: Three-letter warehouse prefix (e.g., 'ZUL')
            asset_type: Asset type (e.g., 'BOMBA')
            year: Year for the code (defaults to current year)
            
        Returns:
            str: Generated asset code
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate inputs
        cls._validate_warehouse_prefix(warehouse_prefix)
        cls._validate_asset_type(asset_type)
        
        if year is None:
            year = timezone.now().year
        
        # Get next sequence number
        sequence = cls._get_next_sequence_number(warehouse_prefix, asset_type, year)
        
        # Generate code
        code = f"{warehouse_prefix}-{asset_type}-{sequence:06d}-{year}"
        
        # Validate generated code
        if not cls.validate_asset_code_format(code):
            raise ValidationError(f"Generated code has invalid format: {code}")
        
        return code
    
    @classmethod
    def evolve_asset_code(cls, current_code: str, new_warehouse_prefix: str) -> str:
        """
        Evolve asset code when transferring to a new warehouse.
        Pattern: {NEW_WAREHOUSE}-{CURRENT_CODE}
        
        Args:
            current_code: Current asset code
            new_warehouse_prefix: New warehouse prefix
            
        Returns:
            str: Evolved asset code
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate inputs
        if not cls.validate_asset_code_format(current_code):
            raise ValidationError(f"Current code has invalid format: {current_code}")
        
        cls._validate_warehouse_prefix(new_warehouse_prefix)
        
        # Parse current code to check if already at this warehouse
        code_info = cls.parse_asset_code(current_code)
        if code_info and code_info.current_warehouse == new_warehouse_prefix:
            raise ValidationError(
                f"Asset is already at warehouse {new_warehouse_prefix}"
            )
        
        # Evolve code
        evolved_code = f"{new_warehouse_prefix}-{current_code}"
        
        # Validate evolved code
        if not cls.validate_asset_code_format(evolved_code):
            raise ValidationError(f"Evolved code has invalid format: {evolved_code}")
        
        return evolved_code
    
    @classmethod
    def parse_asset_code(cls, code: str) -> Optional[AssetCodeInfo]:
        """
        Parse asset code to extract movement history and asset information.
        
        Args:
            code: Asset code to parse
            
        Returns:
            AssetCodeInfo: Parsed code information or None if invalid
        """
        if not code or not isinstance(code, str):
            return None
        
        # Split by dashes
        parts = code.split('-')
        
        if len(parts) < 4:
            return None
        
        try:
            # The last 3 parts should be TYPE-SEQUENCE-YEAR
            year = parts[-1]
            sequence = parts[-2]
            asset_type = parts[-3]
            
            # Validate year and sequence format
            if not (year.isdigit() and len(year) == 4):
                return None
            if not (sequence.isdigit() and len(sequence) == 6):
                return None
            
            # Validate year range
            year_int = int(year)
            current_year = timezone.now().year
            if year_int < 2020 or year_int > current_year + 5:
                return None
            
            # Validate sequence range
            sequence_int = int(sequence)
            if sequence_int <= 0 or sequence_int > 999999:
                return None
            
            # Validate asset type
            if asset_type not in cls.VALID_ASSET_TYPES:
                return None
            
            # Everything before that is warehouse history
            warehouses = parts[:-3]
            
            if not warehouses:
                return None
            
            # Validate all warehouse prefixes
            for warehouse in warehouses:
                if warehouse not in cls.VALID_WAREHOUSE_PREFIXES:
                    return None
            
            current_warehouse = warehouses[0]
            movement_history = warehouses[1:] if len(warehouses) > 1 else []
            
            # Construct original code (last warehouse + type + sequence + year)
            original_warehouse = warehouses[-1] if warehouses else current_warehouse
            original_code = f"{original_warehouse}-{asset_type}-{sequence}-{year}"
            
            # Determine if code is evolved
            is_evolved = len(warehouses) > 1
            transfer_count = len(movement_history)
            
            return AssetCodeInfo(
                current_warehouse=current_warehouse,
                movement_history=movement_history,
                asset_type=asset_type,
                sequence=sequence,
                year=year,
                original_code=original_code,
                is_evolved=is_evolved,
                transfer_count=transfer_count
            )
            
        except (IndexError, ValueError):
            return None
    
    @classmethod
    def validate_asset_code_format(cls, code: str) -> bool:
        """
        Validate asset code format.
        Supports both original and evolved codes.
        
        Args:
            code: Asset code to validate
            
        Returns:
            bool: True if format is valid
        """
        if not code or not isinstance(code, str):
            return False
        
        # Check against full pattern
        if not re.match(cls.FULL_CODE_PATTERN, code):
            return False
        
        # Parse and validate components
        code_info = cls.parse_asset_code(code)
        if not code_info:
            return False
        
        # Validate warehouse prefixes
        all_warehouses = [code_info.current_warehouse] + code_info.movement_history
        for warehouse in all_warehouses:
            if warehouse not in cls.VALID_WAREHOUSE_PREFIXES:
                return False
        
        # Validate asset type
        if code_info.asset_type not in cls.VALID_ASSET_TYPES:
            return False
        
        return True
    
    @classmethod
    def validate_code_evolution_chain(cls, codes: List[str]) -> bool:
        """
        Validate that a list of codes represents a valid evolution chain.
        
        Args:
            codes: List of asset codes in chronological order
            
        Returns:
            bool: True if evolution chain is valid
        """
        if not codes or len(codes) < 2:
            return True  # Single code or empty list is valid
        
        for i in range(1, len(codes)):
            previous_code = codes[i-1]
            current_code = codes[i]
            
            # Current code should be evolution of previous code
            if not current_code.endswith(f"-{previous_code}"):
                return False
            
            # Parse both codes
            prev_info = cls.parse_asset_code(previous_code)
            curr_info = cls.parse_asset_code(current_code)
            
            if not prev_info or not curr_info:
                return False
            
            # Validate that asset type, sequence, and year remain the same
            if (prev_info.asset_type != curr_info.asset_type or
                prev_info.sequence != curr_info.sequence or
                prev_info.year != curr_info.year):
                return False
        
        return True
    
    @classmethod
    def get_movement_history_from_code(cls, code: str) -> List[str]:
        """
        Extract movement history from asset code.
        
        Args:
            code: Asset code
            
        Returns:
            List[str]: List of warehouse prefixes in movement order
        """
        code_info = cls.parse_asset_code(code)
        if not code_info:
            return []
        
        # Return full movement path: original -> intermediate -> current
        full_history = code_info.movement_history.copy()
        full_history.reverse()  # Reverse to get chronological order
        full_history.append(code_info.current_warehouse)
        
        return full_history
    
    @classmethod
    def get_original_code_from_evolved(cls, evolved_code: str) -> Optional[str]:
        """
        Extract original code from evolved code.
        
        Args:
            evolved_code: Evolved asset code
            
        Returns:
            str: Original asset code or None if invalid
        """
        code_info = cls.parse_asset_code(evolved_code)
        if not code_info:
            return None
        
        return code_info.original_code
    
    @classmethod
    def is_code_evolved(cls, code: str) -> bool:
        """
        Check if asset code has been evolved (transferred).
        
        Args:
            code: Asset code to check
            
        Returns:
            bool: True if code has been evolved
        """
        code_info = cls.parse_asset_code(code)
        if not code_info:
            return False
        
        return code_info.is_evolved
    
    @classmethod
    def get_transfer_count(cls, code: str) -> int:
        """
        Get number of transfers from asset code.
        
        Args:
            code: Asset code
            
        Returns:
            int: Number of transfers (0 for original location)
        """
        code_info = cls.parse_asset_code(code)
        if not code_info:
            return 0
        
        return code_info.transfer_count
    
    @classmethod
    def validate_transfer_compatibility(cls, current_code: str, 
                                      origin_warehouse: str, 
                                      destination_warehouse: str) -> bool:
        """
        Validate that a transfer is compatible with the current asset code.
        
        Args:
            current_code: Current asset code
            origin_warehouse: Expected origin warehouse
            destination_warehouse: Destination warehouse
            
        Returns:
            bool: True if transfer is valid
        """
        # Parse current code
        code_info = cls.parse_asset_code(current_code)
        if not code_info:
            return False
        
        # Validate origin matches current location
        if code_info.current_warehouse != origin_warehouse:
            return False
        
        # Validate destination is different from current
        if code_info.current_warehouse == destination_warehouse:
            return False
        
        # Validate warehouse prefixes
        if (origin_warehouse not in cls.VALID_WAREHOUSE_PREFIXES or
            destination_warehouse not in cls.VALID_WAREHOUSE_PREFIXES):
            return False
        
        return True
    
    @classmethod
    def generate_batch_codes(cls, warehouse_prefix: str, asset_type: str, 
                           count: int, year: Optional[int] = None) -> List[str]:
        """
        Generate multiple asset codes in batch.
        
        Args:
            warehouse_prefix: Warehouse prefix
            asset_type: Asset type
            count: Number of codes to generate
            year: Year for codes (defaults to current year)
            
        Returns:
            List[str]: List of generated asset codes
            
        Raises:
            ValidationError: If parameters are invalid
        """
        if count <= 0:
            raise ValidationError("Count must be positive")
        
        if count > 1000:
            raise ValidationError("Cannot generate more than 1000 codes at once")
        
        # Validate inputs
        cls._validate_warehouse_prefix(warehouse_prefix)
        cls._validate_asset_type(asset_type)
        
        if year is None:
            year = timezone.now().year
        
        # Get starting sequence number
        start_sequence = cls._get_next_sequence_number(warehouse_prefix, asset_type, year)
        
        codes = []
        for i in range(count):
            sequence = start_sequence + i
            code = f"{warehouse_prefix}-{asset_type}-{sequence:06d}-{year}"
            
            # Validate generated code
            if not cls.validate_asset_code_format(code):
                raise ValidationError(f"Generated code has invalid format: {code}")
            
            codes.append(code)
        
        return codes
    
    # Private helper methods
    
    @classmethod
    def _validate_warehouse_prefix(cls, prefix: str) -> None:
        """Validate warehouse prefix"""
        if not prefix or not isinstance(prefix, str):
            raise ValidationError("Warehouse prefix is required")
        
        if prefix not in cls.VALID_WAREHOUSE_PREFIXES:
            raise ValidationError(
                f"Invalid warehouse prefix: {prefix}. "
                f"Valid prefixes: {', '.join(cls.VALID_WAREHOUSE_PREFIXES)}"
            )
    
    @classmethod
    def _validate_asset_type(cls, asset_type: str) -> None:
        """Validate asset type"""
        if not asset_type or not isinstance(asset_type, str):
            raise ValidationError("Asset type is required")
        
        if asset_type not in cls.VALID_ASSET_TYPES:
            raise ValidationError(
                f"Invalid asset type: {asset_type}. "
                f"Valid types: {', '.join(cls.VALID_ASSET_TYPES)}"
            )
    
    @classmethod
    def _get_next_sequence_number(cls, warehouse_prefix: str, asset_type: str, 
                                year: int) -> int:
        """
        Get the next sequence number for asset code generation.
        
        This method needs to be implemented to work with the actual database.
        For now, it provides a basic implementation that should be overridden
        or enhanced based on the specific ORM being used.
        """
        # This is a placeholder implementation
        # In a real implementation, this would query the database
        # to find the highest sequence number for the given combination
        
        try:
            # Try to import the ActivoInventario model
            from .models import ActivoInventario
            
            # Find the highest sequence number for this combination
            pattern = rf"^{warehouse_prefix}-{asset_type}-(\d+)-{year}$"
            
            existing_codes = ActivoInventario.objects.filter(
                codigo_original__regex=pattern
            ).values_list('codigo_original', flat=True)
            
            max_sequence = 0
            for code in existing_codes:
                match = re.match(pattern, code)
                if match:
                    sequence = int(match.group(1))
                    max_sequence = max(max_sequence, sequence)
            
            return max_sequence + 1
            
        except ImportError:
            # Fallback if model is not available
            # Use a simple counter based on the parameters
            # This ensures different combinations get different sequences
            import hashlib
            
            # Create a hash of the parameters to ensure uniqueness
            param_string = f"{warehouse_prefix}-{asset_type}-{year}"
            hash_value = int(hashlib.md5(param_string.encode()).hexdigest()[:6], 16)
            
            # Use the hash as a base sequence number (mod 1000000 to keep it 6 digits)
            return (hash_value % 999999) + 1
    
    @classmethod
    def get_code_statistics(cls, codes: List[str]) -> Dict[str, Any]:
        """
        Get statistics about a list of asset codes.
        
        Args:
            codes: List of asset codes
            
        Returns:
            Dict: Statistics about the codes
        """
        if not codes:
            return {
                'total_codes': 0,
                'valid_codes': 0,
                'invalid_codes': 0,
                'evolved_codes': 0,
                'original_codes': 0,
                'warehouses': [],
                'asset_types': [],
                'years': [],
                'max_transfers': 0,
                'avg_transfers': 0.0
            }
        
        valid_codes = []
        invalid_count = 0
        evolved_count = 0
        warehouses = set()
        asset_types = set()
        years = set()
        transfer_counts = []
        
        for code in codes:
            if cls.validate_asset_code_format(code):
                valid_codes.append(code)
                code_info = cls.parse_asset_code(code)
                
                if code_info:
                    if code_info.is_evolved:
                        evolved_count += 1
                    
                    warehouses.add(code_info.current_warehouse)
                    asset_types.add(code_info.asset_type)
                    years.add(code_info.year)
                    transfer_counts.append(code_info.transfer_count)
            else:
                invalid_count += 1
        
        return {
            'total_codes': len(codes),
            'valid_codes': len(valid_codes),
            'invalid_codes': invalid_count,
            'evolved_codes': evolved_count,
            'original_codes': len(valid_codes) - evolved_count,
            'warehouses': sorted(list(warehouses)),
            'asset_types': sorted(list(asset_types)),
            'years': sorted(list(years)),
            'max_transfers': max(transfer_counts) if transfer_counts else 0,
            'avg_transfers': sum(transfer_counts) / len(transfer_counts) if transfer_counts else 0.0
        }


class AssetCodeValidator:
    """
    Specialized validator class for asset codes.
    Provides detailed validation with specific error messages.
    """
    
    @classmethod
    def validate_code_with_details(cls, code: str) -> Tuple[bool, List[str]]:
        """
        Validate asset code and return detailed error messages.
        
        Args:
            code: Asset code to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        if not code:
            errors.append("Asset code cannot be empty")
            return False, errors
        
        if not isinstance(code, str):
            errors.append("Asset code must be a string")
            return False, errors
        
        # Check basic format first
        if not re.match(AssetCodeGenerator.FULL_CODE_PATTERN, code):
            errors.append("Asset code does not match required pattern")
            # Still try to parse for more specific errors
        
        # Parse code for detailed validation
        code_info = AssetCodeGenerator.parse_asset_code(code)
        if not code_info:
            # Try to give more specific errors by parsing manually
            parts = code.split('-')
            if len(parts) < 4:
                errors.append("Asset code must have at least 4 parts separated by dashes")
            else:
                # Check each part
                warehouses = parts[:-3]
                asset_type = parts[-3] if len(parts) >= 3 else ""
                sequence = parts[-2] if len(parts) >= 2 else ""
                year = parts[-1] if len(parts) >= 1 else ""
                
                # Validate warehouses
                for warehouse in warehouses:
                    if warehouse not in AssetCodeGenerator.VALID_WAREHOUSE_PREFIXES:
                        errors.append(f"Invalid warehouse prefix: {warehouse}")
                
                # Validate asset type
                if asset_type not in AssetCodeGenerator.VALID_ASSET_TYPES:
                    errors.append(f"Invalid asset type: {asset_type}")
                
                # Validate sequence
                if not sequence.isdigit() or len(sequence) != 6:
                    errors.append(f"Invalid sequence format: {sequence}")
                elif int(sequence) <= 0:
                    errors.append(f"Invalid sequence number: {int(sequence)}")
                
                # Validate year
                if not year.isdigit() or len(year) != 4:
                    errors.append(f"Invalid year format: {year}")
                else:
                    year_int = int(year)
                    current_year = timezone.now().year
                    if year_int < 2020 or year_int > current_year + 5:
                        errors.append(f"Invalid year: {year_int}")
            
            return False, errors
        
        # If we got here, the code parsed successfully
        return len(errors) == 0, errors
    
    @classmethod
    def validate_evolution_step(cls, old_code: str, new_code: str) -> Tuple[bool, List[str]]:
        """
        Validate that new_code is a valid evolution of old_code.
        
        Args:
            old_code: Previous asset code
            new_code: New asset code
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate both codes individually
        old_valid, old_errors = cls.validate_code_with_details(old_code)
        new_valid, new_errors = cls.validate_code_with_details(new_code)
        
        if not old_valid:
            errors.extend([f"Old code: {error}" for error in old_errors])
        
        if not new_valid:
            errors.extend([f"New code: {error}" for error in new_errors])
        
        if not old_valid or not new_valid:
            return False, errors
        
        # Check evolution relationship
        if not new_code.endswith(f"-{old_code}"):
            errors.append("New code is not a valid evolution of old code")
            return False, errors
        
        # Parse both codes
        old_info = AssetCodeGenerator.parse_asset_code(old_code)
        new_info = AssetCodeGenerator.parse_asset_code(new_code)
        
        if not old_info or not new_info:
            errors.append("Unable to parse codes for evolution validation")
            return False, errors
        
        # Validate that core components remain the same
        if old_info.asset_type != new_info.asset_type:
            errors.append("Asset type changed during evolution")
        
        if old_info.sequence != new_info.sequence:
            errors.append("Sequence number changed during evolution")
        
        if old_info.year != new_info.year:
            errors.append("Year changed during evolution")
        
        # Validate transfer count increment
        if new_info.transfer_count != old_info.transfer_count + 1:
            errors.append("Transfer count did not increment correctly")
        
        return len(errors) == 0, errors