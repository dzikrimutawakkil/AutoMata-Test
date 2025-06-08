import subprocess
import requests
import asyncio
import time

class AppiumManager:
    def __init__(self):
        self.appium_process = None

    async def start_appium(self):
        try:
            # Set execution policy to allow PowerShell scripts to run
            subprocess.run(["powershell", "-Command", "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"], check=True)
            
            # Start Appium server using PowerShell
            self.appium_process = subprocess.Popen(["powershell", "-Command", "appium"], shell=True)
            
            # Wait for Appium server to be ready
            server_ready = await self.wait_for_appium_server()
            return server_ready
        except Exception as e:
            print(f"Failed to start Appium server: {e}")
            return False

    async def wait_for_appium_server(self, timeout=60):
        url = "http://127.0.0.1:4723"
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/status")
                if response.status_code == 200:
                    print("Appium server is running.")
                    return True
            except requests.exceptions.RequestException:
                pass  
            
            await asyncio.sleep(1)
        print("Appium server failed to start within the timeout period.")
        return False

    def stop_appium(self):
        if self.appium_process:
            self.appium_process.terminate()
            self.appium_process.wait()
            print("Appium server stopped.")
