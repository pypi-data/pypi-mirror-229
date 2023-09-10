import logging
from subprocess import call as _subprocess_call
from os import path as _os_path, walk as _os_walk
from yaml import safe_load as _yaml_safe_load
from pandas import DataFrame as _DataFrame, Series as _Series
from checksumdir import dirhash


def filehash(fpath):
    from hashlib import md5, sha1, sha256
    try:
        with open(fpath, 'rb') as _file:
            _fcontent = _file.read()
            return {
                'md5': md5(_fcontent).hexdigest(),
                'sha1': sha1(_fcontent).hexdigest(),
                'sha256': sha256(_fcontent).hexdigest()
            }
    except FileNotFoundError:
        logging.warning(f"The target file is not found ({fpath})")
        return {'md5': '', 'sha1': '', 'sha256': ''}


class Subject:
    headers = ['probeID', 'result']

    def __init__(self, fpath):
        Subject.validate_path(fpath)
        self.path = fpath
        self.hash = filehash(fpath)

    @staticmethod
    def validate_path(fpath):
        # TODO: assert is elf file
        assert _os_path.isfile(fpath), f"Not an ELF {fpath}"

    @property
    def filename(self):
        return _os_path.basename(self.path)

    def __repr__(self):
        return self.filename

    def to_json(self):
        # Exclude self.hash. Computed when the instance is initialized
        return {'path': self.path, 'hash': self.hash}


class Probe:
    def __init__(self, dirpath):

        if not Probe.validate_probe_structure(dirpath):
            raise ValueError("Not parser directory. Missing 'main.py' and/or .conf file")
        self.root_dir = dirpath
        with open(_os_path.join(dirpath, '.conf'), 'r') as pbconffile:
            self.conf = _yaml_safe_load(pbconffile)
            self.conf.update({'sha256': dirhash(_os_path.dirname(dirpath), "sha256")})

    @property
    def name(self):
        return _os_path.basename(self.root_dir)

    @property
    def exec_path(self):
        return _os_path.abspath(_os_path.join(self.root_dir, 'main.py'))

    def __repr__(self):
        return f"{self.name} ({self.conf.get('id')})"

    @staticmethod
    def validate_probe_structure(dirpath) -> bool:
        """

        :param dirpath: Dir path pointing to a probe dir
        :return: True if dirpath points to a valid probe dir. False otherwise
        """
        return _os_path.isfile(_os_path.join(dirpath, 'main.py')) and _os_path.isfile(_os_path.join(dirpath, '.conf'))

    def run(self, target_path) -> int:
        """Prepares the environment to execute the probe and runs it.


        :param target_path: path to the file to be analyzed
        :return: an integer number, depending on the result of the probe
        """
        # Execute the probe
        logging.info(f"Executing probe '{self.name}' on file {target_path}")
        returncode = _subprocess_call(f"{self.exec_path} {target_path}'", shell=True)

        # Return probe id and result
        if returncode not in [0, 255]:
            logging.error(f"Probe '{self.name}' failed ({returncode})")
            return 901
        else:
            logging.info(f"Probe completed ({returncode})")
            return returncode

    def parse_cli(self, cmd=None):
        import argparse
        parser = argparse.ArgumentParser(
            prog=_os_path.join(self.name, 'main.py'),
            description=self.conf.get('description')
        )
        parser.add_argument('target', help="Target (ELF) file to be analyzed")
        _args = parser.parse_args(cmd)
        _args.__setattr__('probe_conf', self.conf)
        return _args


class AnalysisMatrix:
    columns = ['Probe']

    def __init__(self):
        self.matrix = _DataFrame(columns=AnalysisMatrix.columns)

    def count_probes(self):
        return self.matrix.shape[0]

    def count_targets(self):
        return self.matrix.shape[1] - 1

    def add_subjects(self, subj_list: list):
        # TODO: add_subjects
        assert isinstance(subj_list, list), \
            f"Unexpected type ({type(subj_list)}) for param 'subj_list'. Expected: list"
        for fpath in subj_list:
            try:
                # Add column 'Subject' with all empty rows for each probe (row) in self
                self.matrix.insert(
                    self.matrix.shape[1],
                    Subject(fpath),
                    _Series(["Pending"] * self.count_probes()),
                    False)
            except ValueError:
                logging.error(f"Not an ELF {fpath}. Skipping this target")

    def add_probe(self, pb_path):
        if not Probe.validate_probe_structure(pb_path):
            logging.error(f"Not a Probe directory ({pb_path})")
            return
        self.matrix.loc[len(self.matrix)] = [Probe(pb_path)]

    @staticmethod
    def load_probes(dirpath):
        # https://stackoverflow.com/questions/141291/how-to-list-only-top-level-directories-in-python
        # iterate (absolute path) entries in this directory and filter by the sub-files included in it
        logging.info("Loading probes")
        _loaded = AnalysisMatrix()
        for i in filter(Probe.validate_probe_structure,
                        [_os_path.join(dirpath, x) for x in next(_os_walk(dirpath))[1]]):
            try:
                _loaded.add_probe(_os_path.join(dirpath, i))
            except ValueError:
                continue
        logging.info(f"({len(_loaded.matrix)}) Probes loaded: {[x.name for x in _loaded.matrix['Probe']]}")
        return _loaded

    def analyze(self, include=None, exclude=None):
        # TODO: run all the corresponding probe
        # TODO: apply parallelism. The computations of each item are independent from the rest
        """
        Analyze the current Matrix
        :param include: If not None, only those Probe IDs will be executed
        :param exclude: If not None, only those Probe IDs NOT IN this list are executed
        :return: None
        """
        for x_coord, tg in enumerate(self.matrix.columns[1:], 1):
            for y_coord, probe in enumerate(self.matrix["Probe"]):
                if (include is not None and probe.id in include) or (exclude is not None and probe.id not in exclude):
                    self.matrix.at[y_coord, tg] = probe.run(tg)
                elif include is not None or exclude is not None:
                    # If either params is not None and this clause is reached => filter was not passed
                    self.matrix.at[y_coord, tg] = "Excluded"
                else:
                    # If both are None, probes are not filtered, thus all of them are run
                    self.matrix.at[y_coord, tg] = probe.run(tg)
