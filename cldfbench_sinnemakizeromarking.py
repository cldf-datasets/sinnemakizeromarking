import io
import pathlib
import re
import sys
import unicodedata
import zipfile
from itertools import chain
from urllib import request

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
    sources = {}
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
        return f'{glottocode}-{slug(name)}'
    else:
        return glottocode


def prepare_references_string(ref):
    ref = re.sub(
        r'\((?:quoted )?in ([^)]+)\)',
        r'\1',
        ref,
        flags=re.IGNORECASE)
    ref = ref.strip()
    return ref


def iter_references(references_string):
    rest = prepare_references_string(references_string)
    while rest:
        reference = {}
        # skip 'Personal knowledge'
        personal_knowledge_match = re.match('\s*Personal knowledge,?\s*', rest)
        if personal_knowledge_match:
            rest = rest[len(personal_knowledge_match.group()):]
            continue

        author_match = re.match('[^0-9(]+', rest)
        if author_match is None:
            raise ValueError("Expected author: '{}' (in '{}')".format(
                rest, references_string))
        reference['author'] = author_match.group().strip(', ')
        rest = rest[len(author_match.group()):]

        # skip (p.c.)
        pc_match = re.match(r'\(p.c.\),?\s*', rest)
        if pc_match:
            rest = rest[len(pc_match.group()):]
            continue

        # XXX: this can prob be one regex
        year_match = (
            re.match(r'\((no year|to appear)\)', rest)
            # for Hoel et al 1994-2003
            or re.match(r'(1994)-2003', rest)
            # for Sapir 1990 [1909]
            or re.match(r'(1990) \[1909\]', rest)
            # for Launey 2001-2
            or re.match(r'(2001-2)', rest)
            or re.match(r'(\d+[a-z]*)', rest))
        if year_match is None:
            raise ValueError("Expected year: '{}' (in '{}')".format(
                rest, references_string))
        reference['year'] = year_match.group(1).strip()
        rest = rest[len(year_match.group()):].strip()

        pages_match = re.match(
            r': ?(?:(?:[0-9\-]+|passim|iv|vi),?\s*)*',
            rest)
        if pages_match is not None:
            reference['pages'] = pages_match.group().strip(':, ')
            rest = rest[len(pages_match.group()):].strip()
        yield reference


VAN_PARTS = ['van', 'de', 'der']


def first_author_no_van(reference):
    names = [
        name
        for name in reference['author'].split()
        if name.lower() not in VAN_PARTS]
    return names[0]


def first_author_with_van(reference):
    name_parts = []
    for name in reference['author'].split():
        if name.lower() in VAN_PARTS:
            name_parts.append(name)
        else:
            name_parts.append(name)
            break
    return ''.join(name_parts)


def unaccent(s):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if c.isascii())


def prepare_author(author):
    author = author.replace('Lindström', 'Lindstroem')
    author = author.replace('Schönig', 'Schoenig')
    author = author.replace('Facundes', 'SilvaFacundes')
    author = unaccent(author.strip(', '))
    return author


def add_pages(bibkey, reference):
    if 'pages' in reference:
        return '{}[{}]'.format(bibkey, reference['pages'])
    else:
        return bibkey


def get_bibkey(reference, sources, lang_id):
    bibkey = None

    guess = '{}{}'.format(
        prepare_author(first_author_no_van(reference)),
        reference['year'])
    if guess in sources:
        return add_pages(guess, reference)

    guess = '{}{}'.format(
        prepare_author(first_author_with_van(reference)),
        reference['year'])
    if guess in sources:
        return add_pages(guess, reference)

    # TODO: match reference against manually added matches, to find missing
    # refs.
    # print(
    #     'WARNING: {}: cannot match reference:'.format(lang_id), reference,
    #     file=sys.stderr)
    return None


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
        custom_parameters = self.etc_dir.read_csv('parameters.csv', dicts=True)
        custom_parameters = {param['ID']: param for param in custom_parameters}
        custom_codes = {
            code['ID']: code
            for code in self.etc_dir.read_csv('codes.csv', dicts=True)}

        with open(metadata_folder / 'LingVariables.yaml') as f:
            ling_variables = load_yaml(f, YamlLoader)
            for parameter in ling_variables.values():
                if 'Levels' in parameter:
                    # Apparently, codes are stored in a multi-line string
                    # containing something that is almost yaml
                    codes_string = parameter['Levels'].replace(': >', ':')
                    parameter['Levels'] = load_yaml(codes_string, YamlLoader)

        reference_assocs = {
            gc: [trimmed for r in refs.split(';') if (trimmed := r.strip())]
            for gc, refs in self.etc_dir.read_csv('language-references.csv')}

        with open(bib_folder / 'references.bib', encoding='utf-8') as f:
            bibtex_strings = [
                clean_bibtex(entry_string)
                for entry_string in iter_bibtex_entries(f)]

        # create cldf data

        sources = parse_bibtex(bibtex_strings)
        language_references = {
            row['glottocode']:
            (
                row['Sources'],
                sorted(filter(None, set(chain(
                    (get_bibkey(
                        reference,
                        sources,
                        language_id(row['glottocode'], row['language']))
                     for reference in iter_references(row['Sources'])),
                    reference_assocs.get(row['glottocode']) or [])))),
            )
            for row in value_data}

        language_table = [
            {new_name: lang[old_name]
             for new_name, old_name in LANGUAGE_COL_MAP}
            for lang in language_data]
        for lang in language_table:
            source_prose, bibkeys = language_references[lang['Glottocode']]
            lang['Source_prose'] = source_prose
            lang['Source'] = list(filter(None, bibkeys))
            lang['ID'] = language_id(lang['Glottocode'], lang['Name'])
            if lang['Latitude']:
                lang['Latitude'] = float(lang['Latitude'].replace(',', '.'))
            if lang['Longitude']:
                lang['Longitude'] = float(lang['Longitude'].replace(',', '.'))

        parameter_table = [
            {
                'ID': slug(param_name),
                'Name': param_name,
                'Original_Name': param_name,
                'Description': param['Description'].strip(),
            }
            for param_name, param in ling_variables.items()
            if param.get('VariableType') == 'data']
        for param in parameter_table:
            if (custom_parameter := custom_parameters.get(param['ID'])):
                param['Name'] = custom_parameter.get('Name')
                param['Description'] = custom_parameter.get('Description')
                if (grammacodes := custom_parameter.get('Grammacodes')):
                    param['Grammacodes'] = [
                        id_.strip()
                        for id_ in grammacodes.split(',')]
        code_table = [
            {
                'ID': '{}-{}'.format(slug(param_id), slug(value)),
                'Parameter_ID': slug(param_id),
                'Name': value,
                'Description': description,
            }
            for param_id, param in ling_variables.items()
            for value, description in param.get('Levels', {}).items()]
        for code in code_table:
            if (custom_code := custom_codes.get(code['ID'])):
                code['Name'] = custom_code.get('Name', '')
                code['Description'] = custom_code.get('Description', '')
                code['Map_Icon'] = custom_code.get('Map_Icon', '')

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
            for parameter in map(lambda p: p['Original_Name'], parameter_table)
            if row.get(parameter, '').strip()]

        # cldf schema

        args.writer.cldf.add_component(
            'LanguageTable',
            'WALS_code', 'Genus', 'Family', 'Area', 'Continent',
            'Macrocontinent', 'Macrocontinent_SplitOldWorld', 'Circumpacific',
            {
                'datatype': 'string',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source',
                'separator': ';',
                'name': 'Source',
            },
            'Source_prose')
        args.writer.cldf.add_component(
            'ParameterTable',
            {
                'name': 'Grammacodes',
                'separator': ';',
            })
        args.writer.cldf.add_component('CodeTable', 'Map_Icon')

        # write cldf

        args.writer.cldf.add_sources(*sources.values())
        args.writer.objects['LanguageTable'] = language_table
        args.writer.objects['ParameterTable'] = parameter_table
        args.writer.objects['CodeTable'] = code_table
        args.writer.objects['ValueTable'] = value_table
