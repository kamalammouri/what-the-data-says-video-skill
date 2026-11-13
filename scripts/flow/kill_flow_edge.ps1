# Closes the Flow Edge window (profile flow-profile*) and its browser.mjs launcher; never the user's own Edge, never shells.
Get-CimInstance Win32_Process | Where-Object {
  ($_.Name -eq 'node.exe' -and $_.CommandLine -match 'browser\.mjs') -or ($_.Name -eq 'msedge.exe' -and $_.CommandLine -match 'flow-profile')
} | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }
