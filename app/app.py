import os
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Local imports
from srt_controller import SRTController
from iperf_controller import IperfController
from stats_manager import StatsManager
from config import ConfigManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize controllers
srt_controller = SRTController()
iperf_controller = IperfController()
stats_manager = StatsManager()
config_manager = ConfigManager()

# Global state
running_srt = False
running_iperf = False
srt_thread = None
iperf_thread = None

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/srt-config')
def srt_config():
    return render_template('srt_config.html')

@app.route('/iperf-config')
def iperf_config():
    return render_template('iperf_config.html')

@app.route('/stats')
def stats_viewer():
    return render_template('stats.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

# SRT Configuration Endpoints
@app.route('/api/srt/config', methods=['GET', 'POST'])
def srt_config_api():
    if request.method == 'POST':
        config = request.json
        config_manager.save_srt_config(config)
        return jsonify({"status": "success", "message": "SRT configuration saved"})

    return jsonify(config_manager.get_srt_config())

@app.route('/api/srt/start', methods=['POST'])
def start_srt():
    global running_srt, srt_thread

    if running_srt:
        return jsonify({"status": "error", "message": "SRT is already running"})

    config = config_manager.get_srt_config()
    srt_thread = threading.Thread(target=srt_controller.start_srt, args=(config,))
    srt_thread.daemon = True
    srt_thread.start()
    running_srt = True

    return jsonify({"status": "success", "message": "SRT started"})

@app.route('/api/srt/stop', methods=['POST'])
def stop_srt():
    global running_srt

    if not running_srt:
        return jsonify({"status": "error", "message": "SRT is not running"})

    srt_controller.stop_srt()
    running_srt = False

    return jsonify({"status": "success", "message": "SRT stopped"})

# Iperf Configuration Endpoints
@app.route('/api/iperf/config', methods=['GET', 'POST'])
def iperf_config_api():
    if request.method == 'POST':
        config = request.json
        config_manager.save_iperf_config(config)
        return jsonify({"status": "success", "message": "Iperf configuration saved"})

    return jsonify(config_manager.get_iperf_config())

@app.route('/api/iperf/start', methods=['POST'])
def start_iperf():
    global running_iperf, iperf_thread

    if running_iperf:
        return jsonify({"status": "error", "message": "Iperf is already running"})

    config = config_manager.get_iperf_config()
    iperf_thread = threading.Thread(target=iperf_controller.start_iperf, args=(config,))
    iperf_thread.daemon = True
    iperf_thread.start()
    running_iperf = True

    return jsonify({"status": "success", "message": "Iperf started"})

@app.route('/api/iperf/stop', methods=['POST'])
def stop_iperf():
    global running_iperf

    if not running_iperf:
        return jsonify({"status": "error", "message": "Iperf is not running"})

    iperf_controller.stop_iperf()
    running_iperf = False

    return jsonify({"status": "success", "message": "Iperf stopped"})

# Statistics Endpoints
@app.route('/api/stats/srt')
def get_srt_stats():
    stats = stats_manager.get_srt_stats()
    return jsonify(stats)

@app.route('/api/stats/iperf')
def get_iperf_stats():
    stats = stats_manager.get_iperf_stats()
    return jsonify(stats)

@app.route('/api/stats/export/csv')
def export_stats_csv():
    stats = stats_manager.get_all_stats()
    df = pd.DataFrame(stats)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'srt_stats_{timestamp}.csv'
    )

@app.route('/api/stats/export/pdf')
def export_stats_pdf():
    stats = stats_manager.get_all_stats()

    # Create PDF report
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("SRT Monitoring Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))

    # Convert stats to table data
    data = [['Timestamp', 'Throughput (Mbps)', 'Packet Loss', 'Retransmits', 'Latency (ms)']]
    for stat in stats:
        data.append([
            stat.get('timestamp', 'N/A'),
            f"{stat.get('throughput', 0):.2f}",
            f"{stat.get('packet_loss', 0):.2f}%",
            stat.get('retransmits', 0),
            f"{stat.get('latency', 0):.2f}"
        ])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'srt_report_{timestamp}.pdf'
    )

# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def background_stats_updater():
    while True:
        if running_srt:
            stats = srt_controller.get_current_stats()
            stats_manager.update_srt_stats(stats)
            socketio.emit('srt_stats_update', stats)

        if running_iperf:
            stats = iperf_controller.get_current_stats()
            stats_manager.update_iperf_stats(stats)
            socketio.emit('iperf_stats_update', stats)

        time.sleep(1)

# Start background thread
stats_thread = threading.Thread(target=background_stats_updater, daemon=True)
stats_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
