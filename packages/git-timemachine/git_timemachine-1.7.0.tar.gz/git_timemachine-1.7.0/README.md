<p align="center">
    <img src="https://raw.githubusercontent.com/he-yaowen/git-timemachine/main/logo/git-timemachine.png" alt="Logo"/>
</p>

![license](https://img.shields.io/github/license/he-yaowen/git-timemachine)
![build](https://img.shields.io/github/actions/workflow/status/he-yaowen/git-timemachine/ubuntu-jammy.yml)
![version](https://img.shields.io/pypi/v/git-timemachine)
![python](https://img.shields.io/pypi/pyversions/git-timemachine)
![format](https://img.shields.io/pypi/format/git-timemachine)
![implementation](https://img.shields.io/pypi/implementation/git-timemachine)
![downloads](https://img.shields.io/pypi/dm/git-timemachine)

# git-timemachine

A command-line tool that helps you record commits on [Git][1] repositories at
any time node.

## Features

* Show commit logs of a repository in specified format.
* Check consistence of commit logs.
* Record a commit on repository at the specified time node.
* Review commit logs.
* Limit maximum commits per day.

## Installation

To install git-timemachine, you can:

1. Install git-timemachine via `pip`:

    ```
    pip install --user --upgrade git-timemachine
    ```

2. Download from [Releases][2], make sure command `git-timemachine` is in
   your `$PATH` environment variable.

## License

Copyright (C) 2022 HE Yaowen <he.yaowen@hotmail.com>

The GNU General Public License (GPL) version 3, see [COPYING](./COPYING).

[1]: https://git-scm.com/

[2]: https://github.com/he-yaowen/git-timemachine/releases
