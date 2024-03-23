import scrapy
import json
import os

from ..settings import *
from ..items import *

class Gitpider(scrapy.Spider):
    name = 'github'
    token = get_github_token()
    custom_settings = save_into_json()
    all_repo_items = {}  # Dictionary to store the last item for each RepoID


    def start_requests(self):
        user_ids = ['johnkim6823']
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
        }

        for user_id in user_ids:
            url = f'{API_URL}/users/{user_id}'
            yield scrapy.Request(url, headers=headers, callback=self.parse_user, meta={'GithubID': user_id})

    def parse_user(self, response):
        GithubID = response.meta['GithubID']
        student = json.loads(response.text)

        item = STUDENT()
        item['GithubID'] = student['login']
        item['Follower_CNT'] = student['followers']
        item['Following_CNT'] = student['following']
        item['Public_repos_CNT'] = student['public_repos']
        item['Github_profile_Create_Date'] = student['created_at']
        item['Github_profile_Update_Date'] = student['updated_at']
        item['Crawled_Date'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        yield item

        # Requesting repositories for the user
        repos_url = f'{API_URL}/users/{GithubID}/repos'
        yield scrapy.Request(repos_url, headers=response.request.headers, callback=self.parse_repos, meta={'GithubID': GithubID})


    def parse_repos(self, response):
        GithubID = response.meta['GithubID']
        repos = json.loads(response.text)

        for repo in repos:
            repo_item = REPO()  # Assuming you have a REPO item defined similar to STUDENT
            repo_item['RepoID'] = repo['id']
            repo_item['RepoURL'] = repo['html_url']
            repo_item['OwnerGithubID'] = repo['owner']['login']
            repo_item['CreationDate'] = repo['created_at']
            repo_item['ForkCount'] = repo['forks_count']
            repo_item['StarCount'] = repo['stargazers_count']
            repo_item['OpenIssueCount'] = repo['open_issues_count']
            repo_item['LicenseName'] = repo['license']['name'] if repo['license'] else None
            repo_item['ProjectDescription'] = repo['description']


            # Fetch additional data for each repository
            languages_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/languages'
            yield scrapy.Request(languages_url, headers=response.request.headers, callback=self.parse_languages, meta={'repo_item': repo_item, 'GithubID': GithubID, 'repo_name': repo["name"]})

    def parse_languages(self, response):
        repo_item = response.meta['repo_item']
        languages = json.loads(response.text) if response.text else {}
        repo_item['ProgrammingLanguage'] = list(languages.keys()) if languages else None
        
        # Fetch contributors
        contributors_url = f'{API_URL}/repos/{response.meta["GithubID"]}/{response.meta["repo_name"]}/contributors'
        yield scrapy.Request(contributors_url, headers=response.request.headers, callback=self.parse_contributors, meta={'repo_item': repo_item})

    def parse_contributors(self, response):
        repo_item = response.meta['repo_item']
        contributors = json.loads(response.text) if response.text else []
        repo_item['Contributors'] = [contributor['login'] for contributor in contributors if 'login' in contributor] if contributors else None
        
        # Fetch commits
        commits_url = f'{API_URL}/repos/{response.meta["GithubID"]}/{response.meta["repo_name"]}/commits'
        yield scrapy.Request(commits_url, headers=response.request.headers, callback=self.parse_commits, meta={'repo_item': repo_item})

    def parse_commits(self, response):
        repo_item = response.meta['repo_item']
        commits = json.loads(response.text) if response.text else []
        repo_item['CommitCount'] = len(commits) if commits else 0
        
        # Fetch readme
        readme_url = f'{API_URL}/repos/{response.meta["GithubID"]}/{response.meta["repo_name"]}/readme'
        yield scrapy.Request(readme_url, headers=response.request.headers, callback=self.parse_readme, meta={'repo_item': repo_item})

     def parse_readme(self, response):
        repo_item = response.meta['repo_item']
        repo_item['HasReadME'] = True if response.status == 200 else False
        
        # Fetch release information
        release_url = f'{API_URL}/repos/{response.meta["GithubID"]}/{response.meta["repo_name"]}/releases/latest'
        yield scrapy.Request(release_url, headers=response.request.headers, callback=self.parse_release, meta={'repo_item': repo_item})

    def parse_release(self, response):
        repo_item = response.meta['repo_item']
        if response.status == 200 and response.text:
            release = json.loads(response.text)
            repo_item['ReleaseVersion'] = release.get('tag_name', None)
        else:
            repo_item['ReleaseVersion'] = None
        
        # Now that all data is collected, yield the repo_item
        yield repo_item

            # # Fetch additional data for each repository
            # languages_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/languages'
            # yield scrapy.Request(languages_url, headers=response.request.headers, callback=self.parse_languages, meta={'repo_item': repo_item})

            # #contributors_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/contributors'
            # #yield scrapy.Request(contributors_url, headers=response.request.headers, callback=self.parse_contributors, meta={'repo_item': repo_item})

            # commits_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/commits'
            # yield scrapy.Request(commits_url, headers=response.request.headers, callback=self.parse_commits, meta={'repo_item': repo_item})

            # readme_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/readme'
            # yield scrapy.Request(readme_url, headers=response.request.headers, callback=self.parse_readme, meta={'repo_item': repo_item})

            # release_url = f'{API_URL}/repos/{GithubID}/{repo["name"]}/releases/latest'
            # yield scrapy.Request(release_url, headers=response.request.headers, callback=self.parse_release, meta={'repo_item': repo_item})

    # def parse_languages(self, response):
    #     repo_item = response.meta['repo_item']
    #     languages = json.loads(response.text) if response.text else {}
    #     repo_item['ProgrammingLanguage'] = list(languages.keys()) if languages else None
        
    #     # Continue the chain by fetching the next piece of data
    #     contributors_url = f'{API_URL}/repos/{response.meta["GithubID"]}/{response.meta["repo_name"]}/contributors'
    #     yield scrapy.Request(contributors_url, headers=response.request.headers, callback=self.parse_contributors, meta={'repo_item': repo_item})


    # def parse_contributors(self, response):
    #     repo_item = response.meta['repo_item']
    #     contributors = json.loads(response.text) if response.text else []
    #     repo_item['Contributors'] = [contributor['login'] for contributor in contributors if 'login' in contributor] if contributors else None
    #     yield repo_item

    # def parse_commits(self, response):
    #     repo_item = response.meta['repo_item']
    #     commits = json.loads(response.text) if response.text else []
    #     repo_item['CommitCount'] = len(commits) if commits else 0  # Or set to None if you prefer
    #     yield repo_item

    # def parse_readme(self, response):
    #     repo_item = response.meta['repo_item']
    #     # If the status is 404 or another non-200, set HasReadME to None
    #     repo_item['HasReadME'] = True if response.status == 200 else None
    #     yield repo_item

    # def parse_release(self, response):
    #     repo_item = response.meta['repo_item']
    #     if response.status == 200 and response.text:
    #         release = json.loads(response.text)
    #         repo_item['ReleaseVersion'] = release['tag_name']
    #     elif response.status == 404:
    #         repo_item['ReleaseVersion'] =  None
    #     else:
    #         pass
    #     yield repo_item
        
    # def parse_issues(self, response):
    #     issues = json.loads(response.text)
    #     for issue in issues:
    #         issue_item = ISSUE()
    #         issue_item['ISSUEID'] = issue['id']
    #         issue_item['IssuePublisherID'] = issue['user']['login']
    #         issue_item['OwnerGithubID'] = issue['repository']['owner']['login']
    #         issue_item['RepoURL'] = issue['repository_url']
    #         issue_item['IssueDate'] = issue['created_at']
    #         issue_item['Title'] = issue['title']
    #         yield issue_item

    # def parse_pulls(self, response):
    #     pulls = json.loads(response.text)
    #     for pr in pulls:
    #         pr_item = PR()
    #         pr_item['PRID'] = pr['id']
    #         pr_item['RequesterID'] = pr['user']['login']
    #         pr_item['OwnerGithubID'] = pr['head']['repo']['owner']['login']
    #         pr_item['RepoURL'] = pr['url']
    #         pr_item['PRDate'] = pr['created_at']
    #         pr_item['Title'] = pr['title']
    #         yield pr_item
