import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}

        headers = {'user-agent': 'jxyuan@uci.edu'}
        r = requests.get(self.fileurl, headers=headers)
        
        self.filejson = r.json()

        self.cik_json_to_dict()
    
    def cik_json_to_dict(self):
        self.namedict = {}
        self.tickerdict = {}

        for company in self.filejson.values():
            cik = str(company['cik_str']).zfill(10)
            ticker = company['ticker']
            title = company['title']

            self.namedict[title.lower()] = (cik, ticker, title)
            self.tickerdict[ticker.lower()] = (cik, ticker, title)
    
    def name_to_cik(self, name):
        return self.namedict.get(name.lower())

    def ticker_to_cik(self, ticker):
        return self.tickerdict.get(ticker.lower())

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
print(se.ticker_to_cik('AAPL'))
print(se.name_to_cik('Apple Inc.'))
