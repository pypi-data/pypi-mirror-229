from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz


class BaseCz(ConventionalCommitsCz):
    def schema_pattern(self) -> str:
        PATTERN = (
            r"(feat|fix|security|change|refactor|prepare|perf|deprecate|remove|revert|style|test|docs|build|chore)"
            r"(\(\S+\))?!?:(\s.*)"
        )
        return PATTERN
