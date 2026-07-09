import socket
import threading
import time
from python_srt import Socket, AF_INET, SOCK_DGRAM, SRTO_PACKETFILTER, SRTO_SNDBUF, SRTO_RCVBUF
import json

class SRTController:
    def __init__(self):
        self.srt_socket = None
        self.running = False
        self.stats = {
            'timestamp': None,
            'throughput': 0,
            'packet_loss': 0,
            'retransmits': 0,
            'latency': 0,
            'dropped_packets': 0,
            'out_of_order': 0,
            'available_bandwidth': 0
        }

    def start_srt(self, config):
        """Start SRT connection based on configuration"""
        self.running = True

        try:
            # Parse configuration
            mode = config.get('mode', 'caller')
            ingress_ip = config.get('ingress_ip', '0.0.0.0')
            ingress_port = config.get('ingress_port', 9000)
            egress_ip = config.get('egress_ip', '127.0.0.1')
            egress_port = config.get('egress_port', 9001)
            buffer_size = config.get('buffer_size', 8192)
            latency = config.get('latency', 120)
            payload_size = config.get('payload_size', 1316)

            # Create SRT socket
            self.srt_socket = Socket(AF_INET, SOCK_DGRAM)
            self.srt_socket.setsockopt(SRTO_SNDBUF, buffer_size)
            self.srt_socket.setsockopt(SRTO_RCVBUF, buffer_size)
            self.srt_socket.setsockopt(SRTO_PACKETFILTER, f"recv {latency}")

            if mode == 'caller':
                self.srt_socket.bind((ingress_ip, ingress_port))
                print(f"SRT Caller bound to {ingress_ip}:{ingress_port}")
            else:  # listener
                self.srt_socket.listen((ingress_ip, ingress_port))
                print(f"SRT Listener waiting on {ingress_ip}:{ingress_port}")

            # Start statistics thread
            stats_thread = threading.Thread(target=self._collect_stats)
            stats_thread.daemon = True
            stats_thread.start()

            # Start data transfer
            self._transfer_data(mode, egress_ip, egress_port, payload_size)

        except Exception as e:
            print(f"SRT Error: {str(e)}")
            self.running = False

    def _transfer_data(self, mode, egress_ip, egress_port, payload_size):
        """Handle data transfer based on mode"""
        try:
            if mode == 'caller':
                # Caller connects to listener
                self.srt_socket.connect((egress_ip, egress_port))
                print(f"SRT Caller connected to {egress_ip}:{egress_port}")

                # Send data
                counter = 0
                while self.running:
                    data = b'X' * payload_size
                    self.srt_socket.send(data)
                    counter += 1
                    time.sleep(0.001)  # ~1ms delay

            else:  # listener
                # Listener accepts connection
                conn, addr = self.srt_socket.accept()
                print(f"SRT Listener accepted connection from {addr}")

                # Receive data
                while self.running:
                    data = conn.recv(payload_size)
                    if not data:
                        break

        except Exception as e:
            print(f"Data transfer error: {str(e)}")
        finally:
            self.stop_srt()

    def _collect_stats(self):
        """Collect SRT statistics"""
        while self.running:
            try:
                # In a real implementation, use SRT API to get actual stats
                # This is a simulation
                self.stats = {
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'throughput': 10.5 + (hash(str(time.time())) % 5),  # Simulated
                    'packet_loss': 0.2 + (hash(str(time.time())) % 0.5),
                    'retransmits': 5 + (hash(str(time.time())) % 10),
                    'latency': 45.0 + (hash(str(time.time())) % 20),
                    'dropped_packets': 2 + (hash(str(time.time())) % 3),
                    'out_of_order': 1 + (hash(str(time.time())) % 2),
                    'available_bandwidth': 100.0 - (hash(str(time.time())) % 20)
                }

                time.sleep(1)

            except Exception as e:
                print(f"Stats collection error: {str(e)}")
                time.sleep(2)

    def get_current_stats(self):
        """Get current statistics"""
        return self.stats.copy()

    def stop_srt(self):
        """Stop SRT connection"""
        self.running = False
        if self.srt_socket:
            try:
                self.srt_socket.close()
            except:
                pass
        self.srt_socket = None
        print("SRT stopped")
