import re
import string

URL_REGEX = r'((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*'
clean_url = lambda text: re.sub(URL_REGEX, ' ', text)
DOT_REGEX = r"(?<!\w)(?:[A-Z][A-Za-z]{,3}|[a-z]{1,2})\."

class Preprocessing:
    def __init__(self, content: str) -> str:
        self.content = content

    def _clear_abbreviation_dot(self, text: str) -> str:
        """used to rip off abbreviation dot in given text"""

        text_list = list(text)
        matches = re.finditer(DOT_REGEX, text)
        for i, m in enumerate(matches):
            no_dot = m.group().replace('.', '')
            start_end_idx = m.span()
            text_list[start_end_idx[0]-i: start_end_idx[1]-i] = no_dot

        # join list text and clear multiple whitespace
        text = ''.join(text_list)
        text = re.sub(r" +", ' ', text)

        return text

    def _process_text(self) -> str:
        """used to preprocess text article"""

        self.content = self._clear_abbreviation_dot(self.content)
        self.content = clean_url(self.content)

        # clear leading/tailing whitespaces & puncts
        self.content = self.content.strip(string.punctuation)
        self.content = self.content.strip()

        # clear from line boundaries (\n\n, \n)
        self.content = self.content.splitlines()
        self.content = " ".join(self.content)

        # clear bold, italic, and heading markdown
        self.content = re.sub(r'([_*]){1,}(\S(.*?\S)?)([_*]){1,}', r'\2', self.content)
        self.content = re.sub(r'[#]{1,}', '', self.content)

        # change multiple whitespaces to single one
        self.content = re.sub(' +', ' ', self.content)

        # clear whitespace before dot
        self.content = re.sub(r'\s+([?,.!"])', r'\1', self.content)

        return self.content