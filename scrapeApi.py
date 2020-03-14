import flask
from urllib.request import urlopen
from bs4 import BeautifulSoup
from json import dumps
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def scrape(url):
    try:
       # query the website and return the html to the variable ‘page’
        page = urlopen(url)
    except urllib.error.URLError as e:
         print(e.reason)
    return page     

def flatten(listToFlatten):
        flat_list = []
        for sublist in listToFlatten:
            for item in sublist:
                flat_list.append(item)
        return flat_list

def cleanValue(value):
    #remove unwanted values in []
    indexOfStart = value.find('[')
    return value[0:indexOfStart:] + value[len(value)::]

@app.route('/api/v1/coronavirus/stats', methods=['GET'])
def statesCoronoVirusStatsReportedCases():
    quote_page = 'https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html'

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(scrape(quote_page), 'html.parser')

    # get the table information
    div = soup.find('div', attrs={'class':'table-responsive'})
    table_body = div.find('tbody')
    rows = table_body.find_all('tr')
    listOfStats = []
    dictOfStats = {}
    for row in rows:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]
        listOfStats.append(cols)
        
    #key = first value in the list Value= Third value in list
    dictOfStats = {each[0]: each[2] for each in listOfStats}
    return jsonify(dictOfStats)    
        
@app.route('/api/v1/coronavirus/stats/wiki', methods=['GET'])
def statesCoronoVirusStatsRecoveredAndDead():
    quote_page = 'https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Canada'      


    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(scrape(quote_page), 'html.parser')
    div = soup.find('div', attrs={'class':'mw-parser-output'})
    table = div.find('table', attrs={'class':'infobox'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    listOfTitlesFromInfoBox = []
    listOfValuesFromInfoBox = []
    for row in rows:
        colsTd=row.find_all('td')
        colsTd=[x.text.strip() for x in colsTd]
        listOfValuesFromInfoBox.append(colsTd)
        colsTh=row.find_all('th')
        colsTh=[x.text.strip() for x in colsTh]
        listOfTitlesFromInfoBox.append(colsTh)

    #delete first value in the list
    del listOfValuesFromInfoBox[0]

    #using zip merge lists and convert them to dictionary        
    dictOfAllStats = {k:v for k,v in zip(flatten(listOfTitlesFromInfoBox),flatten(listOfValuesFromInfoBox))}
    
    dictOfDeathAndRecovered = {}
    for key, value in dictOfAllStats.items():
        if key=='Deaths':
            dictOfDeathAndRecovered[key]=cleanValue(value)
        elif key == 'Recovered':
            dictOfDeathAndRecovered[key]=cleanValue(value)
    return jsonify(dictOfDeathAndRecovered) 

if __name__ == "__main__":
    app.run()
