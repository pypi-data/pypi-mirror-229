# VBA-like and Useful Functions in Python

This module provides a set of VBA-like and other useful functions that you can use directly in your Python projects. Save the `cC.py` file to your project folder and import the functions using the following import statement:

```python
from cC import *
```

Alternatively you can import it with `pip`.

```python
pip install -U morvba
```

---
# Functions

---

## savesetting(a='', b='', c='', d='')
Save a setting to an INI file.

**Arguments:**

- `a`: Group name
- `b`: Subgroup name
- `c`: Item name
- `d`: Value

**Example:**

```python
savesetting("app", "window", "width", "1024")
```

---

## getsetting(a='', b='', c='', d='')
Retrieve a setting from an INI file.

**Arguments:**

- `a`: Group name
- `b`: Subgroup name
- `c`: Item name
- `d`: Default value (optional)

**Example:**

```python
window_width = getsetting("app", "window", "width", "")
```

---

## savesettingreg(a='', b='', c='', d='')
Save a setting to the Windows registry.

**Arguments:**

- `a`: Main key name
- `b`: Subkey name
- `c`: Value name
- `d`: Data to set

**Example:**

```python
savesettingreg("Software", "MyApp", "Version", "1.0")
```

---

## getsettingreg(a='', b='', c='', d='')
Retrieve a setting from the Windows registry.

**Arguments:**

- `a`: Main key name
- `b`: Subkey name
- `c`: Value name
- `d`: Default value (optional)

**Example:**

```python
version = getsettingreg("Software", "MyApp", "Version", "1.0")
```

---

## left(str_text='', int_len=1)
Return the left part of a string.

**Arguments:**

- `str_text`: Input string
- `int_len`: Number of characters to return (default is 1)

**Example:**

```python
result = left("Hello, world!", 5)
```

---

## right(str_text='', int_len=1)
Return the right part of a string.

**Arguments:**

- `str_text`: Input string
- `int_len`: Number of characters to return (default is 1)

**Example:**

```python
result = right("Hello, world!", 6)
```

---

## mid(str_text='', int_start=1, int_len=1)
Return a substring from the middle of a string.

**Arguments:**

- `str_text`: Input string
- `int_start`: Starting position
- `int_len`: Number of characters to return

**Example:**

```python
result = mid("Hello, world!", 8, 5)
```

---

## pricap(str_text='')
Capitalize the first letter of each word in a string.

**Arguments:**

- `str_text`: Input string

**Example:**

```python
result = pricap("hello, world!")
```

---

## instr(int_start=1, str_text='', str_what='')
Return the position of a substring in a string.

**Arguments:**

- `int_start`: Starting position
- `str_text`: Input string
- `str_what`: Substring to search for

**Example:**

```python
position = instr(1, "Hello, world!", "world")
```

---

## trim(str_text='', str_char=' ')
Trim spaces or a specific character from a string.

**Arguments:**

- `str_text`: Input string
- `str_char`: Character to trim (default is space)

**Example:**

```python
result = trim("   Hello, world!   ")
```

---

## pkey(str_text='', str_ini='', str_end='', boo_trim=True)
Extract a string between two delimiters.

**Arguments:**

- `str_text`: Input string
- `str_ini`: Starting delimiter
- `str_end`: Ending delimiter
- `boo_trim`: Whether to trim spaces (default is True)

**Example:**

```python
result = pkey("Example: [Hello, world!]", "[", "]")
```

---

## err(e='')
Print a formatted error message.

**Arguments:**

- `e`: The error message or exception

**Example:**

```python
try:
    # some code that might raise an exception
except Exception as e:
    err(e)
```

---

## text_to_list(text='')
Convert a string representation of a list back to a list.

**Arguments:**

- `text`: Input string representing a list

**Example:**

```python
my_list = text_to_list("[1, 2, 3]")
```

---

## remove_first_part_of_domain(url='')
Remove the subdomain from a given URL.

**Arguments:**

- `url`: The input URL

**Example:**

```python
domain = remove_first_part_of_domain("sub.example.com")
```

---

## get_base_url(url='')
Extract the base URL (portion before the "?").

**Arguments:**

- `url`: The input URL

**Example:**

```python
base = get_base_url("https://example.com/page?query=value")
```

---

## remove_html(text='')
Remove HTML, script, and style tags from a given text.

**Arguments:**

- `text`: The input text with HTML content

**Example:**

```python
clean_text = remove_html("<div>Hello <span>World</span></div>")
```

---

## extract_hrefs(html='')
Extract all href values from anchor tags in an HTML string.

**Arguments:**

- `html`: The input HTML content

**Example:**

```python
links = extract_hrefs("<a href='link1.html'>Link 1</a> <a href='link2.html'>Link 2</a>")
```

---

## remove_extra_whitespace(t='')
Remove extra whitespace from a given text.

**Arguments:**

- `t`: The input text

**Example:**

```python
cleaned_text = remove_extra_whitespace("This   is   a    text.")
```

---

## remove_html_tags(text='')
Remove all HTML tags from a given text.

**Arguments:**

- `text`: The input text with HTML content

**Example:**

```python
clean_text = remove_html_tags("<div>Hello <span>World</span></div>")
```

---

## remove_html_scripts(text='')
Remove script and style tags from a given HTML text.

**Arguments:**

- `text`: The input text with HTML content

**Example:**

```python
clean_text = remove_html_scripts("<script>alert('Hi');</script><div>Hello</div>")
```

---

## clean_space_line(text='')
Clean spaces and line breaks from a given text.

**Arguments:**

- `text`: The input text

**Example:**

```python
cleaned_text = clean_space_line("This   is   a    text.")
```

---

## convert_url_to_filename(url='')
Convert a URL to a filename by removing the protocol and replacing invalid characters.

**Arguments:**

- `url`: The input URL

**Example:**

```python
filename = convert_url_to_filename("https://example.com/page?query=value")
```

---

## md5(value='')
Generate an MD5 hash for a given value.

**Arguments:**

- `value`: The input value

**Example:**

```python
hash_value = md5("Hello World")
```

---

## jsGetUTCTime()
Get the current UTC time in a specific format.

**Example:**

```python
current_time = jsGetUTCTime()
```

---

## jsURLenc(u='')
URL encode a given string.

**Arguments:**

- `u`: The input string

**Example:**

```python
encoded = jsURLenc("Hello World!")
```

---

## jsURLdec(u='')
URL decode a given string.

**Arguments:**

- `u`: The encoded string

**Example:**

```python
decoded = jsURLdec("Hello%20World%21")
```

---

## jsGetDomainName(hostName='')
Get the domain name from a given URL or hostname.

**Arguments:**

- `hostName`: The input URL or hostname

**Example:**

```python
domain = jsGetDomainName("https://sub.example.com/page")
```

---

## is_url(str='')
Check if a given string is a valid URL.

**Arguments:**

- `str`: The input string

**Example:**

```python
is_valid = is_url("https://example.com")
```

---

## is_email(email_addr='')
Check if a given string is a valid email address.

**Arguments:**

- `email_addr`: The input email address

**Example:**

```python
is_valid_email = is_email("test@example.com")
```

---

## is_date(string='', fuzzy=False)
Check if a given string can be interpreted as a date.

**Arguments:**

- `string`: The input string
- `fuzzy`: Whether to ignore unknown tokens in the string

**Example:**

```python
is_valid_date = is_date("2023-09-07")
```

---

## num_tokens(messages='', model="gpt-4", stat_adjust=1.55)
Calculate the number of tokens used by a list of messages.

**Arguments:**

- `messages`: The input messages
- `model`: The model name (default is "gpt-4")
- `stat_adjust`: Statistical adjustment factor

**Example:**

```python
tokens = num_tokens(["Hello", "World"])
```

---

## open_encoding(file='')
Detect and open a file with its correct encoding.

**Arguments:**

- `file`: The path to the file

**Example:**

```python
content = open_encoding("sample.txt")
```

---

You can use these functions in your Python code without referencing the class name, just like you would in VBA.
