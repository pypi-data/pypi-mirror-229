import pytest
import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import subprocess
from semv.interface import Version
from semv.version_control_system import Git, sanitize_commit_json, RawCommit


@pytest.fixture
def git_repo():
    with TemporaryDirectory() as td:
        subprocess.run(
            'git init',
            shell=True,
            cwd=td,
        )
        subprocess.run('git config user.name "tester"', shell=True, cwd=td)
        subprocess.run('git config user.email "tester"', shell=True, cwd=td)
        yield Repo(td)


class TestCurrentVersion:
    def test_tagged_version(self, git_repo):
        git_repo: Repo
        git_repo.add_to_file('test.txt', 'First line')
        git_repo.git('add test.txt')
        git_repo.git('commit -m "First commit"')
        git_repo.git('tag v1.0.0')
        git_repo.add_to_file('test.txt', 'Second line')
        git_repo.git('add test.txt')
        git_repo.git('commit -m "Second commit"')

        with git_repo.as_working_dir():
            g = Git()
            assert str(g.get_current_version()) == 'v1.0.0'

    def test_default_version_if_no_tags(self, git_repo):
        git_repo: Repo
        git_repo.add_to_file('test.txt', 'First line')
        git_repo.git('add test.txt')
        git_repo.git('commit -m "First commit"')
        with git_repo.as_working_dir():
            g = Git()
            assert str(g.get_current_version()) == 'v0.0.0'


class TestCommitsWithout:
    def test_commits_without(self, git_repo):
        git_repo: Repo
        git_repo.commit_change('test.txt', 'First line', 'First commit')
        git_repo.commit_change('test.txt', 'Second line', 'Second commit')
        git_repo.git('tag v1.0.0')
        git_repo.commit_change('test.txt', 'Third line', 'Third commit')
        git_repo.commit_change('test.txt', 'Fourth line', 'Fourth commit')

        with git_repo.as_working_dir():
            g = Git()
            commits = g.get_commits_without(Version(major=1, minor=0, patch=0))
            titles = set(c.title for c in commits)
            assert titles == {'Third commit', 'Fourth commit'}


class TestSanitizeJsonCommit:
    def test_sane_commit_message(self):
        rc = sanitize_commit_json(
            '{"sha": "d938a11", "title": "test(unit): testing", "body": ""}'
        )
        assert rc == RawCommit(
            sha='d938a11', title='test(unit): testing', body=''
        )

    def test_line_break_at_end_of_body(self):
        rc = sanitize_commit_json(
            '{"sha": "d938a11", "title": "test(unit): testing", "body": "some text\n"}'
        )
        assert rc == RawCommit(
            sha='d938a11', title='test(unit): testing', body='some text'
        )

    def test_double_quotes_in_title(self):
        rc = sanitize_commit_json(
            '{"sha": "d938a11", "title": "Reverts commit "test(unit): testing"", "body": ""}'
        )
        assert rc == RawCommit(
            sha='d938a11', title='Reverts commit "test(unit): testing"', body=''
        )


class Repo:
    def __init__(self, d: str):
        self.d = d

    def git(self, cmd: str):
        subprocess.run('git ' + cmd, shell=True, cwd=self.d)

    def add_to_file(self, name: str, text: str):
        with open(os.path.join(self.d, name), 'a') as f:
            f.write(text + '\n')

    def commit_change(self, filename: str, newline: str, msg: str):
        self.add_to_file(filename, newline)
        self.git(f'add {filename}')
        self.git(f'commit -m "{msg}"')

    @contextmanager
    def as_working_dir(self):
        old_wd = os.getcwd()
        try:
            os.chdir(self.d)
            yield
        finally:
            os.chdir(old_wd)
