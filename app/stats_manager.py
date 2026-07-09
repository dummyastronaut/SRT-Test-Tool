import time
from datetime import datetime

class StatsManager:
    def __init__(self):
        self.srt_stats_history = []
        self.iperf_stats_history = []
        self.udp_stats_history = []

    def update_srt_stats(self, stats):
        """Update SRT statistics"""
        stats['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.srt_stats_history.append(stats.copy())

        # Keep only last 1000 entries
        if len(self.srt_stats_history) > 1000:
            self.srt_stats_history.pop(0)

    def update_iperf_stats(self, stats):
        """Update Iperf statistics"""
        stats['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.iperf_stats_history.append(stats.copy())

        if len(self.iperf_stats_history) > 1000:
            self.iperf_stats_history.pop(0)

    def update_udp_stats(self, stats):
        """Update UDP statistics"""
        stats['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.udp_stats_history.append(stats.copy())

        if len(self.udp_stats_history) > 1000:
            self.udp_stats_history.pop(0)

    def get_srt_stats(self):
        """Get latest SRT statistics"""
        if self.srt_stats_history:
            return self.srt_stats_history[-1]
        return {
            'timestamp': None,
            'throughput': 0,
            'packet_loss': 0,
            'retransmits': 0,
            'latency': 0,
            'dropped_packets': 0,
            'out_of_order': 0,
            'available_bandwidth': 0
        }

    def get_iperf_stats(self):
        """Get latest Iperf statistics"""
        if self.iperf_stats_history:
            return self.iperf_stats_history[-1]
        return {
            'timestamp': None,
            'sent': 0,
            'received': 0,
            'bandwidth': 0,
            'jitter': 0,
            'lost_packets': 0,
            'total_packets': 0
        }

    def get_all_stats(self):
        """Get all statistics combined"""
        all_stats = []

        # Combine SRT stats
        for stat in self.srt_stats_history:
            all_stats.append({
                **stat,
                'source': 'SRT',
                'metric_type': 'throughput'
            })

        # Combine Iperf stats
        for stat in self.iperf_stats_history:
            all_stats.append({
                **stat,
                'source': 'Iperf',
                'metric_type': 'bandwidth'
            })

        return all_stats
