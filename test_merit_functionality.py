#!/usr/bin/env python3
"""
Test script for Merit List Generation functionality
This script validates the structure and imports of our DocTypes
"""

import os
import sys
import json

def test_doctype_structure():
    """Test if all DocType JSON files are valid"""

    base_path = "/opt/bench/erpnext/apps/education_management/education_management/education_management/doctype"

    doctypes = [
        "merit_score_submission",
        "merit_subject_score",
        "merit_score_validation",
        "merit_list_generation_tool",
        "education_management_settings"
    ]

    results = {}

    for doctype in doctypes:
        doctype_path = os.path.join(base_path, doctype)
        json_file = os.path.join(doctype_path, f"{doctype}.json")
        py_file = os.path.join(doctype_path, f"{doctype}.py")
        init_file = os.path.join(doctype_path, "__init__.py")

        results[doctype] = {
            "json_exists": os.path.exists(json_file),
            "py_exists": os.path.exists(py_file),
            "init_exists": os.path.exists(init_file),
            "json_valid": False
        }

        # Test JSON validity
        if results[doctype]["json_exists"]:
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
                results[doctype]["json_valid"] = True
            except json.JSONDecodeError as e:
                results[doctype]["json_error"] = str(e)

    return results

def test_python_imports():
    """Test if Python files have correct imports"""

    # Add the education_management app to path
    app_path = "/opt/bench/erpnext/apps/education_management"
    if app_path not in sys.path:
        sys.path.append(app_path)

    import_tests = {}

    try:
        from education_management.education_management.doctype.merit_score_submission import merit_score_submission
        import_tests["merit_score_submission"] = "SUCCESS"
    except Exception as e:
        import_tests["merit_score_submission"] = f"FAILED: {str(e)}"

    try:
        from education_management.education_management.doctype.merit_subject_score import merit_subject_score
        import_tests["merit_subject_score"] = "SUCCESS"
    except Exception as e:
        import_tests["merit_subject_score"] = f"FAILED: {str(e)}"

    try:
        from education_management.education_management.doctype.merit_score_validation import merit_score_validation
        import_tests["merit_score_validation"] = "SUCCESS"
    except Exception as e:
        import_tests["merit_score_validation"] = f"FAILED: {str(e)}"

    try:
        from education_management.education_management.doctype.merit_list_generation_tool import merit_list_generation_tool
        import_tests["merit_list_generation_tool"] = "SUCCESS"
    except Exception as e:
        import_tests["merit_list_generation_tool"] = f"FAILED: {str(e)}"

    try:
        from education_management.education_management.doctype.education_management_settings import education_management_settings
        import_tests["education_management_settings"] = "SUCCESS"
    except Exception as e:
        import_tests["education_management_settings"] = f"FAILED: {str(e)}"

    try:
        import education_management.utils as utils
        import_tests["utils"] = "SUCCESS"
    except Exception as e:
        import_tests["utils"] = f"FAILED: {str(e)}"

    return import_tests

def main():
    print("=" * 60)
    print("MERIT LIST GENERATION FUNCTIONALITY TEST")
    print("=" * 60)

    # Test DocType structure
    print("\n1. Testing DocType Structure:")
    print("-" * 40)
    doctype_results = test_doctype_structure()

    for doctype, results in doctype_results.items():
        print(f"\n{doctype.replace('_', ' ').title()}:")
        print(f"  ✓ JSON file exists: {'Yes' if results['json_exists'] else 'No'}")
        print(f"  ✓ Python file exists: {'Yes' if results['py_exists'] else 'No'}")
        print(f"  ✓ Init file exists: {'Yes' if results['init_exists'] else 'No'}")
        print(f"  ✓ JSON is valid: {'Yes' if results['json_valid'] else 'No'}")

        if not results['json_valid'] and 'json_error' in results:
            print(f"    Error: {results['json_error']}")

    # Test Python imports
    print("\n\n2. Testing Python Imports:")
    print("-" * 40)
    import_results = test_python_imports()

    for module, result in import_results.items():
        status = "✓" if result == "SUCCESS" else "✗"
        print(f"  {status} {module}: {result}")

    # Summary
    print("\n\n3. Summary:")
    print("-" * 40)

    all_doctypes_valid = all(
        results['json_exists'] and results['py_exists'] and
        results['init_exists'] and results['json_valid']
        for results in doctype_results.values()
    )

    all_imports_valid = all(
        result == "SUCCESS" for result in import_results.values()
    )

    if all_doctypes_valid and all_imports_valid:
        print("✓ All tests PASSED! Merit list functionality is ready.")
    else:
        print("✗ Some tests FAILED. Please check the issues above.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()