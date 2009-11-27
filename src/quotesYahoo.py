def downloadQuotes(symbol):
	print('Downloading historical data for ' + symbol + '...')
	import http.client
	conn = http.client.HTTPConnection('ichart.finance.yahoo.com')
	
	'''
	Notes on the yahoo parameters:
	d=end month-1 
	e=end day
	f=end year
	g=d?
	a=start month-1 (0 = January)
	b=start day (2)
	c=start year (2002)
	'''
	
	import datetime
	today = datetime.date.today()
	endYear = today.strftime('%Y')
	endMonth = str(int(today.strftime('%m'))-1)
	endDay = today.strftime('%d')
	
	startYear='2002'
	startMonth='0'
	startDay='1'
	
	conn.request('GET', '/table.csv?s=' + symbol + '&d=' + endMonth + '&e=' + endDay + '&f=' + endYear + '&g=d&a=' + startMonth + '&b=' + startDay + '&c=' + startYear + '&ignore=.csvc')
	response=conn.getresponse()
	print(response.status, response.reason)
	data=response.read()
	conn.close()
	if response.status==200 and response.reason=='OK':
		data = data.decode('windows-1252')
		reformatAndSaveQuotes(data, symbol)
		print('Saved historical data for ' + symbol + '.\n')
	else:
		print('Download failed for symbol ' + symbol + '.\n')
		return False
	return True

def reformatAndSaveQuotes(data, symbol):
	quotes=[]
	lines = data.split('\n')
	i=0
	for line in lines:
		if(i>0):
			quotes.append(line)
		i=i+1
	
	# we want the list to go from oldest quote to newest
	quotes.reverse()

	filename='data/yahoo/quotes/' + symbol + '.csv'
	file=open(filename, 'w')
	i=0
	for line in quotes:
		if(i>0):
			file.write(line + '\n')
		i=i+1
	file.close()

def cleanUp():
	import os
	if os.path.exists('data/yahoo/quotes'):
		import shutil
		shutil.rmtree('data/yahoo/quotes')
	os.makedirs('data/yahoo/quotes/')

def downloadAllQuotes():
	cleanUp()
	
	symbolFilename = 'data/symbols/symbols.txt'
	symbolFile = open(symbolFilename, 'r')
	symbols = symbolFile.readlines()
	symbolFile.close()
	
	failedSymbolsFilename = 'data/yahoo/failedQuotesSymbols.txt'
	failedSymbolsFile = open(failedSymbolsFilename, 'w')
	
	while symbols:
		print(str(len(symbols)) + ' symbols remaining.')
		symbol = symbols.pop()
		symbol = symbol.replace('\n','')
		if not downloadQuotes(symbol):
			failedSymbolsFile.write(symbol + '\n')
	
	failedSymbolsFile.close()

#########################################################################
### These are all for loading the dataset once it's been downloaded. ####
#########################################################################

def getAllQuotes():
	symbols=getSymbolsFromQuoteFiles()
	quotes={}
	for symbol in symbols:
		print('Loading symbol ' + symbol + '.')
		quotes[symbol]=getQuotes(symbol)
	return quotes

def getQuotes(symbol):
	inputFilename='data/yahoo/quotes/' + symbol + '.csv'
	inputFile=open(inputFilename, 'r')

	quotes={}
	quotes['Date']=[]
	quotes['Open']=[]
	quotes['High']=[]
	quotes['Low']=[]
	quotes['Close']=[]
	quotes['Volume']=[]
	quotes['AdjClose']=[]
	
	import datetime
	import csv
	reader=csv.reader(inputFile)
	
	for Date, Open, High, Low, Close, Volume, AdjClose in reader:
		dt=Date.split('-')
		Date=datetime.date(int(dt[0]), int(dt[1]), int(dt[2]))
		
		quotes['Date'].append(Date)
		quotes['Open'].append(float(Open))
		quotes['High'].append(float(High))
		quotes['Low'].append(float(Low))
		quotes['Close'].append(float(Close))
		quotes['Volume'].append(int(Volume))
		quotes['AdjClose'].append(float(AdjClose))
	
	inputFile.close()
	return quotes

# returns the index of the quote for the given date for quotes[symbol]
def getIndex(date, quotes):
	try:
		return quotes['Date'].index(date)
	except ValueError:
		return False

# returns False if there is no quote for the currentDate
# otherwise returns the list [0, currentDate)
def getSubquoteForSymbol(symbol, currentDate, quotes):
	index=getIndex(currentDate, quotes[symbol])
	if not index:
		return False
	
	subquote={}
	for item in quotes[symbol]:
		subquote[item]=quotes[symbol][item][0:index]
	return subquote

# returns False if there is no quote for the currentDate
# otherwise returns the list [0, currentDate)
def getSubquote(currentDate, quotes):
	subquote={}
	
	for symbol in quotes:
		index=getIndex(currentDate, quotes[symbol])
		if index:		
			subquote[symbol]={}		
			for item in quotes[symbol]:
				subquote[symbol][item]=quotes[symbol][item][0:index]
	
	if len(subquote)>0:
		return subquote
	
	return False

def getSymbolsFromQuoteFiles():
	dirname='data/yahoo/quotes'
	symbols=[]
	import os
	files=os.listdir(dirname)
	for file in files:
		symbols.append(file.replace('.csv', ''))
	return symbols
