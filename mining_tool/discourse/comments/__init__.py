import os

import requests
from mining_tool.base.comments import IssueCommentReport
from mining_tool.utils import conform, transform
from pydiscourse import DiscourseClient
from bs4 import BeautifulSoup

MAPPING = {
  'html_url': 'html_url',
  'username': 'login',
  'author_association': 'author_association',
  'cooked': 'body',
}

class DiscourseIssueCommentReport(IssueCommentReport):
    def __init__(self, id, host, username = '', api_key = None):
      super().__init__(id)
      self.host = host
      self.username = username or os.getenv('DISCOURSE_USERNAME')
      self.api_key = api_key or os.getenv('DISCOURSE_KEY')

    
    def fetch_data(self):
      posts = self.topic_posts(self.id)
      for post in posts['post_stream']['posts']:
        temp = conform(post, ['username', 'created_at', 'cooked'])
        temp['author_association'] = 'CONTRIBUTOR' if post['moderator'] else 'MEMBER' if post['admin'] or post['staff'] else 'NONE'
        temp['cooked'] = BeautifulSoup(temp['cooked'], "lxml").text
        self.data.append(transform(temp, MAPPING))
        for reply in self.post_replies(post['id']):
          temp = conform(reply, ['username', 'created_at', 'cooked'])
          temp['author_association'] = 'CONTRIBUTOR' if reply['moderator'] else 'MEMBER' if reply['admin'] or reply['staff'] else 'NONE'
          temp['cooked'] = BeautifulSoup(temp['cooked'], "lxml").text
          self.data.append(transform(temp, MAPPING))

    def topic_posts(self, id):
      response = requests.get(f'{self.host}/t/{id}/posts.json', headers={'Accept': 'application/json', 'Api-Username': self.username, 'Api-Key': self.api_key})
      return response.json()

    def post_replies(self, id):
      response = requests.get(f'{self.host}/posts/{id}/replies.json', headers={'Accept': 'application/json', 'Api-Username': self.username, 'Api-Key': self.api_key})
      return response.json()