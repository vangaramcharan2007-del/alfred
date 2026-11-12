Set-Location "C:\Users\vanga\Desktop\NEXUS_Java_V7_Startup_Edition"
$javaFiles = Get-ChildItem -Path "src" -Filter "*.java" -Recurse | Select-Object -ExpandProperty FullName
$javaFiles | Out-File -Encoding ascii "sources.txt"
$cp = "lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar;bin"
& javac -cp $cp -d bin "@sources.txt"
$res = $LASTEXITCODE
if (Test-Path "sources.txt") { Remove-Item "sources.txt" }
if ($res -eq 0) {
    Write-Host ">>> NEXUS BUILD SUCCESSFUL <<<"
} else {
    Write-Host ">>> NEXUS BUILD FAILED WITH CODE $res <<<"
}
exit $res
