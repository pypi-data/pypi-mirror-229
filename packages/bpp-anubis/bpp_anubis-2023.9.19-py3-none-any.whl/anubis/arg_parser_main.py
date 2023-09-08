import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser('Running in parallel mode')
    # anubis-specific stuff
    parser.add_argument('--aggregate', required=False, default='aggregate.json')
    parser.add_argument('--env', required=True, type=str)
    parser.add_argument('--feature_dir', required=False, default=['features'], nargs='*')
    parser.add_argument('--junit', required=False, type=str, default='results.xml')
    parser.add_argument('--output', required=False, default='.tempoutput')
    parser.add_argument('--pass-threshold', required=False, type=float, default=1.0)
    parser.add_argument('--processes', required=False, default=5, type=int)
    parser.add_argument('--unit', required=False, type=str, default='scenario')
    parser.add_argument('--log-file', type=str, default='latest.log')

    # flags
    parser.add_argument('--dry-run', required=False, action='store_true')
    parser.add_argument('--hide-failed', required=False, action='store_true')
    parser.add_argument('--hide-passed', required=False, action='store_true')
    parser.add_argument('--hide-summary', required=False, action='store_true')
    parser.add_argument('--pass-with-no-tests', required=False, action='store_true')
    parser.add_argument('--verbose', required=False, action='store_true')

    # sent directly to behave
    parser.add_argument('--stage', required=True, type=str)
    parser.add_argument('--tags', required=False, nargs='*', action='append', default=[])
    parser.add_argument('-D', required=False, nargs='*')

    known, unknown = parser.parse_known_args()

    # format anything that needs to be formatted
    # output files
    known.output = os.path.join(os.getcwd(), known.output)
    known.aggregate = os.path.join(known.output, known.aggregate)
    known.junit = os.path.join(known.output, known.junit)
    known.log_file = os.path.join(known.output, known.log_file)

    # misc updates to D
    known.D.append(f'env="{known.env}"')

    return known, unknown
