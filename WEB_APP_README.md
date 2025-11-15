# Advanced DC Series Motor Simulator - Web Application

## 🌐 Overview

A comprehensive web-based DC series motor simulator with multi-physics modeling, real-time visualization, and advanced analysis capabilities. This application provides an interactive interface for solving Example 29.32 and performing detailed motor analysis.

## ✨ Features

### 🎯 Core Functionality

1. **Example 29.32 Solution**
   - Interactive solver for series motor speed/torque curve analysis
   - Visual representation of characteristic curves
   - Detailed analytical results with practical insights

2. **Real-Time Simulation**
   - Multi-physics modeling (electromagnetic, thermal, mechanical)
   - Dual ODE solvers (RK45 adaptive, Euler fixed-step)
   - Live parameter adjustment
   - Real-time chart updates

3. **Advanced Motor Control**
   - Open Loop Control
   - PI Speed Control (adjustable Kp, Ki, setpoint)
   - Field Weakening
   - Chopper Control
   - PWM Control (adjustable duty cycle and frequency)

4. **Multi-Physics Analysis**
   - **Electromagnetic**: Nonlinear flux saturation, temperature effects
   - **Thermal**: Coupled heat transfer, thermal derating curves
   - **Mechanical**: Inertia, friction, torque transients

5. **Detailed Loss Breakdown**
   - Copper losses (I²R)
   - Iron losses (core losses)
   - Mechanical friction losses
   - Stray load losses
   - Real-time pie charts and trend analysis

6. **Economic Analysis**
   - Annual energy consumption and costs
   - 10-year cost projection
   - CO₂ emissions calculation
   - Loss cost breakdown
   - Cost optimization recommendations

7. **Thermal Management**
   - Temperature rise visualization
   - Thermal derating curves
   - Real-time thermal status monitoring
   - Overheat warnings

## 🚀 Installation & Setup

### Prerequisites

- Python 3.6 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Install Dependencies

```bash
cd advnaced-sieci2
pip install -r requirements.txt
```

Required packages:
- `flask>=2.0.0` - Web framework
- `flask-cors>=3.0.10` - Cross-Origin Resource Sharing
- `numpy>=1.21.0` - Numerical computing
- `scipy>=1.7.0` - Scientific computing
- `matplotlib>=3.4.0` - Plotting (for compatibility)

### Step 2: Run the Application

```bash
python3 web_app.py
```

The application will start on `http://localhost:5000`

### Step 3: Open in Browser

Navigate to:
```
http://localhost:5000
```

## 📋 Usage Guide

### Quick Start

1. **Start the Server**
   ```bash
   python3 web_app.py
   ```

2. **Open Browser**
   - Navigate to `http://localhost:5000`
   - The application will automatically create a simulation instance

3. **Solve Example 29.32**
   - Click on "Example 29.32" tab
   - Click "Solve Example 29.32" button
   - View detailed solution and characteristic curves

4. **Run Real-Time Simulation**
   - Go to "Main Control" tab
   - Adjust motor parameters using sliders
   - Click "Start" to begin simulation
   - Watch real-time graphs update
   - Click "Stop" to pause, "Reset" to restart

### Detailed Features

#### Main Control Tab

**Motor Parameters:**
- Supply Voltage (0-1000 V)
- Armature Resistance (0.1-2 Ω)
- Armature Inductance (0.01-0.2 H)
- Moment of Inertia (0.1-2 kg·m²)
- Friction Coefficient (0-0.1)
- Load Torque (0-500 N·m)

**Real-Time Monitoring:**
- 6 dynamic charts showing current, speed, torque, temperature, power, and efficiency
- Live status display with current values
- ODE solver selection (RK45/Euler)

#### Motor Control Tab

**Control Strategies:**
- **Open Loop**: Direct voltage control
- **PI Speed Control**: Closed-loop speed regulation
  - Adjustable Kp (proportional gain)
  - Adjustable Ki (integral gain)
  - Speed setpoint (0-3000 RPM)
- **Field Weakening**: Extended speed range
- **Chopper Control**: DC-DC conversion
- **PWM Control**: Pulse-width modulation
  - Duty cycle (0-1)
  - Frequency (100-20000 Hz)

#### Performance Analysis Tab

**Visualizations:**
- Loss breakdown pie chart
- Losses over time (all four types)
- Speed-torque characteristic scatter plot
- Efficiency vs torque curve

#### Thermal Analysis Tab

**Parameters:**
- Ambient Temperature (0-50 °C)
- Thermal Resistance (0.1-10 °C/W)
- Thermal Capacitance (100-5000 J/°C)
- Maximum Temperature (100-200 °C)

**Visualizations:**
- Temperature rise over time
- Thermal derating curve
- Real-time thermal status (OK/Warning/Danger)

#### Economic Analysis Tab

**Inputs:**
- Energy Cost ($/kWh)
- Operating Hours (hours/year)
- Maintenance Cost ($/year)

**Results:**
- Annual energy consumption and costs
- 10-year cost projection
- CO₂ emissions
- Loss breakdown percentages
- Cost optimization suggestions

**Visualizations:**
- Cost breakdown pie chart
- 10-year cumulative cost projection

#### Example 29.32 Tab

**Problem:**
Given static torque test data, deduce the complete speed/torque characteristic curve for a series motor at 460 V supply.

**Solution Features:**
- Automatic curve fitting (T = k·I^n)
- Back-EMF calculations
- Speed calculations for each operating point
- Extended range analysis
- Three detailed characteristic curves:
  - Torque vs Current
  - Speed vs Current
  - Speed vs Torque (main result)

## 🏗️ Architecture

### Backend (Flask)

**File:** `web_app.py`

**Key Components:**
- `MotorSimulation` class: Core simulation engine
- RESTful API endpoints:
  - `/api/create_simulation` - Initialize new simulation
  - `/api/update_params` - Update motor parameters
  - `/api/update_control` - Update control parameters
  - `/api/start` - Start simulation
  - `/api/stop` - Stop simulation
  - `/api/reset` - Reset simulation
  - `/api/step` - Perform simulation step
  - `/api/solve_example` - Solve Example 29.32
  - `/api/calculate_economics` - Calculate economic analysis
  - `/api/get_losses` - Get detailed loss data

**Simulation Engine:**
- Multi-physics ODE solver
- RK45 (adaptive step) or Euler (fixed step)
- Coupled electromagnetic-thermal-mechanical equations
- Temperature-dependent parameters
- Nonlinear effects (saturation, etc.)

### Frontend

**HTML Template:** `templates/index.html`
- Responsive multi-tab interface
- Parameter input controls
- Chart containers
- Status displays

**CSS Styling:** `static/css/style.css`
- Modern gradient design
- Responsive grid layouts
- Professional color scheme
- Smooth animations and transitions
- Auto-scaling for different screen sizes

**JavaScript:** `static/js/app.js`
- Chart.js integration
- Real-time data updates
- API communication
- Tab management
- Parameter synchronization

## 📊 Technical Details

### Mathematical Models

**Electromagnetic Model:**
```
V = Eb + Ia·Ra + La·dIa/dt
Eb = ke·Φ·ω (where Φ ∝ Ia for series motor)
```

**Mechanical Model:**
```
J·dω/dt = T_motor - T_load - B·ω
T = kt·Φ·Ia ∝ Ia² (series motor characteristic)
```

**Thermal Model:**
```
C·dT/dt = P_loss - (T - T_amb)/R_th
Temperature-dependent resistance: Ra(T) = Ra0·(1 + α·ΔT)
```

### Loss Calculations

1. **Copper Losses**: P_copper = Ia² · Ra(T)
2. **Iron Losses**: P_iron = k · ω²
3. **Mechanical Losses**: P_mech = B · ω²
4. **Stray Losses**: P_stray = k · V · Ia

### ODE Solvers

**RK45 (Runge-Kutta 4-5):**
- Adaptive step size
- High accuracy
- Automatic error control

**Euler Method:**
- Fixed step size
- Simple and fast
- Good for real-time visualization

## 🎨 User Interface

### Design Features

- **Gradient Theme**: Purple-blue gradient background
- **Tab Navigation**: 6 comprehensive tabs
- **Responsive Layout**: Works on desktop, tablet, mobile
- **Real-Time Charts**: Chart.js with smooth animations
- **Interactive Controls**: Sliders with live value display
- **Status Indicators**: Color-coded warnings (green/yellow/red)
- **Professional Typography**: Clean, readable fonts

### Responsive Breakpoints

- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## 🔧 API Reference

### POST /api/create_simulation

Creates a new simulation instance.

**Response:**
```json
{
  "sim_id": "uuid-string"
}
```

### POST /api/update_params

Updates motor parameters.

**Request:**
```json
{
  "sim_id": "uuid-string",
  "params": {
    "V_supply": 460.0,
    "R_armature": 0.5,
    ...
  }
}
```

**Response:**
```json
{
  "status": "success"
}
```

### POST /api/step

Performs one simulation step and returns current state.

**Request:**
```json
{
  "sim_id": "uuid-string"
}
```

**Response:**
```json
{
  "state": {
    "current": 25.5,
    "speed": 157.08,
    "torque": 120.3,
    "temperature": 45.2,
    "power_in": 11500,
    "power_out": 9800
  },
  "history": {
    "time": [...],
    "current": [...],
    "speed": [...],
    ...
  },
  "time": 5.5,
  "is_running": true
}
```

### POST /api/solve_example

Solves Example 29.32.

**Response:**
```json
{
  "test_data": {...},
  "extended_data": {...},
  "coefficients": {
    "k_torque": 0.985,
    "n": 1.95
  },
  "analysis": {
    "max_torque": 550.2,
    "min_speed": 850.5,
    "max_speed": 1100.8
  }
}
```

## 🌟 Advanced Features

### 1. Temperature Derating

The simulator includes automatic thermal derating:
- Below rated temperature (120°C): 100% capability
- Above rated temperature: Linear derating
- Above maximum temperature: Shutdown warning

### 2. Control Strategy Optimization

Each control method provides:
- Description and best use cases
- Parameter adjustment guidelines
- Real-time performance feedback

### 3. Economic Optimization

The economic analysis provides:
- Cost breakdown by category
- Loss cost analysis
- Efficiency improvement recommendations
- Environmental impact assessment

### 4. Multi-Physics Coupling

All physical domains are coupled:
- Temperature affects resistance
- Resistance affects current
- Current affects torque and losses
- Losses affect temperature rise

## 🐛 Troubleshooting

### Issue: Application won't start

**Solution:**
```bash
# Check if port 5000 is available
lsof -i :5000

# Or run on different port
python3 web_app.py --port 5001
```

### Issue: Charts not updating

**Solution:**
- Ensure JavaScript is enabled in browser
- Check browser console for errors (F12)
- Verify Flask server is running
- Hard refresh the page (Ctrl+F5)

### Issue: Slow performance

**Solution:**
- Close other browser tabs
- Use Euler solver instead of RK45
- Reduce update frequency (modify `setInterval` in app.js)

### Issue: CORS errors

**Solution:**
- Ensure flask-cors is installed
- Check that CORS is properly configured in web_app.py

## 📱 Browser Compatibility

**Fully Supported:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Partial Support:**
- IE 11 (basic functionality, no modern features)

## 🔐 Security Notes

**For Production Deployment:**

1. Change secret key in `web_app.py`
2. Enable HTTPS
3. Add authentication if needed
4. Configure proper CORS origins
5. Use production WSGI server (gunicorn, uwsgi)

**Example Production Command:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

## 📈 Performance

**Typical Performance:**
- Simulation update rate: 20 Hz
- Chart refresh rate: 20 Hz
- Response time: < 50ms
- Memory usage: ~50 MB per session

**Optimization Tips:**
- Limit history to 500 points (already configured)
- Use 'none' animation mode for Chart.js updates
- Clear inactive sessions regularly

## 🎓 Educational Use

This web application is ideal for:

1. **Classroom Demonstrations**
   - Project on screen
   - Live parameter changes
   - Real-time visualization

2. **Student Experiments**
   - Individual exploration
   - Parameter sensitivity analysis
   - Control system design

3. **Research Applications**
   - Motor characterization
   - Control algorithm testing
   - Thermal analysis

4. **Professional Analysis**
   - Motor selection
   - Performance prediction
   - Economic evaluation

## 🤝 Contributing

To extend or modify:

1. **Add new control method:**
   - Update `apply_control()` in `web_app.py`
   - Add UI controls in `index.html`
   - Update `updateControlMethod()` in `app.js`

2. **Add new chart:**
   - Create chart in `initializeCharts()` in `app.js`
   - Add canvas element in `index.html`
   - Update data in appropriate update function

3. **Add new analysis:**
   - Create API endpoint in `web_app.py`
   - Add UI controls and display in `index.html`
   - Create fetch function in `app.js`

## 📝 License

This web application is provided for educational and professional use in electrical engineering.

## 🙏 Credits

**Technologies Used:**
- Flask (web framework)
- Chart.js (data visualization)
- NumPy (numerical computing)
- SciPy (scientific computing)
- HTML5, CSS3, JavaScript (ES6)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Check browser console for errors
4. Review Flask server logs

## 🚀 Future Enhancements

Potential additions:
- WebSocket for real-time bidirectional communication
- Database integration for saving simulations
- User authentication and sessions
- PDF report generation
- Batch simulation capability
- Comparison of multiple motors
- 3D visualization of thermal distribution
- Mobile app version

---

**Version:** 1.0.0
**Last Updated:** 2024
**Developed for:** Advanced Electrical Engineering Education and Professional Motor Analysis

## 🎯 Key Differentiators

This is not just a simple calculator - it's a **comprehensive engineering tool** that combines:

✅ Rigorous multi-physics modeling
✅ Real-time interactive visualization
✅ Advanced control strategies
✅ Economic and environmental analysis
✅ Professional-grade accuracy
✅ Educational value
✅ Practical engineering insights

Perfect for students, educators, researchers, and practicing engineers!
