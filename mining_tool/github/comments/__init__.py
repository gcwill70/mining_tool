import os
import random
import re

from github import Github
from mining_tool.base.comments import IssueCommentReport
from mining_tool.utils import conform

DEFAULT_FIELDS = ['html_url', 'created_at', 'updated_at', 'login', 'author_association', 'body']

class GitHubIssueCommentReport(IssueCommentReport):
    def __init__(self, id: int, gh: str):
      super().__init__(id)
      matches = re.findall(r'^(\w*)/(\w*)$', gh)
      self.owner = matches[0][0]
      self.name = matches[0][1]
    
    def fetch_data(self, fields = DEFAULT_FIELDS):
      self.gh = Github(os.getenv('GH_PRIVATE_KEY')).get_repo(f"{self.owner}/{self.name}")
      self.__fetch_issuebody__(fields)
      self.__fetch_comments__(fields)

    def __fetch_issuebody__(self, fields):
      # get issue
      issue = self.gh.get_issue(self.id)
      # assign login (so it is the same format as issue comments)
      issue.raw_data['login'] = issue.raw_data['user']['login']
      # add issue title to data
      self.data.append(conform({**issue.raw_data, 'body': issue.raw_data['title']}, fields))
      # add issue body to data
      self.data.append(conform(issue.raw_data.copy(), fields))

    def __fetch_comments__(self, fields):
      # get comments list for issue
      comments = self.gh.get_issue(self.id).get_comments()
      # create indices
      remaining = comments.totalCount; page_num = 0
      while remaining > 0:
        # get next page
        page = comments.get_page(page_num)
        for entry in page:
          entry.raw_data['login'] = entry.raw_data['user']['login']
          self.data.append(conform(entry.raw_data.copy(), fields))
        # update indeces
        remaining -= len(page)
        page_num += 1