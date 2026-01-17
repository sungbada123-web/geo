$RepoDir = "G:\我的云端硬盘\AI+项目\GEO"
$TargetDir = "G:\我的云端硬盘\AI+项目\GEO\发布日报"

Write-Host ">>> 正在连接云端获取日报..."
Set-Location $RepoDir

# 1. 拉取最新数据
git pull

# 2. 检查是否有新报告
if (Test-Path "$RepoDir\GEO_Reports") {
    # 复制 md 和 png 到目标文件夹
    Copy-Item -Path "$RepoDir\GEO_Reports\*.md" -Destination $TargetDir -Force
    Copy-Item -Path "$RepoDir\GEO_Reports\*.png" -Destination $TargetDir -Force
    
    Write-Host "--------------------------------------------------"
    Write-Host "✅ 日报已更新！"
    Write-Host "📂 请查看: $TargetDir"
    Write-Host "--------------------------------------------------"
}
else {
    Write-Host "⚠️ 暂无日报文件 (可能是云端还没发布，或者还没推送到 GitHub)"
}

# 自动打开文件夹 (可选，如果是后台运行则不需要)
# Invoke-Item $TargetDir

Write-Host "✅ 同步完成"

