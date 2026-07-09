import yaml
import os
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.config_dir = 'data/configs'
        os.makedirs(self.config_dir, exist_ok=True)

        # Default configurations
        self.default_srt_config = {
            'mode': 'caller',
            'ingress_ip': '0.0.0.0',
            'ingress_port': 9000,
            'egress_ip': '127.0.0.1',
            'egress_port': 9001,
            'buffer_size': 8192,
            'latency': 120,
            'payload_size': 1316,
            'srt_enabled': True
        }

        self.default_iperf_config = {
            'mode': 'client',
            'server_address': '127.0.0.1',
            'port': 5201,
            'protocol': 'tcp',
            'bandwidth': '10M',
            'duration': 10,
            'parallel': 1,
            'size': 1460,
            'iperf_enabled': False
        }

    def save_srt_config(self, config):
        """Save SRT configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config_dir, f'srt_config_{timestamp}.yaml')
        with open(filename, 'w') as f:
            yaml.dump(config, f)
        return filename

    def save_iperf_config(self, config):
        """Save Iperf configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config_dir, f'iperf_config_{timestamp}.yaml')
        with open(filename, 'w') as f:
            yaml.dump(config, f)
        return filename

    def get_srt_config(self):
        """Get SRT configuration"""
        # In a real app, load from file or database
        return self.default_srt_config

    def get_iperf_config(self):
        """Get Iperf configuration"""
        # In a real app, load from file or database
        return self.default_iperf_config
