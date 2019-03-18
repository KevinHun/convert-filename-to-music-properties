import discogs_client


class Discogs(object):
    def __init__(self):
        self.client = discogs_client.Client('My App', user_token='VRxFhqqGluzQDDcmnpGgaDnoxQSztozjCBIPedZC')

    def search_release(self, search_term):
        return self.client.search(search_term, type='release')
