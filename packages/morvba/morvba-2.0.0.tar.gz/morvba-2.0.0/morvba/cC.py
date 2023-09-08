import ast
import chardet
import colorama
import configparser
import datetime
import hashlib
import os
import re
import tiktoken
import traceback
import urllib.parse
import winreg
from colorama import Fore, Back, Style, init
from dateutil.parser import parse
from typing import Optional, List

class C:
    def __init__(self):
        """
        Initialize the class and set up colorama for terminal color support.
        """
        colorama.init(autoreset=True)

    def savesetting(self, a: str = '', b: str = '', c: str = '', d: str = '') -> None:
        """
        Save a setting to an INI file in a 'settings' directory.

        Args:
            a, b, c: Components of the filename.
            d: The key value to be saved.
        """
        path = "settings"
        if not os.path.exists(path):
            os.makedirs(path)
        config = configparser.ConfigParser()
        config[a + '_' + b + '_' + c] = {'key': d}
        with open(os.path.join(path, a + '_' + b + '_' + c + '.ini'), 'w') as configfile:
            config.write(configfile)

    def getsetting(self, a: str = '', b: str = '', c: str = '', d: str = '') -> Optional[str]:
        """
        Retrieve a setting from an INI file in the 'settings' directory.

        Args:
            a, b, c: Components of the filename.
            d: If provided, saves the setting before retrieving.

        Returns:
            The retrieved setting or an empty string if not found.
        """
        try:
            path = "settings"
            if not os.path.exists(path):
                os.makedirs(path)
            config = configparser.ConfigParser()
            config.read(os.path.join(path, a + '_' + b + '_' + c + '.ini'))
            if d == '':
                return config.get(a + '_' + b + '_' + c, 'key')
            else:
                self.savesetting(a, b, c, d)
                return d
        except:
            return ''

    def savesettingreg(self, a: str = '', b: str = '', c: str = '', d: str = '') -> None:
        """
        Save a setting to the Windows registry.

        Args:
            a, b: Components of the registry path.
            c: The registry key.
            d: The value to be saved.
        """
        registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'Software\\VB and VBA Program Settings\\{a}\\{b}')
        winreg.SetValueEx(registry_key, c, 0, winreg.REG_SZ, d)
        winreg.CloseKey(registry_key)

    def getsettingreg(self, a: str = '', b: str = '', c: str = '', d: str = '') -> Optional[str]:
        """
        Retrieve a setting from the Windows registry.

        Args:
            a, b: Components of the registry path.
            c: The registry key to retrieve.
            d: If provided, saves the setting to the registry before retrieving.

        Returns:
            The retrieved setting or an empty string if not found.
        """
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'Software\\VB and VBA Program Settings\\{a}\\{b}')
            value, regtype = winreg.QueryValueEx(registry_key, c)
            winreg.CloseKey(registry_key)
            if d == '':
                return value
            else:
                self.savesettingreg(a, b, c, d)
                return d
        except:
            return ''

    def left(self, str_text: str = '', int_len: int = 1) -> str:
        """
        Extract a substring from the left of the given string.

        Args:
            str_text: The input string.
            int_len: The number of characters to extract.

        Returns:
            The extracted substring.
        """
        return str_text[:int_len]

    def right(self, str_text: str = '', int_len: int = 1) -> str:
        """
        Extract a substring from the right of the given string.

        Args:
            str_text: The input string.
            int_len: The number of characters to extract.

        Returns:
            The extracted substring.
        """
        return str_text[-int_len:]

    def mid(self, str_text: str = '', int_start: int = 1, int_len: int = 1) -> str:
        """
        Extract a substring from the middle of the given string.

        Args:
            str_text: The input string.
            int_start: The starting position (1-indexed).
            int_len: The number of characters to extract.

        Returns:
            The extracted substring.
        """
        return str_text[int_start - 1:(int_start + int_len - 1)]

    def pricap(self, str_text: str = '') -> str:
        """
        Convert the given string to title case.

        Args:
            str_text: The input string.

        Returns:
            The title-cased string.
        """
        return str_text.title()

    def instr(self, int_start: int = 1, str_text: str = '', str_what: str = '') -> int:
        """
        Find the position of a substring in a string, starting from a given position.

        Args:
            int_start: The starting position (1-indexed).
            str_text: The input string.
            str_what: The substring to find.

        Returns:
            The position (1-indexed) of the substring, or 0 if not found.
        """
        return str_text.find(str_what, int_start - 1) + 1

    def trim(self, str_text: str = '', str_char: str = ' ') -> str:
        """
        Trim extra spaces from the given string.

        Args:
            str_text: The input string.
            str_char: The character to trim (default is space).

        Returns:
            The trimmed string.
        """
        x = str_text.strip()
        while self.instr(1, x, '  ') > 0:
            x = x.replace('  ', ' ')
        return x

    def pkey(self, str_text: str = '', str_ini: str = '', str_end: str = '', boo_trim: bool = True) -> str:
        """
        Extract a substring from between two other substrings.

        Args:
            str_text: The input string.
            str_ini: The starting delimiter.
            str_end: The ending delimiter.
            boo_trim: Whether to trim extra spaces from the result.

        Returns:
            The extracted substring, or an empty string if the delimiters are not found.
        """
        if self.instr(1, str_text, str_ini) > 0 and self.instr(1, str_text, str_end) > 0:
            if boo_trim:
                return self.trim(self.mid(str_text, self.instr(1, str_text, str_ini) + len(str_ini),
                                          self.instr(self.instr(1, str_text, str_ini) + len(str_ini), str_text,
                                                     str_end) - (self.instr(1, str_text, str_ini) + len(str_ini))))
            else:
                return self.mid(str_text, self.instr(1, str_text, str_ini) + len(str_ini),
                                self.instr(self.instr(1, str_text, str_ini) + len(str_ini), str_text, str_end) - (
                                            self.instr(1, str_text, str_ini) + len(str_ini)))
        else:
            return ''

    def err(self, e: str = '') -> None:
        """
        Display an error message with traceback information.

        Args:
            e: The error message or exception object.
        """
        current_dtime = datetime.now()
        formatted_datetime = current_dtime.strftime("%Y-%m-%d %H:%M:%S")   
        if e.__traceback__: 
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print(f"\n  {Fore.LIGHTYELLOW_EX}-- An error occurred in function '{tb.name}' at line {tb.lineno}:\n    {Fore.LIGHTBLACK_EX}{type(e).__name__} {Fore.LIGHTYELLOW_EX}// {Fore.LIGHTRED_EX}{str(e)}{Fore.LIGHTYELLOW_EX} at {str(formatted_datetime)}.{Style.RESET_ALL}\n")
            print(f"\n {Fore.LIGHTCYAN_EX}Traceback info:\n")    
            tb_info = traceback.extract_tb(e.__traceback__)
            i = "YELLOW"
            for frame in tb_info:
                color = Fore.YELLOW if i == "YELLOW" else Fore.CYAN
                print(f"{color}    File \"{frame.filename}\",\n        line {frame.lineno}, in {frame.name}{Fore.RESET}")        
                # Alternate the color
                i = "CYAN" if i == "YELLOW" else "YELLOW"
        else:
            print(f"\n  {Fore.LIGHTYELLOW_EX}-- An error occurred: {Fore.LIGHTRED_EX}{str(e)}\n")

    def text_to_list(self, text: str = '') -> List[str]:
        """
        Convert a string representation of a list to an actual list.

        Args:
            text: The input string.

        Returns:
            The converted list.
        """
        return ast.literal_eval(text)

    def remove_first_part_of_domain(self, url: str = '') -> str:
        """
        Remove the subdomain from a URL.

        Args:
            url: The input URL.

        Returns:
            The domain without the subdomain.
        """
        domain = urllib.parse.urlparse(url).netloc
        parts = domain.split('.')
        return '.'.join(parts[1:]) if len(parts) > 1 else domain

    def get_base_url(self, url: str = '') -> str:
        """
        Extract the base URL (portion before the "?").

        Args:
            url: The input URL.

        Returns:
            The base URL.
        """
        g = url.split('?')[0]
        return str(g).replace('/', '')

    def extract_hrefs(self, html: str = '') -> List[str]:
        """
        Extract all href attributes from anchor tags in an HTML string.

        Args:
            html: The input HTML string.

        Returns:
            A list of href values.
        """
        pattern = r'<a[^>]+href="([^">]+)"'
        hrefs = re.findall(pattern, html)
        return hrefs

    def remove_extra_whitespace(self, t: str = '') -> str:
        """
        Remove extra whitespace from a string.

        Args:
            t: The input string.

        Returns:
            The cleaned string.
        """
        t = re.sub('[ \t]+', ' ', t)  # replace multiple spaces or tabs with one space    
        t = t.replace('\n ','\n')
        t = re.sub('\n+', '\n', t)  # replace multiple newlines with one
        return t.strip()  # remove leading and trailing whitespace

    def remove_html_tags(self, text: str = '') -> str:
        """
        Remove all HTML tags from a string.

        Args:
            text: The input string.

        Returns:
            The cleaned string.
        """
        clean = re.compile('<.*?>', re.DOTALL)
        x = re.sub(clean, '', str(text).replace('&nbsp;', ' ').replace(' ', ' '))
        return remove_extra_whitespace(x)

    def remove_html_scripts(self, text: str = '') -> str:
        """
        Remove all script and style tags from an HTML string.

        Args:
            text: The input HTML string.

        Returns:
            The cleaned string.
        """
        clean = re.compile('<script.*?</script>', re.DOTALL)
        c = re.sub(clean, '', text)
        clean = re.compile('<style.*?</style>', re.DOTALL)
        return re.sub(clean, '', c)

    def clean_space_line(self, text: str = '') -> str:
        """
        Clean up extra spaces and newlines from a string.

        Args:
            text: The input string.

        Returns:
            The cleaned string.
        """
        t = re.sub('\s+', ' ', text)  # replace multiple spaces and newlines with one space
        t = re.sub('[ \t]+', ' ', t)  # replace multiple spaces or tabs with one space    
        t = t.replace('\n ','\n')
        t = re.sub('\n+', '\n', t)  # replace multiple newlines with one
        return t.strip()  # remove leading and trailing whitespace

    def remove_html(self, text: str = '') -> str:
        """
        Remove all HTML tags, scripts, and styles from a string.

        Args:
            text: The input string.

        Returns:
            The cleaned string.
        """
        clean = re.compile('<script.*?</script>', re.DOTALL)
        c = re.sub(clean, '', text)
        clean = re.compile('<style.*?</style>', re.DOTALL)
        d = re.sub(clean, '', c)
        clean = re.compile('<.*?>', re.DOTALL)
        r = re.sub(clean, '', str(d).replace('&nbsp;', ' ').replace(' ', ' '))
        return clean_space_line(r)

    def convert_url_to_filename(self, url: str = '') -> str:
        """
        Convert a URL to a valid filename by removing the protocol and replacing invalid characters.

        Args:
            url: The input URL.

        Returns:
            The converted filename.
        """
        # Remove the protocol and replace invalid characters with '_'
        filename = re.sub(r'https?://', '', url)  # Remove 'http://' or 'https://'
        filename = re.sub(r'[\\/:*?"<>|]', '_', filename)  # Replace invalid characters with '_'
        filename = re.sub(r'[. ]$', '', filename)  # Remove trailing '.' or ' '
        return filename

    def md5(self, value: str = '') -> str:
        """
        Compute the MD5 hash of a string.

        Args:
            value: The input string.

        Returns:
            The MD5 hash.
        """
        m = hashlib.md5()
        m.update(value.encode('utf-8'))
        return m.hexdigest()

    def jsGetUTCTime(self) -> str:
        """
        Get the current UTC time in a JavaScript-friendly format.

        Returns:
            The formatted UTC time.
        """
        d = datetime.utcnow()
        return d.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def jsURLenc(self, u: str = '') -> str:
        """
        URL-encode a string.

        Args:
            u: The input string.

        Returns:
            The URL-encoded string.
        """
        return urllib.parse.quote(u)

    def jsURLdec(self, u: str = '') -> str:
        """
        URL-decode a string.

        Args:
            u: The URL-encoded string.

        Returns:
            The decoded string.
        """
        return urllib.parse.unquote(u)

    def jsGetDomainName(self, hostName: str = '') -> str:
        """
        Extract the domain name from a URL.

        Args:
            hostName: The input URL.

        Returns:
            The domain name.
        """
        parsed_uri = urllib.parse.urlparse(hostName)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        return domain

    def is_url(self, str: str = '') -> bool:
        """
        Check if a string is a valid URL.

        Args:
            str: The input string.

        Returns:
            True if the string is a valid URL, False otherwise.
        """
        pattern = re.compile(
            r'^(https?:\/\/)?'  # protocol
            r'((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|'  # domain name and extension
            r'((\d{1,3}\.){3}\d{1,3}))'  # OR ip (v4) address
            r'(\:\d+)?'  # port
            r'(\/[-a-z\d%_.~+]*)*'  # path
            r'(\?[;&a-z\d%_.~+=-]*)?'  # query string
            r'(\#[-a-z\d_]*)?$',  # fragment locator
            re.IGNORECASE
        )
        return bool(pattern.match(str))

    def is_email(self, email_addr: str = '') -> bool:
        """
        Check if a string is a valid email address.

        Args:
            email_addr: The input string.

        Returns:
            True if the string is a valid email address, False otherwise.
        """
        reg_ex = re.compile(r"^[-+.\w]{1,64}@[-.\w]{1,64}\.[-.\w]{2,6}$")
        return bool(reg_ex.match(email_addr))

    def is_date(self, string: str = '', fuzzy: bool = False) -> bool:
        """
        Check if a string can be interpreted as a date.

        Args:
            string: The input string.
            fuzzy: If True, ignore unknown tokens in the string.

        Returns:
            True if the string can be interpreted as a date, False otherwise.
        """
        try: 
            parse(string, fuzzy=fuzzy)
            return True
        except:
            return False

    def num_tokens(self, messages: str = '', model: str = "gpt-4", stat_adjust: float = 1.55) -> int:
        """
        Estimate the number of tokens used by a list of messages.

        Args:
            messages: The input messages.
            model: The model name (default is "gpt-4").
            stat_adjust: A statistical adjustment factor.

        Returns:
            The estimated number of tokens.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        if model[:4] == "gpt-":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
        else: # Approximate the number of tokens in a text string.
            text = messages.replace("+", " ").replace(".", " ").replace(",", " ").replace("-", " ").replace("_", " ").replace("!", " ").replace("?", " ").replace(":", " ").strip()
            while "  " in text:
                text = text.replace("  ", " ")
            num_words = len(text.split(' '))
            num_tokens = stat_adjust * num_words  # statistical adjustment for real tokens

        return int(num_tokens)

    def open_encoding(self, file: str = '') -> str:
        """
        Open a file with the correct character encoding.

        Args:
            file: The path to the file.

        Returns:
            The file content as a string.
        """
        with open(file, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result.get('encoding', 'utf-8')  # Default to utf-8 if encoding can't be determined
            return rawdata.decode(encoding, errors='replace')  # Decode using the detected encoding
        

# Wrapper functions
def savesetting(a: str = '', b: str = '', c: str = '', d: str = '') -> None:
    c_instance = C()
    return c_instance.savesetting(a, b, c, d)


def getsetting(a: str = '', b: str = '', c: str = '', d: str = '') -> Optional[str]:
    c_instance = C()
    return c_instance.getsetting(a, b, c, d)


def savesettingreg(a: str = '', b: str = '', c: str = '', d: str = '') -> None:
    c_instance = C()
    return c_instance.savesettingreg(a, b, c, d)


def getsettingreg(a: str = '', b: str = '', c: str = '', d: str = '') -> Optional[str]:
    c_instance = C()
    return c_instance.getsettingreg(a, b, c, d)


def left(str_text: str = '', int_len: int = 1) -> str:
    c_instance = C()
    return c_instance.left(str_text, int_len)


def right(str_text: str = '', int_len: int = 1) -> str:
    c_instance = C()
    return c_instance.right(str_text, int_len)


def mid(str_text: str = '', int_start: int = 1, int_len: int = 1) -> str:
    c_instance = C()
    return c_instance.mid(str_text, int_start, int_len)


def pricap(str_text: str = '') -> str:
    c_instance = C()
    return c_instance.pricap(str_text)


def instr(int_start: int = 1, str_text: str = '', str_what: str = '') -> int:
    c_instance = C()
    return c_instance.instr(int_start, str_text, str_what)


def trim(str_text: str = '', str_char: str = ' ') -> str:
    c_instance = C()
    return c_instance.trim(str_text, str_char)


def pkey(str_text: str = '', str_ini: str = '', str_end: str = '', boo_trim: bool = True) -> str:
    c_instance = C()
    return c_instance.pkey(str_text, str_ini, str_end, boo_trim)


def err(e: str = '') -> None:
    c_instance = C()
    return c_instance.err(e)


def text_to_list(text: str = '') -> List[str]:
    c_instance = C()
    return c_instance.text_to_list(text)


def remove_first_part_of_domain(url: str = '') -> str:
    c_instance = C()
    return c_instance.remove_first_part_of_domain(url)


def get_base_url(url: str = '') -> str:
    c_instance = C()
    return c_instance.get_base_url(url)


def remove_html(text: str = '') -> str:
    c_instance = C()
    return c_instance.remove_html(text)


def extract_hrefs(html: str = '') -> List[str]:
    c_instance = C()
    return c_instance.extract_hrefs(html)


def remove_extra_whitespace(t: str = '') -> str:
    c_instance = C()
    return c_instance.remove_extra_whitespace(t)


def remove_html_tags(text: str = '') -> str:
    c_instance = C()
    return c_instance.remove_html_tags(text)


def remove_html_scripts(text: str = '') -> str:
    c_instance = C()
    return c_instance.remove_html_scripts(text)


def clean_space_line(text: str = '') -> str:
    c_instance = C()
    return c_instance.clean_space_line(text)


def convert_url_to_filename(url: str = '') -> str:
    c_instance = C()
    return c_instance.convert_url_to_filename(url)


def md5(value: str = '') -> str:
    c_instance = C()
    return c_instance.md5(value)


def jsGetUTCTime() -> str:
    c_instance = C()
    return c_instance.jsGetUTCTime()


def jsURLenc(url: str = '') -> str:
    c_instance = C()
    return c_instance.jsURLenc(url)


def jsURLdec(url: str = '') -> str:
    c_instance = C()
    return c_instance.jsURLdec(url)


def jsGetDomainName(hostName: str = '') -> str:
    c_instance = C()
    return c_instance.jsGetDomainName(hostName)


def is_url(str: str = '') -> bool:
    c_instance = C()
    return c_instance.is_url(str)


def is_email(email_addr: str = '') -> bool:
    c_instance = C()
    return c_instance.is_email(email_addr)


def is_date(string: str = '', fuzzy: bool = False) -> bool:
    c_instance = C()
    return c_instance.is_date(string, fuzzy)


def num_tokens(messages: str = '', model: str = "gpt-4", stat_adjust: float = 1.55) -> int:
    c_instance = C()
    return c_instance.num_tokens(messages, model, stat_adjust)


def open_encoding(file: str = '') -> str:
    c_instance = C()
    return c_instance.open_encoding(file)

