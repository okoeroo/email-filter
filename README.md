# Email filter

To support requests for information, after approvals, the procedure is to request for a timeframe of email and receive a PST file.
In particular cases post-delivery and pre-processing filtering is required on the PST file to ensure that only the requested data is in the output.

## Motivation to publish

This script is published to offer transparancy, feedback via the Issues tracker, and as part of the WOO ruling itself to implicitly publish.

## emailfilter.py

This script:

1. Takes a PST file as input and used `readpst` to extract all emails, agenda items and attachments content. It dumps these into a temporary folder.
2. a list of emails is read from file.
3. The script (currently) discards all files and removes them from the tmpdir. Only .eml files are left.
4. Each .eml files is parsed and the filtering starts.
5. Based on the begin date and end date, all emails must have a Date header within the time window to be flagged as matched.
6. The list of emailaddresses is matched per email. If any of the emailaddresses is matched in the From, To, CC or BCC fields, the mail is flagged as matched.
7. When the email is matched both based on the timeframe and association, the file is kept on file. Otherwise, the file is discarded and removed.

## Commandline options

```txt
usage: emailfilter.py [-h] [-v] [--local-timezone LOCAL_TIMEZONE] --input-pst-path INPUT_PST_PATH
                      [--filter-match-emailaddresses-file-path FILTER_MATCH_EMAILADDRESSES_FILE_PATH] [--filter-match-emailaddresses-must-match {yes,no}]
                      [--filter-match-keywords-file-path FILTER_MATCH_KEYWORDS_FILE_PATH] [--filter-match-keywords-must-match {yes,no}]
                      [--filter-timeframe-begin-datetime FILTER_DATETIME_FRAME_BEGIN_DATETIME] [--filter-timeframe-end-datetime FILTER_DATETIME_FRAME_END_DATETIME]
                      --output-folder OUTPUT_FOLDER

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode. Default is off
  --local-timezone LOCAL_TIMEZONE
                        Set the local timezone, default is 'Europe/Amsterdam'
  --input-pst-path INPUT_PST_PATH
                        Input PST file.
  --filter-match-emailaddresses-file-path FILTER_MATCH_EMAILADDRESSES_FILE_PATH
                        Filepath to a file which lists emailaddresses to match. When any emailaddress matches To, CC, BCC or From the mail is selected. When not set, no
                        filter is applied on sender nor recipients.
  --filter-match-emailaddresses-must-match {yes,no}
                        When an emailaddress is on the list and 'yes' is set, the email is matched. When 'no' is set, the email will not match.
  --filter-match-keywords-file-path FILTER_MATCH_KEYWORDS_FILE_PATH
                        Filepath to a file which lists keywords to match. When any keyword matches, the email is selected. When not set, no mails are filtered
  --filter-match-keywords-must-match {yes,no}
                        When an keyword is on the list and 'yes' is set, the keyword is matched. When 'no' is set, the keyword will not match.
  --filter-timeframe-begin-datetime FILTER_DATETIME_FRAME_BEGIN_DATETIME
                        Begin datetime in ISO format, optional with timezone. Example: 2001-01-01T00:00:00+01:00
  --filter-timeframe-end-datetime FILTER_DATETIME_FRAME_END_DATETIME
                        End datetime in ISO format, optional with timezone. Example: 2030-01-24T23:59:59+01:00
  --output-folder OUTPUT_FOLDER
                        This is the output directory in which all results will be moved into
```

## Requirements

Python libraries:

* pip install pytz

Requires readpst:

* sudo apt-get install libpst-dev
* brew install libpst

