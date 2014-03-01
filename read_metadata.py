#mike mommsen
import sys
from bs4 import BeautifulSoup

def readMetdata(url):
    f = urllib2.urlopen(url)
    content = f.read()
    soup = BeautifulSoup(content)
    for row in soup('table')[4].findAll('tr'):
        tds = row('td')
        print tds


def main():
    url = sys.argv[1]
    outpath = sys.argv[2]
    

if __name__ == '__main__':
    main()
  
