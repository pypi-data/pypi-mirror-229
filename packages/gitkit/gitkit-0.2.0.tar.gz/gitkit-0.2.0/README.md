# gitkit
A tool for analyzing and synchronizing git repositories with github

## Installation

`python3 -m pip install gitkit --upgrade`

**Test version**

`python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gitkit --upgrade`

## Usage
`gitkit [OPTIONS] COMMAND [ARGS]...`

### **Options:**

| Option           | Typ  | Description |
| ---------------- | ---- | ----------- |
| -t, --target-dir | TEXT | The local target/source path
| -u, --user       | TEXT | The github username
| -p, --password   | TEXT | The github password
| -l, --list       |      | Print results. Does not execute any command.
| --help           |      | Show this message and exit.

### **Commands:**

| Command | Description |
| ------- | ----------- |
| clone   | Clone repositories |
| commit  | Commit repositories |
| find    | Search local repositories |
| pull    | Pull repositories |
| push    | Push repositories |

#### **find Options:**

| Option                            | Description |
| --------------------------------- | ----------- |
| -p, --private / -np, --no-private | -p = Private only, -np = Public only - Default with private and public. |
| -f, --forks / -nf, --no-forks     | -f = Forks only, -nf = Without forks - Default with forks. |
| -o, --owner / -no, --no-owner     | -o = Owned only, -no = Not owned only - Default owned and not owned. |
| -d, --dirty / -nd, --no-dirty     | -d = Dirty only, -nd = Clean only - Default clean and dirty. |
| -a, --ahead / -na, --no-ahead     | -a = local branch is ahead of remote, -nd = local branch is not ahead of remote. Default both. |
| -b, --behind / -nb, --no-behind   | -b = local branch is behind remote, -nd = local branch is not behind remote. Default both. |
| -r, --remote                      | -r = Remote github repositories only. Default all. |
| --help |                          | Show this message and exit. |


**Samples:**
| Description | Command |
| ----------- | ------- |
| Help | `gitkit --help`    |
| Clone all repositories.   | `gitkit -u <USERNAME> -p <PASSWORD> -t /tmp/src/github clone` |
| Pull all repositories.    | `gitkit -u <USERNAME> -p <PASSWORD> -t /tmp/src/github pull` |
| Push all repositories.    | `gitkit -u <USERNAME> -p <PASSWORD> -t /tmp/src/github push` |
| Commit all repositories.  | `gitkit -u <USERNAME> -p <PASSWORD> -t /tmp/src/github commit` |
| Find all repositories     | `gitkit -t /tmp/src/github find` |
| Find all repositories     | `cd /your/path/ && gitkit find` |
| Find dirty repositories   | `gitkit -t /tmp/src/github find -d` |
| Find private repositories | `gitkit -t /tmp/src/github find -p` |
| Find private dirty repositories | `gitkit -t /tmp/src/github find -pd` |
| Find public repositories  | `gitkit -t /tmp/src/github find -np` |
| Find forked repositories  | `gitkit -t /tmp/src/github find -f` |
| Find owned repositories   | `gitkit -t /tmp/src/github find -o` |
| Find ahead remote repositories | `gitkit -t /tmp/src/github find -a` |
| Find behind remote repositories | `gitkit -t /tmp/src/github find -a` |
| Find not owned repositories |`gitkit -u dotupNET -t /tmp/src/github/ -l find -no`|
| Find remote, not cloned, repositories only |`gitkit -l find -r`|
| Push your own repositories | `gitkit -u <USERNAME> -p <PASSWORD> find -a -o push` |
| Stage, Commit and Push your own dirty repositories | `gitkit -u <USERNAME> -p <PASSWORD> find -o -d push -ac` |
| Pull your forked repositories | `gitkit -u <USERNAME> -p <PASSWORD> find -b -o -f pull` |

> Environment variable for user, password and target available
>
> ```ini
> user=XYZ
> password=XYZ
> target-dir=/tmp/src
> ```

### Grouped clone:

You can group your sources into different folders.

| Command       | Description |
| ------------- | ----------- |
| --group forks | Rpositories will be cloned into subfolder "forks" |
| --group owner | Rpositories will be cloned into subfolder, named with the github login name |

```bash
mkdir -p /tmp/src
cd /tmp/src
gitkit -u dotupNET -p TopSecret clone --group forks --group owner
```

**The target folders will be:**

For your own repositories: */tmp/src/dotupNET*

For your own forked repositories: */tmp/src/dotupNET/forks*

For repositories you don't own: */tmp/src/RepositoryOwner*

For forked repositories you don't own: */tmp/src/RepositoryOwner/forks*


https://github.com/dotupNET/gitkit
