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

#### <ins>exec()</ins>
exec() is used to call the correct function to parse a pdf. then function name is provided in a yaml. <br>

References:
- [Read python function from a text file and assign it to variable](https://stackoverflow.com/questions/31920197/read-python-function-from-a-text-file-and-assign-it-to-variable)
- [How do I get the return value using python exec](https://stackoverflow.com/questions/23917776/how-do-i-get-the-return-value-when-using-python-exec-on-the-code-object-of-a-fun)
