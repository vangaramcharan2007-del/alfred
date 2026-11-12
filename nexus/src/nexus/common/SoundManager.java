package nexus.common;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.SourceDataLine;

public class SoundManager implements NexusListener {

    public SoundManager() {
        EventBus.getInstance().subscribe("TASK_COMPLETED", this);
        EventBus.getInstance().subscribe("PRODUCT_PURCHASED", this);
        EventBus.getInstance().subscribe("ERROR", this);
    }

    @Override
    public void onEvent(NexusEvent event) {
        new Thread(() -> {
            if ("TASK_COMPLETED".equals(event.getType())) {
                playTone(1000, 150, 0.5); // High pitch ping
            } else if ("PRODUCT_PURCHASED".equals(event.getType())) {
                playTone(600, 100, 0.5); // Cash register-like beep 1
                try { Thread.sleep(50); } catch (InterruptedException e) {}
                playTone(800, 150, 0.5); // Cash register-like beep 2
            } else if ("ERROR".equals(event.getType())) {
                playTone(200, 300, 0.5); // Low thud
            }
        }).start();
    }

    private void playTone(int frequency, int durationMs, double vol) {
        try {
            float sampleRate = 44100f;
            AudioFormat format = new AudioFormat(sampleRate, 8, 1, true, false);
            SourceDataLine line = AudioSystem.getSourceDataLine(format);
            line.open(format);
            line.start();

            byte[] buf = new byte[durationMs * 44100 / 1000];
            for (int i = 0; i < buf.length; i++) {
                double angle = i / (sampleRate / frequency) * 2.0 * Math.PI;
                buf[i] = (byte) (Math.sin(angle) * 127.0 * vol);
            }
            
            line.write(buf, 0, buf.length);
            line.drain();
            line.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
