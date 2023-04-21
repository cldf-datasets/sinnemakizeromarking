import io
import pathlib
import zipfile
from urllib import request

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from cldfbench import Dataset as BaseDataset


UPSTREAM_REPO = 'https://version.helsinki.fi/hals/sinnemaki/sinnemaki2010'
UPSTREAM_COMMIT = '4b37720b3c2e643660ab1426c73d9e3729f5b43f'
UPSTREAM_URL = '{repo}/-/archive/{commit}/sinnemaki2010-{commit}.zip'.format(
    repo=UPSTREAM_REPO,
    commit=UPSTREAM_COMMIT)


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
