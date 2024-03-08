import random
import re
from time import sleep


class IssueCommentReport(object):
    def __init__(self, id: str):
      self.data: list[dict] = []
      self.id = id

    def fetch_data_with_retries(self, retries=1):
      if retries <= 0:
          raise Exception('out of retries') 
      try:
          self.fetch_data()
      except Exception as e:
          sleep(100 // retries)
          self.fetch_data_with_retries(retries - 1)
    
    def fetch_data(self):
      raise NotImplementedError()

    def matches(self, field, wl=[], bl=[]):
      wl_match = []; bl_match = []
      for comment in self.data:
        for pattern in wl:
          result = re.findall(pattern, str(comment[field]), re.IGNORECASE)
          wl_match.extend((match, pattern) for match in result)
        for pattern in bl:
          result = re.findall(pattern, str(comment[field]), re.IGNORECASE)
          bl_match.extend((match, pattern) for match in result)
      return wl_match, bl_match

    def sample_amount(self, sample_amount: int) -> list:
      n = len(self.data)
      if sample_amount > n:
          raise Exception(f" Requested sample size ({sample_amount}) is larger than report size ({n}).")
      else:
        self.data = random.sample(self.data, round(sample_amount))
        print(f" Sampling Successful: {sample_amount} of {n} Issues Sampled")

    def sample_percentage(self, percent: int, min: int = 20) -> list:
      if 1 < percent > 100:
        raise Exception(" Sample percentage must be between 0 and 100.")
      amt = len(self.data) * percent / 100
      if amt < min:
        print(f" \n WARNING: Clipping sample size to {min} instead of {amt}")
        amt = min
      print(f" Sample {len(amt)} / {len(self.data)} issues")
      self.data = random.sample(self.data, max())
