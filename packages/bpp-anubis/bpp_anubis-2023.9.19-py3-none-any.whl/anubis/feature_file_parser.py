import re
from anubis.gherkin import Background, Feature, Row, Step, Test, Table
from glob import glob
from os.path import join
from typing import Tuple, Union


breaking_kwds = [
    'Feature',
    'Rule',
    # 'Example',
]

section_kwds = [
    'Background',
    'Scenario Outline',
    'Scenario Template',
    'Scenario',
]

step_kwds = [
    'Given',
    'When',
    'Then',
    'And',
    'But',
    r'\*',
]

primary_kw = [
    'Scenarios',
    'Examples',
]

meta_kw = ['|', '@']
ignore_kw = ['"""', '#']


def __get_kw_and_description(line: str) -> Tuple[Union[str, None], Union[str, None]]:
    kwds = breaking_kwds + section_kwds + step_kwds + primary_kw
    pattern = re.compile(r'^(?P<kw>' + "|".join(kw for kw in kwds) + ')(:)?(?P<description>.*)$')
    match = re.match(pattern, line)
    if match:
        return match.group('kw'), match.group('description').lstrip().rstrip()
    return None, None


def better_gherkin_parser(fp):
    with open(fp, 'r') as f:
        lines = [line.lstrip().replace('\n', '') for line in f.readlines()]
    lines.reverse()

    feature = None
    tests = []
    steps = []
    background = Background()
    current_test = Test()
    current_test_tables = []
    current_table = Table()

    for ln, line in enumerate(lines):
        line_num = str(len(lines) - ln)

        if any([line.startswith(kw) for kw in step_kwds]):
            kw, desc = __get_kw_and_description(line)
            steps.append(Step(desc, fp, kw, line_num, current_table))
            current_table = Table()
        elif any([line.startswith(kw) for kw in section_kwds]) or line.startswith('Background'):
            kw, desc = __get_kw_and_description(line)
            steps.reverse()

            current_test.file = fp
            current_test.line = line_num
            current_test.steps = steps
            current_test.path = f'{fp}:{line_num}'

            if kw != 'Background':
                current_test.description = desc
                current_test.keyword = kw
                current_test.tables = current_test_tables
                tests.append(current_test)
                current_test = Test()
            else:
                background.steps = steps
                background.description = desc

            current_test_tables = []
            current_table = Table()
            steps = []
        elif line.startswith('@'):
            (tests[-1] if ln != len(lines) - 1 else feature).tags.extend([tag.replace('@', '') for tag in line.split()])
        elif line.startswith('|'):
            current_table.rows.append(
                Row([data.strip() for data in line.split('|') if data], fp, line_num))
        elif line.startswith('Examples'):
            current_table.rows.reverse()
            current_test_tables.append(current_table)
            current_table = Table()
        elif line.startswith('Feature'):
            tests.reverse()
            feature = Feature(
                description=__get_kw_and_description(line)[1],
                background=background,
                file=fp,
                line=line_num,
                tests=tests
            )
    return feature


def get_parsed_gherkin(feature_dir):
    all_paths = []
    parsed_gherkin = []

    for directory in feature_dir:
        all_paths.extend(glob(join(directory, '**', '*.feature'), recursive=True))

    for fp in all_paths:
        parsed_gherkin.append(better_gherkin_parser(fp))
    return parsed_gherkin
