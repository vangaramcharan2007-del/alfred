param([string]$Text = "Hey boss! E-V voice is online and ready!")
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female)
$synth.Rate = 1
$synth.Speak($Text)
