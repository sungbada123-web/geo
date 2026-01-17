import subprocess
import os

key_path = r"g:\我的云端硬盘\AI+项目\GEO\Keys\gcp_vm_key"
if os.path.exists(key_path):
    os.remove(key_path)
if os.path.exists(key_path + ".pub"):
    os.remove(key_path + ".pub")

cmd = [
    "ssh-keygen",
    "-t", "rsa",
    "-b", "4096",
    "-C", "antigravity-local",
    "-f", key_path,
    "-N", ""
]

try:
    subprocess.run(cmd, check=True)
    print("Key generation successful.")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
