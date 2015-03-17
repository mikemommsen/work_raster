
org = getOrg()

class Order(object):
  """"""
  
  def __init__(self, orderNum):
    """"""
    pass
  
  @classmethod
  def loadFromTrello(orderNum):
    """"""
    # one idea would be to save this information when making cards
    # this would allow functions to work on these newly created objects
    # and also on the database based ones if we saved the information from makeTrelloCards
    # we could also store the p1data and iOrder data as a json file as an attachment on the master Card
    masterboard = getBoard('Mastercards by day')
    cards = masterboard.all_cards()
    matchCards = [x for x in cards if x.name[:len(orderNum)] == orderNum]
    if not matchCards:
      print 'there was no match for {}'.format(orderNum)
    if len(matchCards) != 1:
      print 'there was more than one card for (). thats fucked up'.format(orderNum)
    masterCard = matchCards[0]
    masterCard.fetch()
    checklists = masterCard.checklists
    if not checklists:
      print 'master card has no checklist. order number: {}. .format(orderNum)
    checklist = checklists[0]
    childCards = []
    for item in checklist:
      name = item.name
      start = name.index('[')
      end = name.index(']') - 1
      url = item.name[start:end]
      json = requests.request('GET', url + '.json')
      card = trello.Card.from_json(json)
      childCards.append(card)
      
      
      
