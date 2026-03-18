import psutil
import GPUtil
import time
import logging
from prometheus_client import start_http_server, Gauge
import ray
from pathlib import Path
import json
import numpy as np
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.setup_logging()
        self.initialize_metrics()
        self.history = []
        self.anomaly_threshold = 0.95
        ray.init(address='auto', ignore_reinit_error=True)

    def setup_logging(self):
        logging.basicConfig(
            filename='/app/logs/system_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def initialize_metrics(self):
        self.cpu_usage = Gauge('cpu_usage', 'CPU Usage Percentage')
        self.memory_usage = Gauge('memory_usage', 'Memory Usage Percentage')
        self.gpu_usage = Gauge('gpu_usage', 'GPU Usage Percentage')
        self.gpu_memory = Gauge('gpu_memory', 'GPU Memory Usage')
        self.disk_usage = Gauge('disk_usage', 'Disk Usage Percentage')

    def collect_metrics(self):
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'gpu': self.get_gpu_metrics()
        }
        self.history.append(metrics)
        if len(self.history) > 1000:
            self.history.pop(0)
        return metrics

    def get_gpu_metrics(self):
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return {
                    'usage': gpus[0].load * 100,
                    'memory': gpus[0].memoryUtil * 100,
                    'temperature': gpus[0].temperature
                }
        except Exception as e:
            logging.error(f"GPU metrics collection failed: {e}")
        return None

    def detect_anomalies(self, metrics):
        if not self.history:
            return False
        recent_metrics = np.array([m['cpu'] for m in self.history[-50:]])
        mean = np.mean(recent_metrics)
        std = np.std(recent_metrics)
        z_score = abs(metrics['cpu'] - mean) / std
        return z_score > 3

    @ray.remote
    def optimize_resources(self, metrics):
        if metrics['cpu'] > 80:
            self.scale_resources('cpu')
        if metrics.get('gpu', {}).get('memory', 0) > 80:
            self.scale_resources('gpu')

    def scale_resources(self, resource_type):
        config_path = Path('/app/configs/scaling.json')
        try:
            with config_path.open('r+') as f:
                config = json.load(f)
                if resource_type == 'cpu':
                    config['cpu_allocation'] *= 1.2
                elif resource_type == 'gpu':
                    config['gpu_memory_limit'] *= 1.2
                f.seek(0)
                json.dump(config, f)
                f.truncate()
        except Exception as e:
            logging.error(f"Resource scaling failed: {e}")

    def run(self):
        start_http_server(9090)
        logging.info("System monitoring started")
        while True:
            try:
                metrics = self.collect_metrics()
                # Update Prometheus metrics
                self.cpu_usage.set(metrics['cpu'])
                self.memory_usage.set(metrics['memory'])
                self.disk_usage.set(metrics['disk'])
                if metrics.get('gpu'):
                    self.gpu_usage.set(metrics['gpu']['usage'])
                    self.gpu_memory.set(metrics['gpu']['memory'])

                # Anomaly detection
                if self.detect_anomalies(metrics):
                    logging.warning(f"Anomaly detected: {metrics}")
                    ray.get(self.optimize_resources.remote(self, metrics))

                # Save metrics to disk periodically
                if len(self.history) % 100 == 0:
                    self.save_metrics()

                time.sleep(5)
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                time.sleep(10)

    def save_metrics(self):
        metrics_path = Path('/app/logs/metrics.json')
        try:
            with metrics_path.open('w') as f:
                json.dump(self.history, f)
        except Exception as e:
            logging.error(f"Failed to save metrics: {e}")

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
