# Installation Guide - Advanced DC Motor Simulator

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install numpy scipy matplotlib
```

### 2. Verify Installation

Run the test script to verify all dependencies are installed:
```bash
python3 test_motor_simulator.py
```

You should see all tests pass with ✓ marks.

### 3. Run the Simulator

```bash
python3 advanced_dc_motor_simulator.py
```

## System Requirements

- **Python**: 3.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **Display**: Minimum 1280x900 resolution recommended
- **RAM**: 512 MB minimum, 1 GB recommended

## Dependencies

### Required Packages

1. **NumPy** (≥1.21.0)
   - Numerical computing library
   - Used for array operations and mathematical calculations
   - Install: `pip install numpy`

2. **SciPy** (≥1.7.0)
   - Scientific computing library
   - Used for ODE solvers (RK45, Euler)
   - Install: `pip install scipy`

3. **Matplotlib** (≥3.4.0)
   - Plotting library
   - Used for real-time visualization
   - Install: `pip install matplotlib`

4. **Tkinter**
   - GUI framework (usually included with Python)
   - If missing on Linux: `sudo apt-get install python3-tk`

## Platform-Specific Instructions

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Open Command Prompt
3. Navigate to the project directory
4. Run: `pip install -r requirements.txt`
5. Run: `python advanced_dc_motor_simulator.py`

### macOS

1. Install Python (comes pre-installed or via Homebrew: `brew install python3`)
2. Open Terminal
3. Navigate to the project directory
4. Run: `pip3 install -r requirements.txt`
5. Run: `python3 advanced_dc_motor_simulator.py`

### Linux (Ubuntu/Debian)

```bash
# Install Python and Tkinter
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk

# Navigate to project directory
cd /path/to/advnaced-sieci2

# Install dependencies
pip3 install -r requirements.txt

# Run simulator
python3 advanced_dc_motor_simulator.py
```

### Linux (Fedora/RHEL/CentOS)

```bash
# Install Python and Tkinter
sudo dnf install python3 python3-pip python3-tkinter

# Navigate to project directory
cd /path/to/advnaced-sieci2

# Install dependencies
pip3 install -r requirements.txt

# Run simulator
python3 advanced_dc_motor_simulator.py
```

## Troubleshooting

### Issue: "No module named 'tkinter'"

**Solution**:
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Tkinter should be included; reinstall Python if missing
- **Windows**: Tkinter should be included; reinstall Python with Tk/Tcl option checked

### Issue: "No module named 'numpy'" (or scipy, matplotlib)

**Solution**:
```bash
pip install numpy scipy matplotlib
```

Or with user flag if permission denied:
```bash
pip install --user numpy scipy matplotlib
```

### Issue: Permission Denied

**Solution**:
Use `--user` flag or virtual environment:
```bash
# Option 1: User installation
pip install --user -r requirements.txt

# Option 2: Virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Multiple Python Versions

**Solution**:
Specify Python version explicitly:
```bash
python3.8 -m pip install -r requirements.txt
python3.8 advanced_dc_motor_simulator.py
```

### Issue: Display Issues on Linux

**Solution**:
Ensure X11 forwarding is enabled if using SSH:
```bash
ssh -X user@host
```

Or install virtual display:
```bash
sudo apt-get install xvfb
xvfb-run python3 advanced_dc_motor_simulator.py
```

## Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python3 -m venv motor_sim_env

# Activate virtual environment
# On Linux/macOS:
source motor_sim_env/bin/activate
# On Windows:
motor_sim_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run simulator
python advanced_dc_motor_simulator.py

# Deactivate when done
deactivate
```

## Verification

After installation, verify everything works:

```bash
# Run test script
python3 test_motor_simulator.py

# Expected output:
# ✓ Import Test: PASS
# ✓ Example 29.32 Solution: PASS
# ✓ Motor Parameters: PASS
# ✓ ODE Solver: PASS
# ✓ ALL TESTS PASSED
```

## Performance Optimization

For better performance:

1. **Use NumPy with BLAS**:
   ```bash
   pip install numpy --upgrade --force-reinstall
   ```

2. **Use latest SciPy**:
   ```bash
   pip install scipy --upgrade
   ```

3. **Close other applications** to free up system resources

4. **Increase window size** for better visualization

## Development Setup

For development and modifications:

```bash
# Clone repository
git clone <repository-url>
cd advnaced-sieci2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install pylint black pytest

# Run tests
python3 test_motor_simulator.py

# Run simulator
python3 advanced_dc_motor_simulator.py
```

## Uninstallation

To remove the application:

```bash
# If using virtual environment
rm -rf motor_sim_env  # or venv directory

# If installed globally
pip uninstall numpy scipy matplotlib

# Remove project directory
rm -rf advnaced-sieci2
```

## Support

If you encounter issues:

1. Check the [README](README_MOTOR_SIMULATOR.md) for usage instructions
2. Verify Python version: `python3 --version` (should be 3.6+)
3. Verify dependencies: `pip list | grep -E "numpy|scipy|matplotlib"`
4. Run test script: `python3 test_motor_simulator.py`

## Additional Resources

- [NumPy Documentation](https://numpy.org/doc/)
- [SciPy Documentation](https://docs.scipy.org/doc/scipy/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

---

**Note**: This simulator requires a graphical display. It cannot run in headless environments without X11 forwarding or virtual display.
