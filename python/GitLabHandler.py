from __future__ import absolute_import
from __future__ import print_function
import os, sys
import re

import json
import requests

from datetime import datetime
## python < 3.7
#import dateutil.parser

"""
Original Author: Andrea Carlo Marini
Original Date: Fri Aug 17 14:51:52 CEST 2018
License:  GNU LGPLv3 
"""


class Base:
    """All Objects from gitlab inheriths from me"""

    def __init__(self):
        pass

    def ParseRequest(self, req):
        pass

    def Print(self):
        pass


class MergeReq(Base):
    def __init__(self):
        Base.__init__(self)
        self.sha = ""
        self.title = ""
        self.labels = []
        self.merge_status = ""
        self.iid = -1
        self.id = -1
        self.origin_id = ""

    def ParseRequest(self, req):
        Base.ParseRequest(self, req)
        #print("DEBUG: req for MR is", req)
        self.sha = req["sha"]
        self.title = req["title"]
        self.labels = req["labels"]
        self.merge_status = req["merge_status"]  #: "can_be_merged",
        self.iid = req["iid"]
        self.id = req["id"]
        self.origin_id = req["source_project_id"]

    def Print(self):
        Base.Print(self)

        print(" --- MERGE REQ:", self.id, self.iid, "----")
        print(" title:", self.title)
        print(" labels:", self.labels)
        print(" merge_status:", self.merge_status)
        print(" sha:", self.sha)
        print(" origin id:", self.origin_id)
        print(" --------------------------------------")


class Commit(Base):
    def __init__(self):
        Base.__init__(self)
        self.sha = None
        self.date = None
        self.author = None
        self.title = None
        self.statuses = {}  # name->(status,date)

    def ParseRequest(self, req):
        Base.ParseRequest(self, req)
        # print "Request is ",req
        self.sha = req["id"]
        self.date = datetime.fromisoformat(req["created_at"])
        self.author = req["author_name"]
        self.title = req["title"]

    def ParseStatusRequest(self, req):
        for st in req:  ## this is a list  of dict
            status = st["status"]
            name = st["name"]
            date = datetime.fromisoformat(st["created_at"])
            self.statuses[name] = (status, date)

    def Print(self):
        Base.Print(self)

        print(" --- Commit:", self.sha, "----")
        print("date:", self.date)
        print("status", self.statuses)
        print("-----------------------------")


class Pipeline(Base):
    def __init__(self):
        Base.__init__(self)
        self.web_url = ""
        self.id = None
        self.iid = None
        self.title = ""
        self.description = ""
        self.status = None
        self.sha = None
        self.ref = None
        self.variables = {}

    def ParseRequest(self, req, req2=None):
        """Optionally pass req2 for parsing variables. Either req or req2 could be none to skip that part"""
        if req:
            Base.ParseRequest(self, req)
            self.web_url = req["web_url"]
            self.id = req["id"]
            self.iid = req["iid"]
            self.status = req["status"]
            self.sha = req["sha"]
            self.ref = req["ref"]
            self.title = self.sha[-6:-1]
        if req2:  ## for the variables
            self.variables = {}
            for key in req2:
                self.variables[key["key"]] = key["value"]
                if key["key"] == "PIPELINE_TITLE":
                    self.title = key["value"]
                if key["key"] == "PIPELINE_DESCRIPTION":
                    self.description = key["value"]

    def Print(self, short=True):
        print(" -- Pipeline: ", self.id, self.iid, "---")
        print(self.title)
        if self.description != "":
            print(self.description)
        print(self.web_url)
        print(self.status)
        if not short:
            print(self.variables)
        print("-----------------------------")

class Epic(Base):
    def __init__(self):
        Base.__init__(self)
        self.title=""
        self.id=None
        self.iid=None
        self.group=""
    def ParseRequest(self,req):
        self.title=req["title"]
        self.id=req["id"]
        self.iid=req["iid"]
        if 'group' in req: self.group=req["group"]
    def Print(self):
        Base.Print(self)

        print(" --- EPIC:", self.id, self.iid, "----")
        print(" title:", self.title)
        print(" group:",self.group)
        print(" --------------------------------------")

    def __str__(self):
        ''' when printing inside other functions, use the title'''
        return self.title

class MileStone(Base):
    def __init__(self):
        Base.__init__(self)
        self.title=""
        self.due_date=None
        self.id=-1
        self.iid=-1
        self.created_at = None
        self.due_date = None
        self.format= '%Y-%m-%dT%H:%M:%S'
        self.project_id = None

    def ParseRequest(self,req):
        self.id = req["id"]
        self.iid = req["iid"]
        self.title = req["title"]
        self.created_at = datetime.fromisoformat(req["created_at"])
        self.due_date = datetime.fromisoformat(req["due_date"])
        self.project_id = req["project_id"]
        # "project_id" : 4,
        # "state" : "closed",
        # "description" : "Rerum est voluptatem provident consequuntur molestias similique ipsum dolor.",

    def __str__(self):
        return self.title

    def Print(self):
        print(" --- MILESTONE:", self.id, self.iid, "----")
        print(" title:", self.title)
        print(" due_date:",self.due_date)
        print(" --------------------------------------")

class LabelEvent(Base):
    def __init__(self):
        self.id=None
        self.action=None
        self.user=None
        self.date = None
        self.label_id= None
        self.label = None

    def ParseRequest(self,req):
        ''' GET /projects/:id/issues/:issue_iid/resource_label_events'''
        #print ("DEBUG Request label event is ",req)
        self.id = req['id']
        self.action = req['action']
        self.date = datetime.fromisoformat(req["created_at"])
        self.label_id = req['label']['id']
        self.label = req['label']['name']
        self.user = req['user']['name']

    def Print(self):
        print ("--- LABEL EVENT ---" )
        print ("label",self.label)
        print ("action",self.action)
        print ("date",self.date)
    
    def __str__(self):
        return ("+" if self.action == "add" else '-') + self.label +"("+ str(self.date) + ")"


class Issue(Base):
    def __init__(self):
        Base.__init__(self)
        self.title = ""
        self.labels = []
        self.iid = -1
        self.id = -1
        self.origin_id = ""
        self.epic= None
        self.milestone=None
        self.label_events_filled=False
        self.label_events=[] ## not necessarily filled

    def ParseRequest(self, req):
        Base.ParseRequest(self, req)
        #print("DEBUG: req for ISSUE is", req)
        self.title = req["title"]
        self.labels = req["labels"]
        self.iid = req["iid"]
        self.id = req["id"]
        if 'epic' in req and req['epic'] != None:
            self.epic =Epic()
            self.epic.ParseRequest(req["epic"])
        if 'milestone' in req and req['milestone'] != None:
            self.milestone = MileStone()
            self.milestone.ParseRequest(req["milestone"])
        return self

    def Print(self):
        Base.Print(self)

        print(" --- ISSUE:", self.id, self.iid, "----")
        print(" title:", self.title)
        print(" labels:", self.labels)
        print(" epic:", self.epic)
        print(" milestone:", self.milestone)
        print(" origin id:", self.origin_id)
        if self.label_events_filled: print(" label_events:",' '.join( [str(x) for x in self.label_events]) ) 
        print(" --------------------------------------")
#with_labels_details    boolean    no    If true, 
#the response returns more details for each label in labels field: 
#:name, :color, :description, :description_html, :text_color. Default is false. 
#The description_html attribute was  not implemented yet
##
# class Tag(base)


class GitLabHandler:
    """Handle Interface with gitlabapi"""

    def __init__(self, repo):
        self.SetRepo(repo)
        self.baseurl = "https://gitlab.cern.ch/api/v4"
        self.auth = ""
        self.per_page = 100
        self.ca_file = True
        ## in CentOS7 it is not configured correctly. Use True for system.
        #self.ca_file = "/etc/ssl/certs/ca-bundle.crt"

    def SetRepo(self, repo):
        """Set the repository. Clear cached"""
        self.repo = re.sub("/", "%2F", repo)
        # self.repoid=None
        self.merge_requests = []
        self.issues = []
        self.commits = {}  # sha-> Commit

    def _check(self):
        """Private method. Check if authentication method is available or if runnig anonymously"""
        if self.auth == "":
            print("Running w/o authentication")
        return self

    def _request(self, resource, params={}, within_repo=True):
        """Private method. Make a request GET to the api"""
        # alternate authentication in the url
        # ?private_token=9xxx

        self._check()

        headers = {}
        if self.auth != "":
            headers["Private-Token"] = self.auth

        if within_repo:
            url = self.baseurl + "/projects/" + self.repo + "/" + resource
        else:
            url = self.baseurl + "/" + resource

        r = requests.get(url, params=params, headers=headers, verify=self.ca_file)

        # print "DEBUG: Response is",r
        # print "DEBUG:", r.json()

        if "Private-Token" in headers:
            headers["Private-Token"] = "****"
        if r.status_code == 403:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            raise Exception("403 Response")
        if r.status_code == 404:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            raise Exception("404 Response")

        return r

    def _post(self, resource, params={}, within_repo=True):
        """Private method. Make a POST request to the api"""

        self._check()

        headers = {}
        if self.auth != "":
            headers["Private-Token"] = self.auth

        # url=self.baseurl +"/" + self.repo + "/" +resource

        if within_repo:
            url = self.baseurl + "/projects/" + self.repo + "/" + resource
        else:
            url = self.baseurl + "/" + resource

        data = json.dumps(params)
        r = requests.post(url, params=params, headers=headers, verify=self.ca_file)

        if "Private-Token" in headers:
            headers["Private-Token"] = "****"
        if r.status_code == 404:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("404 Response")
        if r.status_code == 401:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("401 Response")
        if r.status_code == 400:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("400 Response")

        return r

    def _put(self, resource, params):
        # PUT /projects/:id/merge_requests/:merge_request_iid
        """Private method. Make a PUT request to the api"""

        self._check()

        headers = {}
        if self.auth != "":
            headers["Private-Token"] = self.auth

        url = self.baseurl + "/projects/" + self.repo + "/" + resource

        r = requests.put(url, params=params, headers=headers, verify=self.ca_file)

        if "Private-Token" in headers:
            headers["Private-Token"] = "****"
        if r.status_code == 404:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("404 Response")
        if r.status_code == 401:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("401 Response")
        if r.status_code == 400:
            print("Request Failed:")
            print("   URL= '" + url + "'")
            print("   PARAMS= '" + str(params) + "'")
            print("   HEADER= '" + str(headers) + "'")
            print(r.json())
            raise Exception("400 Response")

        return r

    def PrintProject(self):
        resource = ""
        params = {"simple": True}
        r = self._request(resource, params)

        print("PROJECTS")
        print("-----------------")
        pj = r.json()
        for key in pj:
            print(key, ":", pj[key])
        print("-----------------")

    def PrintProjects(self):
        resource = "projects/"
        params = {"simple": True}
        r = self._request(resource, params, False)

        print("PROJECTS")
        for pj in r.json():
            print("-----------------")
            for key in pj:
                print(key, ":", pj[key])
            print("-----------------")
        return self

    def GetProjects(self, path):
        # GET /groups/:id/subgroups
        # GET /groups/:id/projects
        mypath = re.sub("/", "%2F", path)
        resource = "groups/" + mypath + "/subgroups"
        params = {}
        r = self._request(resource, params, False)
        sg = []
        for o in r.json():
            sg.append(o["full_path"])

        resource = "groups/" + mypath + "/projects"
        # params={"simple":True}
        params = {"per_page": self.per_page, "page": 1}

        pj = []
        loop = True
        while loop:
            r = self._request(resource, params, False)
            for o in r.json():
                pj.append((o["path"], o["ssh_url_to_repo"]))
            if len(r.json()) < self.per_page:
                loop = False
            else:
                params["page"] += 1
                # print "DEBUG","going to Page",params["page"]

        return (sg, pj)

    def GetProjectUrl(self, path):
        resource = "projects/" + re.sub("/", "%2F", path)
        req = self._request(resource, {}, False)
        return req.json()["ssh_url_to_repo"]

    def CreateProject(self, path):
        name = path.split("/")[-1]
        params = {
            "name": name,
            "visibility": "private",
        }
        # get id of the group/namespace
        if "/" in path:
            mypath = re.sub("/", "%2F", "/".join(path.split("/")[:-1]))
            # GET /groups/:id/
            resource = "groups/" + mypath

            r = self._request(resource, {}, False)

            print("-> Group info are:", r.json()["name"], r.json()["id"])
            # print r.json()

            params["namespace_id"] = r.json()["id"]

        # create project
        resource = "projects/"
        print("-> Creating project", path)
        # print "REQ will be",resource,params
        r = self._post(resource, params, False)
        return self

    def GetMergeRequests(self):
        """Update the list of open merge requests"""
        # resource="merge_requests?state=opened"
        # GET /projects/:id/merge_requests
        # GET /projects/:id/merge_requests?state=opened
        # GET /merge_requests?labels=bug,reproduced
        # GET /merge_requests?milestone=release
        resource = "merge_requests"
        params = {"state": "opened"}
        r = self._request(resource, params)

        self.merge_requests = []
        for req in r.json():
            myMR = MergeReq()
            myMR.ParseRequest(req)
            #myMR.Print()
            self.merge_requests.append(myMR)

    def GetPipelines(self):
        """Update the list of running pipelines"""
        resource = "pipelines"
        params = {}
        r = self._request(resource, params)
        self.pipelines = []
        for req in r.json():
            myP = Pipeline()
            myP.ParseRequest(req)
            resource = "pipelines/%d/variables" % (myP.id)
            req2 = self._request(resource, params)
            myP.ParseRequest(None, req2.json())
            # myP.Print()
            self.pipelines.append(myP)

    def SetLabel(self, mr, newlabels=[]):
        # PUT /projects/:id/merge_requests/:merge_request_iid
        iid = mr.iid
        resource = "merge_requests/" + str(iid)
        labelsstr = ",".join(newlabels)
        params = {"labels": labelsstr}

        self._put(resource, params)

    def ChangeLabel(self, mr, add=[], remove=[]):
        # PUT /projects/:id/merge_requests/:merge_request_iid
        iid = mr.iid
        labels = mr.labels
        resource = "merge_requests/" + str(iid)
        labels.extend(add)
        newlabels = [l for l in labels if l not in remove]
        labelsstr = ",".join(newlabels)
        params = {"labels": labelsstr}

        # print "DEBUG Setting labels to be '"+labelsstr +"'"
        self._put(resource, params)

    def GetCommit(self, sha):
        """Get a specific Commit"""
        # GET /projects/:id/repository/commits/sha
        # curl --header "PRIVATE-TOKEN: abc" "https://gitlab.example.com/api/v4/projects/5/repository/commits/master

        resource = "repository/commits/" + sha
        params = {}
        r = self._request(resource, params)
        myCommit = Commit()
        myCommit.ParseRequest(r.json())

        ## STATUSES
        # GET /projects/:id/repository/commits/:sha/statuses
        # "status":"pending"
        # "name" : "bundler:audit",
        # "description" : null,

        # already return the latest ones. otherwise pass in params all:true
        params = {"all": False}
        resource = "repository/commits/" + sha + "/statuses"
        r2 = self._request(resource, params)
        myCommit.ParseStatusRequest(r2.json())

        self.commits[sha] = myCommit

        return sha

    def GetUser(self, name):
        "GET /users"
        resource = "users"
        params = {"search": name}
        r = self._request(resource, params, False)
        ret = []
        for user in r.json():
            ret.append((user["id"], user["username"], user["name"]))
        return ret

    def AddMember(self, user_id, access_level=20):
        # 10 => Guest access
        # 20 => Reporter access
        # 30 => Developer access
        # 40 => Maintainer access
        # 50 => Owner access # Only valid for groups
        # def _post(self, resource, params={},within_repo=True):
        resource = "members"
        params = {"user_id": user_id, "access_level": access_level}
        r = self._post(resource, params)
        return True

    def SetStatus(self, sha, name, state, url=""):
        # POST /projects/:id/statuses/:sha
        # id     integer/string  yes     The ID or URL-encoded path of the project owned by the authenticated user
        # sha     string  yes     The commit SHA
        # state   string  yes     The state of the status. Can be one of the following: pending, running, success, failed, canceled
        # ref     string  no  The ref (branch or tag) to which the status refers
        # name or context     string  no  The label to differentiate this status from the status of other systems. Default value is default
        # target_url  string  no  The target URL to associate with this status
        # description     string  no  The short description of the status
        resource = "statuses/" + sha
        params = {"state": state, "name": name}
        if url != "":
            params["target_url"] = url

        print("Setting status of", sha, "name=", state)
        r = self._post(resource, params)

        return True

    def PostMergeReqComment(self, iid, comment):
        """Post a comment on a Merge Request"""
        # print "DEBUG: Commenting on PR ",iid, "with body:",comment
        resource = "merge_requests/" + str(iid) + "/notes"
        params = {"body": comment}
        r = self._post(resource, params)
        # print r, r.json()
        if r.status_code == 200:
            return True
        return False

    def GetIssues(self):
        #
        # GET /projects/42/issues/:id
        """Update the list of open merge requests"""
        # resource="merge_requests?state=opened"
        # GET /projects/:id/merge_requests
        # GET /projects/:id/merge_requests?state=opened
        # GET /merge_requests?labels=bug,reproduced
        # GET /merge_requests?milestone=release
        resource = "issues"
        params = {"state": "opened","with_labels_details":True}
        r = self._request(resource, params)

        self.issues = []
        for req in r.json():
            myIssue = Issue()
            myIssue.ParseRequest(req)
            #myIssue.Print()
            self.issues.append(myIssue)
        return self

    def GetLabelEvents(self, issue=-1):
        ''' Get Label Events for issues n or all'''
        #''' GET /projects/:id/issues/:issue_iid/resource_label_events'''
        for myIssue in self.issues:
            if issue >= 0 and myIssue.iid != issue: continue
            resource = f"issues/{myIssue.iid}/resource_label_events"
            params={}
            r = self._request(resource,params)
            myIssue.label_events_filled = True
            myIssue.label_events=[]
            for rle in r.json():
                le = LabelEvent()
                le.ParseRequest(rle)
                myIssue.label_events.append(le)

    def read_token_fromfile(self, name):
        f = open(name)
        for l in f:
            l.split("#")[0]
            l = l.replace("\n", "")
            if l != "":
                self.auth = l[:]
                break
        f.close()


if __name__ == "__main__":
    print("Testing ...")
    gitlab = GitLabHandler("amarini/test")
    gitlab.read_token_fromfile(os.environ["HOME"]+ "/.ssh/gitlab_token")
    # gitlab.PrintProject()
    # gitlab.PrintProjects()
    print ("------------ MERGE REQUESTS ----------------")
    gitlab.GetMergeRequests()
    # iid = gitlab.merge_requests[0].iid
    # gitlab.PostComment(iid, "this is an API test")
    if len(gitlab.merge_requests) >0:
        sha = gitlab.merge_requests[0].sha
        gitlab.GetCommit(sha)
        gitlab.commits[sha].Print()

        ## example on work with status
        # gitlab.SetStatus(sha,"test","failed","https://amarini.web.cern.ch/amarini/cms-private")
        # gitlab.SetStatus(sha,"test","pending")
        # gitlab.SetStatus(sha,"test","success","https://amarini.web.cern.ch/amarini/cms-private")

        #gitlab.GetCommit(sha)
        #gitlab.commits[sha].Print()

        # example to work with labels
        # gitlab.SetLabel(gitlab.merge_requests[0],["new","new2"]) # labels will become this exact list
        # gitlab.ChangeLabel(gitlab.merge_requests[0],["new"]) # add, remove
        # gitlab.ChangeLabel(gitlab.merge_requests[0],[],["old"])

        #gitlab.GetMergeRequests()
        gitlab.merge_requests[0].Print()

    print ("------------ ISSUES ----------------")
    gitlab.GetIssues()
    gitlab.GetLabelEvents() ## to get issues label events
    if len(gitlab.issues)>0:
        gitlab.issues[0].Print()
    # create a repository in a existing namespace
    # testrepo="amarini-testgroup/subgroup/Repo3"
    # gitlab.CreateProject(testrepo)
