import os
import time
import re
from openpyxl import Workbook
import pywinauto

# Try to use the same TTS engine
try:
    import sys
    sys.path.insert(0, os.path.abspath("src"))
    from jarvisx.core.voice.tts_engine import TTSEngine
    tts = TTSEngine()
    def speak(text):
        print(f"[Alfred] {text}")
        tts.speak(text)
except:
    def speak(text):
        print(f"[Alfred] {text}")

def text_to_table_2023(raw_text):
    lines = raw_text.strip().split('\n')
    table = [["Sl. No", "Name of the AE", "DOB", "Present place of working", "Date of conversion as AE", "Date of commencement of probation"]]
    for line in lines:
        match = re.match(r'^(\d+)\s+([A-Za-z\.\s]+)\s+(\d{2}[\.\-]\d{2}[\.\-]\d{4})\s+(.+?)\s+(\d{2}[\.\-]\d{2}[\.\-]\d{4}\s+FN)\s+(\d{2}[\.\-]\d{2}[\.\-]\d{4}\s+FN)$', line.strip())
        if match:
            table.append(list(match.groups()))
    return table

def text_to_table_2025(raw_text):
    lines = raw_text.strip().split('\n')
    table = [["Sl.No.", "Name of the AE", "DOB", "Place of Working"]]
    for line in lines:
        match = re.match(r'^(\d+)\s+([A-Za-z\.\s]+)\s+(\d{2}[\.\-]\d{2}[\.\-]\d{2,4})\s+(.+)$', line.strip())
        if match:
            table.append(list(match.groups()))
    return table

def create_excel(table, filepath):
    wb = Workbook()
    ws = wb.active
    for row in table:
        ws.append(row)
    wb.save(filepath)

def run_automation():
    speak("Yes sir. I am extracting the tables from the provided PDF memos and converting them into Excel workbooks.")
    
    out_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_WhatsApp_Automation", "Outbox")
    os.makedirs(out_dir, exist_ok=True)
    
    # 2023 Memo Data
    data_2023 = """
1 G. Surender 10.04.1967 AE/Distn./Mamnoor 18.03.2012 FN 02.11.2010 FN
2 G. Nagaraju 02.04.1975 AE/I.TICorp. Office Warangal 05-08-2014 FN 04.01.2012 FN
3 K. Venkateshwara Rao 15.04.1972 AE/DPE/Kothagudem 16.12.2015 FN 16.12.2015 FN
4 G. Ramesh 10.05.1977 AE/Opn./Damera 17-12-2015 FN 17.12.2015 FN
5 G. Padma 25.01.1985 AE/C&O/Sircilla 09-12-2015 FN 09-12-2015 FN
6 Ch. Sridhar 08.01.1980 AE/Prot./Khammam 07.12.2015 FN 07.12.2015 FN
7 B. Anjaneyulu 14.08.1983 AE/Comml/DO/Huzurabad 09-12-2015 FN 09-12-2015 FN
8 Fasih Ahmed 27.05.1980 AE/Op/Manakondur 09.12.2015 FN 09.12.2015 FN
9 D. Srinivas 21.08.1974 AE/Op/D-I/Nizamabad 09.12.2015 FN 09.12.2015 FN
10 D. Srinivas 07.08.1980 AE/Op/T. 8/Karimnagar 09.12.2015 FN 09.12.2015 FN
11 K. Aravind Reddy 29.10.1976 AE/Op/Nustulapur 09-12-2015 FN 09-12-2015 FN
12 K.Viswa Prasad 06.10.1968 AE/Opn./Parkal Rural 09.12.2015 FN 09.12.2015 FN
13 K.Chandra Shekar 10.04.1979 AE/Tech/DO/Jagtial 09-12-2015 FN 09-12-2015 FN
14 Vanga Ravinder 09.04.1978 AE/Comml/DOWarangal 09.12.2015 FN 09.12.2015 FN
15 A. Venkat Reddy 01.09.1973 AE/SPMIJagtial 09-12-2015 FN 09-12-2015 FN
16 M. Anil kumar 10.05.1980 AE/Const/Hanumakonda Rural 07.12.2015 FN 07.12.2015 FN
17 P. Srinivas 15.07.1981 AE/Op/Pegadapally 09.12.2015 FN 09.12.2015 FN
18 Lakavath Savai 15.10.1979 AE/Op/Achampally 10-12-2015 FN 10-12-2015 FN
19 B. Srinivas 03.07.1975 AE/Op/Jannepally 08.12.2015 FN 08.12.2015 FN
20 T. Ram Mohan 05.04.1979 AE/Op/T 6/Karimnagar 09.05.2016 FN 09.05.2016 FN
21 Gudelli Srinivas 02.06.1980 AE/TRE/Karimnagar 09.05.2016 FN 09.05.2016 FN
22 Nasreen Sulthana 19.08.1982 AE/Tech/DOWarangal 06.05.2016 FN 06.05.2016 FN
23 A. Rajesh 25.08.1984 AE/Op'Thallada 05.05.2016 FN 05.05.2016 FN
24 K. Purna Chander 20.03.1979 AE/Comml/Corp. OfficeWGL 06.05.2016 FN 06.05.2016 FN
25 S. Murali Krishna 20.06.1981 AE/Distn./Kazipet 11.05.2016 FN 11.05.2016 FN
26 V. Shivaprasad 12.06.1979 AE/Op/Kallur 11.05.2016 FN 11.05.2016 FN
27 A. Muneender Reddy 06.08.1975 AE/Op/Chilavakodur 30-05-2017 FN 21.11.2016 FN
28 G. Sailoo 08.01.1982 AE/Op/Dichpally 07-11-2017 FN 23.11.2016 FN
"""
    # 2025 Memo Data
    data_2025 = """
1 R. Ramesh Khanna 15-05-66 AE/Projects/Corporate Office
2 M. Ramya 29.12.1983 AE(lT)/Corporate Ofiice
3 K. Swarnalatha 23.07.1982 AE/Techl./CO/Bupalpally
4 M.Ramulu Naik 26-09-71 AE/T/DO/Mahabubabad
5 M. Mallikarjun Rao 10.05.1975 AE/DPE/Mahabubabad
6 l. Irlallaiah 15.06.1987 AE/Enquiries/Corpoarte Office
7 B. Bhavageethika 13.05.1989 AE(Deputed to TSPCC)
8 B. Sandhya Rani 23.03.1985 AE(Deputed to TSPCC)
9 Ch. Radhika 22.03.1980 AE(Tech.)/D.O./T/ Hanamkonda(R)
10 J. Srujana 19.06.1985 AE[l.]/Corp. Office^/Varangal
11 D. Rajin Kumar 17.12.1987 AE/Distn./ Station Road
12 h/. Madhusudhan 18.02.1983 AE/OP/Sangem
13 K. Rishma 11.07.1981 AE/Tech/DO/Warangal
14 P.Sudhakar 17.10.1977 AE/OP/Narmetta
15 G. Laxminarayana 22.05.1978 AE/OP/Rajavaram
16 V. Venu Kumar 04-06-1979 Ex: AE/Opn.Thadwai
17 Burra Srinivas 03-06-1981 Ex: AE/Op/Manakondur
18 K. Sreenivas 03.06.1975 AE/Operation Section, Challur
19 Thotha IVlallesham 01.07.1976 AE-'l/DPE-lliPeddaPllY
20 K. Gopinath 28.08.1980 AEffech., Division Offae, Town
21 K. Mallaih 09.10.1976 AE/Operation Seclion' Alugunur
22 M. Veera Chary 10-04-1969 AE/Operation Section, Alugunur
23 Habeebunneesa 06.05.1985 AE/lndoor, District Stores
"""

    table1 = text_to_table_2023(data_2023)
    table2 = text_to_table_2025(data_2025)
    
    file1 = os.path.join(out_dir, "Memo_17_01_2023_Converted.xlsx")
    file2 = os.path.join(out_dir, "Memo_27_03_2025_Converted.xlsx")
    
    create_excel(table1, file1)
    create_excel(table2, file2)
    
    time.sleep(1)
    speak("Conversion complete. Opening the Excel workbooks for your review.")
    
    os.startfile(file1)
    time.sleep(1.5)
    os.startfile(file2)
    time.sleep(2)
    
    speak("Sending the converted files back to WhatsApp.")
    
    # Try to automate WhatsApp
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=".*WhatsApp.*", timeout=2)
        window = app.window(title_re=".*WhatsApp.*")
        window.set_focus()
        time.sleep(0.5)
        
        # Select chat (assuming search box works or we are in the chat)
        window.type_keys("^f")
        time.sleep(0.5)
        window.type_keys("Dad{ENTER}")
        time.sleep(1.0)
        
        import subprocess
        # Copy file 1 to clipboard
        cmd = f'powershell.exe -command "Set-Clipboard -Path \'{file1}\'"'
        subprocess.run(cmd, shell=True)
        time.sleep(0.5)
        window.type_keys("^v")
        time.sleep(1.0)
        window.type_keys("{ENTER}")
        time.sleep(1.0)
        
        # Copy file 2 to clipboard
        cmd = f'powershell.exe -command "Set-Clipboard -Path \'{file2}\'"'
        subprocess.run(cmd, shell=True)
        time.sleep(0.5)
        window.type_keys("^v")
        time.sleep(1.0)
        window.type_keys("{ENTER}")
        
        speak("I have successfully delivered the converted Excel workbooks back to the chat.")
    except Exception as e:
        speak("I could not automate WhatsApp, but the files have been successfully converted and saved in the Outbox.")
        print(f"WhatsApp UI error: {e}")

if __name__ == "__main__":
    run_automation()
