from flask import Flask, render_template, jsonify, request
import subprocess
import sys
import os
import threading
import time

app = Flask(__name__)

# Paths to your AR scripts
SCRIPT_PATHS = {
    "Piano": r"D:\college\abi kamu(don of kce) project\testpanio1.py",
    "Drums": r"D:\college\abi kamu(don of kce) project\drums.py",
    "Tabla": r"D:\college\abi kamu(don of kce) project\tablea\testtable.py"
}

# Store running processes to manage them
running_processes = {}

def run_script(script_path, instrument_name):
    """Run a script in a new process"""
    try:
        # Kill existing process if running
        if instrument_name in running_processes:
            try:
                running_processes[instrument_name].terminate()
                time.sleep(0.5)  # Give it time to terminate
            except:
                pass
        
        # Start new process
        process = subprocess.Popen(
            [sys.executable, script_path], 
            cwd=os.path.dirname(script_path)
        )
        running_processes[instrument_name] = process
        return True, f"{instrument_name} started successfully"
    except FileNotFoundError:
        return False, f"Error: The script at '{script_path}' was not found."
    except Exception as e:
        return False, f"An error occurred while trying to run the script: {e}"

def stop_script(instrument_name):
    """Stop a running script"""
    try:
        if instrument_name in running_processes:
            running_processes[instrument_name].terminate()
            del running_processes[instrument_name]
            return True, f"{instrument_name} stopped successfully"
        else:
            return False, f"{instrument_name} is not currently running"
    except Exception as e:
        return False, f"Error stopping {instrument_name}: {e}"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/run_instrument', methods=['POST'])
def run_instrument():
    """API endpoint to run an instrument"""
    data = request.get_json()
    instrument = data.get('instrument')
    
    if instrument not in SCRIPT_PATHS:
        return jsonify({'success': False, 'message': 'Invalid instrument'})
    
    script_path = SCRIPT_PATHS[instrument]
    
    if not os.path.exists(script_path):
        return jsonify({
            'success': False, 
            'message': f'Script file for {instrument} not found at {script_path}'
        })
    
    success, message = run_script(script_path, instrument)
    return jsonify({'success': success, 'message': message})

@app.route('/stop_instrument', methods=['POST'])
def stop_instrument():
    """API endpoint to stop an instrument"""
    data = request.get_json()
    instrument = data.get('instrument')
    
    if instrument not in SCRIPT_PATHS:
        return jsonify({'success': False, 'message': 'Invalid instrument'})
    
    success, message = stop_script(instrument)
    return jsonify({'success': success, 'message': message})

@app.route('/status')
def get_status():
    """Get status of all instruments"""
    status = {}
    for instrument in SCRIPT_PATHS.keys():
        status[instrument] = instrument in running_processes
    return jsonify(status)

# Create templates directory and index.html file
def create_template():
    """Create the HTML template"""
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AR Music Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 600px;
            width: 100%;
        }

        .title {
            text-align: center;
            color: white;
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
            letter-spacing: 2px;
        }

        .subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
            margin-bottom: 40px;
            font-weight: 300;
        }

        .instruments-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .instrument-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .instrument-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            background: rgba(255, 255, 255, 0.2);
        }

        .instrument-name {
            color: white;
            font-size: 1.5rem;
            margin-bottom: 15px;
            font-weight: 400;
        }

        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-start {
            background: linear-gradient(45deg, #00c851, #007e33);
            color: white;
        }

        .btn-start:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 200, 81, 0.4);
        }

        .btn-stop {
            background: linear-gradient(45deg, #ff4444, #cc0000);
            color: white;
        }

        .btn-stop:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255, 68, 68, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status-running {
            background-color: #00c851;
        }

        .status-stopped {
            background-color: #666;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        }

        .notification.success {
            background: linear-gradient(45deg, #00c851, #007e33);
        }

        .notification.error {
            background: linear-gradient(45deg, #ff4444, #cc0000);
        }

        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }

        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 30px;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            .title {
                font-size: 2rem;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">AR Music Hub</h1>
        <p class="subtitle">Experience Augmented Reality Music</p>
        
        <div class="instruments-grid">
            <div class="instrument-card" data-instrument="Piano">
                <div class="instrument-name">
                    <span class="status-indicator status-stopped" id="status-Piano"></span>
                    🎹 Piano
                </div>
                <div class="button-group">
                    <button class="btn btn-start" onclick="startInstrument('Piano')">Start</button>
                    <button class="btn btn-stop" onclick="stopInstrument('Piano')">Stop</button>
                </div>
            </div>
            
            <div class="instrument-card" data-instrument="Drums">
                <div class="instrument-name">
                    <span class="status-indicator status-stopped" id="status-Drums"></span>
                    🥁 Drums
                </div>
                <div class="button-group">
                    <button class="btn btn-start" onclick="startInstrument('Drums')">Start</button>
                    <button class="btn btn-stop" onclick="stopInstrument('Drums')">Stop</button>
                </div>
            </div>
            
            <div class="instrument-card" data-instrument="Tabla">
                <div class="instrument-name">
                    <span class="status-indicator status-stopped" id="status-Tabla"></span>
                    🪘 Tabla
                </div>
                <div class="button-group">
                    <button class="btn btn-start" onclick="startInstrument('Tabla')">Start</button>
                    <button class="btn btn-stop" onclick="stopInstrument('Tabla')">Stop</button>
                </div>
            </div>
        </div>
        
        <div class="footer">
            AR Music Hub - Interactive Musical Experience
        </div>
    </div>

    <div id="notification" class="notification"></div>

    <script>
        // Function to show notifications
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Function to update status indicators
        function updateStatusIndicator(instrument, isRunning) {
            const indicator = document.getElementById(`status-${instrument}`);
            if (isRunning) {
                indicator.className = 'status-indicator status-running';
            } else {
                indicator.className = 'status-indicator status-stopped';
            }
        }

        // Function to start an instrument
        async function startInstrument(instrument) {
            try {
                const response = await fetch('/run_instrument', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ instrument: instrument })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    updateStatusIndicator(instrument, true);
                } else {
                    showNotification(data.message, 'error');
                }
            } catch (error) {
                showNotification('Network error occurred', 'error');
            }
        }

        // Function to stop an instrument
        async function stopInstrument(instrument) {
            try {
                const response = await fetch('/stop_instrument', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ instrument: instrument })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    updateStatusIndicator(instrument, false);
                } else {
                    showNotification(data.message, 'error');
                }
            } catch (error) {
                showNotification('Network error occurred', 'error');
            }
        }

        // Function to check status of all instruments
        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const status = await response.json();
                
                for (const [instrument, isRunning] of Object.entries(status)) {
                    updateStatusIndicator(instrument, isRunning);
                }
            } catch (error) {
                console.log('Error checking status:', error);
            }
        }

        // Check status every 5 seconds
        setInterval(checkStatus, 5000);
        
        // Initial status check
        checkStatus();
    </script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, 'index.html'), 'w',encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Create the HTML template
    create_template()
    
    print("🎵 AR Music Hub Web Application")
    print("=" * 40)
    print("Creating templates...")
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Clean up any existing processes on startup
    for process in running_processes.values():
        try:
            process.terminate()
        except:
            pass
    running_processes.clear()
    
    # Run the Flask app
    app.run(host='localhost', port=5000, debug=True)