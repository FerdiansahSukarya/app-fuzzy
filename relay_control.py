import subprocess
import signal

class RelayControl:
    def __init__(self):
        self.process = None

    def start_relay(self):
        if self.process is None or self.process.poll() is not None:
            # Jalankan relay.py sebagai proses baru
            self.process = subprocess.Popen(['python3', 'relay.py'])
            return True
        else:
            # Relay sudah berjalan
            return False

    def stop_relay(self):
        if self.process and self.process.poll() is None:
            # Hentikan proses relay.py dengan sinyal SIGINT
            self.process.send_signal(signal.SIGINT)
            self.process.wait()
            self.process = None
            return True
        else:
            # Relay sudah tidak berjalan
            return False

    def is_running(self):
        return self.process is not None and self.process.poll() is None


# Test manual (optional)
if __name__ == '__main__':
    rc = RelayControl()
    rc.start_relay()
    input("Tekan Enter untuk stop relay...")
    rc.stop_relay()
