import requests
from datetime import datetime

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}

        self.headers = {'user-agent': 'jxyuan@uci.edu'}
        r = requests.get(self.fileurl, headers=self.headers)
        
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

    def annual_filing(self, cik, year):
        response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=self.headers)
        data = response.json()
        
        dates = data['filings']['recent']['filingDate']
        form = data['filings']['recent']['form']
        for i, date in enumerate(dates):
            if form[i] == '10-K':
                filing_date_year = dates[i].split('-')[0]
                if str(year) == filing_date_year:
                    accessionNumber = data['filings']['recent']['accessionNumber'][i]
                    primaryDocument = data['filings']['recent']['primaryDocument'][i]

                    return {
                        "date": date,
                        "accessionNumber": accessionNumber.replace("-", ""),
                        "primaryDocument": primaryDocument,
                        "cik": cik
                    }
        print(f"No 10-K filing found for {year}")
        return {}
    
    

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
print(se.annual_filing('0000320193', 2020))
print(se.quarterly_filing('0000320193', 2020, "Q2"))
print(se.name_to_cik('Apple Inc.'))
