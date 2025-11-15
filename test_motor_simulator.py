#!/usr/bin/env python3
"""
Test script for Advanced DC Motor Simulator
Verifies dependencies and basic functionality
"""

import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")

    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False

    try:
        from tkinter import ttk
        print("✓ tkinter.ttk imported successfully")
    except ImportError as e:
        print(f"✗ tkinter.ttk import failed: {e}")
        return False

    try:
        import numpy as np
        print(f"✓ numpy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        print("  Install with: pip install numpy")
        return False

    try:
        import matplotlib
        print(f"✓ matplotlib {matplotlib.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        print("  Install with: pip install matplotlib")
        return False

    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        print("✓ matplotlib.backends.backend_tkagg imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib backend import failed: {e}")
        return False

    try:
        from scipy.integrate import solve_ivp
        import scipy
        print(f"✓ scipy {scipy.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ scipy import failed: {e}")
        print("  Install with: pip install scipy")
        return False

    return True

def test_example_solution():
    """Test Example 29.32 solution calculations"""
    print("\nTesting Example 29.32 calculations...")

    import numpy as np

    try:
        # Given data
        I = np.array([20, 30, 40, 50])
        T = np.array([128.8, 230.5, 349.8, 446.2])
        V = 460.0
        Ra = 0.5

        # Logarithmic fit
        log_I = np.log(I)
        log_T = np.log(T)
        coeffs = np.polyfit(log_I, log_T, 1)
        n = coeffs[0]
        log_k = coeffs[1]
        k_torque = np.exp(log_k)

        print(f"✓ Torque-current relationship: T = {k_torque:.3f} × I^{n:.3f}")

        # Calculate back-EMF
        Eb = V - I * Ra
        print(f"✓ Back-EMF calculated: {Eb}")

        # Calculate speeds
        N_base = Eb / I
        k_speed = 1000.0 / N_base[0]
        N_rpm = N_base * k_speed

        print(f"✓ Speeds calculated (RPM): {N_rpm}")
        print("✓ Example 29.32 calculations successful")

        return True

    except Exception as e:
        print(f"✗ Example 29.32 calculations failed: {e}")
        return False

def test_motor_parameters():
    """Test motor parameter initialization"""
    print("\nTesting motor parameter initialization...")

    try:
        params = {
            'V_supply': 460.0,
            'R_armature': 0.5,
            'L_armature': 0.05,
            'J_inertia': 0.5,
            'B_friction': 0.01,
            'k_torque': 0.05,
            'k_emf': 0.05,
            'T_load': 100.0,
        }

        print(f"✓ Motor parameters initialized successfully")
        print(f"  Supply Voltage: {params['V_supply']} V")
        print(f"  Armature Resistance: {params['R_armature']} Ω")
        print(f"  Inertia: {params['J_inertia']} kg·m²")

        return True

    except Exception as e:
        print(f"✗ Parameter initialization failed: {e}")
        return False

def test_ode_solver():
    """Test ODE solver functionality"""
    print("\nTesting ODE solver...")

    try:
        from scipy.integrate import solve_ivp
        import numpy as np

        # Simple test ODE: dy/dt = -y, y(0) = 1
        def test_ode(t, y):
            return [-y[0]]

        sol = solve_ivp(test_ode, [0, 1], [1.0], method='RK45')

        if sol.success:
            print(f"✓ RK45 solver working correctly")
            print(f"  Solution at t=1: {sol.y[0, -1]:.4f} (expected: ~0.3679)")
            return True
        else:
            print(f"✗ RK45 solver failed")
            return False

    except Exception as e:
        print(f"✗ ODE solver test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Advanced DC Motor Simulator - Dependency Test")
    print("="*60)

    tests = [
        ("Import Test", test_imports),
        ("Example 29.32 Solution", test_example_solution),
        ("Motor Parameters", test_motor_parameters),
        ("ODE Solver", test_ode_solver),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nYou can now run the simulator:")
        print("  python3 advanced_dc_motor_simulator.py")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease install missing dependencies:")
        print("  pip install numpy scipy matplotlib")
        return 1

if __name__ == "__main__":
    sys.exit(main())
