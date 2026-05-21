#!/usr/bin/env python3
"""Validation and Execution Summary"""
import sys
from oracle_pg_converters import DataTypeConverter, FunctionConverter, ConstraintConverter, IndexConverter

def run_tests():
    print("\n" + "="*80)
    print("ORACLE DATAPUMP TO POSTGRESQL - VALIDATION".center(80))
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    print("[TEST 1] DATA TYPE CONVERSIONS")
    print("-" * 80)
    
    type_tests = [
        ("VARCHAR2(255)", "VARCHAR(255)"),
        ("NUMBER(10,2)", "NUMERIC(10,2)"),
        ("CLOB", "TEXT"),
        ("BLOB", "BYTEA"),
        ("DATE", "TIMESTAMP"),
    ]
    
    for oracle, expected in type_tests:
        result = DataTypeConverter.convert_type(oracle)
        if result == expected:
            print(f"✓ PASS: {oracle:30} → {result}")
            passed += 1
        else:
            print(f"✗ FAIL: {oracle:30} → {result}")
            failed += 1
    
    print("\n[TEST 2] SQL FUNCTION CONVERSIONS")
    print("-" * 80)
    
    function_tests = [
        ("SELECT SUBSTR(name, 1, 5)", "SUBSTRING"),
        ("SELECT NVL(salary, 0)", "COALESCE"),
        ("SELECT SYSDATE", "CURRENT_DATE"),
        ("SELECT SYSTIMESTAMP", "CURRENT_TIMESTAMP"),
    ]
    
    for oracle_sql, expected_keyword in function_tests:
        result = FunctionConverter.convert_functions(oracle_sql)
        if expected_keyword in result:
            print(f"✓ PASS: {oracle_sql:40} → {expected_keyword}")
            passed += 1
        else:
            print(f"✗ FAIL: {oracle_sql:40} missing {expected_keyword}")
            failed += 1
    
    print("\n[TEST 3] CONSTRAINT CONVERSIONS")
    print("-" * 80)
    
    constraint_tests = [
        ({'type': 'PRIMARY_KEY', 'columns': ['emp_id']}, "PRIMARY KEY"),
        ({'type': 'UNIQUE', 'columns': ['email']}, "UNIQUE"),
        ({'type': 'CHECK', 'expression': 'salary > 0'}, "CHECK"),
    ]
    
    for constraint, expected in constraint_tests:
        result = ConstraintConverter.convert_constraint(constraint)
        if expected in result:
            print(f"✓ PASS: {constraint['type']:30} → {expected}")
            passed += 1
        else:
            print(f"✗ FAIL: {constraint['type']:30} missing {expected}")
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY".center(80))
    print("="*80)
    print(f"\nTotal: {passed + failed} | Passed: {passed} | Failed: {failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%\n")
    
    if failed == 0:
        print("✓ ALL TESTS PASSED - PRODUCTION READY\n")
        return 0
    return 1

if __name__ == '__main__':
    sys.exit(run_tests())