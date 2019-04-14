from multiprocessing.dummy import Pool as ThreadPool

import requests


def multi_request(urls):
    return ThreadPool().map(requests.get, urls)
