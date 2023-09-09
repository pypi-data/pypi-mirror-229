#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
import logging
from os import listdir, remove, walk
from os.path import isfile, join
from os.path import split as split_filename
from typing import List

from kami_logging import benchmark_with, logging_with

filemanager_logger = logging.getLogger('filemanager')


@benchmark_with(filemanager_logger)
@logging_with(filemanager_logger)
def csv_to_json(csv_file_path: str, json_file_path: str):
    json_array = []
    try:
        with open(csv_file_path, encoding='utf-8') as csvf:
            csv_reader = csv.DictReader(csvf)
            for row in csv_reader:
                json_array.append(row)

        with open(json_file_path, 'w', encoding='utf-8') as jsonf:
            json_string = json.dumps(json_array, indent=4)
            jsonf.write(json_string)
    except Exception as e:
        filemanager_logger.exception('An unknow error occurred:', e)


@benchmark_with(filemanager_logger)
@logging_with(filemanager_logger)
def get_file_list_from(folder_path: str) -> List[str]:
    file_list = []
    try:
        file_list = [
            folder_path + '/' + f
            for f in listdir(folder_path)
            if isfile(join(folder_path, f))
        ]
        filemanager_logger.info(f'__Folder: {folder_path}')
        [
            filemanager_logger.info(f'____File: {cuurent_file}')
            for cuurent_file in file_list
        ]
    except Exception as e:
        filemanager_logger.exception('An unknow error occurred:', e)
    return file_list


@benchmark_with(filemanager_logger)
@logging_with(filemanager_logger)
def get_folder_list_from(rootdir: str) -> List[str]:
    folders = []
    try:
        for (
            rootdir,
            dirs,
            files,
        ) in walk(rootdir):
            for subdir in dirs:
                folders.append(join(rootdir, subdir))
        filemanager_logger.info(f'__Root Folder: {rootdir}')
        [
            filemanager_logger.info(f'____Sub Folder: {folder}')
            for folder in folders
        ]
    except Exception as e:
        filemanager_logger.exception('An unknow error occurred:', e)
    return folders


@benchmark_with(filemanager_logger)
@logging_with(filemanager_logger)
def delete_files_from(folderpath: str):
    try:
        selected_files = get_file_list_from(folderpath)
        if len(selected_files):
            for selected_file in selected_files:
                selected_filepath, selected_filename = split_filename(
                    selected_file
                )
                filemanager_logger.info(
                    f'Deleting {selected_filename} From {selected_filepath}'
                )
                remove(selected_file)
    except Exception as e:
        filemanager_logger.exception('An unknow error occurred:', e)
