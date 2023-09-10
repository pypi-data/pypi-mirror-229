import logging
import subprocess
import os

import pandas as pd
import yaml
import json
from checksumdir import dirhash


# __install_dir__ = ''
def hash_file(fpath):
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
        self.probes = pd.DataFrame(columns=Subject.headers)
        self.hash = hash_file(fpath)

    @staticmethod
    def validate_path(fpath):
        # TODO: assert is elf file
        assert os.path.isfile(fpath), f"Not an ELF {fpath}"

    @property
    def filename(self):
        return os.path.basename(self.path)

    # def add_probe_section(self, info: dict, result: int):
    #     self.probes.append(ProbeSection(info, result))
    #     # TODO: get prob by prob_id, and the result
    def add_probe(self, probe_id: int, result: int):
        # self.probes.append(ProbeSection(probe_id=probe_id, res=result))
        self.probes.loc[len(self.probes)] = [probe_id, result]

    def add_probes(self, results: list[tuple]):
        for i in results:
            self.add_probe(i[0], i[1])

    def __repr__(self):
        return self.filename

    def to_json(self):
        # Exclude self.hash. Computed when the instance is initialized
        return {'path': self.path, 'probes': self.probes.to_json()}

    def to_string(self):
        return f"FILE ANALYSIS {self.filename}:\n{self.probes.to_string()}"


class Probe:
    def __init__(self, dirpath):
        if not Probe.validate_probe_structure(dirpath):
            raise ValueError("Not parser directory. Missing 'main.py' and/or .conf file")
        self.root_dir = dirpath
        self.conf = Probe.read_conf(os.path.join(self.root_dir, '.conf'))

    @property
    def name(self):
        return os.path.basename(self.root_dir)

    @property
    def exec_path(self):
        return os.path.abspath(os.path.join(self.root_dir, 'main.py'))

    def __repr__(self):
        return f"{self.name} ({self.conf.get('id')})"

    @staticmethod
    def read_conf(path) -> dict:
        with open(path, 'r') as pbconffile:
            _pbconf = yaml.safe_load(pbconffile)
            _pbconf.update({'hash': dirhash(os.path.dirname(path), "sha256")})
            return _pbconf

    @staticmethod
    def validate_probe_structure(dirpath) -> bool:
        """

        :param dirpath: Dir path pointing to a probe dir
        :return: True if dirpath points to a valid probe dir. False otherwise
        """
        return os.path.isfile(os.path.join(dirpath, 'main.py')) and os.path.isfile(os.path.join(dirpath, '.conf'))
        # f'.{os.path.basename(dirpath)}' in <' '.join(os.listdir(dirpath)))

    def run(self, target_path) -> tuple[str | int]:
        """Prepares an environment to execute the probe

                Parses and validates the configuration file of the probe specified in the parameter, and the target file.
                Returns an object with all the information parsed. See :class:`ProbeEnvironment` for more information.

                :param target_path:
                :return:
                    Exit code (see Exit codes in the documentation for more info)
                """

        # def _probe_fullpath():
        #     return os.path.abspath(os.path.join(os.path.dirname(__file__), probe_dir, 'main.py'))

        # Parse conf file
        try:
            # __probe_dir__ = os.path.abspath(os.path.dirname(_probe_fullpath()))
            # _probe_fullpath = os.path.abspath(os.path.join(self.path, 'main.py'))
            with open(os.path.join(self.root_dir, '.conf'), 'r') as conffile:
                _conf = yaml.safe_load(conffile)
                logging.debug(f"Probe initialized:{_conf}")
        except Exception:
            logging.exception("Unexpected error")
            exit(1)
            # raise error.FileNotFound
        # Execute the probe
        logging.info(f"Executing probe '{self.name}' on file {target_path}")
        returncode = subprocess.call(f"{self.exec_path} {target_path} '{json.dumps(_conf)}'", shell=True)

        # Return probe id and result
        if returncode not in [0, 255]:
            logging.error(f"Probe '{self.name}' failed ({returncode})")
            return [_conf['id'], 901]
        else:
            logging.info(f"Probe completed ({returncode})")
            return [_conf['id'], returncode]

    @staticmethod
    def parse_cli(cmd=None):
        import argparse
        # TODO: re-do parser
        pass
        # try:
        #     return {'epath': argv[1], '_conf': json.loads(sys.argv[2])}
        # except Exception:
        #     logging.exception("Unexpected error parsing arguments")

    # def list_probes():
    #     # this is artsem
    #     assert __install_dir__ not in ['', None], "__install_dir__ not specified"
    #     _prob_dir = os.path.join(__install_dir__, 'src', 'main', 'probe')
    #     _filtered = [os.path.abspath(i) for i in filter(
    #         lambda x: os.path.isfile(os.path.join(x, '.conf')) and os.path.isfile(os.path.join(x, 'main.py')),
    #         [os.path.join(_prob_dir, i) for i in next(os.walk(_prob_dir))[1]])]
    #     logging.debug(f"{len(_filtered)} probes found")
    #     return _filtered


# class AnalysisMatrix(pd.DataFrame):
class AnalysisMatrix:
    columns = ['Probe']
    states = ['Excluded', 'Pending']
    # temporary properties
    # _internal_names = pd.DataFrame._internal_names + ["internal_cache"]
    # _internal_names_set = set(_internal_names)
    #
    # # normal properties
    # _metadata = ["added_property"]
    #
    # @property
    # def _constructor(self):
    #     return AnalysisMatrix

    def __init__(self, data=None, *args, **kwargs):
        self.matrix = pd.DataFrame(columns=AnalysisMatrix.columns)
        # super(AnalysisMatrix, self).__init__(data=data, columns=AnalysisMatrix.columns, *args, **kwargs)

    def count_probes(self):
        return self.matrix.shape[0]

    def count_targets(self):
        return self.matrix.shape[1] - 1

    def add_subjects(self, subj_list: list):
        # TODO: add_subjects
        assert isinstance(subj_list, list), \
            f"Unexpected type ({type(subj_list)}) for parameter 'subj_list'. Expected: list"
        for fpath in subj_list:
            try:
                # Add column 'Subject' with all empty rows for each probe (row) in self
                # df['Address'] = address
                # ["Pending"] * len("hola")
                self.matrix.insert(-1, Subject(fpath), ["Pending"] * len(self.matrix), False)

            except AssertionError:
                logging.error(f"Not an ELF {fpath}. Skipping this target")

    def add_probe(self, pb_path):
        # df = df.append(df2, ignore_index=True)
        if not Probe.validate_probe_structure(pb_path):
            logging.error(f"Not a Probe directory ({pb_path})")
            return
        self.matrix.loc[len(self.matrix)] = [Probe(pb_path)]
        # self.loc[len(_loaded.index)] = [Probe(os.path.join(dirpath, i))]

    @staticmethod
    def load_probes(dirpath):
        # Esto es de artsem? Si y no
        # SI: artsem tiene una funcion para listar los templates DENTRO de la app
        # NO: artsemLib.parser tiene una funcion que lista todos los parsers existentes en un directorio (path)
        # RESOULUCION: hacer una funcion generica que liste los parsers de path, donde path es un directorio

        # https://stackoverflow.com/questions/141291/how-to-list-only-top-level-directories-in-python
        # iterate (absolute path) entries in this directory and filter by the sub-files included in it
        logging.info("Loading probes")
        _loaded = AnalysisMatrix()
        for i in filter(Probe.validate_probe_structure, next(os.walk(dirpath))[1]):
            try:
                # _loaded.loc[len(_loaded.index)] = [Probe()]
                _loaded.add_probe(os.path.join(dirpath, i))
                # _loaded.append(Probe(os.path.join(dirpath, i)))
            except ValueError:
                continue
        logging.info(f"({len(_loaded.matrix)}) Probes loaded: {[x.name for x in _loaded.matrix['Probe']]}")
        return _loaded

    def get_by_id(self, probe_id):
        pass

    def filter_by_id(self, include=None, exclude=None) -> list:
        # Esto es de artsemLib.db -> NO HACE FALTA DB ya que lo tengo cargado en memoria como objeto python
        # Elaborate the final samples list: all | included | all - excluded
        if include is not None:
            # TODO: query db
            # _final_tests = set(__db__.table('Probes').all()) & set(args.include)
            # return list(filter(lambda x: x.get('id') in set(include), self.connector.table('Probes').all()))
            return list(filter(lambda x: x.conf.get('id') in set(include), list(self.matrix['Probe'])))
        elif exclude is not None:
            # _final_tests = set(__db__.table('Probes').all()) - set(args.exclude)
            # return list(filter(lambda x: x.get('id') not in set(exclude), self.connector.table('Probes').all()))
            return list(filter(lambda x: x.conf.get('id') not in set(exclude), list(self.matrix['Probe'])))
        else:
            return list(self)

    def analyze(self, include=None, exclude=None):
        # analyze_elf(elf_path=tg, test_battery=_final_tests, verbosity=args.v)
        # TODO: run all the corresponding probe
        # TODO: apply parallelism. The computations of each item are independent from the rest
        """
        for tg in self.columns[1:]:
            for probe in self["Probe"]:
                if (include is not None and probe.id in include) or (exclude is not None and probe.id not in exclude):
                    self[probe][tg] = probe.run(tg)
                elif include is not None or exclude is not None:
                    # If either in or ex are not None and this clause is reached, it means that the filter was not passed
                    self[probe][tg] = "Excluded"
                else:
                    # If both are None, probes are not filtered, thus all of them are run
                    self[probe][tg] = probe.run(tg)
        :param include:
        :param exclude:
        :return:
        """
        # analysis = SingleTargetAnalysis(target)
        # # Map: [prob_id] -> [prob_path] -> Probe object
        # # probe_list = [artsemLib.Probe(os.path.join(__probe_dir__, p['name'])) for p in
        # #               _filter_probes_by_id(include=include, exclude=exclude)]
        # # _results = []
        # for probe in __probes__.filter_by_id(include=include, exclude=exclude):
        #     # _results.append(single_probe(probe, target))
        #     # _results.append(probe.run(target))
        #     analysis.add_probe(probe.run(target))
        # # _df = pd.DataFrame(_results, columns=['probe_id', 'result'])
        # logging.info(f"Analysis completed: {analysis.to_string()}")
        # # return reports.SubjectSection(target, _df)
        # # return {target: _results}
        # # return {target: _df}
        # return analysis
        pass
