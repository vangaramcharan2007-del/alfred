import asyncio
import pyttsx3

async def main():
    print('=============================================')
    print('  FRIDAY ACADEMIC TUTOR (VOICE ENABLED)      ')
    print('=============================================')
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
            
    engine.setProperty('rate', 160)

    def speak(text):
        print(f'\n[Friday Voice]: {text}')
        engine.say(text)
        engine.runAndWait()

    print('[*] Calibrating Tutor Mode according to schedule...')
    speak('Good evening. I have synchronized with your timetable. Activating Tutor Mode for Transforms, Advanced Object-Oriented Programming, and Data Structures.')
    
    lesson = '''Let's connect today's subjects.
First, a Fourier Transform converts a signal from time to frequency.
Second, in Python, you can build a Transform class using Advanced Object-Oriented Programming. This class will encapsulate the mathematical methods and state.
Third, to process a huge signal quickly, you would store the frequency data in a contiguous Array or hash map Data Structure for immediate O(1) lookups.
Math defines the logic, OOP structures it, and DSA optimizes it!'''

    print('\n[*] Processing curriculum via Alfred -> Friday...')
    
    # Simulate LLM response time
    await asyncio.sleep(2)
    
    speak(lesson)
    
    print('\n[*] Tutor session complete.')

if __name__ == '__main__':
    asyncio.run(main())
