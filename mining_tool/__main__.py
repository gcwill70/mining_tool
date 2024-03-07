import argparse
from glob import glob
import os
import re
import sys
from random import Random

from mining_tool.base.comments.analyzer import (classify_comment,
                                                   get_utterances, getLines)
from mining_tool.base.comments import IssueCommentReport
from mining_tool.base import IssueReport
from mining_tool.csv import freq_write, read, write
from mining_tool.discourse import DiscourseIssueReport
from mining_tool.github import GitHubIssueReport
from mining_tool.github.comments import GitHubIssueCommentReport
from mining_tool.discourse.comments import DiscourseIssueCommentReport
from mining_tool.utils import find_file, setup
from mining_tool.query import get_query


def main(args):
    # arg parsing
    parser = argparse.ArgumentParser(
        'mining_tool',
        description='Mine discussions for analysis.'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help="Setup this tool.",
    )
    parser.add_argument(
        '--github',
        required=False,
        help="<owner>/<repo> of GitHub Repository to search",
        type=str,
    )
    parser.add_argument(
        '--discourse',
        required=False,
        help="URL of discourse forum.",
        type=str,
    )
    parser.add_argument(
        '--imp',
        required=False,
        help="Search imported local CSV file instead of pulling from GitHub API.",
        type=str,
    )
    parser.add_argument(
        '--min-comments',
        required=False,
        help="Filters report for all issues with at least the specified minimum amount of comments",
        type=int,
        default=0,
    )
    parser.add_argument(
        '--state',
        required=False,
        help="State of issues to retrieve.",
        type=str,
        default="[OPEN, CLOSED]",
    )
    parser.add_argument(
        '--title-wl',
        required=False,
        help="File of whitelisted title keywords",
        type=str,
    )
    parser.add_argument(
        '--title-bl',
        required=False,
        help="File of blacklisted title keywords",
        type=str,
    )
    parser.add_argument(
        '--randomize',
        action='store_true',
        help="Shuffle the order of the issues.",
    )
    parser.add_argument(
        '--sample-amount',
        required=False,
        help="Number of issues to randomly sample from the issue report",
        type=int,
        default=0,
    )
    parser.add_argument(
        '--sample-percent',
        required=False,
        help="Percentage of issues to randomly sample from the issue report",
        type=int,
        default=0,
    )
    parser.add_argument(
        '--exp',
        required=False,
        help="Export filename of issues. Defaults to OWNER_REPO_issues.csv",
        type=str,
    )
    parser.add_argument(
        '--freq',
        required=False,
        help="Export file that counts frequency of words in issue titles.",
        type=str,
    )
    parser.add_argument(
        '--comments-imp',
        required=False,
        help="Filepath prefix to use when importing comments.",
        type=str,
    )
    parser.add_argument(
        '--comments-fetch-disable',
        action='store_true',
        help="Disable fetching of new comment reports.",
    )
    parser.add_argument(
        '--comments-wl',
        required=False,
        help="File of whitelisted comment keywords",
        type=str,
    )
    parser.add_argument(
        '--comments-bl',
        required=False,
        help="File of blacklisted comment keywords",
        type=str,
    )
    parser.add_argument(
        '--comments-exp',
        required=False,
        help="Filepath prefix to use when exporting comments.",
        type=str,
    )
    parser.add_argument(
        '--comments-overwrite-disable',
        action='store_true',
        help="Disable storage of comment reports that already exist.",
    )
    parser.add_argument(
        '--comments-utterances-exp',
        required=False,
        help="Filepath prefix to use when exporting each issue comment's utterances.",
        type=str,
    )
    parser.add_argument(
        '--comments-utterances-overwrite-disable',
        action='store_true',
        help="Disable storage of comment utterance reports that already exist.",
    )
    parser.add_argument(
        '--comments-categorize-exp',
        required=False,
        help="Filepath prefix to use when exporting each issue's categorized comments.",
        type=str,
    )
    parser.add_argument(
        '--comments-categorize-overwrite-disable',
        action='store_true',
        help="Disable storage of comment category reports that already exist.",
    )
    parser.add_argument(
        '--comments-query-imp',
        required=False,
        help="File to use when importing existing query results.",
        type=str,
    )
    parser.add_argument(
        '--comments-query',
        required=False,
        help="Query to run on each comment.",
        type=str,
    )
    parser.add_argument(
        '--comments-query-exp',
        required=False,
        help="File to use when exporting query results.",
        type=str,
    )
    args = parser.parse_args(args)

    # Setup
    if args.setup:
        setup()
        return

    # Input validation
    if args.github and args.discourse:
        raise Exception("Up to one of --github and --discourse can be used.")
    if args.github and re.match(r'^\w*/\w*$', args.github) == None:
        raise Exception("--github arg must be in <owner>/<repo> format.")
    if args.sample_amount != 0 and args.sample_percent != 0:
        raise Exception("Cannot sample by both percent and amount.")

    # Create issue report
    if args.github:
        issue_report = GitHubIssueReport(args.github)
    elif args.discourse:
        issue_report = DiscourseIssueReport(args.discourse)
    else:
        issue_report = IssueReport()

    # Get data
    if args.imp and os.path.exists(args.imp):
        issue_report.data = read(args.imp)
    elif args.exp:
        issue_report.fetch_data_with_retries(5)

    # Filter
    if (issue_report.data != None):
        issue_report.filter_by_state(args.state)
        if args.min_comments > 0:
            issue_report.filter_by_comments(args.min_comments)
        wl = []; bl = []
        if args.title_wl:
            wl = [kw.replace('\n', '') for kw in open(args.title_wl, "r").readlines()]
        if args.title_bl:
            bl = [kw.replace('\n', '') for kw in open(args.title_bl, "r").readlines()]
        issue_report.filter_by_field('title', wl, bl)

    # Shuffle issues
    if args.randomize and issue_report.data != None:
        Random(2).shuffle(issue_report.data)
    
    # Comment processing
    ## Get IDs
    ids = []
    ### Get IDs from imported issue list
    if issue_report.data != None:
        try:
            ids.extend([issue['issue ID'] for issue in issue_report.data])
        except:
            pass
    ### Get IDs from imported comments
    if args.comments_imp:
        for filename in glob(f'{args.comments_imp}*'):
            try:
                substr = filename[len(args.comments_imp):]
                ids.append(re.search(r'\d+', substr)[0])
            except:
                pass
    ### Make ID list unique
    ids = list(set(ids))
    ## Create query
    if args.comments_query:
        query_merged = []
        if args.comments_query_imp:
            query_old = read(args.comments_query_imp)
        else:
            query_old = []
    ## Process each issue
    for id in ids:
        issue = next((issue for issue in issue_report.data or [] if issue['issue ID'] == id), {})
        # Create comment report
        if args.github:
            comment_report = GitHubIssueCommentReport(id, args.github)
        elif args.discourse:
            comment_report = DiscourseIssueCommentReport(id, args.discourse, args.discourse_username)
        else:
            comment_report = IssueCommentReport(id)
        # Get data
        filename = find_file(f"{args.comments_imp}{id}.*")
        if filename != None:
            comment_report.data = read(filename)
        elif args.comments_exp and not args.comments_fetch_disable:
            comment_report.fetch_data_with_retries(5)
        else:
            continue
        # Filter
        wl = []; bl = []
        if args.comments_wl:
            wl.extend([kw.replace('\n', '') for kw in open(args.comments_wl, "r").readlines()])
        if args.comments_bl:
            bl.extend([kw.replace('\n', '') for kw in open(args.comments_bl, "r").readlines()])
        wl_matches, bl_matches = comment_report.matches('body', wl, bl)
        issue.update({'matches': [item for item in wl_matches]})
        if len(wl_matches) == 0 and len(bl_matches) > 0:
            issue_report.data.remove(issue)
            continue
        # Store
        filename = find_file(f"{args.comments_exp}{id}.*")
        if args.comments_exp and (filename == None or not args.comments_overwrite_disable):
            write(comment_report.data, filename or f"{args.comments_exp}{id}.csv")
        # Analyze
        if args.comments_utterances_exp:
            analysis = []
            for comment in comment_report.data:
                for commentLine in getLines(comment['body']):
                    for utterance in get_utterances(commentLine):
                        obj = comment.copy()
                        obj['body'] = utterance
                        analysis.append(obj)
            filename = find_file(f"{args.comments_utterances_exp}{id}.*")    
            if filename == None or not args.comments_utterances_overwrite_disable:
                write(analysis, filename or f"{args.comments_utterances_exp}{id}.csv")
        if args.comments_categorize_exp:
            analysis = []
            for comment in comment_report.data:
                for commentLine in getLines(comment['body']):
                    obj = comment.copy()
                    obj['body'] = commentLine
                    obj['parsed'], obj['category'] = classify_comment(commentLine)
                    analysis.append(obj)
            filename = find_file(f"{args.comments_categorize_exp}{id}.*")
            if filename == None or not args.comments_categorize_overwrite_disable:
                write(analysis, filename or f'{args.comments_categorize_exp}{id}.csv')
        # Query
        if args.comments_query:
            query_new: list[dict] = get_query(comment_report.data, args.comments_query)
            # Add new items to existing query
            for query_new_item in query_new:
                # add in associated issue data
                copy = issue.copy()
                copy.update(query_new_item)
                query_new_item = copy
                # find existing query
                query_old_match: dict = next((query_old_item for query_old_item in query_old if query_old_item['body'] == query_new_item['body']), None)
                # merge data
                if query_old_match:
                    copy = query_old_match.copy()
                    copy.update(query_new_item)
                    query_merged.append(copy)
                else:
                    query_merged.append(query_new_item)

    # Sample
    if args.sample_amount == 0 and args.sample_percent == 0:
        pass
    elif 0 < args.sample_percent <= 100:
        issue_report.sample_report_percent(args.sample_percent)
    elif args.sample_amount > 0:
        issue_report.sample_report_amount(args.sample_amount)
    else:
        raise Exception("Invalid sample amount or sample percent.")

    # Store
    if args.exp:
        write(issue_report.data, args.exp)
    if args.freq:
        freq_write(issue_report.data, args.freq)
    if args.comments_query_exp:
        write(query_merged, args.comments_query_exp)

if __name__ == "__main__":
    main(sys.argv[1:])
