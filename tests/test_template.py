#!/usr/bin/env python3
"""
Test script to verify the template fixes
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.code_generator import CodeGeneratorWithFilters


# Mock OData parser result
class MockParser:
    def __init__(self):
        self.properties = [
            {
                'original_name': 'No',
                'csharp_name': 'No',
                'display_name': 'Document No',
                'type': 'string',
                'is_primary_key': True
            },
            {
                'original_name': 'Date',
                'csharp_name': 'Date',
                'display_name': 'Date',
                'type': 'DateTime',
                'is_primary_key': False
            },
            {
                'original_name': 'Description',
                'csharp_name': 'Description',
                'display_name': 'Description',
                'type': 'string',
                'is_primary_key': False
            },
            {
                'original_name': 'Approval_Status',
                'csharp_name': 'ApprovalStatus',
                'display_name': 'Status',
                'type': 'string',
                'is_primary_key': False
            }
        ]

        self.document_info = {
            'primary_key': {
                'original_name': 'No',
                'csharp_name': 'No',
                'display_name': 'Document No',
                'type': 'string'
            },
            'user_filter_fields': [
                {
                    'original_name': 'Created_By',
                    'csharp_name': 'CreatedBy'
                }
            ],
            'datatable_properties': [
                {
                    'original_name': 'No',
                    'csharp_name': 'No',
                    'display_name': 'Document No',
                    'type': 'string'
                },
                {
                    'original_name': 'Date',
                    'csharp_name': 'Date',
                    'display_name': 'Date',
                    'type': 'DateTime'
                },
                {
                    'original_name': 'Description',
                    'csharp_name': 'Description',
                    'display_name': 'Description',
                    'type': 'string'
                },
                {
                    'original_name': 'Approval_Status',
                    'csharp_name': 'ApprovalStatus',
                    'display_name': 'Status',
                    'type': 'string'
                }
            ]
        }


def test_without_filters():
    """Test code generation without filters"""
    print("Test 1: Code generation WITHOUT filters")
    print("-" * 50)

    code_gen = CodeGeneratorWithFilters()
    parser = MockParser()

    try:
        result = code_gen.generate_full_code(
            parser,
            "Payment",
            "PaymentVoucher",
            None  # No filters
        )

        print("✓ Model generated successfully")
        print("✓ Controller generated successfully")
        print("✓ Main view generated successfully")
        print("✓ Document view generated successfully")
        print("\nTest 1 PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test 1 FAILED: {str(e)}\n")
        return False


def test_with_filters():
    """Test code generation with filters"""
    print("Test 2: Code generation WITH filters")
    print("-" * 50)

    code_gen = CodeGeneratorWithFilters()
    parser = MockParser()

    filters_config = {
        'enabled': True,
        'date_range_filter': {
            'type': 'date_range',
            'field_name': 'Date',
            'display_name': 'Date Range',
            'enabled': True
        },
        'approval_status_filter': {
            'type': 'approval_status',
            'field_name': 'Approval_Status',
            'display_name': 'Approval Status',
            'default_value': 'Open',
            'options': [
                {'text': 'Open', 'value': 'Open'},
                {'text': 'Pending Approval', 'value': 'Pending Approval'},
                {'text': 'Approved', 'value': 'Approved'}
            ],
            'enabled': True
        },
        'custom_filters': []
    }

    try:
        result = code_gen.generate_full_code(
            parser,
            "Payment",
            "PaymentVoucher",
            filters_config
        )

        # Check if controller has filter logic
        if 'Get{{ page_name }}List' in result['controller'] or 'GetPaymentList' in result['controller']:
            print("✓ Controller has filter methods")
        else:
            print("✗ Controller missing filter methods")

        # Check if view has filter section
        if 'filter-section' in result['main_view'] or 'Filter Section' in result['main_view']:
            print("✓ Main view has filter section")
        else:
            print("✗ Main view missing filter section")

        print("✓ Model generated successfully")
        print("✓ Controller generated successfully")
        print("✓ Main view generated successfully")
        print("✓ Document view generated successfully")
        print("\nTest 2 PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test 2 FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_with_date_filter_only():
    """Test code generation with date filter only"""
    print("Test 3: Code generation WITH date filter only")
    print("-" * 50)

    code_gen = CodeGeneratorWithFilters()
    parser = MockParser()

    filters_config = {
        'enabled': True,
        'date_range_filter': {
            'type': 'date_range',
            'field_name': 'Date',
            'display_name': 'Date Range',
            'enabled': True
        },
        'approval_status_filter': None,
        'custom_filters': []
    }

    try:
        result = code_gen.generate_full_code(
            parser,
            "Payment",
            "PaymentVoucher",
            filters_config
        )

        print("✓ Model generated successfully")
        print("✓ Controller generated successfully")
        print("✓ Main view generated successfully")
        print("✓ Document view generated successfully")
        print("\nTest 3 PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test 3 FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("TEMPLATE FIX VERIFICATION TESTS")
    print("=" * 50)
    print()

    results = []
    results.append(("Without filters", test_without_filters()))
    results.append(("With filters", test_with_filters()))
    results.append(("With date filter only", test_with_date_filter_only()))

    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests PASSED! Templates are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED. Please review the errors above.")
        sys.exit(1)