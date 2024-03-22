# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KuGithubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class STUDENT(scrapy.Item):
    GithubID = scrapy.Field()
    Follower_CNT = scrapy.Field()
    Following_CNT = scrapy.Field()
    Public_repos_CNT = scrapy.Field()
    Github_profile_Create_Date = scrapy.Field()
    Github_profile_Update_Date = scrapy.Field()
    Crawled_Date = scrapy.Field()

class REPO(scrapy.Item):
    RepoID = scrapy.Field()
    RepoURL = scrapy.Field()
    OwnerGithubID = scrapy.Field()
    CreationDate = scrapy.Field()
    ForkCount = scrapy.Field()
    StarCount = scrapy.Field()
    OpenIssueCount = scrapy.Field()
    LicenseName = scrapy.Field()
    ProjectDescription = scrapy.Field()
    ProgrammingLanguage = scrapy.Field()
    Contributors = scrapy.Field()
    CommitCount = scrapy.Field()
    HasReadME = scrapy.Field()
    ReleaseVersion = scrapy.Field()