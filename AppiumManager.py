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
            # Allow PowerShell scripts (Windows only)
            if sys.platform == "win32":
                subprocess.run([
                    "powershell", 
                    "-Command", 
                    "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
                ], check=True)

            # Launch Appium server (log output to file for debugging)
            log_file = open("appium_server.log", "w")
            self.appium_process = subprocess.Popen(
                ["appium"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                shell=True if sys.platform == "win32" else False
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
            try:
                self.appium_process.terminate()
                self.appium_process.wait(timeout=10)
                print("🛑 Appium server stopped.")
            except subprocess.TimeoutExpired:
                print("⚠️ Timeout expired, but skipping kill() for now...")
            finally:
                self.appium_process = None

