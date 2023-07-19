# Overview
`mining_tool` can collect, process, and analyze [GitHub issues](https://github.com/features/issues) or [Discourse forums](https://www.discourse.org).
Python 3.9 is required.

# Features
* Collect issues and comments from a provided repository
* Sample, query, and filter based on keywords.
* Importing and exporting at each step of the process.
* Import/export to CSV or Excel spreadsheets.
* Backoff and retry on rate limit errors.

# Setup
Run these commands to setup.
```
pip install -r requirements.txt
python -m mining_tool --setup
```

`.env` files can be used for API credentials.
```
GH_PRIVATE_KEY=<FILL IN>
DIASPORA_DISCOURSE_USERNAME=<FILL IN>
DIASPORA_DISCOURSE_KEY=<FILL IN>
```

# Usage
```
usage: issuereport [-h] [--github GITHUB] [--discourse DISCOURSE] [--discourse-username DISCOURSE_USERNAME] [--imp IMP] [--min-comments MIN_COMMENTS]
                   [--state STATE] [--title-wl TITLE_WL] [--title-bl TITLE_BL] [--randomize] [--sample-amount SAMPLE_AMOUNT]
                   [--sample-percent SAMPLE_PERCENT] [--exp EXP] [--freq FREQ] [--comments-imp COMMENTS_IMP] [--comments-fetch-disable]
                   [--comments-wl COMMENTS_WL] [--comments-bl COMMENTS_BL] [--comments-exp COMMENTS_EXP] [--comments-overwrite-disable]
                   [--comments-utterances-exp COMMENTS_UTTERANCES_EXP] [--comments-utterances-overwrite-disable]
                   [--comments-categorize-exp COMMENTS_CATEGORIZE_EXP] [--comments-categorize-overwrite-disable]
                   [--comments-query-imp COMMENTS_QUERY_IMP] [--comments-query COMMENTS_QUERY] [--comments-query-exp COMMENTS_QUERY_EXP]

create an issue report for a repository

optional arguments:
  -h, --help            show this help message and exit
  --github GITHUB       <owner>/<repo> of GitHub Repository to search
  --discourse DISCOURSE
                        URL of discourse forum.
  --discourse-username DISCOURSE_USERNAME
                        discourse forum username.
  --imp IMP             Search imported local CSV file instead of pulling from GitHub API.
  --min-comments MIN_COMMENTS
                        Filters report for all issues with at least the specified minimum amount of comments
  --state STATE         State of issues to retrieve.
  --title-wl TITLE_WL   File of whitelisted title keywords
  --title-bl TITLE_BL   File of blacklisted title keywords
  --randomize           Shuffle the order of the issues.
  --sample-amount SAMPLE_AMOUNT
                        Number of issues to randomly sample from the issue report
  --sample-percent SAMPLE_PERCENT
                        Percentage of issues to randomly sample from the issue report
  --exp EXP             Export filename of issues. Defaults to OWNER_REPO_issues.csv
  --freq FREQ           Export file that counts frequency of words in issue titles.
  --comments-imp COMMENTS_IMP
                        Filepath prefix to use when importing comments.
  --comments-fetch-disable
                        Disable fetching of new comment reports.
  --comments-wl COMMENTS_WL
                        File of whitelisted comment keywords
  --comments-bl COMMENTS_BL
                        File of blacklisted comment keywords
  --comments-exp COMMENTS_EXP
                        Filepath prefix to use when exporting comments.
  --comments-overwrite-disable
                        Disable storage of comment reports that already exist.
  --comments-utterances-exp COMMENTS_UTTERANCES_EXP
                        Filepath prefix to use when exporting each issue comment's utterances.
  --comments-utterances-overwrite-disable
                        Disable storage of comment utterance reports that already exist.
  --comments-categorize-exp COMMENTS_CATEGORIZE_EXP
                        Filepath prefix to use when exporting each issue's categorized comments.
  --comments-categorize-overwrite-disable
                        Disable storage of comment category reports that already exist.
  --comments-query-imp COMMENTS_QUERY_IMP
                        File to use when importing existing query results.
  --comments-query COMMENTS_QUERY
                        Query to run on each comment.
  --comments-query-exp COMMENTS_QUERY_EXP
                        File to use when exporting query results.
```

# References
The mining tool was forked from [this repository](https://github.com/JacobSPalmer/repo_issues_dc).