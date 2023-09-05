from .lexer import Lexeme, LexemeCodes


class Parser:
    def __init__(self, lexemes: list[Lexeme]) -> None:
        self.__lexemes = lexemes
        self.__lexeme_count = 0

    def _get_current_lexeme(self) -> Lexeme:
        return self.__lexemes[self.__lexeme_count]

    def get_random_choice_ast(self) -> dict:
        random_choice_ast = {
            'type': 'random_choice',
            'nodes': []
        }
        node_value_count = 0

        while self.__lexeme_count < len(self.__lexemes):
            lexeme = self._get_current_lexeme()

            if lexeme.code == LexemeCodes.delimiter:
                node_value_count += 1

            if lexeme.code == LexemeCodes.random_mixing_start:
                self.__lexeme_count += 1
                if len(random_choice_ast['nodes']) == node_value_count:
                    random_choice_ast['nodes'].append([])

                if self._get_current_lexeme().code != LexemeCodes.random_mixing_delimiter:
                    random_choice_ast['nodes'][node_value_count].append(
                        self.get_random_mixing_ast()
                    )
                else:
                    self.__lexeme_count += 1
                    random_choice_ast['nodes'][node_value_count].append(
                        self.get_random_mixing_with_delimiter_ast()
                    )

            if lexeme.code == LexemeCodes.text:
                if len(random_choice_ast['nodes']) == node_value_count:
                    random_choice_ast['nodes'].append([])

                random_choice_ast['nodes'][node_value_count].append(
                    lexeme.value
                )

            if lexeme.code == LexemeCodes.random_choice_start:
                self.__lexeme_count += 1
                if len(random_choice_ast['nodes']) == node_value_count:
                    random_choice_ast['nodes'].append([])

                random_choice_ast['nodes'][node_value_count].append(
                    self.get_random_choice_ast()
                )

            if lexeme.code == LexemeCodes.random_choice_end:
                break
            self.__lexeme_count += 1
        return random_choice_ast

    def get_random_mixing_ast(self) -> dict:
        random_mixing_ast = {
            'type': 'random_mixing',
            'nodes': []
        }
        node_value_count = 0

        while self.__lexeme_count < len(self.__lexemes):
            lexeme = self._get_current_lexeme()

            if lexeme.code == LexemeCodes.delimiter:
                node_value_count += 1

            if lexeme.code == LexemeCodes.random_choice_start:
                self.__lexeme_count += 1
                if len(random_mixing_ast['nodes']) == node_value_count:
                    random_mixing_ast['nodes'].append([])

                random_mixing_ast['nodes'][node_value_count].append(
                    self.get_random_choice_ast()
                )

            if lexeme.code == LexemeCodes.text:
                if len(random_mixing_ast['nodes']) == node_value_count:
                    random_mixing_ast['nodes'].append([])

                random_mixing_ast['nodes'][node_value_count].append(
                    lexeme.value
                )

            if lexeme.code == LexemeCodes.random_mixing_end:
                break
            self.__lexeme_count += 1
        return random_mixing_ast

    def get_random_mixing_with_delimiter_ast(self) -> dict:
        random_mixing_with_delimiter_ast = {
            'type': 'random_mixing_with_delimiter',
            'nodes': []
        }
        node_value_count = 0

        if self._get_current_lexeme().code == LexemeCodes.random_mixing_delimiter:
            random_mixing_with_delimiter_ast['delimiter'] = ''
            self.__lexeme_count += 1
        else:
            random_mixing_with_delimiter_ast['delimiter'] = self._get_current_lexeme(
            ).value
            self.__lexeme_count += 2

        while self.__lexeme_count < len(self.__lexemes):
            lexeme = self._get_current_lexeme()

            if lexeme.code == LexemeCodes.delimiter:
                node_value_count += 1

            if lexeme.code == LexemeCodes.random_choice_start:
                self.__lexeme_count += 1
                if len(random_mixing_with_delimiter_ast['nodes']) == node_value_count:
                    random_mixing_with_delimiter_ast['nodes'].append([])

                random_mixing_with_delimiter_ast['nodes'][node_value_count].append(
                    self.get_random_choice_ast()
                )

            if lexeme.code == LexemeCodes.text:
                if len(random_mixing_with_delimiter_ast['nodes']) == node_value_count:
                    random_mixing_with_delimiter_ast['nodes'].append([])

                random_mixing_with_delimiter_ast['nodes'][node_value_count].append(
                    lexeme.value
                )

            if lexeme.code == LexemeCodes.random_mixing_end:
                break
            self.__lexeme_count += 1
        return random_mixing_with_delimiter_ast

    def get_ast(self) -> dict:
        ast = {
            'type': 'root',
            'nodes': []
        }

        self.__lexeme_count = 0
        while self.__lexeme_count < len(self.__lexemes):
            lexeme = self._get_current_lexeme()

            if lexeme.code == LexemeCodes.text:
                ast['nodes'].append(lexeme.value)
            if lexeme.code == LexemeCodes.random_choice_start:
                self.__lexeme_count += 1
                ast['nodes'].append(self.get_random_choice_ast())
            if lexeme.code == LexemeCodes.random_mixing_start:
                self.__lexeme_count += 1
                if self._get_current_lexeme().code != LexemeCodes.random_mixing_delimiter:
                    ast['nodes'].append(self.get_random_mixing_ast())
                else:
                    self.__lexeme_count += 1
                    ast['nodes'].append(
                        self.get_random_mixing_with_delimiter_ast()
                    )

            self.__lexeme_count += 1
        return ast
