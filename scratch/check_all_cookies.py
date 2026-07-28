import browser_cookie3

def extract():
    browsers = [
        ('Chrome', browser_cookie3.chrome),
        ('Opera', browser_cookie3.opera),
        ('Opera GX', browser_cookie3.opera_gx),
        ('Edge', browser_cookie3.edge),
        ('Firefox', browser_cookie3.firefox)
    ]
    
    for name, func in browsers:
        try:
            cj = func(domain_name='swayam.gov.in')
            cookies = list(cj)
            print(f"[Alfred]: {name} - Extracted {len(cookies)} cookies for swayam.gov.in")
            if len(cookies) > 0:
                print(f"[Alfred]: Success! Found cookies in {name}.")
        except Exception as e:
            print(f"[Alfred]: {name} - Failed: {e}")

if __name__ == "__main__":
    extract()
