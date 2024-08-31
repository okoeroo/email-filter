# emailfilter.py
This script:
1. Takes a PST file as input and used `readpst` to extract all emails, agenda items and attachments content. It dumps these into a temporary folder.
2. a list of emails is read from file.
3. The script (currently) discards all files and removes them from the tmpdir. Only .eml files are left.
4. Each .eml files is parsed and the filtering starts.
5. Based on the begin date and end date, all emails must have a Date header within the time window to be flagged as matched.
6. The list of emailaddresses is matched per email. If any of the emailaddresses is matched in the From, To, CC or BCC fields, the mail is flagged as matched.
7. When the email is matched both based on the timeframe and association, the file is kept on file. Otherwise, the file is discarded and removed.

## Commandline options
```
usage: emailfilter.py [-h] [-v] --input-pst-path INPUT_PST_PATH [--file-with-emailaddresses FILE_WITH_EMAILADDRESSES] --output-folder OUTPUT_FOLDER
                      [--begin-datetime BEGIN_DATETIME] [--end-datetime END_DATETIME] [--local-timezone LOCAL_TIMEZONE]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode. Default is off
  --input-pst-path INPUT_PST_PATH
                        Input PST file.
  --file-with-emailaddresses FILE_WITH_EMAILADDRESSES
                        File with emailaddresses
  --output-folder OUTPUT_FOLDER
                        This is the output directory in which all results will be moved into
  --begin-datetime BEGIN_DATETIME
                        Begin datetime, optional with timezone
  --end-datetime END_DATETIME
                        End datetime, optional with timezone
  --local-timezone LOCAL_TIMEZONE
                        Set the local timezone, default is 'Europe/Amsterdam'
```


## Requirements
Python libraries:
* pip install pytz 

Requires readpst:
* sudo apt-get install libpst-dev
* brew install libpst