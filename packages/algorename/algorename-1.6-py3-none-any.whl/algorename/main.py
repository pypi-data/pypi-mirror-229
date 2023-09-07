#!/usr/bin/env python3

import os
import json
import time
import logging
import argparse
import importlib.util
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from .env file
cwd = os.getcwd()
load_dotenv(dotenv_path=os.path.join(cwd, '.env'))

# Setting verbosity levels, log file name and algorithm path
VERBOSITY = os.getenv("FCLOG_LEVEL", "INFO").upper()
LOG_FILENAME = os.getenv("FCLOG_NAME", "algorename.log").lower()
ALGORITHM_PATHS = os.getenv("FCLOG_PATH", "./algorithms").split(os.pathsep)

def setup_logging(verbosity_level: str, filename: str = LOG_FILENAME, max_size: int = (1024 ** 2) * 1):
    """Setting up logging
    
    Args:
        verbosity_level (str): Log verbosity level; can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_handler = RotatingFileHandler(filename, maxBytes=max_size, backupCount=5)
    logging.basicConfig(handlers=[log_handler], format=log_format, level=getattr(logging, verbosity_level, VERBOSITY))
    logging.debug("Logging setup complete.")

def log_error(error_message: str = "An unexpected error occurred.", silent: bool = False):
    logging.error(error_message)
    if not silent:
        print(error_message)

# Set up logging
setup_logging(VERBOSITY, filename=LOG_FILENAME, max_size=(1024 ** 2) * 1)

def log_json(action: str, old: str, new: str, metadata: dict = None):
    """Logs messages in JSON.

    Args:
        action (str): Description of the performed action.
        old (str): Original filename or path.
        new (str): New filename or path.
        metadata (dict): Additional metadata. Default is None if not specified.
    """
    log_entry = {"action": action, "old_name": old, "new_name": new}
    if metadata:
        log_entry.update(metadata)
    logging.info(json.dumps(log_entry))


def _try_load_module(module_path: str, algorithm_name: str):
    logging.debug(f"Trying to load module from {module_path}/{algorithm_name}.py")
    try:
        spec = importlib.util.spec_from_file_location("module.name", f"{module_path}/{algorithm_name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, 'apply_algorithm')
    except (ImportError, AttributeError, ModuleNotFoundError, FileNotFoundError) as e:
        logging.debug(f"Module load failed: {e}")
        return None


def load_algorithm(algorithm_name: str) -> callable:
    """Dynamically loads an algorithm.
    
    This function first attempts to load an algorithm from the internal algorithms package. 
    If unsuccessful, it then tries to load it from external directories specified in the ALGORITHM_PATHS environment variable.

    Args:
        algorithm_name (str): The name of the algorithm to be loaded.

    Returns:
        callable: The apply_algorithm function from the loaded module or None if the algorithm could not be loaded.
    """
    logging.info(f"Loading algorithm: {algorithm_name}")
    try:
        module = importlib.import_module(f'algorithms.{algorithm_name}')
        logging.debug(f"Successfully loaded algorithm {algorithm_name} from internal package.")
        return getattr(module, 'apply_algorithm')
    except (ImportError, AttributeError, ModuleNotFoundError, FileNotFoundError) as e:
        logging.debug(f"Failed to load algorithm from internal package: {e}")
        # Try loading the algorithm from external directories
        return next((res for res in (_try_load_module(path, algorithm_name) for path in ALGORITHM_PATHS) if res), None)

def list_algorithms():
    """List all available algorithms along with their metadata.
    
    This function scans both the project's 'algorithms/' directory and 
    any directories specified in the ALGORITHM_PATHS variable.
    """
    logging.info("Listing available algorithms...")

    def load_and_print_algorithms(directory):
        """Load and display algorithm metadata from a specific directory.
        
        Parameters:
            directory (str): The directory from which to load algorithm files.
        """
        try:
            algorithm_files = [file[:-3] for file in os.listdir(directory) if file.endswith('.py') and file != '__init__.py']
            if not algorithm_files:
                return
              
            # Display the source directory
            print(f"Source Directory: {directory}")
            print('-' * 80)

            for algorithm_file in algorithm_files:
                spec = importlib.util.spec_from_file_location("module.name", f"{directory}/{algorithm_file}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Display the algorithm information
                print(f" - Algorithm: {module.algorithm_metadata['name']}")
                print(f"   - Description: {module.algorithm_metadata['description']}")

            print('')
                
        except FileNotFoundError:
            logging.error(f"The directory {directory} was not found.")
            
        except PermissionError:
            logging.error(f"Permission denied when attempting to access {directory}.")

    # List algorithms from the project's 'algorithms/' directory
    load_and_print_algorithms('../algorithms')
    
    # List algorithms from external directories specified in ALGORITHM_PATHS
    for ALGORITHM_PATH in ALGORITHM_PATHS:
        load_and_print_algorithms(ALGORITHM_PATH)


def file_task(folder_path: str, filename: str, algorithm, logging_disabled: bool):
    """Task to rename a single file.

    Args:
        folder_path (str): The path to the folder containing the file.
        filename (str): The filename to be changed.
        algorithm (callable): The algorithm to apply to the filename.
    """

    if not logging_disabled:
        logging.debug(f"Starting file task for {filename} in folder {folder_path}")

    original_path = os.path.join(folder_path, filename)
    new_filename = algorithm(filename)
    new_path = os.path.join(folder_path, new_filename)
    os.rename(original_path, new_path)
    log_json("Changed Directory File", original_path, new_path)


def directory_task(folder_path: str, algorithm: callable, recursive: bool, logging_disabled: bool):
    """Rename all files in the given directory using the specified algorithm.

    Args:
        folder_path (str): Path to the directory whose filenames need to be changed.
        algorithm (callable): The algorithm to apply to each filename.
        recursive (bool): Whether to apply the algorithm recursively to sub-directories.
    """
    logging.debug(f"Starting directory task for folder: {folder_path}, recursive: {recursive}")
    with os.scandir(folder_path) as entries:
        filenames = []
        sub_dirs = []
        
        for entry in entries:
            if entry.is_file():
                filenames.append(entry.name)
            elif entry.is_dir() and recursive:
                sub_dirs.append(entry.path)
        with ThreadPoolExecutor(10) as executor:
            futures = (executor.submit(file_task, folder_path, fname, algorithm, logging_disabled) for fname in filenames)
            for future in as_completed(futures):
                future.result()
        
        if recursive:
            for sub_dir in sub_dirs:
                directory_task(sub_dir, algorithm, recursive=True, logging_disabled=logging_disabled)

def check_and_delete_empty_file(filepath: str, silent: bool):
    """
    Checks if the specified file exists and is empty, and deletes it if both conditions are met.
    
    Args:
    - filepath (str): The path to the file to check and potentially delete.
    - silent (bool): True means prints don't show up and false means they do.
    """
    try:
        msg = ""
        # Check if file exists
        if os.path.exists(filepath):
            # Check if file is empty
            if os.path.getsize(filepath) == 0:
                os.remove(filepath)
                msg = f"Deleted empty file: {filepath}"
                logging.info(msg)
                if not silent:
                    print(msg)
            else:
                msg = f"File is not empty: {filepath}"
                logging.error(msg)
                if not silent:
                    print(msg)
        else:
            msg = f"File does not exist: {filepath}"
            logging.error(msg)
            if not silent:
                print(msg)
    except Exception as e:
        msg = f"An error occurred: {e}"
        logging.error(msg)
        if not silent:
            print(msg)

def main():
    """Main function.
    It sets up the logging, parses CLI arguments, and calls the appropriate function to rename files or directories.
    """
    logging.debug("Starting main function.")
    parser = argparse.ArgumentParser(description="Change file or directory names based on a chosen algorithm.")
    parser.add_argument("-s", "--silent", help="Suppress errors.", action="store_true", default=False)
    parser.add_argument("-a", "--algorithm", help="Algorithm to be used.", type=str, default='example')
    parser.add_argument("-r", "--recursive", help="Apply changes recursively to directories.", action="store_true", default=False)
    parser.add_argument("-nl", "--no-log", help="Does not create a log file.", action="store_true", default=False)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Specify the path of a single file to change.", type=str)
    group.add_argument("-d", "--dir", help="Specify the directory path to change all file names.", type=str)
    group.add_argument("-l", "--list", help="List available algorithms.", action="store_true")

    args = parser.parse_args()
    
    if args.no_log:
        logger = logging.getLogger()
        logger.disabled = True
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        check_and_delete_empty_file(LOG_FILENAME, args.silent)

    # Load the algorithm
    algorithm = load_algorithm(args.algorithm)
    if algorithm is None:
        error = f"Algorithm {args.algorithm} could not be loaded."
        log_error(error, args.silent)
        return

    try:
        error = ""
        if args.list:
            list_algorithms()
        elif args.file:
            if os.path.exists(args.file) and os.path.isfile(args.file):
                folder_path, filename = os.path.split(args.file)
                file_task(folder_path, filename, algorithm, args.no_log)
            else:
                error = f"The file {args.file} does not exist or is not a file."
                log_error(error, args.silent)

        elif args.dir:
            if os.path.exists(args.dir) and os.path.isdir(args.dir):
                directory_task(args.dir, algorithm, recursive=args.recursive, logging_disabled=args.no_log)
            else:
                error = f"The directory {args.dir} does not exist or is not a directory."
                log_error(error, args.silent)
    except Exception as e:
        error = f"An unexpected error occurred: {e}"
        logging.critical(error)
        if not args.silent:
            print(error)
   
    if not error:
        print("[+] Renaming successful")
    logging.debug("Main function execution completed.")

if __name__ == "__main__":
    main()