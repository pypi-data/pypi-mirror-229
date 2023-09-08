from os.path import join
from subprocess import call, STDOUT, DEVNULL


def command_generator(arguments: dict) -> str:
    pgi, tests, args, args_unknown = arguments

    # get arguments and construct the behave command
    results_json_file = join(args.output, f'{pgi}.json')
    user_defs = ' '.join('-D "{}"'.format(arg) for arg in args.D) if args.D else ''
    tags = ' '.join('--tags "{}"'.format(','.join(t for t in g)) for g in args.tags)
    stage = f'--stage="{args.stage}"' if args.stage else ''
    output = f'-f json -o "{join(args.output, str(pgi))}.json"'

    command = (
        f'behave {stage} -D "parallel={pgi}" {user_defs}'
        f' {tags} {output} {" ".join(args_unknown)} '
    )

    feature_files = set(thing.path.split(':')[0] for thing in tests)
    if args.unit not in ['feature', 'example', 'scenario']:
        args.unit = 'scenario'

    if args.unit == 'feature':
        command += ' '.join(feature_files)
    else:
        command += ' '.join(thing.path for thing in tests)

    if args.dry_run:
        print(command)
        return ''

    if args.verbose:
        print(command)
        call(command, shell=True)
    else:
        call(command, shell=True, stdout=DEVNULL, stderr=STDOUT)

    return results_json_file
