# __main__.py
import os
import sys
import shutil
from datetime import datetime
from multiprocessing import Pool
from random import choice
from anubis import feature_file_parser, arg_parser_main, feature_splitter, results
from anubis.parallelizer import command_generator
from anubis.copy import art, power
import logging


def main():
    # Misc Setup ---------------------------------------------------------------------------------
    start = datetime.now()
    args, args_unknown = arg_parser_main.parse_arguments()
    print(
        choice(art) + '\nRunning tests with Anubis  |  powered by ' + choice(power),
        end='\n\n') if args.verbose else None

    # Set up output dirs and files ---------------------------------------------------------------------------------
    # create a directory that will contain results and be exported
    print(f'--- Setting Up Output\n\tSending output to <{args.output}>') if args.verbose else None

    if os.path.isdir(args.output):
        shutil.rmtree(args.output)
    os.makedirs(args.output, exist_ok=True)

    # set up logging
    logging.basicConfig(
        filename=args.log_file,
        filemode='w',
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    root_logger = logging.getLogger()
    root_logger.info('Args: \n\t' + "\n\t".join(a.__repr__() for a in args._get_kwargs()))

    # Group features and tests ---------------------------------------------------------------------------------
    if args.verbose:
        print('\n--- Grouping Tests')
        print('\tfeatures: <' + ", ".join(d for d in args.feature_dir) + '>')
        print(f'\ttags: <{", ".join(str(g) for g in args.tags) if args.tags else "n/a"}>')

    # get all features and testable tests
    features = feature_file_parser.get_parsed_gherkin(args.feature_dir)
    features_with_tests = [f for f in features if f.get_testable_tests(args.tags)]

    # split the features into groups as evenly as possible
    tests_to_run = feature_splitter.get_grouped_tests(
        features_with_tests,
        args.tags,
        args.processes,  # max number of processes
        args.unit,  # unit to split by
    )

    logging.info('\n\t' + '\n\t'.join(str(group) for group in tests_to_run))

    # make the args available to each group
    for group in tests_to_run:
        group.extend([args, args_unknown])

    # Run the tests ---------------------------------------------------------------------------------
    # run all the processes and save the locations of the result files
    num_groups = len(tests_to_run)
    passed, failed, total = 0, 0, 0
    if args.verbose and not args.dry_run:
        print(f'\n--- RUNNING IN <{num_groups}> PROCESS{"ES" * int(num_groups > 1)}\n')

    if tests_to_run:
        # set up the multiple processes
        pool = Pool(args.processes)
        result_files = pool.map(command_generator, tests_to_run)
        logging.info(f'output files: {result_files}')

        results.write_result_aggregate(files=result_files, aggregate_out_file=args.aggregate)

        if args.dry_run:
            return 0

        # do the math to print out the results summary
        results.write_junit(args.aggregate, args.junit)
        passed, failed, total = results.get_result_values(args.aggregate)
        end = datetime.now()
        results.print_result_summary(args, args.D, start, end, passed, failed)
        root_logger.info(f'passed: {passed}')
        root_logger.info(f'failed: {failed}')

    shutil.rmtree(args.output) if args.output.endswith('.tempoutput') else None

    # exit correctly
    if args.pass_with_no_tests or not tests_to_run or total == 0:
        print('𓃥 no tests found --> this run passes by default 𓃥')
        return 0
    return 0 if passed / total >= args.pass_threshold else 1


if __name__ == '__main__':
    # run everything
    sys.exit(main())
