import socket
import threading
import time
import random
import struct

class UDPGenerator:
    def __init__(self):
        self.running = False
        self.socket = None

    def start_generator(self, config):
        """Start UDP traffic generator"""
        self.running = True

        try:
            bind_ip = config.get('bind_ip', '0.0.0.0')
            bind_port = config.get('bind_port', 10000)
            target_ip = config.get('target_ip', '127.0.0.1')
            target_port = config.get('target_port', 10001)
            packet_size = config.get('packet_size', 1024)
            rate = config.get('rate', 100)  # packets per second
            duration = config.get('duration', 60)

            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((bind_ip, bind_port))

            print(f"UDP Generator started: {bind_ip}:{bind_port} -> {target_ip}:{target_port}")

            # Start generator thread
            generator_thread = threading.Thread(
                target=self._generate_traffic,
                args=(target_ip, target_port, packet_size, rate, duration)
            )
            generator_thread.daemon = True
            generator_thread.start()

            # Start receiver thread
            receiver_thread = threading.Thread(
                target=self._receive_packets
            )
            receiver_thread.daemon = True
            receiver_thread.start()

        except Exception as e:
            print(f"UDP Generator error: {str(e)}")
            self.running = False

    def _generate_traffic(self, target_ip, target_port, packet_size, rate, duration):
        """Generate UDP traffic"""
        try:
            packet = b'X' * packet_size
            interval = 1.0 / rate
            end_time = time.time() + duration

            while self.running and time.time() < end_time:
                start_time = time.time()

                # Send packet
                self.socket.sendto(packet, (target_ip, target_port))

                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)

        except Exception as e:
            print(f"Traffic generation error: {str(e)}")
        finally:
            self.stop_generator()

    def _receive_packets(self):
        """Receive UDP packets and count statistics"""
        received = 0
        lost = 0
        sequence = 0
        last_sequence = -1

        try:
            while self.running:
                data, addr = self.socket.recvfrom(65535)
                received += 1

                # Simple sequence number tracking (if included in packet)
                if len(data) >= 4:
                    current_seq = struct.unpack('!I', data[:4])[0]
                    if current_seq != last_sequence + 1:
                        lost += (current_seq - last_sequence - 1)
                    last_sequence = current_seq

        except Exception as e:
            print(f"Receiver error: {str(e)}")

    def stop_generator(self):
        """Stop UDP generator"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
