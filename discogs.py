import discogs_client
from time import sleep


class Discogs(object):
    def __init__(self):
        self.client = discogs_client.Client('My App', user_token='VRxFhqqGluzQDDcmnpGgaDnoxQSztozjCBIPedZC')

    def search_release(self, search_term):
        try:
            search_results = self.client.search(search_term, type='release')
        except:
            #sleep 3 seconds and try again
            sleep(3)
            search_results = self.client.search(search_term, type='release')
        return search_results
