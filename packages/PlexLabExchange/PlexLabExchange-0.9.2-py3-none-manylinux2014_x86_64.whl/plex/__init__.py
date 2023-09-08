import json
import os
import subprocess

from enum import Enum
from typing import Dict, List


class ScatteringMethod(Enum):
    # values are camel case to match GoLang CLI
    DOT_PRODUCT = 'dotProduct'
    CROSS_PRODUCT = 'crossProduct'


class CoreTools(Enum):
    EQUIBIND = "QmZWYpZXsrbtzvBCHngh4YEgME5djnV5EedyTpc8DrK7k2"
    DIFFDOCK = "QmfKhJh48aDHgckzwGEASNmZd1SYstQiR5qLqqYmLQFzq9"
    COLABFOLD_MINI = "QmcRH74qfqDBJFku3mEDGxkAf6CSpaHTpdbe1pMkHnbcZD"
    COLABFOLD_STANDARD = "QmXnM1VpdGgX5huyU3zTjJovsu42KPfWhjxhZGkyvy9PVk"
    COLABFOLD_LARGE = "QmPYqMy19VFFuYztL6b5ruo4Kw4JWT583emStGrSYTH5Yi"
    BAM2FASTQ = "QmbPUirWiWCv9sgdHLekf5AnoCdw4QPU2SyfGGKs9JRRbq"
    ODDT = "QmUx7NdxkXXZvbK1JXZVUYUBqsevWkbVxgTzpWJ4Xp4inf"
    RFDIFFUSION = "QmTyFGjt2oqTLGQRE5u8mtfiQNft5nzMsieYdvwnpfk3HJ"
    REPEATMODELER = "QmZdXxnUt1sFFR39CfkEUgiioUBf6qP5CUs8TCb7Wqn4MC"
    GNINA = "QmZiQWEXj3aMRnJLoU39HHcknMDfKQD2txpfk6ubJAdDRx"
    BATCH_DLKCAT = "QmQTjvP2utNb1JTtUHeQ8mQPvNkCTg5VRc4LVdptWkUcJ7"
    OPENBABEL_PDB_TO_SDF = "QmbbDSDZJp8G7EFaNKsT7Qe7S9iaaemZmyvS6XgZpdR5e3"
    OPENBABEL_RMSD = "QmUxrKgAs5r42xVki4vtMskJa1Z7WA64wURkwywPMch7dA"
    COLABDESIGN = "QmXvptBDQDbWCYMYz4YZBu3Dtzqf36TRb7XUo1ejeSiUHC"

class PlexError(Exception):
    def __init__(self, message):
        self.message = message
        self.github_issue_message = ("If this error persists, please submit an issue at "
                                     "https://github.com/labdao/plex/issues")
        super().__init__(f"{self.message}\n{self.github_issue_message}")


def plex_init(tool_path: str, scattering_method=ScatteringMethod.DOT_PRODUCT.value, plex_path="plex", auto_run=False, **kwargs):
    cwd = os.getcwd()
    plex_work_dir = os.environ.get("PLEX_WORK_DIR", os.path.dirname(os.path.dirname(cwd)))

    # Convert all relative file paths in kwargs to absolute paths
    for key, value in kwargs.items():
        if isinstance(value, list):
            for i in range(len(value)):
                # If the value is a string and represents a file path
                if isinstance(value[i], str) and os.path.isfile(value[i]):
                    # Convert the relative path to an absolute path
                    value[i] = os.path.abspath(value[i])
        # If the value is a string and represents a file path
        elif isinstance(value, str) and os.path.isfile(value):
            kwargs[key] = os.path.abspath(value)

    # Convert kwargs dictionary to a JSON string
    inputs = json.dumps(kwargs)

    cmd = [plex_path, "init", "-t", tool_path, "-i", inputs, f"--scatteringMethod={scattering_method}", f"--autoRun={str(auto_run).lower()}"]

    print(' '.join(cmd))

    io_json_cid = ""
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=plex_work_dir) as p:
        for line in p.stdout:
            if "Pinned IO JSON CID:" in line:
                parts = line.split()
                io_json_cid = parts[-1]
            print(line, end='')
        for line in p.stderr:
            print(line, end='')

    if io_json_cid == "":
        raise PlexError("Failed to initialize IO JSON CID")

    return io_json_cid


def plex_vectorize(io_path: str, tool_cid: str, output_dir="", plex_path="plex"):
    cwd = os.getcwd()
    plex_work_dir = os.environ.get("PLEX_WORK_DIR", os.path.dirname(os.path.dirname(cwd)))

    cmd = [plex_path, "vectorize", "-i", io_path, "-t", tool_cid, "-o", output_dir]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=plex_work_dir) as p:
        outvects = ""
        for line in p.stdout:
            if "Output Vectors were saved at:" in line:
                parts = line.split()
                io_vector_outpath = parts[-1]
                with open(io_vector_outpath, 'r') as f:
                    outvects = json.load(f)
                os.remove(io_vector_outpath)
            print(line, end='')
        for line in p.stderr:
            print(line, end='')

    if outvects == "":
        raise PlexError("Failed to vectorize IO JSON CID")

    return outvects


def plex_upload(file_path: str, wrap_file=True, plex_path="plex"):
    cmd = [plex_path, "upload", "-p", file_path]

    if not wrap_file:
        cmd.append("-w=false")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        file_cid = ""
        for line in p.stdout:
            if "Uploaded CID:" in line:
                parts = line.split()
                file_cid = parts[-1]
            print(line, end='')
        for line in p.stderr:
            print(line, end='')

    if file_cid == "":
        raise PlexError("Failed to upload file to IPFS")

    return file_cid


def plex_run(io_json_cid: str, output_dir="", verbose=False, show_animation=False, max_time="60" ,concurrency="1", annotations=None, plex_path="plex"):
    cwd = os.getcwd()
    plex_work_dir = os.environ.get("PLEX_WORK_DIR", os.path.dirname(cwd))
    cmd = [plex_path, "run", "-i", io_json_cid]

    if output_dir:
        cmd.append(f"-o={output_dir}")

    if verbose:
        cmd.append("-v=true")

    if max_time:
        cmd.append(f"-m={max_time}")

    if concurrency:
        cmd.append(f"--concurrency={concurrency}")

    if annotations is None:
        annotations = []

    # Ensure "python" is always in the annotations list
    if "python" not in annotations:
        annotations.append("python")

    # Add each annotation as a separate parameter to cmd
    for annotation in annotations:
        cmd.append(f"--annotations={annotation}")

    if not show_animation:  # default is true in the CLI
        cmd.append("--showAnimation=false")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=plex_work_dir) as p:
        io_json_cid = ""
        io_json_local_filepath = ""
        for line in p.stdout:
            if "Completed IO JSON CID:" in line:
                parts = line.split()
                io_json_cid = parts[-1]
            if "Initialized IO file at:" in line:
                parts = line.split()
                io_json_local_filepath = parts[-1]
            print(line, end='')
        for line in p.stderr:
            print(line, end='')

    if io_json_cid == "" or io_json_local_filepath == "":
        raise PlexError("Failed to run IO JSON CID")

    return io_json_cid, io_json_local_filepath


def plex_mint(io_json_cid: str, image_cid="", plex_path="plex"):
    cwd = os.getcwd()
    plex_work_dir = os.environ.get("PLEX_WORK_DIR", os.path.dirname(os.path.dirname(cwd)))
    cmd = [plex_path, "mint", "-i", io_json_cid]

    if image_cid:
        cmd.append(f"-imageCid={image_cid}")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=plex_work_dir) as p:
        for line in p.stdout:
            print(line, end='')
        for line in p.stderr:
            print(line, end='')


def print_io_graph_status(io_graph):
    state_count = {}

    # Iterate through the io_list and count the occurrences of each state
    for io in io_graph:
        state = io['state']
        if state in state_count:
            state_count[state] += 1
        else:
            state_count[state] = 1

    # Print the total number of IOs
    print(f"Total IOs: {len(io_graph)}")

    # Print the number of IOs in each state
    for state, count in state_count.items():
        print(f"IOs in {state} state: {count}")
