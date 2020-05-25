#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DCASE 2020 Challenge Task 1: Submission validator
# ---------------------------------------------
# Author: Toni Heittola ( toni.heittola@tuni.fi ), Tampere University / Audio Research Group
# License: MIT

import sys
import argparse
import zipfile
from utils import *
from validators import *

try:
    import yaml
except ImportError:
    raise ImportError('Unable to import YAML module. You can install it with `pip install pyyaml`.')


def main(argv):
    param = {
        'filename': {

        },
        'A': {
            'output': {
                'fields': ['filename', 'scene_label', 'airport', 'bus', 'metro', 'metro_station',
                           'park', 'public_square', 'shopping_mall', 'street_pedestrian', 'street_traffic', 'tram'],
                'fields_float': ['airport', 'shopping_mall', 'metro_station', 'street_pedestrian',
                    'public_square', 'street_traffic', 'tram', 'bus', 'metro', 'park'],
                'scene_labels': [
                    'airport', 'shopping_mall', 'metro_station', 'street_pedestrian',
                    'public_square', 'street_traffic', 'tram', 'bus', 'metro', 'park'],
                'filename': {
                    'index_min': 0,
                    'index_max': 11879,
                },
                'unique_file_count': 11880
            },
            'meta': {
                'submission': {
                    'required_fields': ['label', 'name', 'abbreviation', 'authors'],
                    'authors': {
                        'required_fields': ['lastname', 'firstname', 'email', 'affiliation'],
                    }
                },
                'system': {
                    'required_fields': ['description', 'complexity', 'external_datasets', 'source_code'],
                    'description': {
                        'required_fields': ['input_sampling_rate', 'acoustic_features', 'embeddings', 'data_augmentation', 'machine_learning_method', 'ensemble_method_subsystem_count', 'decision_making', 'external_data_usage'],
                    },
                    'complexity': {
                        'required_fields': ['total_parameters']
                    },
                    'external_datasets': {
                        'required_fields': ['name', 'url', 'total_audio_length']
                    }
                },
                'results': {
                    'required_fields': ['development_dataset'],
                    'development_dataset': {
                        'required_fields': ['overall', 'class_wise', 'device_wise'],
                        'overall': {
                            'required_fields': ['accuracy', 'logloss'],
                        },
                        'class_wise': {
                            'required_fields': ['airport', 'shopping_mall', 'metro_station', 'street_pedestrian',
                                                'public_square', 'street_traffic', 'tram', 'bus', 'metro', 'park'],
                            'required_fields_per_item': ['accuracy', 'logloss']

                        },
                        'device_wise': {
                            'required_fields': ['a', 'b', 'c', 's1', 's2', 's3', 's4', 's5', 's6'],
                            'required_fields_per_item': ['accuracy', 'logloss']
                        }
                    }
                }
            }
        },
        'B': {
            'output': {
                'fields': ['filename', 'scene_label', 'indoor', 'outdoor', 'transportation'],
                'fields_float': ['indoor', 'outdoor', 'transportation'],
                'scene_labels': ['indoor', 'outdoor', 'transportation'],
                'filename': {
                    'index_min': 0,
                    'index_max': 8639,
                },
                'unique_file_count': 8640
            },
            'meta': {
                'submission': {
                    'required_fields': ['label', 'name', 'abbreviation', 'authors'],
                    'authors': {
                        'required_fields': ['lastname', 'firstname', 'email', 'affiliation'],
                    }
                },
                'system': {
                    'required_fields': ['description', 'complexity', 'external_datasets', 'source_code'],
                    'description': {
                        'required_fields': ['input_sampling_rate', 'acoustic_features', 'embeddings',
                                            'data_augmentation', 'machine_learning_method',
                                            'ensemble_method_subsystem_count', 'decision_making',
                                            'external_data_usage', 'complexity_management'],
                    },
                    'complexity': {
                        'required_fields': ['total_parameters', 'total_parameters_non_zero', 'model_size']
                    },
                    'external_datasets': {
                        'required_fields': ['name', 'url', 'total_audio_length']
                    }
                },
                'results': {
                    'required_fields': ['development_dataset'],
                    'development_dataset': {
                        'required_fields': ['overall', 'class_wise'],
                        'overall': {
                            'required_fields': ['accuracy', 'logloss'],
                        },
                        'class_wise': {
                            'required_fields': ['indoor', 'outdoor', 'transportation'],
                            'required_fields_per_item': ['accuracy', 'logloss']

                        }
                    }
                }
            }
        },
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--package', help='Submission package', type=str)
    parser.add_argument('-t', '--task', help='Task selector: A or B', type=str)
    parser.add_argument('-o', '--output', help='System output file in CSV format', type=str)
    parser.add_argument('-m', '--meta', help='System meta information file in YAML format', type=str)
    args = parser.parse_args()

    error_count = 0

    print('Task1 submission checker')
    print('======================================================')

    if args.package is not None:
        if not os.path.exists(args.package):
            raise IOError('Package file not found [{filename:}]'.format(filename=args.package))
        print('Validating ZIP package [{filename:}]'.format(filename=args.package))
        print('------------------------------------------------------')
        print('')
        with zipfile.ZipFile(args.package, "r") as z:
            # Check for bad files in zip package
            bad_files = z.testzip()
            if bad_files:
                print_error('ZIP', 'Bad files found in ZIP package.')

            # Collect files from the package
            file_list = z.namelist()
            task_files = {}
            for name in file_list:
                file_info = z.getinfo(name)
                if not file_info.is_dir() and 'task1' in name and '.pdf' not in name:
                    path_parts = os.path.split(name)[0].split('/')
                    subtask = path_parts[2].split('_')[2]

                    if subtask not in task_files:
                        if subtask not in ['task1a', 'task1b']:
                            print_error('ZIP', 'Unknown task indicator [{tag:}] in [{name:}]'.format(tag=subtask, name=name))
                        else:
                            task_files[subtask] = {}

                    submission_label = path_parts[2]
                    if submission_label not in task_files[subtask]:
                        task_files[subtask][submission_label] = {}

                    if '.output.csv' in name:
                        task_files[subtask][submission_label]['output'] = name
                    elif '.meta.yaml' in name:
                        task_files[subtask][submission_label]['meta'] = name
                    else:
                        print_error('ZIP', 'Possibly wrongly formatted filename [{filename:s}]'.format(filename=name))

            for subtask in task_files:
                if 'task1a' in subtask.lower():
                    subtask_index = 'A'

                elif 'task1b' in subtask.lower():
                    subtask_index = 'B'

                for submission_label in task_files[subtask]:
                    print('Validate [{subtask:} -> {submission_label:}]'.format(subtask=subtask, submission_label=submission_label))
                    print('------------------------------------------------------')

                    output_filename = os.path.split(task_files[subtask][submission_label]['output'])[-1]
                    meta_filename = os.path.split(task_files[subtask][submission_label]['meta'])[-1]

                    # Load output data
                    print(' Output file: [{filename}]'.format(filename=task_files[subtask][submission_label]['output']))
                    with z.open(task_files[subtask][submission_label]['output'], 'r') as file:
                        output = file.read()

                    # Check data
                    error_count += validate_output(data=output.decode("utf-8"), param=param[subtask_index]['output'])

                    print('')

                    # Load meta data
                    print(' Meta file:   [{filename}]'.format(filename=task_files[subtask][submission_label]['meta']))
                    try:
                        with z.open(task_files[subtask][submission_label]['meta'], 'r') as infile:
                            meta = yaml.load(infile, Loader=yaml.FullLoader)

                    except yaml.YAMLError as exc:
                        print_error('meta', 'Wrongly formatted YAML file, see error below.')

                        if hasattr(exc, 'problem_mark'):
                            error = ["Error while parsing YAML file [{file}]".format(file=meta_filename)]
                            if exc.context is not None:
                                error.append(str(exc.problem_mark) + '\n  ' + str(exc.problem) + ' ' + str(exc.context))
                                error.append('  Please correct meta file and retry.')

                            else:
                                error.append(str(exc.problem_mark) + '\n  ' + str(exc.problem))
                                error.append('  Please correct meta file  and retry.')
                            raise IOError('\n'.join(error))

                        else:
                            raise IOError("Something went wrong while parsing yaml file [{file}]".format(file=meta_filename))

                    # Check data
                    error_count += validate_meta_data(meta, subtask, param[subtask_index]['meta'])
                    error_count += validate_submission_label(output_filename, meta_filename, meta['submission']['label'])

                    if submission_label != meta['submission']['label']:
                        print_error('label', 'Submission label used in the dir/filenames and meta information differs [{submission_label:} != {submission_label_meta:}]'.format(
                            submission_label=submission_label,
                            submission_label_meta=meta['submission']['label']
                        ))
                    print()

    else:
        # Check arguments
        if args.task.lower() not in ['a', 'b']:
            raise ValueError('Illegal task selector {selector:}'.format(args.task))

        if args.output is None:
            raise ValueError('Please give system output file')

        if args.meta is None:
            raise ValueError('Please give system meta information')

        if not os.path.exists(args.output):
            raise IOError('System output file not found [{filename:}]'.format(filename=args.output))

        if not os.path.exists(args.meta):
            raise IOError('System meta information file not found [{filename:}]'.format(filename=args.meta))

        # Get subtask label and index
        if args.task.lower() == 'a':
            subtask_index = 'A'
            subtask_label = 'task1a'

        elif args.task.lower() == 'b':
            subtask_index = 'B'
            subtask_label = 'task1b'

        # Check file naming
        output_filename = os.path.split(args.output)[-1]
        output_filename_parts = output_filename.split('.')
        output_submission_label = output_filename_parts[0].split('_')

        # Check filename formatting for output file
        if len(output_filename_parts) != 3:
            print_error('filename', [
                'System output has filename in wrong format [{filename:}]'.format(filename=output_filename),
                'Correct format is [SUBMISSION LABEL].output.csv'
            ])
            error_count += 1

        if output_submission_label[2] != subtask_label:
            print_error('label', [
                'Submission label in system OUTPUT filename is wrong [{filename:}]'.format(filename=output_filename),
                'Correct format is [AUTHORLASTNAME]_[INSTITUTE]_[{subtask:}]_[1-4]'.format(subtask=subtask_label)
            ])
            error_count += 1
        else:
            if int(output_submission_label[3]) > 4 or int(output_submission_label[3]) < 1:
                print_error('label', [
                    'Submission label in system OUTPUT filename is wrong [{filename:}]'.format(filename=output_filename),
                    'Submission index number in submission label has to be 1-4'
                ])
                error_count += 1

        meta_filename = os.path.split(args.meta)[-1]
        meta_filename_parts = meta_filename.split('.')
        meta_submission_label = meta_filename_parts[0].split('_')

        # Check filename formatting for meta file
        if len(meta_filename_parts) != 3:
            print_error('filename', [
                'System meta information has filename in wrong format [{filename:}]'.format(filename=meta_filename),
                'Correct format is [SUBMISSION LABEL].meta.yaml'
            ])
            error_count += 1

        if meta_submission_label[2] != subtask_label:
            print_error('label', [
                'Submission label in system META information filename is wrong [{filename:}]'.format(filename=meta_filename),
                'Correct format is [AUTHORLASTNAME]_[INSTITUTE]_[{subtask:}]_[1-4]'.format(subtask=subtask_label)
            ])
            error_count += 1

        else:
            if int(meta_submission_label[3]) > 4 or int(meta_submission_label[3]) < 1:
                print_error('label', [
                    'Submission label in system META information filename is wrong [{filename:}]'.format(filename=meta_filename),
                    'Submission index number in submission label has to be 1-4'
                ])
                error_count += 1

        # Load output data
        print(' Output file: [{filename}]'.format(filename=args.output))
        with open(args.output, 'r') as file:
            output = file.read()

        # Check data
        error_count += validate_output(data=output, param=param[subtask_index]['output'])

        print('')

        # Load meta data
        print(' Meta file:   [{filename}]'.format(filename=args.meta))
        try:
            with open(args.meta, 'r') as infile:
                meta = yaml.load(infile, Loader=yaml.FullLoader)

        except yaml.YAMLError as exc:
            print('[ERR] [META]     Wrongly formatted YAML file, see error below')
            print(' ')
            error_count += 1

            if hasattr(exc, 'problem_mark'):
                error = ["Error while parsing YAML file [{file}]".format(file=meta_filename)]
                if exc.context is not None:
                    error.append(str(exc.problem_mark) + '\n  ' + str(exc.problem) + ' ' + str(exc.context))
                    error.append('  Please correct meta file and retry.')

                else:
                    error.append(str(exc.problem_mark) + '\n  ' + str(exc.problem))
                    error.append('  Please correct meta file  and retry.')
                raise IOError('\n'.join(error))

            else:
                raise IOError("Something went wrong while parsing yaml file [{file}]".format(file=meta_filename))

        # Check data
        error_count += validate_meta_data(meta, subtask_label, param[subtask_index]['meta'])
        error_count += validate_submission_label(output_filename, meta_filename, meta['submission']['label'])

    if error_count == 0:
        print('------------------------------------------------------')
        print('No errors found!')
        print('Files are ready for submission to DCASE2020 Challenge.')

    else:
        print('------------------------------------------------------')
        print('In total {count:} errors found, please correct them before submitting to the challenge.'.format(count=error_count))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
