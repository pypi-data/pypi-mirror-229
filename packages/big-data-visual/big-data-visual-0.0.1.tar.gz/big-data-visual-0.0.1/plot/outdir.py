import os

def get_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output')
    return 'output/'