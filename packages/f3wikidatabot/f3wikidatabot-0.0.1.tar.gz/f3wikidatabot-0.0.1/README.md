# F3 Wikidata Bot

f3wikidatabot is a command-line toolbox for the wikidata `Forges project <https://www.wikidata.org/wiki/Wikidata:WikiProject_Informatics/Forges>`_

## Setup

```sh
git clone --recursive https://lab.forgefriends.org/friendlyforgeformat/f3-wikidata-bot.git
cd f3-wikidata-bot
echo layout python3 > .envrc
direnv allow
pip install poetry
poetry install
```

## Usage

```sh
PYTHONPATH=$(pwd) python bin/f3wikidatabot  --help
```

## License

This project is licensed under the GPLv3+ License.
