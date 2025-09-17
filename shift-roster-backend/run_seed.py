import os
from seed_from_csv import main as seed_main, CSV_DIR


def _default_csv_dir():
    # Prefer explicit env var if set; else keep auto-detected CSV_DIR
    return os.environ.get('CSV_DIR') or CSV_DIR


if __name__ == '__main__':
    # Ensure working dir is the backend root so src imports work
    os.chdir(os.path.dirname(__file__))
    # Optionally set CSV_DIR if passed in env; seed script will print what it uses
    os.environ['CSV_DIR'] = _default_csv_dir()
    seed_main()
