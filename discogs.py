import discogs_client
from time import sleep


class Discogs(object):
    def __init__(self):
        self.client = discogs_client.Client('My App', user_token='VRxFhqqGluzQDDcmnpGgaDnoxQSztozjCBIPedZC')

    def search_release(self, search_term):
        counter = 0
        sleep_seconds = 3
        while True:
            try:
                search_results = self.client.search(search_term, type='release')
                return search_results
            except:
                #sleep 3 seconds and try again
                sleep(sleep_seconds)
                print("I have tried {0} times for {1} seconds".format(counter, sleep_seconds))
                if counter > 5:
                    raise RuntimeError("Cannot get search results after 6 retries!")
