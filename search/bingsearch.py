from pybing import Bing


if __name__ == '__main__':
    bing = Bing('335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC')
    response = bing.search_web('python bing')
    results = response['SearchResponse']['Web']['Results']
    print len(results)
