#!/usr/bin/python3

from html.parser import HTMLParser
from pprint import pprint
import urllib.request
import datetime
import json

class SantanderHTMLParser(HTMLParser):
  in_sell_rate = False
  in_buy_rate = False
  in_span = False
  sell_rate=""
  buy_rate=""
  label=""
  rates={}

  def handle_starttag(self, tag, attributes):
    if tag == 'span':
      #print("span start")
      self.in_span = True
    if tag == 'div':
      for att,name in attributes:
        if name == 'exchange_office__rate js-exchange_office__rate':
          self.label = attributes[1][1]
          return
        if name == 'exchange_office__table-value js-exchange_office__rate-sell-value':
          self.in_sell_rate = True
          self.sell_rate=""
          return  
        if name == 'exchange_office__table-value js-exchange_office__rate-buy-value':
          self.in_buy_rate = True
          self.buy_rate=""
          return                
  def handle_data(self, data):
    if self.in_sell_rate and self.in_span:
      self.sell_rate = float(data.replace(',','.'))
    if self.in_buy_rate and self.in_span:      
      self.buy_rate = float(data.replace(',','.'))
  def handle_endtag(self, tag):
    if tag == 'span':
      self.in_span = False    
    if tag == 'div':
      if self.label != '':
        self.rates[self.label]={'sell': self.sell_rate, 'buy': self.buy_rate}
      self.in_sell_rate = False
      self.in_buy_rate = False

def send_notification(currency, rate):
  with open('/home/ubuntu/currency-tools/api_key.txt') as keyfile:
    api_key = keyfile.read()
  body = {"value1":currency,"value2": rate }
  url = 'https://maker.ifttt.com/trigger/currency/with/key/{}'.format(api_key)
  req = urllib.request.Request(url)
  req.add_header('Content-Type', 'application/json; charset=utf-8')
  jsondata = json.dumps(body)
  jsondataasbytes = jsondata.encode('utf-8')
  req.add_header('Content-Length', len(jsondataasbytes))
  response = urllib.request.urlopen(req, jsondataasbytes)


## MAIN ##
with open('/home/ubuntu/currency-tools/alerts.json') as alerts_file:
  alerts = json.load(alerts_file)
parser = SantanderHTMLParser()
with urllib.request.urlopen('https://www.santander.pl/klient-indywidualny/karty-platnosci-i-kantor/kantor-santander') as r:
  html = str(r.read())
parser.feed(html)
timestamp = datetime.datetime.now()
for currency in ['USD', 'CHF']:
  rate = "%s / PLN" % currency
  line ="%s;%s;%s\n" % (timestamp.strftime("%Y-%m-%d %H:%M:%S"),parser.rates[rate]['sell'],parser.rates[rate]['buy'])
  fname = "/home/ubuntu/%s-PLN.csv" % currency
  with open(fname,'a+') as f:
    f.write(line)

  if parser.rates[rate]['sell'] > alerts[currency]['sell']:
    send_notification(currency, parser.rates[rate]['sell'])
  if parser.rates[rate]['buy'] < alerts[currency]['buy']:
    send_notification(currency, parser.rates[rate]['buy'])
