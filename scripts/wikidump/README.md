# WikiDump Scripts

- `dump_parser.py`
  - Description: [Parse](https://dumps.wikimedia.org/) the dump file and write the text to a file.

- `match_wikidump_with_milqa_title.py`
  - Description: This script matches the milqa dataset with the wikidump dataset.

- `wikiDump_extract_with_categories`
  - Description: Extract the wiki dump with the categories.
  - [git](https://github.com/attardi/wikiextractor) command: python -m wikiextractor.WikiExtractor data.xml
  - You can filter the wiki page's title with that [link](https://petscan.wmflabs.org/).
  
- `wikitext.py`
  - This script is used to extract the raw text from the wikitext file and store it in elasticsearch