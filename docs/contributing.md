# Contributing to maya-zen-tools

## For Contributors and Code Owners

1.  Clone and Install

    To install this project for development of *this library*,
    clone this repository (replacing "~/Code", below, with the directory
    under which you want your project to reside), then run `make`:

    ```bash
    cd ~/Code && \
    git clone\
    https://github.com/enorganic/maya-zen-tools.git maya-zen-tools && \
    cd maya-zen-tools && \
    make
    ```

2.  Create a new branch for your changes (replacing "descriptive-branch-name"
    with a *descriptive branch name*, and replacing *feature* with *bugfix*
    if the branch addresses a bug):

    ```shell
    git branch feature/descriptive-branch-name
    ```

3.  Make some changes.
4.  Format and lint your code:

    ```shell
    make format
    ```

5.  Test your changes:

    ```shell
    make test
    ```

6.  Push your changes and create a pull request.

## For Everyone Else

If you are not a contributor on this project, you can still create pull
requests, however you will need to fork this project, push changes
to your fork, and create a pull request from your forked repository.
