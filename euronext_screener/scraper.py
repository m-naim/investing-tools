import requests

i=0
def get_peg(ticker):
    ticker= ticker.replace('.PA','')
    url=f'https://www.gurufocus.com/term/peg/xpar:{ticker}/PEG%252BRatio'
    response = requests.get(url)

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    font= soup.find('div', attrs={"id":"def_body_detail_height"}).font
    peg=font.text.split(" ")[1]
    
    print(peg)
    try : 
        return float(peg)
    except:
        return peg