# History
Historical scripts

## Notes
#### <ins>Regex</ins>

Regex is used to parse a pdf link (i.e., the url).  Resources for regex:
- [Regex Match all characters between two strings](https://stackoverflow.com/questions/6109882/regex-match-all-characters-between-two-strings)
- [Regular Expression for getting everything after last slash](https://stackoverflow.com/questions/8945477/regular-expression-for-getting-everything-after-last-slash)

Results:
To match everything after http[s]// you can use <br>
`(?<=\/\/).*(?=\/)`  (to the last slash in url) <br>
or <br>
`(?<=\/\/).*?(?=\/)` (to the next slash url) <br>

To match the text after last slash of url <br>
`([^\/]+$)` <br>
