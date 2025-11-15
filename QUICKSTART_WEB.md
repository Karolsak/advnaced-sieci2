# 🚀 Quick Start Guide - Web Application

## Get Started in 3 Steps!

### Step 1: Install Dependencies

```bash
cd advnaced-sieci2
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- NumPy (numerical computing)
- SciPy (scientific computing)
- Matplotlib (compatibility)

### Step 2: Start the Server

```bash
python3 web_app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

### Step 3: Open in Browser

Open your web browser and go to:
```
http://localhost:5000
```

## ✅ You're Ready!

The web application is now running with all features:

### 🎯 Try These First:

#### 1. Solve Example 29.32
- Click **"Example 29.32"** tab
- Click **"Solve Example 29.32"** button
- View the complete solution with graphs!

#### 2. Run a Real-Time Simulation
- Go to **"Main Control"** tab
- Adjust any parameter slider (try Load Torque)
- Click **"▶ Start"** button
- Watch the graphs update in real-time!
- Click **"⏸ Stop"** when done

#### 3. Try Different Control Methods
- Go to **"Motor Control"** tab
- Select "PI Speed Control"
- Adjust Kp, Ki, and Speed Setpoint
- Go back to Main Control and click Start
- See how the motor maintains constant speed!

#### 4. Analyze Performance
- Go to **"Performance Analysis"** tab
- Run a simulation first (Main Control → Start)
- View loss breakdown and efficiency curves

#### 5. Check Thermal Status
- Go to **"Thermal Analysis"** tab
- Run simulation and watch temperature rise
- See thermal derating in action

#### 6. Calculate Economics
- Go to **"Economic Analysis"** tab
- Run simulation for a while
- Enter your energy cost
- Click **"Calculate Economics"**
- View 10-year cost projection!

## 📱 Browser Compatibility

Works best with:
- ✅ Chrome
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## 🎨 Features at a Glance

| Tab | What You Can Do |
|-----|----------------|
| **Main Control** | Adjust parameters, start/stop simulation, view 6 real-time graphs |
| **Motor Control** | Select control strategy (PI, PWM, Field Weakening, etc.) |
| **Performance Analysis** | View loss breakdown, efficiency curves, speed-torque curves |
| **Thermal Analysis** | Monitor temperature, view derating curves, thermal status |
| **Economic Analysis** | Calculate costs, view projections, CO₂ emissions |
| **Example 29.32** | Solve the series motor problem with detailed analysis |

## 🎛️ Interactive Controls

### Sliders
- Drag to adjust values in real-time
- Current value shown on the right
- Changes applied immediately

### Buttons
- **▶ Start**: Begin simulation
- **⏸ Stop**: Pause simulation
- **↻ Reset**: Clear all data and restart

### Charts
- Auto-update during simulation
- Hover for exact values
- Zoom and pan supported

## 💡 Pro Tips

1. **For Smooth Animation**: Use RK45 solver
2. **For Faster Updates**: Use Euler solver
3. **To See Thermal Effects**: Run for longer time
4. **Best Performance**: Use Chrome browser
5. **Mobile Access**: Works on tablets and phones!

## 🔧 Troubleshooting

### Problem: Port already in use
```bash
# Find what's using port 5000
lsof -i :5000

# Kill it (if safe) or use different port
python3 web_app.py  # Edit port in web_app.py
```

### Problem: Charts not showing
- Hard refresh: `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Clear browser cache
- Check browser console (F12) for errors

### Problem: Slow performance
- Close other browser tabs
- Use Euler solver instead of RK45
- Reduce parameter changes during simulation

## 📊 Understanding the Graphs

### Main Control Tab:
1. **Current**: Shows armature current in Amps
2. **Speed**: Motor speed in RPM
3. **Torque**: Electromagnetic torque in N·m
4. **Temperature**: Winding temperature in °C
5. **Power**: Input (blue) and output (green) power in kW
6. **Efficiency**: Motor efficiency in %

### Performance Analysis Tab:
1. **Loss Pie**: Breakdown of all losses
2. **Loss Time**: How losses change over time
3. **Speed-Torque**: Operating points scatter plot
4. **Efficiency Curve**: Efficiency vs torque

### Example 29.32 Tab:
1. **Torque vs Current**: Shows T ∝ I² relationship
2. **Speed vs Current**: How speed varies with current
3. **Speed vs Torque**: **Main Result** - complete characteristic curve

## 🌟 Advanced Features

### Custom Control Strategy
Edit `web_app.py` → `apply_control()` method to add your own!

### Export Data
Data available via API endpoints - use browser dev tools to capture

### Multiple Sessions
Each browser tab gets its own simulation instance

## 📚 Full Documentation

For complete details, see:
- **WEB_APP_README.md** - Complete documentation
- **README_MOTOR_SIMULATOR.md** - Technical details
- **INSTALL.md** - Installation guide

## 🎓 Educational Use

Perfect for:
- Classroom demonstrations (project to screen)
- Student lab exercises
- Research projects
- Motor design and selection
- Control system development

## 🚀 What's Next?

Once you're comfortable:
1. Experiment with different control strategies
2. Try extreme parameter values
3. Compare different operating points
4. Analyze economic impact of efficiency
5. Study thermal behavior under different loads

## 🎉 Enjoy!

You now have a professional-grade DC motor simulator running in your browser!

Questions? Check the full documentation in **WEB_APP_README.md**

---

**Happy Simulating! ⚡🔧**
