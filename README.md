# DC Motor Simulator with Dynamic Visualization

A comprehensive Python tkinter application for analyzing DC motors with real-time ODE solvers and dynamic visualization.

## Features

- **Interactive Sliders**: Adjust all motor parameters in real-time
- **Automatic Window Resizing**: Responsive layout that adapts to window changes
- **Dynamic Simulation**: Real-time ODE solvers (RK45 and Euler methods)
- **Results Visualization**: Live graphs showing motor characteristics
- **Three Problem Solvers**:
  1. Shunt Motor Analysis
  2. Series Motor Speed Calculation
  3. Series Motor Torque-Speed Relationship

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 dc_motor_simulator.py
```

## Problem Solutions

### Problem 1: 230-V DC Shunt Motor

**Given:**
- Input power: 11 kW
- Supply voltage: 230 V
- No-load current: 5 A
- No-load speed: 1150 rpm
- Armature resistance: 0.5 Ω
- Field resistance: 110 Ω

**Solution:**

1. **Field Current:**
   ```
   If = V / Rf = 230 / 110 = 2.09 A
   ```

2. **Input Current:**
   ```
   I = P / V = 11000 / 230 = 47.83 A
   ```

3. **Armature Current at Load:**
   ```
   Ia = I - If = 47.83 - 2.09 = 45.74 A
   ```

4. **Armature Current at No-load:**
   ```
   Ia0 = I0 - If = 5 - 2.09 = 2.91 A
   ```

5. **Back EMF at No-load:**
   ```
   Eb0 = V - Ia0 × Ra = 230 - 2.91 × 0.5 = 228.55 V
   ```

6. **Back EMF at Load:**
   ```
   Eb = V - Ia × Ra = 230 - 45.74 × 0.5 = 207.13 V
   ```

7. **(c) Speed at Load:**
   ```
   N = N0 × (Eb / Eb0) = 1150 × (207.13 / 228.55) = 1042.40 rpm
   ```

8. **(a) Torque Developed:**
   ```
   ω = 2π × N / 60 = 109.14 rad/s
   T = (Eb × Ia) / ω = (207.13 × 45.74) / 109.14 = 86.77 N.m
   ```

9. **(b) Efficiency:**
   ```
   Armature Loss = Ia² × Ra = 45.74² × 0.5 = 1046.01 W
   Field Loss = If² × Rf = 2.09² × 110 = 480.48 W
   No-load Loss = V × I0 - Ia0² × Ra - If² × Rf = 669.26 W
   Total Loss = 2195.75 W
   Output Power = 11000 - 2195.75 = 8804.25 W
   Efficiency = (8804.25 / 11000) × 100 = 80.04%
   ```

**Answers:**
- (a) Torque developed: **86.77 N.m**
- (b) Efficiency: **80.04%**
- (c) Speed at load: **1042.40 rpm**

---

### Problem 2: 18.65 kW Series Motor Speed Calculation

**Given:**
- Voltage: 250 V
- Armature resistance: 0.1 Ω
- Field resistance: 0.05 Ω
- Brush voltage drop: 3 V
- At 80 A: speed = 600 rpm
- Find speed when current = 100 A

**Solution:**

For a series motor: N ∝ (Eb / φ) and φ ∝ I

1. **Back EMF at I1 = 80 A:**
   ```
   Eb1 = V - I1(Ra + Rf) - Vb
   Eb1 = 250 - 80(0.1 + 0.05) - 3 = 235 V
   ```

2. **Back EMF at I2 = 100 A:**
   ```
   Eb2 = V - I2(Ra + Rf) - Vb
   Eb2 = 250 - 100(0.1 + 0.05) - 3 = 232 V
   ```

3. **Speed at I2:**
   ```
   N2 / N1 = (Eb2 / Eb1) × (I1 / I2)
   N2 = 600 × (232 / 235) × (80 / 100)
   N2 = 471.49 rpm
   ```

**Answer:** Speed at 100 A = **471.49 rpm**

---

### Problem 3: 220-V Series Motor Torque-Speed

**Given:**
- Voltage: 220 V
- Initial speed: 800 rpm
- Initial current: 100 A
- Find speed when torque is halved

**Solution:**

For series motor: T ∝ φ × I ∝ I²

1. **Current at Half Torque:**
   ```
   T2 / T1 = (I2 / I1)²
   0.5 = (I2 / 100)²
   I2 = 100 × √0.5 = 70.71 A
   ```

2. **Assuming total resistance R = 0.2 Ω:**
   ```
   Eb1 = 220 - 100 × 0.2 = 200 V
   Eb2 = 220 - 70.71 × 0.2 = 205.86 V
   ```

3. **Speed at Half Torque:**
   ```
   N2 / N1 = (Eb2 / Eb1) × (I1 / I2)
   N2 = 800 × (205.86 / 200) × (100 / 70.71)
   N2 = 1163.96 rpm
   ```

**Answer:** Speed at half torque = **1163.96 rpm**

(Note: The exact answer depends on the total resistance value. Adjust the slider in the application to match your specific motor resistance.)

---

## Application Features

### Tab 1: Shunt Motor
- Real-time parameter adjustment with sliders
- Dynamic graphs showing:
  - Speed vs Time
  - Armature Current vs Time
  - Torque vs Time
  - Output Power vs Time
- Calculates torque, efficiency, and speed
- Shows transient response from startup to steady state

### Tab 2: Series Motor Speed
- Compares two operating conditions
- Shows load change transition
- Graphs include:
  - Speed response to load change
  - Current dynamics
  - Torque variation
  - Speed-Current characteristic curve
- Demonstrates series motor behavior

### Tab 3: Series Motor Torque
- Analyzes torque-speed relationship
- Shows response to torque reduction
- Visualizes:
  - Speed increase when torque reduces
  - Current reduction
  - Complete torque-speed characteristic
- Compares initial and final operating points

## ODE Solver Methods

### RK45 (Runge-Kutta 45)
- High accuracy
- Adaptive step size
- Better for stiff equations
- Recommended for precise results

### Euler Method
- Simple first-order method
- Fixed step size
- Faster computation
- Good for educational purposes

## Controls

- **Sliders**: Drag to adjust parameters
- **Text Entry**: Type values and press Enter
- **Solver Selection**: Choose between RK45 and Euler
- **Calculate Button**: Update all calculations and graphs
- **Window Resize**: Graphs automatically adjust to window size

## Technical Details

The simulator models DC motor dynamics using differential equations:

**Shunt Motor:**
```
dω/dt = (T - B×ω) / J
dIa/dt = (V - Eb - Ia×Ra) / La
Eb = Kt × ω × If
```

**Series Motor:**
```
dω/dt = (T - B×ω) / J
dIa/dt = (V - Eb - Ia×(Ra+Rf) - Vb) / (La+Lf)
Eb = φ × ω (where φ ∝ Ia)
T = φ × Ia ∝ Ia²
```

## Author

Created for advanced electrical machines analysis and education.

## License

MIT License
