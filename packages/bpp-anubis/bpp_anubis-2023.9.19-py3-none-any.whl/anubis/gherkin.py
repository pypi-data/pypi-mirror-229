from uuid import uuid4


class Row:
    def __init__(
            self,
            cells:    list = None,
            file:     str = None,
            line:     str = None
    ):
        self.cells    = [] if cells is None else cells
        self.file     = file if file is not None else ''
        self.line     = line if line is not None else ''
        self.path     = f'{self.file}:{self.line}'


class Table:
    def __init__(
            self,
            description: str = None,
            file:        str = None,
            line:        str = None,
            rows:        list[Row] = None
    ):
        self.description = '' if description is None else description
        self.file        = '' if file is None else file
        self.line        = '' if line is None else line
        self.id          = uuid4()
        self.path        = f'{self.file}:{self.line}' if self.file and self.line else ''
        self.rows        = [] if rows is None else rows

    def __bool__(self):
        return bool(self.rows)


class SimpleGherkin:
    def __init__(
            self,
            description: str = None,
            file:        str = None,
            keyword:     str = None,
            line:        str = None
    ):
        self.description = '' if description is None else description
        self.id          = uuid4()
        self.file        = '' if file is None else file
        self.keyword     = '' if keyword is None else keyword
        self.line        = '' if line is None else line
        self.path        = f'{self.file}:{self.line}' if self.file and self.line else ''

    def __repr__(self):
        return f'{self.keyword}: {self.description}'

    def __bool__(self):
        return bool(self.keyword and self.description)


class Step(SimpleGherkin):
    def __init__(
            self,
            description: str   = None,
            file:        str   = None,
            keyword:     str   = None,
            line:        str   = None,
            table:       Table = None
    ):
        super().__init__(description, file, keyword, line)
        self.table = Table() if table is None else table


class Background(SimpleGherkin):
    def __init__(
            self,
            description: str = None,
            file:        str = None,
            line:        str = None,
            steps:       list[Step] = None
    ):
        super().__init__(description, file, 'Background', line)
        self.steps = [] if steps is None else steps


class Test(SimpleGherkin):
    def __init__(
            self,
            background:  Background = None,
            description: str = None,
            file:        str = None,
            keyword:     str = None,
            line:        str = None,
            tags:        list = None,
            steps:       list[Step] = None,
            tables:      list[Table] = None
    ):
        super().__init__(description, file, keyword, line)
        self.background = Background() if background is None else background
        self.tags       = [] if tags is None else tags
        self.tables     = [] if tables is None else tables
        self.steps      = self.background.steps + ([] if steps is None else steps)
        self.path       = f'{self.file}:{self.line}' if self.file and self.line else ''

    def is_testable_based_on_tags(self, tag_expression):
        # compare tags to tag expression
        if not tag_expression:
            return True
        if not self.tags:
            return False

        # separate included and excluded tags
        excluded_tags = [t for e in tag_expression for t in e if t.startswith('~')]
        tag_expression = [[t for t in group if t not in excluded_tags] for group in tag_expression]

        # boolean logic to figure out if the test should run
        matches = []
        for expr in tag_expression:
            res = all([t in self.tags for t in expr])
            matches.append(res)
        return any(matches) and all([t.replace('~', '') not in self.tags for t in excluded_tags if t.startswith('~')])

    def get_test_lines(self):
        entire_test = [self.location]
        examples = [row.location for table in self.tables for row in table.rows[1:]]  # exclude the header row

        return {
            'test': entire_test,
            'examples': examples
        }


class Feature:
    def __init__(
            self,
            description: str = None,
            background:  Background = None,
            file:        str = None,
            line:        str = None,
            tags:        list = None,
            tests:       list[Test] = None
    ):
        self.background  = Background() if background is None else background
        self.description = '' if description is None else description
        self.id          = uuid4()
        self.keyword     = 'Feature'
        self.file        = file
        self.line        = line
        self.path        = f'{self.file}:{self.line}' if self.file and self.line else ''
        self.tags        = [] if tags is None else tags
        self.tests       = [] if tests is None else tests

        for test in self.tests:
            test.background = self.background
            test.tags.extend(self.tags)

    def __repr__(self):
        return f'Feature: {self.description}'

    def __str__(self):
        return f'Feature: {self.description}\n' + '\n'.join([f'\t{t.keyword}: {t.description}' for t in self.tests])

    def get_testable_tests(self, tag_expression):
        return [t for t in self.tests if t.is_testable_based_on_tags(tag_expression)]
