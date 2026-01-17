
Write-Host ">>> Initializing Git Repo..."
if (!(Test-Path .git)) {
    git init
}

Write-Host ">>> Configuring Remote..."
git remote remove origin
git remote add origin https://github.com/sungbada123-web/geo.git

Write-Host ">>> Adding Files..."
git add .

Write-Host ">>> Committing..."
git commit -m "Auto update content"

Write-Host ">>> Pushing to GitHub..."
git branch -M main
git push -u origin main

Write-Host ">>> Sync Complete!"
