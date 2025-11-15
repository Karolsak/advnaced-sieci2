// Advanced DC Motor Simulator - JavaScript Application

let simId = null;
let simulationInterval = null;
let charts = {};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    createSimulation();
    initializeCharts();
    setupEventListeners();
});

// Create new simulation instance
async function createSimulation() {
    try {
        const response = await fetch('/api/create_simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        simId = data.sim_id;
        console.log('Simulation created:', simId);
    } catch (error) {
        console.error('Error creating simulation:', error);
    }
}

// Tab Management
function openTab(evt, tabName) {
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }

    const tabButtons = document.getElementsByClassName('tab-button');
    for (let i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove('active');
    }

    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
}

// Initialize all charts
function initializeCharts() {
    // Main control charts
    charts.current = createLineChart('chart-current', 'Armature Current (A)', '#3498db');
    charts.speed = createLineChart('chart-speed', 'Motor Speed (RPM)', '#2ecc71');
    charts.torque = createLineChart('chart-torque', 'Motor Torque (N·m)', '#e74c3c');
    charts.temperature = createLineChart('chart-temperature', 'Temperature (°C)', '#e67e22');
    charts.power = createMultiLineChart('chart-power', 'Power (kW)', ['Input', 'Output'], ['#9b59b6', '#1abc9c']);
    charts.efficiency = createLineChart('chart-efficiency', 'Efficiency (%)', '#f39c12');

    // Analysis charts
    charts.lossPie = createPieChart('chart-loss-pie', 'Loss Breakdown');
    charts.lossTime = createMultiLineChart('chart-loss-time', 'Losses Over Time (W)',
        ['Copper', 'Iron', 'Mechanical', 'Stray'], ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']);
    charts.speedTorque = createScatterChart('chart-speed-torque', 'Speed (RPM)', 'Torque (N·m)');
    charts.efficiencyCurve = createScatterChart('chart-efficiency-curve', 'Torque (N·m)', 'Efficiency (%)');

    // Thermal charts
    charts.tempRise = createMultiLineChart('chart-temp-rise', 'Temperature (°C)',
        ['Winding Temp', 'Ambient', 'Max'], ['#e74c3c', '#3498db', '#c0392b']);
    charts.derating = createLineChart('chart-derating', 'Power Capability (%)', '#e74c3c');

    // Economic charts
    charts.costBreakdown = createPieChart('chart-cost-breakdown', 'Annual Cost Breakdown');
    charts.costProjection = createLineChart('chart-cost-projection', 'Cumulative Cost ($)', '#27ae60');

    // Example 29.32 charts
    charts.torqueCurrent = createScatterChart('chart-torque-current', 'Current (A)', 'Torque (N·m)');
    charts.speedCurrent = createScatterChart('chart-speed-current', 'Current (A)', 'Speed (RPM)');
    charts.speedTorqueFinal = createScatterChart('chart-speed-torque-final', 'Torque (N·m)', 'Speed (RPM)');
}

// Chart creation helpers
function createLineChart(canvasId, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: color,
                backgroundColor: color + '33',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: label,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (s)'
                    }
                },
                y: {
                    display: true,
                    beginAtZero: true
                }
            }
        }
    });
}

function createMultiLineChart(canvasId, title, labels, colors) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const datasets = labels.map((label, index) => ({
        label: label,
        data: [],
        borderColor: colors[index],
        backgroundColor: colors[index] + '33',
        borderWidth: 2,
        fill: false,
        tension: 0.4
    }));

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (s)'
                    }
                },
                y: {
                    display: true,
                    beginAtZero: true
                }
            }
        }
    });
}

function createPieChart(canvasId, title) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

function createScatterChart(canvasId, xLabel, yLabel) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: `${yLabel} vs ${xLabel}`,
                data: [],
                backgroundColor: '#667eea',
                borderColor: '#764ba2',
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: `${yLabel} vs ${xLabel}`,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: xLabel
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: yLabel
                    }
                }
            }
        }
    });
}

// Parameter updates
async function updateParam(param, value) {
    document.getElementById(param.toLowerCase().replace('_', '-') + '-val').textContent = value;

    const params = {};
    params[param] = parseFloat(value);

    try {
        await fetch('/api/update_params', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sim_id: simId,
                params: params
            })
        });
    } catch (error) {
        console.error('Error updating parameter:', error);
    }
}

async function updateControlParam(param, value) {
    document.getElementById(param.toLowerCase().replace('_', '-') + '-val').textContent = value;

    const params = {};
    params[param] = parseFloat(value);

    try {
        await fetch('/api/update_control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sim_id: simId,
                params: params
            })
        });
    } catch (error) {
        console.error('Error updating control parameter:', error);
    }
}

async function updateControlMethod(method) {
    try {
        await fetch('/api/update_control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sim_id: simId,
                params: { method: method }
            })
        });

        // Update control info
        const infoDiv = document.getElementById('control-info');
        const controlInfo = {
            'Open Loop': 'Direct voltage control without feedback. Simple but no automatic regulation.',
            'PI Speed Control': 'Proportional-Integral controller maintains constant speed under varying loads. Adjust Kp and Ki for desired response.',
            'Field Weakening': 'Extends speed range above base speed by reducing effective field strength. Used for high-speed operation.',
            'Chopper Control': 'DC-DC converter control using duty cycle modulation. Efficient voltage control.',
            'PWM Control': 'Pulse Width Modulation provides smooth voltage control. Adjust duty cycle for desired output.'
        };

        infoDiv.innerHTML = `<p><strong>${method}:</strong> ${controlInfo[method]}</p>`;
    } catch (error) {
        console.error('Error updating control method:', error);
    }
}

// Simulation controls
async function startSimulation() {
    try {
        await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sim_id: simId })
        });

        if (!simulationInterval) {
            simulationInterval = setInterval(updateSimulation, 50); // Update every 50ms
        }
    } catch (error) {
        console.error('Error starting simulation:', error);
    }
}

async function stopSimulation() {
    try {
        await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sim_id: simId })
        });

        if (simulationInterval) {
            clearInterval(simulationInterval);
            simulationInterval = null;
        }
    } catch (error) {
        console.error('Error stopping simulation:', error);
    }
}

async function resetSimulation() {
    try {
        await fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sim_id: simId })
        });

        // Clear all charts
        Object.values(charts).forEach(chart => {
            if (chart.data.labels) {
                chart.data.labels = [];
                chart.data.datasets.forEach(dataset => {
                    dataset.data = [];
                });
                chart.update();
            }
        });

        // Reset status display
        updateStatusDisplay({
            current: 0,
            speed: 0,
            torque: 0,
            temperature: 25,
            power_in: 0,
            power_out: 0
        });
    } catch (error) {
        console.error('Error resetting simulation:', error);
    }
}

// Update simulation state
async function updateSimulation() {
    try {
        const response = await fetch('/api/step', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sim_id: simId })
        });

        const data = await response.json();

        if (data.is_running) {
            updateStatusDisplay(data.state);
            updateCharts(data.history);
            updateAnalysisCharts(data.history);
            updateThermalCharts(data);
        }
    } catch (error) {
        console.error('Error updating simulation:', error);
    }
}

// Update status display
function updateStatusDisplay(state) {
    document.getElementById('status-current').textContent = state.current.toFixed(2) + ' A';
    document.getElementById('status-speed').textContent = (state.speed * 60 / (2 * Math.PI)).toFixed(2) + ' RPM';
    document.getElementById('status-torque').textContent = state.torque.toFixed(2) + ' N·m';
    document.getElementById('status-temp').textContent = state.temperature.toFixed(1) + ' °C';
    document.getElementById('status-power-in').textContent = (state.power_in / 1000).toFixed(2) + ' kW';

    const efficiency = state.power_in > 0 ? (state.power_out / state.power_in * 100) : 0;
    document.getElementById('status-efficiency').textContent = efficiency.toFixed(2) + ' %';
}

// Update main charts
function updateCharts(history) {
    const time = history.time;

    updateSingleChart(charts.current, time, history.current);
    updateSingleChart(charts.speed, time, history.speed);
    updateSingleChart(charts.torque, time, history.torque);
    updateSingleChart(charts.temperature, time, history.temperature);
    updateSingleChart(charts.efficiency, time, history.efficiency);

    // Power chart (multi-line)
    const powerIn = history.power_in.map(p => p / 1000);
    const powerOut = history.power_out.map(p => p / 1000);
    charts.power.data.labels = time;
    charts.power.data.datasets[0].data = powerIn;
    charts.power.data.datasets[1].data = powerOut;
    charts.power.update('none');
}

function updateSingleChart(chart, labels, data) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update('none');
}

// Update analysis charts
async function updateAnalysisCharts(history) {
    // Get loss data
    try {
        const response = await fetch('/api/get_losses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sim_id: simId })
        });

        const lossData = await response.json();

        if (lossData.time && lossData.time.length > 0) {
            // Update loss time chart
            charts.lossTime.data.labels = lossData.time;
            charts.lossTime.data.datasets[0].data = lossData.copper_loss;
            charts.lossTime.data.datasets[1].data = lossData.iron_loss;
            charts.lossTime.data.datasets[2].data = lossData.mech_loss;
            charts.lossTime.data.datasets[3].data = lossData.stray_loss;
            charts.lossTime.update('none');

            // Update loss pie chart (average of recent data)
            const avgCopper = average(lossData.copper_loss.slice(-10));
            const avgIron = average(lossData.iron_loss.slice(-10));
            const avgMech = average(lossData.mech_loss.slice(-10));
            const avgStray = average(lossData.stray_loss.slice(-10));

            charts.lossPie.data.labels = ['Copper', 'Iron', 'Mechanical', 'Stray'];
            charts.lossPie.data.datasets[0].data = [avgCopper, avgIron, avgMech, avgStray];
            charts.lossPie.update('none');
        }

        // Update speed-torque scatter
        if (history.speed && history.torque) {
            const speedTorqueData = history.speed.map((s, i) => ({
                x: history.torque[i],
                y: s
            }));
            charts.speedTorque.data.datasets[0].data = speedTorqueData;
            charts.speedTorque.update('none');

            // Update efficiency curve
            const efficiencyData = history.torque.map((t, i) => ({
                x: t,
                y: history.efficiency[i]
            }));
            charts.efficiencyCurve.data.datasets[0].data = efficiencyData;
            charts.efficiencyCurve.update('none');
        }
    } catch (error) {
        console.error('Error updating analysis charts:', error);
    }
}

// Update thermal charts
function updateThermalCharts(data) {
    const maxTemp = parseFloat(document.getElementById('max-temp').value);
    const ambientTemp = parseFloat(document.getElementById('ambient-temp').value);

    // Temperature rise chart
    const time = data.history.time;
    const temp = data.history.temperature;
    const ambient = Array(time.length).fill(ambientTemp);
    const max = Array(time.length).fill(maxTemp);

    charts.tempRise.data.labels = time;
    charts.tempRise.data.datasets[0].data = temp;
    charts.tempRise.data.datasets[1].data = ambient;
    charts.tempRise.data.datasets[2].data = max;
    charts.tempRise.update('none');

    // Derating curve
    const tempRange = Array.from({length: 100}, (_, i) => i * 2);
    const ratedTemp = 120;
    const derating = tempRange.map(t => {
        if (t <= ratedTemp) return 100;
        return Math.max(0, 100 * (1 - (t - ratedTemp) / 80));
    });

    charts.derating.data.labels = tempRange;
    charts.derating.data.datasets[0].data = derating;
    charts.derating.update('none');

    // Update status
    const currentTemp = data.state.temperature;
    const statusDiv = document.getElementById('derating-status');

    if (currentTemp < ratedTemp) {
        statusDiv.textContent = `Operating at 100% capacity\nCurrent: ${currentTemp.toFixed(1)}°C`;
        statusDiv.className = 'status-ok';
    } else if (currentTemp < maxTemp) {
        const capability = 100 * (1 - (currentTemp - ratedTemp) / 80);
        statusDiv.textContent = `Derated to ${capability.toFixed(1)}% capacity\nCurrent: ${currentTemp.toFixed(1)}°C`;
        statusDiv.className = 'status-warning';
    } else {
        statusDiv.textContent = `OVERHEATING! ${currentTemp.toFixed(1)}°C\nShutdown recommended!`;
        statusDiv.className = 'status-danger';
    }
}

// Calculate economics
async function calculateEconomics() {
    const powerCost = parseFloat(document.getElementById('power-cost').value);
    const operatingHours = parseFloat(document.getElementById('operating-hours').value);
    const maintenanceCost = parseFloat(document.getElementById('maintenance-cost').value);

    try {
        const response = await fetch('/api/calculate_economics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sim_id: simId,
                power_cost: powerCost,
                operating_hours: operatingHours,
                maintenance_cost: maintenanceCost
            })
        });

        const data = await response.json();

        // Display results
        const output = document.getElementById('economic-output');
        output.innerHTML = `
<strong>OPERATING CONDITIONS:</strong>
Average Input Power:    ${data.operating.avg_power_in.toFixed(2)} kW
Average Output Power:   ${data.operating.avg_power_out.toFixed(2)} kW
Average Efficiency:     ${data.operating.avg_efficiency.toFixed(2)}%

<strong>ANNUAL COSTS:</strong>
Energy Consumption:     ${data.annual.energy.toFixed(0)} kWh
Energy Cost:            $${data.annual.energy_cost.toFixed(2)}
Maintenance Cost:       $${data.annual.maintenance_cost.toFixed(2)}
Total Annual Cost:      $${data.annual.total_cost.toFixed(2)}

<strong>ENERGY LOSSES:</strong>
Annual Energy Loss:     ${data.annual.energy_loss.toFixed(0)} kWh
Annual Loss Cost:       $${data.annual.loss_cost.toFixed(2)}

Loss Breakdown:
  Copper Losses:        ${data.loss_breakdown.copper.toFixed(1)}%
  Iron Losses:          ${data.loss_breakdown.iron.toFixed(1)}%
  Mechanical Losses:    ${data.loss_breakdown.mechanical.toFixed(1)}%
  Stray Losses:         ${data.loss_breakdown.stray.toFixed(1)}%

<strong>10-YEAR PROJECTION:</strong>
Total Energy:           ${data.projection.total_energy.toFixed(0)} kWh
Total Cost:             $${data.projection.total_cost.toFixed(2)}

<strong>ENVIRONMENTAL IMPACT:</strong>
Annual CO₂ Emissions:   ${data.environmental.annual_co2.toFixed(0)} kg
10-Year CO₂ Emissions:  ${data.environmental.total_co2.toFixed(0)} kg
        `;

        // Update cost breakdown pie chart
        charts.costBreakdown.data.labels = ['Energy Cost', 'Maintenance Cost'];
        charts.costBreakdown.data.datasets[0].data = [
            data.annual.energy_cost,
            data.annual.maintenance_cost
        ];
        charts.costBreakdown.update();

        // Update cost projection chart
        const years = Array.from({length: 10}, (_, i) => i + 1);
        const cumulativeCost = years.map(y => y * data.annual.total_cost);

        charts.costProjection.data.labels = years;
        charts.costProjection.data.datasets[0].data = cumulativeCost;
        charts.costProjection.update();

    } catch (error) {
        console.error('Error calculating economics:', error);
        document.getElementById('economic-output').textContent = 'Error: ' + error.message;
    }
}

// Solve Example 29.32
async function solveExample() {
    try {
        const response = await fetch('/api/solve_example', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        // Display results
        const output = document.getElementById('example-output');
        output.innerHTML = `
<strong>TORQUE-CURRENT RELATIONSHIP:</strong>
T = ${data.coefficients.k_torque.toFixed(3)} × I^${data.coefficients.n.toFixed(3)}
(Exponent n ≈ ${data.coefficients.n.toFixed(2)}, close to 2 for series motor)

<strong>CALCULATED OPERATING POINTS:</strong>
${'Current'.padEnd(12)}${'Torque'.padEnd(12)}${'Back-EMF'.padEnd(12)}${'Speed'.padEnd(12)}
${'(A)'.padEnd(12)}${'(N·m)'.padEnd(12)}${'(V)'.padEnd(12)}${'(RPM)'.padEnd(12)}
${'-'.repeat(48)}
${data.test_data.current.map((c, i) =>
    `${c.toFixed(1).padEnd(12)}${data.test_data.torque[i].toFixed(1).padEnd(12)}${data.test_data.back_emf[i].toFixed(1).padEnd(12)}${data.test_data.speed[i].toFixed(1).padEnd(12)}`
).join('\n')}

<strong>KEY OBSERVATIONS:</strong>
• As load (torque) increases, speed decreases
• As current increases, torque increases (∝ I^${data.coefficients.n.toFixed(2)})
• Series motor shows characteristic drooping speed-torque curve
• Maximum torque: ${data.analysis.max_torque.toFixed(1)} N·m
• Speed range: ${data.analysis.min_speed.toFixed(0)} - ${data.analysis.max_speed.toFixed(0)} RPM

<strong>PRACTICAL IMPLICATIONS:</strong>
• High starting torque capability
• Speed varies significantly with load
• Suitable for traction applications
• Should not be run without load (runaway speed risk)
        `;

        // Update charts
        // Torque vs Current
        const tcData = data.test_data.current.map((c, i) => ({
            x: c,
            y: data.test_data.torque[i]
        }));
        charts.torqueCurrent.data.datasets = [{
            label: 'Test Data',
            data: tcData,
            backgroundColor: '#e74c3c',
            borderColor: '#c0392b',
            pointRadius: 8
        }];
        charts.torqueCurrent.update();

        // Speed vs Current
        const scData = data.test_data.current.map((c, i) => ({
            x: c,
            y: data.test_data.speed[i]
        }));
        charts.speedCurrent.data.datasets = [{
            label: 'Calculated Speed',
            data: scData,
            backgroundColor: '#2ecc71',
            borderColor: '#27ae60',
            pointRadius: 8
        }];
        charts.speedCurrent.update();

        // Speed vs Torque (main result)
        const stData = data.extended_data.torque.map((t, i) => ({
            x: t,
            y: data.extended_data.speed[i]
        }));
        const stTestData = data.test_data.torque.map((t, i) => ({
            x: t,
            y: data.test_data.speed[i]
        }));

        charts.speedTorqueFinal.data.datasets = [
            {
                label: 'Speed-Torque Curve',
                data: stData,
                backgroundColor: '#667eea',
                borderColor: '#764ba2',
                pointRadius: 2,
                showLine: true,
                borderWidth: 3
            },
            {
                label: 'Test Points',
                data: stTestData,
                backgroundColor: '#e74c3c',
                borderColor: '#c0392b',
                pointRadius: 10,
                showLine: false
            }
        ];
        charts.speedTorqueFinal.options.plugins.title.text = 'SPEED-TORQUE CHARACTERISTIC CURVE (Solution to Example 29.32)';
        charts.speedTorqueFinal.update();

    } catch (error) {
        console.error('Error solving example:', error);
        document.getElementById('example-output').textContent = 'Error: ' + error.message;
    }
}

// Helper functions
function average(arr) {
    if (arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function updateSolver(solver) {
    // This would send solver type to backend if needed
    console.log('Solver changed to:', solver);
}

function setupEventListeners() {
    // Add any additional event listeners here
    console.log('Event listeners setup complete');
}
