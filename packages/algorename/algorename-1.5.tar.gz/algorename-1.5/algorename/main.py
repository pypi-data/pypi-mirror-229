#!/usr/bin/env python3

import importlib
import os
import argparse
import logging
import json
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from concurrent.futures import ProcessPoolExecutor
from importlib import import_module

# Load environment variables from .env file
load_dotenv()

# Setting verbosity levels and log file name
VERBOSITY = os.getenv("FCLOG_LEVEL", "INFO").upper()
LOG_FILENAME = os.getenv("FCLOG_NAME", "algorename.log").lower()


def setup_logging(verbosity_level: str, filename: str = LOG_FILENAME, max_size: int = (1024 ** 2) * 1):
    """Setting up logging

    Args:
        verbosity_level (str): Log verbosity level; can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_handler = RotatingFileHandler(filename, maxBytes=max_size, backupCount=5)
    logging.basicConfig(handlers=[log_handler], format=log_format, level=getattr(logging, verbosity_level, VERBOSITY))


def log_json(action: str, old: str, new: str):
    """Logs messages in JSON.

    Args:
        action (str): Description of the performed action.
        old (str): Original filename or path.
        new (str): New filename or path.
    """
    log_entry = json.dumps({"action": action, "old_name": old, "new_name": new})
    logging.info(log_entry)


def load_algorithm(algorithm_name: str):
    """Dynamically load a file-changing algorithm.

    Args:
        algorithm_name (str): The name of the algorithm to be used for file changing.
    """
    try:
        module = import_module(f'algorithms.{algorithm_name}')
        return getattr(module, 'apply_algorithm')
    except (ImportError, AttributeError):
        logging.error(f"Algorithm {algorithm_name} could not be loaded.")
        return None

def list_algorithms():
    """Lists all available algorithms with their metadata.
    """
    logging.info("Listing available algorithms...")
    
    algorithm_files = [f[:-3] for f in os.listdir('./algorithms') if f.endswith('.py') and f != '__init__.py']
    
    print('-'*50)
    for algorithm_file in algorithm_files:
        spec = importlib.util.spec_from_file_location("module.name", f"./algorithms/{algorithm_file}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"Algorithm: {module.algorithm_metadata['name']}")
        print(f"Description: {module.algorithm_metadata['description']}")
        print('-'*50)

def file_task(folder_path: str, filename: str, algorithm):
    """Task to rename a single file.

    Args:
        folder_path (str): The path to the folder containing the file.
        filename (str): The filename to be changed.
        algorithm (callable): The algorithm to apply to the filename.
    """

    setup_logging(VERBOSITY, filename=LOG_FILENAME, max_size=(1024 ** 2) * 1)

    original_path = os.path.join(folder_path, filename)
    new_filename = algorithm(filename)
    new_path = os.path.join(folder_path, new_filename)
    os.rename(original_path, new_path)
    log_json("Changed Directory File", original_path, new_path)


def directory_task(folder_path: str, algorithm: callable, recursive: bool):
    """Rename all files in the given directory using the specified algorithm.

    Args:
        folder_path (str): Path to the directory whose filenames need to be changed.
        algorithm (callable): The algorithm to apply to each filename.
        recursive (bool): Whether to apply the algorithm recursively to sub-directories.
    """
    with os.scandir(folder_path) as entries:
        filenames = []
        sub_dirs = []
        
        for entry in entries:
            if entry.is_file():
                filenames.append(entry.name)
            elif entry.is_dir() and recursive:
                sub_dirs.append(entry.path)
        
        with ProcessPoolExecutor() as executor:
            executor.map(file_task, [folder_path] * len(filenames), filenames, [algorithm] * len(filenames))
        
        if recursive:
            for sub_dir in sub_dirs:
                directory_task(sub_dir, algorithm, recursive=True)


def main():
    """Main function.
    It sets up the logging, parses CLI arguments, and calls the appropriate function to rename files or directories.
    """

    parser = argparse.ArgumentParser(description="Change file or directory names based on a chosen algorithm.")
    parser.add_argument("-s", "--silent", help="Suppress errors.", action="store_true")
    parser.add_argument("-a", "--algorithm", help="Algorithm to be used.", type=str, default='example')
    parser.add_argument("-r", "--recursive", help="Apply changes recursively to directories.", action="store_true", default=False)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Specify the path of a single file to change.", type=str)
    group.add_argument("-d", "--dir", help="Specify the directory path to change all file names.", type=str)
    group.add_argument("-l", "--list", help="List available algorithms.", action="store_true")

    args = parser.parse_args()

    # Setting up logging after parsing the arguments
    setup_logging(VERBOSITY, filename=LOG_FILENAME, max_size=(1024 ** 2) * 1)
    
    # Load the algorithm
    algorithm = load_algorithm(args.algorithm)
    if algorithm is None:
        print(f"Algorithm {args.algorithm} could not be loaded.")
        return

    try:
        if args.list:
            list_algorithms()
        elif args.file:
            if os.path.exists(args.file) and os.path.isfile(args.file):
                folder_path, filename = os.path.split(args.file)
                new_filename = algorithm(filename)
                new_path = os.path.join(folder_path, new_filename)
                os.rename(args.file, new_path)
                log_json("Changed Single File", args.file, new_path)
            else:
                error = f"The file {args.file} does not exist or is not a file."
                logging.error(error)
                if not args.silent:
                    print(error)

        elif args.dir:
            if os.path.exists(args.dir) and os.path.isdir(args.dir):
                directory_task(args.dir, algorithm, recursive=args.recursive)
            else:
                error = f"The directory {args.dir} does not exist or is not a directory."
                logging.error(error)
                if not args.silent:
                    print(error)
    except Exception as e:
        error = f"An unexpected error occurred: {e}"
        logging.critical(error)
        if not args.silent:
            print(error)


if __name__ == "__main__":
    main()
