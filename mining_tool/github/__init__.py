import os
import re
from time import sleep

import requests
from mining_tool.base import IssueReport


class GitHubIssueReport(IssueReport):
    def __init__(self, gh):
      super().__init__()
      matches = re.findall(r'^(\w*)/(\w*)$', gh)
      self.repo_owner = matches[0][0]
      self.repo_name = matches[0][1]
      self.headers = {"Authorization": f"Bearer {os.getenv('GH_PRIVATE_KEY')}"}

    def __issue_count_template(self, quantity = 100, cursor = 100) -> str:
        q = f"""
            query {{
                repository(owner: "{self.repo_owner}", name: "{self.repo_name}") {{
                    issues(last: 0, states:[OPEN, CLOSED]) {{
                        totalCount
                    }}
                }}
            }}"""
        return q

    def __initialize_pagination_template(self, quantity: int, cursor: str) -> str:
        q = f"""
            query {{
                repository(owner: "{self.repo_owner}", name: "{self.repo_name}") {{
                    issues(last: 1, states:[OPEN, CLOSED]) {{
                      edges {{
                        cursor
                        node {{
                          number
                          url
                          title
                          createdAt
                          closedAt
                          participants {{
                            totalCount
                          }}
                          comments {{
                            totalCount
                          }}
                          labels(first: 10) {{
                            edges {{
                              node {{
                                name
                              }}
                            }}
                          }}
                          locked
                        }}
                      }}
                    }}
                }}
            }}"""
        return q

    def __report_template(self, quantity: int, cursor: str) -> str:
        q = f"""
            query {{
                repository(owner: "{self.repo_owner}", name: "{self.repo_name}") {{
                    issues(last: {quantity}, before: "{cursor}", states:[OPEN, CLOSED]) {{
                      edges {{
                        cursor
                        node {{
                          number
                          url
                          title
                          createdAt
                          closedAt
                          participants {{
                            totalCount
                          }}
                          comments {{
                            totalCount
                          }}
                          labels(first: 10) {{
                            edges {{
                              node {{
                                name
                              }}
                            }}
                          }}
                          locked
                        }}
                      }}
                    }}
                }}
            }}"""
        return q

    def __simple_report_template(self, quantity: int, cursor: str) -> str:
        q = f"""
            query {{
                repository(owner: "{self.repo_owner}", name: "{self.repo_name}") {{
                    issues(last: {quantity}, states:[OPEN, CLOSED]) {{
                      edges {{
                        cursor
                        node {{
                          number
                          url
                          title
                          createdAt
                          closedAt
                          participants {{
                            totalCount
                          }}
                          comments {{
                            totalCount
                          }}
                          labels(first: 10) {{
                            edges {{
                              node {{
                                name
                              }}
                            }}
                          }}
                          locked
                        }}
                      }}
                    }}
                }}
            }}"""
        return q

    def __process_issue_request(self, issue_json: dict) -> list:
        r = issue_json['data']['repository']['issues']['edges']
        result = [
            {
                'cursor': value['cursor'],
                **value['node'],
                'issue ID': int(value['node']['number']),
                'issue title': value['node']['title'],
                'created at': value['node']['createdAt'],
                'closed at': value['node']['closedAt'],
                'participants': value['node']['participants']['totalCount'],
                'comments': value['node']['comments']['totalCount'],
                'locked': value['node']['locked'],
                'labels': ", ".join(x['node']['name'] for x in value['node']['labels']['edges']),
                'repo owner': self.repo_owner,
                'repo name': self.repo_name
            }
            for value in r
        ]
        return result

    def __post_request(self, query_template, quantity = 100, cursor =""):
        request = requests.post('https://api.github.com/graphql', json={'query': query_template(quantity, cursor)}, headers=self.headers)
        if request.status_code == 401:
            raise Exception("Please enter your valid authorization token!")
        elif request.status_code == 200:
            return request.json()
        else:
            raise Exception(f"Query failed to run by returning code of {request.status_code}. {query_template(self, quantity, cursor)}")

    def fetch_data(self):
        num_r = self.__post_request(self.__issue_count_template)
        iss_count = num_r['data']['repository']['issues']['totalCount']
        resultant = []
        if iss_count > 100:
            print() #Buffer print for readability
            pagination_r = self.__post_request(self.__initialize_pagination_template)
            v = pagination_r['data']['repository']['issues']['edges']
            cursor = v[0]['cursor']
            primer = self.__process_issue_request(pagination_r)[0]
            i = iss_count
            while i / 100 > 1:
                i = i - 100
                request = self.__post_request(self.__report_template, 100, cursor)
                t = self.__process_issue_request(request)
                cursor = t[0]['cursor']
                for issues in t:
                    if isinstance(issues, dict):
                      resultant.append(issues.copy())
                # print("Report Loading: " + str(round((((len(resultant)) / iss_count) * 100))) + "% \n")
            request = self.__post_request(self.__report_template, 100, cursor)
            t = self.__process_issue_request(request)
            resultant.append(primer)
            for issues in t:
                if isinstance(issues, dict):
                    resultant.append(issues.copy())
            self.data = resultant.copy()
            return resultant
        elif iss_count > 0:
            request = self.__post_request(self.__simple_report_template)
            t = self.__process_issue_request(request)
            self.data = t.copy()
            return t
