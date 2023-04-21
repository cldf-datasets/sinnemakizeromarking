import collections
import io
import pathlib
import sys
from urllib import request
import zipfile

from pybtex import database
from yaml import load as load_yaml
try:
    from yaml import CLoader as YamlLoader
except ImportError:
    from yaml import Loader as YamlLoader

from cldfbench import CLDFSpec, Dataset as BaseDataset
from csvw.utils import slug


UPSTREAM_REPO = 'https://version.helsinki.fi/hals/sinnemaki/sinnemaki2010'
UPSTREAM_COMMIT = '4b37720b3c2e643660ab1426c73d9e3729f5b43f'
UPSTREAM_URL = '{repo}/-/archive/{commit}/sinnemaki2010-{commit}.zip'.format(
    repo=UPSTREAM_REPO,
    commit=UPSTREAM_COMMIT)

LANGUAGE_COL_MAP = [
    ('Glottocode', 'glottocode'),
    ('ISO639P3code', 'iso_code'),
    ('WALS_code', 'wals_code'),
    ('Name', 'language'),
    ('Genus', 'genus'),
    ('Family', 'family'),
    ('Longitude', 'longitude'),
    ('Latitude', 'latitude'),
    ('Area', 'area'),
    ('Continent', 'continent'),
    ('Macroarea', 'macroarea'),
    ('Macrocontinent', 'macrocontinent.3'),
    ('Macrocontinent_SplitOldWorld', 'macrocontinent.4'),
    ('Circumpacific', 'circumpacific'),
]

LANGUAGES_WITH_DUPLICATE_GLOTTOCODES = [
    # damu1236
    'Galo',
    'Bokar',
    # halk1245
    'Halkomelem (Island)',
    'Halkomelem (Upriver)',
    # tama1331
    'Miisiirii',
    'Tama',
]


def iter_bibtex_entries(lines):
    entry = []
    for line in lines:
        line = line.rstrip('\n')
        if line.startswith('@'):
            if entry:
                yield '\n'.join(entry)
            entry = [line]
        elif line:
            entry.append(line)
    if entry:
        yield '\n'.join(entry)


def parse_bibtex(entry_strings):
    sources = collections.OrderedDict()
    for entry_string in entry_strings:
        bibdata = database.parse_string(entry_string, 'bibtex')
        if not bibdata.entries:
            continue
        assert len(bibdata.entries) == 1, "splitting didn't work: {}".format(
            entry_string)
        bibkey = next(iter(bibdata.entries))
        new_bibkey = bibkey
        number = 1
        while new_bibkey in sources:
            number += 1
            new_bibkey = '{}-{}'.format(bibkey, number)
        if new_bibkey != bibkey:
            print(
                'WARNING: duplicate bibkey', bibkey,
                'renamed to', new_bibkey,
                file=sys.stderr)
        sources[new_bibkey] = bibdata
    return sources


def clean_bibtex(bibtex_code):
    bibtex_code = bibtex_code.replace(
        '  title   = {Deep linguistic prehistory with particular reference to Andamanese},\n',
        '',
        1)
    return bibtex_code


def language_id(glottocode, name):
    if name in LANGUAGES_WITH_DUPLICATE_GLOTTOCODES:
        return '{}-{}'.format(glottocode, slug(name))
    else:
        return glottocode


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "sinnemakizeromarking"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(
            dir=self.cldf_dir,
            module='StructureDataset',
            metadata_fname='cldf-metadata.json')

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        print('downloading zipped raw data...')
        with request.urlopen(UPSTREAM_URL) as response:
            raw_data = response.read()
        print('extracting zipped raw data...')
        with zipfile.ZipFile(io.BytesIO(raw_data)) as zipped_data:
            for member in zipped_data.infolist():
                if member.is_dir():
                    continue
                # strip the the "$REPO-$COMMIT/" folder
                # (I wish there was a less low-level way to do this...)
                path_suffix = member.filename.replace(
                    'sinnemaki2010-{}/'.format(UPSTREAM_COMMIT), '')
                dest = self.raw_dir / 'sinnemaki2010' / path_suffix
                print('extracting {}...'.format(dest))
                if not dest.parent.exists():
                    dest.parent.mkdir(parents=True)
                with open(dest, 'wb') as f:
                    f.write(zipped_data.read(member))

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        >>> args.writer.objects['LanguageTable'].append(...)
        """
        # read raw data

        data_folder = self.raw_dir / 'sinnemaki2010' / 'data'
        metadata_folder = self.raw_dir / 'sinnemaki2010' / 'metadata'
        bib_folder = self.raw_dir / 'sinnemaki2010' / 'bibliography'

        language_data = data_folder.read_csv(
            'Register.csv', delimiter=';', dicts=True)
        value_data = data_folder.read_csv(
            'LingVariables.csv', delimiter=';', dicts=True)

        with open(metadata_folder / 'LingVariables.yaml') as f:
            ling_variables = load_yaml(f, YamlLoader)
            for parameter in ling_variables.values():
                if 'Levels' in parameter:
                    # Apparently, codes are stored in a multi-line string
                    # containing something that is almost yaml
                    codes_string = parameter['Levels'].replace(': >', ':')
                    parameter['Levels'] = load_yaml(codes_string, YamlLoader)

        with open(bib_folder / 'references.bib', encoding='utf-8') as f:
            bibtex_strings = [
                clean_bibtex(entry_string)
                for entry_string in iter_bibtex_entries(f)]

        # create cldf data

        language_table = [
            {new_name: lang[old_name]
             for new_name, old_name in LANGUAGE_COL_MAP}
            for lang in language_data]
        for lang in language_table:
            lang['ID'] = language_id(lang['Glottocode'], lang['Name'])
            lang['Latitude'] = float(
                lang['Latitude'].replace(',', '.') or 0)
            lang['Longitude'] = float(
                lang['Longitude'].replace(',', '.') or 0)

        parameter_table = [
            {
                'ID': slug(param_id),
                'Name': param_id,
                'Description': param['Description'].strip(),
            }
            for param_id, param in ling_variables.items()
            if param.get('VariableType') == 'data']
        code_table = [
            {
                'ID': '{}-{}'.format(slug(param_id), slug(value)),
                'Parameter_ID': slug(param_id),
                'Name': value,
                'Description': description,
            }
            for param_id, param in ling_variables.items()
            for value, description in param.get('Levels', {}).items()]

        sources = parse_bibtex(bibtex_strings)

        # TODO: source column
        value_table = [
            {
                'ID': '{}-{}'.format(
                    language_id(row['glottocode'], row['language']),
                    slug(parameter)),
                'Language_ID': language_id(row['glottocode'], row['language']),
                'Parameter_ID': slug(parameter),
                'Code_ID': '{}-{}'.format(slug(parameter), slug(row[parameter])),
                'Value': row[parameter],
            }
            for row in value_data
            for parameter in map(lambda p: p['Name'], parameter_table)
            if row.get(parameter, '').strip()]

        # cldf schema

        args.writer.cldf.add_component(
            'LanguageTable',
            'WALS_code', 'Genus', 'Family', 'Area', 'Continent',
            'Macrocontinent', 'Macrocontinent_SplitOldWorld' 'Circumpacific')
        args.writer.cldf.add_component('ParameterTable')
        args.writer.cldf.add_component('CodeTable')

        # write cldf

        args.writer.cldf.add_sources(*sources.values())
        args.writer.objects['LanguageTable'] = language_table
        args.writer.objects['ParameterTable'] = parameter_table
        args.writer.objects['CodeTable'] = code_table
        args.writer.objects['ValueTable'] = value_table
