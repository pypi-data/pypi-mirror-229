import re
import os


def deprecate(warning=''):
    def deprecated_wrapper(func):
        def wrapped(*args):
            print(f'WARNING: {func.__name__} is deprecated. {warning}'.strip())
            return func(*args)
        return wrapped
    return deprecated_wrapper


def _extract_content(html_text: str) -> str:
    """Extracts the body of an HTML string"""
    html_match = Placeholder.html_file_pattern.match(html_text)
    if html_match:
        indent_length = len(html_match.group('indent'))
        body_text = html_match.group('body')

        if body_text is None:
            text = ''
        else:
            split_body = body_text.split('\n')
            scrubbed_indentation = [line[indent_length:]
                                    for line in split_body[1:]]
            scrubbed_indentation = '\n'.join(scrubbed_indentation)

            text = split_body[0] + '\n' + scrubbed_indentation

        return text

    return html_text


def _element(name: str, content: str, indentation: int, inline: bool, **element_attributes) -> str:

    attributes = {}
    for key, value in element_attributes.items():
        formatted_key = re.sub(r'[^a-z0-9\-]', '_', key)
        while '__' in formatted_key:
            formatted_key = formatted_key.replace('__', '_')

        attributes[formatted_key] = value

    attributes = [f' {k}="{v}"' if isinstance(v, str)
                  else (f' {k}' if v else '')
                  for k, v in attributes.items()]
    attributes = ''.join(attributes)

    if not inline:
        indent_str = ' ' * 4
        newline = '\n' + (indent_str * indentation)
        indented_newline = newline + indent_str
        trailing_newline = '\n'
    else:
        newline, indented_newline, trailing_newline = '', '', ''

    if content is not None:
        content = content.splitlines()
        content = indented_newline.join(content)
        element_text = (f'{newline}<{name}{attributes}>'
                        f'{indented_newline}{content}'
                        f'{newline}</{name}>{trailing_newline}')
    else:
        element_text = f'{newline}<{name}{attributes}>{trailing_newline}'

    return element_text


class Placeholder:
    _HTML_PATTERN = (r'^<!DOCTYPE html>\s*<html.*>[\s\S]*<head>[\s\S]*<\/head>[\s\S]*'
                     r'<body>\n?(?P<indent>\s*)(?P<body>\S[\s\S]*>)?\s*<\/body>[\s\S]*<\/html>\s*$')
    _TITLE_PATTERN = r'(\s*)(<title>.*</title>)'
    _HEAD_PATTERN = r'<head>\s*'

    html_file_pattern = re.compile(_HTML_PATTERN)
    html_title_pattern = re.compile(_TITLE_PATTERN)
    html_head_pattern = re.compile(_HEAD_PATTERN)

    place_holder_pattern = re.compile(r'[A-Z0-9_]+')

    @staticmethod
    def create(placeholder_name: str) -> re.Pattern:
        if not re.match(Placeholder.place_holder_pattern, placeholder_name):
            raise ValueError

        pattern_str = r'(\s*)(<!-- ' + placeholder_name + r' -->)'

        return re.compile(pattern_str)


@deprecate('Use a FunctionalPage object instead')
class Page:

    def __init__(self, path: str, name: str = None):
        self.name = path.split('/')[-1].split('.')[0] if not name else name

        with open(path, 'r') as index_html_file:
            self._text = index_html_file.read()

        self._write_files = []

    def include_file(self, path: str):
        self._write_files.append(path)

    def inject_text(self, text: str, pattern: re.Pattern, element=None, **element_attributes):
        if Placeholder.html_file_pattern.match(text):
            html_match = Placeholder.html_file_pattern.search(text)
            indent_length = len(html_match.group('indent'))
            body_text = html_match.group('body')

            if body_text is None:
                text = ''
            else:
                split_body = body_text.split('\n')

                scrubbed_indentation = [line[indent_length:]
                                        for line in split_body[1:]]
                scrubbed_indentation = '\n'.join(scrubbed_indentation)

                text = split_body[0] + '\n' + scrubbed_indentation

        attributes = ''.join([f' {k}={v}'
                              for k, v in element_attributes.items()])

        pattern_match = pattern.search(self._text)

        try:
            indentation = pattern_match.group(1)
        except AttributeError:
            raise ValueError(f'pattern not found: {pattern}')

        if element is not None:
            subindentation = indentation + ' ' * 4
            text = text.replace('\n', '\n' + subindentation)
            text = f'{subindentation}{text}\n{indentation}'
            text = f'{indentation}<{element}{attributes}>\n{text}</{element}>'
        else:
            text = text.replace('\n', '\n' + indentation)
            text = f'{indentation}{text}'

        new_html = pattern.sub(text, self._text)
        self._text = new_html

    def inject(self, path: str, pattern: re.Pattern, element=None, **element_attributes):
        with open(path, 'r') as file:
            file_text = file.read()

        self.inject_text(file_text, pattern, element, **element_attributes)

    def write(self, output_folder: str):
        for in_file in self._write_files:
            file_name = in_file.split('/')[-1]
            out_file = os.path.join(output_folder, file_name)
            with open(in_file, 'rb') as file_in, open(out_file, 'wb') as file_out:
                file_out.write(file_in.read())

        index_path = os.path.join(output_folder, self.name + '.html')
        with open(index_path, 'w') as output:
            output.write(self._text)

    @property
    def text(self):
        return self._text


class FunctionalPage:
    def __init__(self, text: str, name: str, include_files=[]):
        self.name = name
        self._text = text
        self._write_files = include_files

    def include_file(self, path: str):
        self._write_files.append(path)
        return self

    def inject(self, text: str, pattern: re.Pattern, element=None, **element_attributes):
        text = _extract_content(text)
        attributes = ''.join([f' {k}={v}' for k, v in element_attributes.items()])
        pattern_match = pattern.search(self._text)

        try:
            indentation = pattern_match.group(1)
        except AttributeError:
            raise ValueError(f'pattern not found: {pattern}')

        if element is not None:
            subindentation = indentation + ' ' * 4
            text = text.replace('\n', '\n' + subindentation)
            text = f'{subindentation}{text}\n{indentation}'
            text = f'{indentation}<{element}{attributes}>\n{text}</{element}>'
        else:
            text = text.replace('\n', '\n' + indentation)
            text = f'{indentation}{text}'

        new_html = pattern.sub(text, self._text)
        return FunctionalPage(new_html, self.name, self._write_files)

    def inject_file(self, path: str, pattern: re.Pattern, 
                    element: str = None, **element_attributes):

        with open(path, 'r') as file:
            file_text = file.read()

        return self.inject(file_text, pattern, element, **element_attributes)

    def inject_title(self, name: str = None):
        name = self.name if not name else name
        element = _element('title', name, 1, True)

        if '<title>' in self.text:
            return self.inject(element, Placeholder.html_title_pattern)
        else:
            head_element = re.search(Placeholder.html_head_pattern, self.text)
            if head_element is None:
                raise ValueError(f'head element not found in {self.name}')
            else:
                head_element_str = head_element.group(0)

            injected_title = head_element_str + element
            text = re.sub(Placeholder.html_head_pattern, injected_title, self.text)
            return FunctionalPage(text, self.name, self._write_files)

    def write(self, output_folder: str):
        try:
            os.makedirs(output_folder)
        except FileExistsError:
            pass

        for in_file in self._write_files:
            file_name = in_file.split('/')[-1]
            out_file = os.path.join(output_folder, file_name)
            with open(in_file, 'rb') as file_in, open(out_file, 'wb') as file_out:
                file_out.write(file_in.read())

        index_path = os.path.join(output_folder, self.name + '.html')
        with open(index_path, 'w') as output:
            output.write(self._text)

        return self

    @property
    def text(self):
        return self._text

    @property
    def content(self):
        return _extract_content(self.text)
