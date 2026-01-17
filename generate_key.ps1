$KeyPath = "g:\我的云端硬盘\AI+项目\GEO\Keys\gcp_vm_key"
if (Test-Path $KeyPath) { Remove-Item $KeyPath }
if (Test-Path "$KeyPath.pub") { Remove-Item "$KeyPath.pub" }

ssh-keygen -t rsa -b 4096 -C "antigravity-local" -f $KeyPath -N ""
