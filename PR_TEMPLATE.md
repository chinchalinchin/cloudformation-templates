# InnoLab Frontend Pull Request Template

## Changes

Description of changes goes here.

## Pre Commit Checklist

1. Ensure code meets linting standards,

```shell
./scripts/lint
```

2. Ensure all new functionality does not introduce security vulnerabilities

```shell
./scripts/scan
```

3. Document code with comments where appropriate.

4. Pull the latest version of `Dev` and merge with it locally (`git pull && git merge Dev`) before opening a PR request into Dev.