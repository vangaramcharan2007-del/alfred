package nexus.realtime;

import nexus.common.EventBus;
import nexus.common.NexusEvent;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class WindowsMediaHook {
    private String lastSong = "";

    public void start() {
        new Thread(() -> {
            while (true) {
                try {
                    ProcessBuilder pb = new ProcessBuilder("powershell.exe", "-Command", 
                        "[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media, ContentType = WindowsRuntime] | Out-Null; $m = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync().GetAwaiter().GetResult(); $s = $m.GetCurrentSession(); if ($s) { $i = $s.TryGetMediaPropertiesAsync().GetAwaiter().GetResult(); Write-Output ($i.Title + ' - ' + $i.Artist) }");
                    
                    Process process = pb.start();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String outputStr = reader.readLine();
                    
                    if (outputStr != null && !outputStr.trim().isEmpty() && !outputStr.equals(lastSong)) {
                        lastSong = outputStr;
                        EventBus.getInstance().publish(new NexusEvent("OS_MEDIA_PLAYING", outputStr, "RealTime"));
                    }
                    
                    Thread.sleep(5000);
                } catch (Exception e) {
                    e.printStackTrace();
                    try {
                        Thread.sleep(5000);
                    } catch (InterruptedException ie) {
                        break;
                    }
                }
            }
        }).start();
    }
}
