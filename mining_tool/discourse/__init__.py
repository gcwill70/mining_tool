import os
import requests
from mining_tool.base import IssueReport
from mining_tool.utils import conform, transform

MAPPING = {
    'id': 'issue ID',
    'title': 'title',
    'created_at': 'created at',
    'closed_at': 'closed at',
    'posts_count': 'comments',
}

class DiscourseIssueReport(IssueReport):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.username = os.getenv('DIASPORA_DISCOURSE_USERNAME')
        self.api_key = os.getenv('DIASPORA_DISCOURSE_KEY')
        

    def fetch_data(self):
        self.data = []
        # For each category
        for category in self.categories()['category_list']['categories']:
            # For each topic page
            pgNum = 1
            while pgNum > 0:
                topics = self.category_topics(category['id'], pgNum)
                try:
                    for topic in topics['topic_list']['topics']:
                        self.data.append(transform(conform(topic, ['id', 'title', 'posts_count', 'created_at']), MAPPING))
                    pgNum = pgNum + 1
                except:
                    pgNum = -1
    
    def categories(self):
        response = requests.get(f'{self.host}/categories.json?include_subcategories=True', headers={'Accept': 'application/json', 'Api-Username': self.username, 'Api-Key': self.api_key})
        return response.json()
    
    def category_topics(self, id, pg):
        response = requests.get(f'{self.host}/c/{id}?page={pg}', headers={'Accept': 'application/json', 'Api-Username': self.username, 'Api-Key': self.api_key})
        return response.json()
