import browser_cookie3
import requests

def test_cookies():
    print("[Alfred]: Stealing Chrome cookies for swayam.gov.in...")
    cj = browser_cookie3.chrome(domain_name='swayam.gov.in')
    
    # Try fetching the NPTEL dashboard
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    r = requests.get('https://swayam.gov.in/nc_details/NPTEL', cookies=cj, headers=headers)
    if r.status_code == 200 and 'Sign In' not in r.text: # simplistic check
        print("[Alfred]: Successfully authenticated as user via headless request!")
        print(f"[Alfred]: Title of page: {r.text.split('<title>')[1].split('</title>')[0]}")
    else:
        print("[Error]: Authentication failed. We might need a specific session token.")

if __name__ == '__main__':
    test_cookies()
