import subprocess
import requests
import asyncio
import time
import sys
import os
import signal

class AppiumManager:
    def __init__(self):
        self.appium_process = None

    async def start_appium(self):
        try:
            # For Windows, start the process in a new process group so we can kill it reliably.
            # For other OSes, preexec_fn is used for the same purpose.
            creation_flags = 0
            preexec_fn = None

            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                preexec_fn = os.setsid

            # Launch Appium server
            log_path = os.path.join(os.path.expanduser("~"), "Documents", "appium_server.log")
            log_file = open(log_path, "w")
            
            # Note the addition of creationflags/preexec_fn
            self.appium_process = subprocess.Popen(
                ["appium"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                shell=True if sys.platform == "win32" else False,
                creationflags=creation_flags,
                preexec_fn=preexec_fn
            )

            # Wait until server is ready
            server_ready = await self.wait_for_appium_server()
            return server_ready

        except Exception as e:
            print(f"❌ Failed to start Appium server: {e}")
            return False

    async def wait_for_appium_server(self, timeout=60):
        url = "http://127.0.0.1:4723"
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.appium_process and self.appium_process.poll() is not None:
                print("❌ Appium process exited prematurely.")
                return False

            try:
                response = requests.get(f"{url}/status", timeout=2)
                if response.status_code == 200:
                    print("✅ Appium server is running.")
                    return True
            except requests.exceptions.RequestException:
                pass

            await asyncio.sleep(1)

        print("⏱️ Appium server failed to start within timeout.")
        return False

    def stop_appium(self):
        if self.appium_process and self.appium_process.poll() is None:
            print("🛑 Forcefully stopping Appium server and its subprocesses...")
            try:
                if sys.platform == "win32":
                    # Use taskkill on Windows to kill the entire process tree
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.appium_process.pid)],
                        check=True
                    )
                else:
                    # Use os.killpg on Unix-like systems
                    os.killpg(os.getpgid(self.appium_process.pid), signal.SIGTERM)
                
                self.appium_process.wait(timeout=10)
                print("✅ Appium server stopped.")

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, PermissionError, OSError) as e:
                print(f"⚠️ An error occurred while stopping the Appium server, but continuing anyway: {e}")
            finally:
                self.appium_process = None
        else:
            print("Appium server process not found or already stopped.")