# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import nox


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["linters"]


@nox.session(python='3')
def bindep(session):
    session.install('bindep')
    session.run('bindep', 'test')


@nox.session(python='3')
def docs(session):
    session.install('-r', 'doc/requirements.txt',
                    '-r', 'test-requirements.txt')
    session.install('-e', '.')
    session.run('sphinx-build', '-E', '-W', '-d', 'doc/build/doctrees',
                '-b', 'html', 'doc/source/', 'doc/build/html')


@nox.session(python='3')
def linters(session):
    session.install('-r', 'requirements.txt',
                    '-r', 'test-requirements.txt')
    session.install('flake8')
    session.run('flake8', *session.posargs)
    session.run('bash', '-c', '"cd roles; find . -type f -regex '
                '\'.*.y[a]?ml\' -print0 | xargs -t -n1 -0 ansible-lint"')


@nox.session(python='3')
def venv(session):
    session.install('-r', 'requirements.txt',
                    '-r', 'test-requirements.txt')
    session.install('-e', '.')
    session.run(*session.posargs)
