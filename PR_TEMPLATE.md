# InnoLab Frontend Pull Request Template

## Changes

Description of changes goes here.

## Pre Commit Checklist

1. Ensure code meets linting standards,

```shell
./scripts/lint
```

2. Ensure all new functionality is covered by unit tests. Run the tests locally and make sure coverage hasn't gone down,

```shell
yarn run test:cover
```

3. Document code with comments where appropriate.

4. Pull the latest version of `Dev` and merge with it locally (`git pull && git merge Dev`) before opening a PR request into Dev.

## Reviewer Checklist

- [] Application builds locally
- [] Unit tests pass locally
- [] Code passes linting style check
- [] All dead code has been removed
- [] No secrets or credentials have been committed
- [] No merge conflicts with target branch