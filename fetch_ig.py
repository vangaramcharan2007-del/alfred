import urllib.request
import re

url = 'https://www.instagram.com/reel/DcQsec-zwoU/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    m1 = re.search(r'<meta property="og:title" content="(.*?)"', html)
    m2 = re.search(r'<meta property="og:description" content="(.*?)"', html)
    print("Title:", m1.group(1) if m1 else "Not found")
    print("Desc:", m2.group(1) if m2 else "Not found")
except Exception as e:
    print("Error:", str(e))
