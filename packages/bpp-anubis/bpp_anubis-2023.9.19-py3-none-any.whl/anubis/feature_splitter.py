from random import shuffle
from enum import StrEnum


class Unit(StrEnum):
    SCENARIO = 'scenario'
    FEATURE = 'feature'
    EXAMPLE = 'example'


def matches_tag_expression(scenario_tags, tag_expression):
    # handle trivial cases
    if not tag_expression:
        return True
    if not scenario_tags:
        return False

    # separate included and excluded tags
    excluded_tags = [t for e in tag_expression for t in e if t.startswith('~')]
    tag_expression = [[t for t in group if t not in excluded_tags] for group in tag_expression]

    # boolean logic to figure out if the test should run
    matches = []
    for expr in tag_expression:
        res = all([t in scenario_tags for t in expr])
        matches.append(res)
    return any(matches) and all([t.replace('~', '') not in scenario_tags for t in excluded_tags if t.startswith('~')])


def get_grouped_tests(features, tags, num_split, unit=None, shuffle_paths=True):
    # split as evenly as possible
    # it's ugly, sorry
    paths = []
    all_tests = []

    for feature in features:

        if unit == Unit.SCENARIO:
            all_tests.extend(feature.get_testable_tests(tags))
        elif unit == Unit.FEATURE:
            all_tests.append(feature)
        elif unit == Unit.EXAMPLE:
            tests = feature.get_testable_tests(tags)
            scenarios = [t for t in tests if t.keyword.lower() == 'scenario']
            examples = [row for test in tests for table in test.tables for row in table.rows[1:]
                        if test.keyword.lower() == 'scenario outline']
            all_tests.extend(scenarios)
            all_tests.extend(examples)

    inc_other = -(-len(all_tests) // num_split)

    if shuffle_paths:
        shuffle(paths)
        shuffle(all_tests)
    test_groups = [all_tests[i:i + inc_other] for i in range(0, len(all_tests), inc_other)]

    return [[i, group] for i, group in enumerate(test_groups)]
