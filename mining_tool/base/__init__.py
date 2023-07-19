import random
import re
from time import sleep

class IssueReport(object):
    def __init__(self):
      self.data: list[dict] = None

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

    def filter_by_field(self, field, wl=[], bl=[]):
      report_copy = self.data.copy()
      for issue in self.data:
        whitelisted = any(re.search(pattern, issue[field], re.IGNORECASE) != None for pattern in wl)
        blacklisted = any(re.search(pattern, issue[field], re.IGNORECASE) != None for pattern in bl)
        if blacklisted and not whitelisted:
          report_copy.remove(issue)
      self.data = report_copy.copy()

    def filter_by_state(self, state):
      report_copy = self.data.copy()
      for issue in self.data:
        filtered = True
        if "OPEN" in state and issue['closed at'] == 'None':
          filtered = False
        if "CLOSED" in state and issue['closed at'] != 'None':
          filtered = False
        if filtered:
          report_copy.remove(issue)
      self.data = report_copy.copy()

    def filter_by_comments(self, min_comments = 0):
      report_copy = self.data.copy()
      for issue in self.data:
          if int(issue['comments']) < min_comments:
              report_copy.remove(issue)
      self.data = report_copy.copy()

    def sample_report_amount(self, sample_amount: int) -> list:
      n = len(self.data)
      if sample_amount > n:
          raise Exception(f" Requested sample size ({sample_amount}) is larger than report size ({n}).")
      else:
        self.data = random.sample(self.data, round(sample_amount))
        print(f" Sampling Successful: {sample_amount} of {n} Issues Sampled")

    def sample_report_percent(self, percent: int, min: int = 20) -> list:
      if 1 < percent > 100:
        raise Exception(" Sample percentage must be between 0 and 100.")
      amt = len(self.data) * percent / 100
      if amt < min:
        print(f" \n WARNING: Clipping sample size to {min} instead of {amt}")
        amt = min
      print(f" Sample {len(amt)} / {len(self.data)} issues")
      self.data = random.sample(self.data, max())
