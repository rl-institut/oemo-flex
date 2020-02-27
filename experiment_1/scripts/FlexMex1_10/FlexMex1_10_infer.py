"""
Run this script from the root directory of the datapackage to update
or create meta data.
"""
import os

from oemof.tabular.datapackage import building

from oemoflex.helpers import get_experiment_paths


name = 'FlexMex1_10'

abspath = os.path.abspath(os.path.dirname(__file__))

path_config = os.path.join(abspath, '../../config.yml')

experiment_paths = get_experiment_paths(name, path_config)


def main():
    r"""Infer the metadata of the datapackage"""
    building.infer_metadata(
        package_name='oemof-tabular-dispatch-example',
        foreign_keys={
            'bus': ['volatile', 'shortage', 'curtailment', 'storage', 'load'],
            'profile': ['load', 'volatile'],
            'from_to_bus': ['link'],
        },
        path=experiment_paths['data_preprocessed']
    )


if __name__ == '__main__':
    main()
