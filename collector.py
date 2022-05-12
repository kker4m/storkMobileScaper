from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from typing import List
import time
from plan import Plan
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import warnings
import itertools
import json
from tqdm import tqdm

class Collector(ABC):
    """
    A collector is responsible for interfacing with external websites, retrieving plans and normalizing them.
    """

    def get(self, url: str, load_as_json: bool = True):
        """
        Make a GET request to a given url.
        This will raise an exception if the response code is >= 400
        """
        response = requests.get(url)
        response.raise_for_status()
        return response.json() if load_as_json else response.content

    @abstractmethod
    def collect(self) -> List[Plan]:
        """
        The main entry point for a collector-
        Collect all esim plans
        """
        r = requests.get(self.url)
        pass


