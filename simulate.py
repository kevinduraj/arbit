import cPickle

def main():
	import datetime
	startDate=datetime.date(2007,1,1)
	endDate=datetime.date(2008,1,1)

	import data
	symbols=data.getSymbols()
	quotes=data.getAllQuotes()

	c=25000
	wins=0
	total=0
	
	for day in range(0, (endDate-startDate).days):
		currentDate=startDate+datetime.timedelta(days=day)

		best_p_vgood=0
		best_symbol=''

		for symbol in symbols:
			filename=str(currentDate) + symbol
			f = open('data/queue/response/' + filename, 'r')
			response=cPickle.load(f)
			p=response['p']

			if p and p['Good']>best_p_vgood:
				# only pick a symbol that we have test data for
				if data.getIndex(currentDate, quotes[symbol]):
					best_p_vgood=p['Good']
					best_symbol=symbol

		# see how we did for today
		if best_symbol:
			index=data.getIndex(currentDate, quotes[best_symbol])

			Open=quotes[best_symbol]['Open'][index]
			Close=quotes[best_symbol]['Close'][index]
			High=quotes[best_symbol]['High'][index]
		
			if High>Open*1.02:
				c=c*1.02
				wins=wins+1
			else:
				c=c*(Close/Open)
			total=total+1
		
			pwin=float(wins)/total
			print str(currentDate) + '\t' \
			+ str(round(c)) +  '\t' \
			+ best_symbol +  '\t' \
			+ str(round(best_p_vgood,5)) + '\t' \
			+ str(round(pwin,5)) + '\t'
main()