import os
import requests
from subprocess import Popen, PIPE

REDMINE_USER_ID = ""
DEBUG_PROCESS_CALLS = False
ACTIONS = {}

def generate_branch_name_func(issue_identifier, issue_title):
	def inner():
		return "%s/%s" % (issue_identifier, issue_title)
	return inner

class Repository:
	def __init__(self, name, path, generate_branch_name_func):
		self.name = name
		self.path = path
		self.generate_branch_name_func = generate_branch_name_func

	def generate_branch_name(self, issue_identifier, issue_title):
		return self.generate_branch_name_func(issue_identifier, issue_title)()

folder_a = "/Users/goncalopalaio/tmp/test_git_repo_a"
folder_b = "/Users/goncalopalaio/tmp/test_git_repo_b"
folder_c = "/Users/goncalopalaio/tmp/test_git_repo_c"
folder_d = "/Users/goncalopalaio/tmp/test_git_repo_d"

REPOSITORIES = [Repository("A", folder_a, generate_branch_name_func),
				Repository("B", folder_b, generate_branch_name_func),
				Repository("C", folder_c, generate_branch_name_func),
				Repository("D", folder_d, generate_branch_name_func),
]

class Issue:
	def __init__(self, identifier, title):
		self.identifier = identifier
		self.title = title
		self.info = []

	def generate_branch_name(self, repository):
		return repository.generate_branch_name(self.identifier, self.title)


class Result:
	"""docstring for Success"""
	def __init__(self, was_successful, message, failure_code = None):
		self.was_successful = was_successful
		self.message = message
		self.failure_code = failure_code

	def __str__ (self):
		return "Result: %s|%s|%s" % (self.was_successful, self.message, self.failure_code)

def Success(message):
	return Result(True, message)

def Failure(message, failure_code = None):
	return Result(False, message, failure_code)

def get_html_content():
	placeholder_issues = [Issue("1001", "issue_1"), Issue("1002", "issue_2")]

	html_start = """
	<html>
		<body>
	"""

	html_end = """
		</body>
	</html>

	"""

	html_content = ""
	html_content += "<h1>General</h1>"

	for repository in REPOSITORIES:
		html_content += "</br>"
		html_content += "<h3>%s</h3>" % (repository.name)
		html_content += "<p>%s</p>" % (git_current_branch(repository.path).message)	
		
		go_to_develop_key = "go_to_develop_%s" % (repository.name)
		fetch_pull_key = "fetch_pull_%s" % (repository.name)

		ACTIONS[go_to_develop_key] = change_branch_func(repository.path, "develop")
		ACTIONS[fetch_pull_key] = fetch_pull_func(folder_c)

		html_content += _str_link(go_to_develop_key, "Go to develop %s" % (repository.name))
		html_content += _str_link(fetch_pull_key, "Fetch and pull %s" % (repository.name))

	for issue in placeholder_issues:
		html_content += "</br>"
		html_content += "<h2>%s</h2>" % (issue.title)
		for repository in REPOSITORIES:
			html_content += "<h3>%s</h3>" % (repository.name)
			key = "create_branch_%s_%s" % (repository.name, issue.identifier)
			branch_name = issue.generate_branch_name(repository)
			ACTIONS[key] = create_branch_func(repository.path, branch_name)

			print("D:: %s" % (branch_name))
			html_content += _str_link(key, "Create branch %s" % (branch_name))

	return html_start + html_content + html_end


def do_action(identifier):
	if not identifier in ACTIONS:
		print("do_action: Action not found %s" % (identifier))
		return False
	func = ACTIONS[identifier]

	print("do_action: Calling %s" % (func))
	return func()


def _str_link(href, label, in_li = True):
	content = """<a href="mano://%s">%s</a>"""	% (href, label)

	if in_li:
		return "<li>" + content + "</li>"

	return content

def change_branch_func(cwd, branch_name):
	def change_branch():
		return git_checkout(cwd, branch_name)

	return change_branch


def fetch_pull_func(cwd):
	def fetch_pull():
		result = git_fetch(cwd)

		if result.was_successful:
			return git_pull(cwd)
		return result

	return fetch_pull


def create_branch_func(cwd, name):
	def create_branch():
		return git_checkout_b(cwd, name)
	return create_branch


def merge_with_origin_develop_func(cwd):
	def merge_with_origin_develop():
		return git_merge_with_develop(cwd)

	return merge_with_origin_develop


def git_checkout_b(working_directory, branch_name):
	return run_process(["git", "checkout", "-b", branch_name], working_directory)


def git_checkout(working_directory, branch_name):
	return run_process(["git", "checkout", branch_name], working_directory)


def git_fetch(working_directory):
	return run_process(["git", "fetch"], working_directory)


def git_pull(working_directory):
	return run_process(["git", "pull"], working_directory)


def git_current_branch(working_directory):
	return run_process(["git", "branch", "--show-current"], working_directory)

def git_merge_with_develop(working_directory):
	return run_process(["git", "merge", "origin/develop"], working_directory)	


def run_process(args, working_directory):
	proc = Popen(args, stdout = PIPE, stderr = PIPE, cwd = working_directory)
	out, err = proc.communicate()
	exit_code = proc.returncode

	if DEBUG_PROCESS_CALLS:
		print("args: %s cwd: %s -> %s -> %s | %s" % (args, working_directory, str(exit_code), str(out), str(err)))

	if exit_code == 0:
		return Success(str(out).strip())
	return Failure(str(err), exit_code)

def redmine_list_users():
	REDMINE_TOKEN = os.environ["REDMINE_TOKEN"]
	REDMINE_URL = os.environ["REDMINE_URL"]
	REDMINE_HEADERS = {"X-Redmine-API-Key": REDMINE_TOKEN}

	response = requests.get("%s%s" % (REDMINE_URL, "users.json"), headers=REDMINE_HEADERS)
	response = response.json()
	print("Response: %s" % (response))

def redmine_list_issues():
	REDMINE_TOKEN = os.environ["REDMINE_TOKEN"]
	REDMINE_URL = os.environ["REDMINE_URL"]
	REDMINE_HEADERS = {"X-Redmine-API-Key": REDMINE_TOKEN}

	response = requests.get("%s%s" % (REDMINE_URL, "issues.json"), headers=REDMINE_HEADERS)
	response = response.json()
	print("Response: %s" % (response))	

