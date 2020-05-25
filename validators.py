#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Toni Heittola ( toni.heittola@tuni.fi ), Tampere University / Audio Research Group
# License: MIT

from utils import *
import csv
import os
from io import StringIO


def print_error(error_type, message):
    if isinstance(message, list):
        for line_id, line in enumerate(message):
            if line_id == 0:
                print('  [{type:6s}]    {message:s}'.format(type=error_type.upper(), message=line))
            else:
                print('               {message:s}'.format(message=line))

    else:
        print('  [{type:6s}]    {message:}'.format(type=error_type.upper(), message=message))


def validate_submission_label(output_filename, meta_filename, submission_label):
    error_count = 0

    output_filename_parts = output_filename.split('.')

    meta_filename_parts = meta_filename.split('.')

    if output_filename_parts[0] != submission_label:
        print_error('LABEL', 'Submission label and filename for system output do not match [{value:} != {filename:}]'.format(
                value=submission_label, filename=output_filename))
        error_count += 1

    if meta_filename_parts[0] != submission_label:
        print_error('LABEL', 'Submission label and filename for meta information do not match [{value:} != {filename:}]'.format(
                value=submission_label, filename=output_filename))

        error_count += 1

    return error_count


def validate_output(data, param):
    error_count = 0

    f = StringIO(data)
    csv_reader = csv.reader(f, delimiter='\t')
    csv_fields = next(csv_reader)

    # Check that headers exists
    if 'filename' not in csv_fields:
        print_error('output', 'No header row in output file')

    # Check field names
    if check_fields(csv_fields, param['fields']):
        print_error('output', ['Errors in header fields in the output file', 'Correct header fields are [{fields:}]'.format(
            fields=','.join(param['fields']))]
        )
        error_count += 1

    filename_index = None
    scene_label_index = None

    if 'filename' in csv_fields:
        filename_index = csv_fields.index('filename')

    if 'scene_label' in csv_fields:
        scene_label_index = csv_fields.index('scene_label')

    file_index = []
    for row_id, row in enumerate(csv_reader):
        row_filename = os.path.split(row[filename_index])[-1]

        if row_filename in file_index:
            print_error('output', 'Duplicate file [{filename:}] at row [{row_id:}]'.format(
                filename=row[filename_index],
                row_id=row_id + 1)
            )
            error_count += 1

        else:
            file_index.append(row_filename)

        if os.path.splitext(row_filename)[-1] != '.wav':
            print_error('output', 'Wrong file extension for file [{filename:}] at row [{row_id:}] (use \'.wav\')'.format(
                filename=row[filename_index],
                row_id=row_id + 1)
            )
            error_count += 1

        if int(os.path.splitext(row_filename)[0]) > param['filename']['index_max']:
            print_error('output', 'Illegal filename [{filename:}] at row [{row_id:}] (file index too large)'.format(
                filename=row[filename_index],
                row_id=row_id + 1)
            )
            error_count += 1

        elif int(os.path.splitext(row_filename)[0]) < param['filename']['index_min']:
            print_error('output', 'Illegal filename [{filename:}] at row [{row_id:}] (file index too small)'.format(
                filename=row[filename_index],
                row_id=row_id + 1)
            )
            error_count += 1

        if len(row) != len(param['fields']):
            print_error('output', 'Wrong field count at row [{row_id:}]'.format(row_id=row_id + 1))
            error_count += 1

        if scene_label_index and row[scene_label_index] not in param['scene_labels']:
            print_error('output', 'Use of illegal scene label [{scene_label:}] at row [{row_id:}]'.format(
                scene_label=row[scene_label_index],
                row_id=row_id + 1)
            )
            error_count += 1

        for field in param['fields_float']:
            index = csv_fields.index(field)
            if index < len(row):
                current_value = row[csv_fields.index(field)]
                if not is_float(current_value):
                    print_error('output', 'Wrong field type at row [{row_id:}] for field [{field:}={value:}]'.format(
                        row_id=row_id + 1,
                        field=field,
                        value=current_value)
                    )
                    error_count += 1

    if len(file_index) != param['unique_file_count']:
        print_error('output', 'Incorrect number of outputted entries [{count:} != {target:}] (unique filenames counted)'.format(
            count=len(file_index),
            target=param['unique_file_count'])
        )
        error_count += 1

    return error_count


def validate_meta_data(meta, task_label, param):
    error_count = 0

    if 'submission' not in meta:
        print_error('meta', [
            '\'submission\' block missing from meta file',
            '\'submission\', \'system\', and \'results\' blocks required at top level.'
        ])
        error_count += 1

    else:
        if check_fields(meta['submission'], param['submission']['required_fields']):
            print_error('meta', [
                '\'submission\' block does not contain all required fields',
                'Fields required [{fields:}]'.format(fields=','.join(param['submission']['required_fields']))
            ])
            error_count += 1

        corresponding_found = 0
        for author in meta['submission']['authors']:
            if check_fields(author, param['submission']['authors']['required_fields']):
                print_error('meta', [
                    '\'submission.author\' block does not contain all required fields',
                    'Fields required [{fields:}]'.format(
                    fields=','.join(param['submission']['authors']['required_fields']))
                ])
                error_count += 1

            if 'corresponding' in list(author.keys()) and author['corresponding']:
                corresponding_found += 1

        if corresponding_found < 1:
            print_error('meta', '\'submission.author\' block has to have one corresponding author marked')
            error_count += 1

        elif corresponding_found > 1:
            print_error('meta', '\'submission.author\' block has more than one corresponding author marked')
            error_count += 1

        if 'label' in meta['submission']:
            submission_label = meta['submission']['label']
            submission_label_parts = submission_label.split('_')
            if len(submission_label_parts) != 4:
                print_error('meta', 'Submission label is wrongly constructed [submission.label={value:}]'.format(
                    value=submission_label))
                error_count += 1

            else:
                if submission_label_parts[2] != task_label:
                    print_error('meta', 'Submission label is wrongly constructed [submission.label={value:}]'.format(
                        value=submission_label))

                    error_count += 1

        if 'abbreviation' in meta['submission'] and len(meta['submission']['abbreviation']) > 10:
            print_error('meta', 'Submission abbreviation is too long [\'{value:}\' > 10]'.format(
                value=meta['submission']['abbreviation']))

            error_count += 1

    if 'system' not in meta:
        print_error('meta', [
            '\'system\' block missing from meta file',
            '\'submission\', \'system\', and \'results\' blocks required at top level.'
        ])
        error_count += 1

    else:
        if check_fields(meta['system'], param['system']['required_fields']):
            print_error('meta', [
                '\'system\' block does not contain all required fields',
                'Fields required [{fields:}]'.format(fields=','.join(param['system']['required_fields']))
            ])
            error_count += 1

        if 'description' in meta['system']:
            if check_fields(meta['system']['description'], param['system']['description']['required_fields']):
                print_error('meta', [
                    '\'system.description\' block does not contain all required fields',
                    'Fields required [{fields:}]'.format(fields=','.join(param['system']['description']['required_fields']))
                ])
                error_count += 1

        if 'complexity' in meta['system']:
            if check_fields(meta['system']['complexity'], param['system']['complexity']['required_fields']):
                print_error('meta', [
                    '\'system.complexity\' block does not contain all required fields',
                    'Fields required [{fields:}]'.format(fields=','.join(param['system']['complexity']['required_fields']))
                ])
                error_count += 1

        if not is_int(meta['system']['complexity']['total_parameters']):
            print_error('meta', '\'system.complexity.total_parameters\' value not a number')
            error_count += 1

        if 'external_datasets' in meta['system']:
            for item in meta['system']['external_datasets']:
                if check_fields(item, param['system']['external_datasets']['required_fields']):
                    print_error('meta', [
                        '\'system.external_datasets\' block does not contain all required fields',
                        'Fields required [{fields:}]'.format(fields=','.join(param['system']['external_datasets']['required_fields']))
                    ])
                    error_count += 1

    if 'results' not in meta:
        print_error('meta', [
            '\'results\' block missing from meta file',
            '\'submission\', \'system\', and \'results\' blocks required at top level.'
        ])
        error_count += 1

    else:
        if check_fields(meta['results'], param['results']['required_fields']):
            print_error('meta', [
                '\'results\' block does not contain all required fields',
                'Fields required [{fields:}]'.format(fields=','.join(param['results']['required_fields']))
            ])
            error_count += 1

        if 'development_dataset' in meta['results']:
            if check_fields(meta['results']['development_dataset'], param['results']['development_dataset']['required_fields']):
                print_error('meta', [
                    '\'results.development_dataset\' block does not contain all required fields',
                    'Fields required [{fields:}]'.format(fields=','.join(param['results']['development_dataset']['required_fields']))
                ])
                error_count += 1

            if 'overall' in meta['results']['development_dataset'] and meta['results']['development_dataset']['overall']:
                if check_fields(meta['results']['development_dataset']['overall'],
                                param['results']['development_dataset']['overall']['required_fields']):
                    print_error('meta', [
                        '\'results.development_dataset.overall\' block does not contain all required fields',
                        'Fields required [{fields:}]'.format(fields=','.join(param['results']['development_dataset']['overall']['required_fields']))
                    ])
                    error_count += 1

                for item in meta['results']['development_dataset']['overall']:
                    if not is_float(meta['results']['development_dataset']['overall'][item]):
                        print_error('meta', '\'results.development_dataset.overall.{item:}\' value is not numeric.'.format(item=item))

            if 'class_wise' in meta['results']['development_dataset'] and meta['results']['development_dataset']['class_wise']:
                if check_fields(meta['results']['development_dataset']['class_wise'],
                                param['results']['development_dataset']['class_wise']['required_fields']):
                    print_error('meta', [
                        '\'results.development_dataset.class_wise\' block does not contain all required fields',
                        'Fields required [{fields:}]'.format(fields=','.join(param['results']['development_dataset']['class_wise']['required_fields']))
                    ])
                    error_count += 1

                for item in meta['results']['development_dataset']['class_wise']:
                    if check_fields(meta['results']['development_dataset']['class_wise'][item],
                                    param['results']['development_dataset']['class_wise']['required_fields_per_item']):
                        print_error('meta', [
                            '\'results.development_dataset.class_wise.{item:}\' block does not contain all required fields'.format(item=item),
                            'Fields required [{fields:}]'.format(fields=','.join(param['results']['development_dataset']['class_wise']['required_fields_per_item']))
                        ])
                        error_count += 1

                    for item2 in meta['results']['development_dataset']['class_wise'][item]:
                        if not is_float(meta['results']['development_dataset']['class_wise'][item][item2]):
                            print_error('meta', '\'results.development_dataset.class_wise.{item:}.{item2:}\' value is not numeric.'.format(item=item, item2=item2))

            if 'device_wise' in meta['results']['development_dataset'] and meta['results']['development_dataset']['device_wise']:
                if check_fields(meta['results']['development_dataset']['device_wise'],
                                param['results']['development_dataset']['device_wise']['required_fields']):
                    print_error('meta', [
                        '\'results.development_dataset.device_wise\' block does not contain all required fields',
                        'Fields required [{fields:}]'.format(
                            fields=','.join(param['results']['development_dataset']['device_wise']['required_fields'])
                        )
                    ])
                    error_count += 1

                for item in meta['results']['development_dataset']['device_wise']:
                    if check_fields(meta['results']['development_dataset']['device_wise'][item],
                                    param['results']['development_dataset']['device_wise']['required_fields_per_item']):
                        print_error('meta', [
                            '\'results.development_dataset.device_wise.{item:}\' block does not contain all required fields'.format(item=item),
                            'Fields required [{fields:}]'.format(
                                fields=','.join(param['results']['development_dataset']['device_wise']['required_fields_per_item'])
                            )
                        ])
                        error_count += 1

                    for item2 in meta['results']['development_dataset']['device_wise'][item]:
                        if not is_float(meta['results']['development_dataset']['device_wise'][item][item2]):
                            print_error('meta', '\'results.development_dataset.device_wise.{item:}.{item2:}\' value is not numeric.'.format(item=item, item2=item2))

    return error_count
