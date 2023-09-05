import random


class Compiler:
    def __init__(self, ast: dict) -> None:
        self.__ast = ast

    def render_random_mixing_node(self, node: dict) -> str:
        values = []

        for sub_value in node['nodes']:
            sub_value_result = ''

            for value in sub_value:
                if isinstance(value, str):
                    sub_value_result += value
                elif value.get('type') == 'random_choice':
                    sub_value_result += self.render_random_choice_node(value)
                elif value.get('type') == 'random_mixing_with_delimiter':
                    sub_value_result += self.render_random_mixing_with_delimiter_node(
                        value
                    )
            values.append(sub_value_result)

        random.shuffle(values)
        return ''.join(values)

    def render_random_mixing_with_delimiter_node(self, node: dict) -> str:
        values = []

        for sub_value in node['nodes']:
            sub_value_result = ''

            for value in sub_value:
                if isinstance(value, str):
                    sub_value_result += value
                elif value.get('type') == 'random_choice':
                    sub_value_result += self.render_random_choice_node(value)
            values.append(sub_value_result)

        random.shuffle(values)
        render_result = node['delimiter'].join(values)
        return render_result

    def render_random_choice_node(self, node: dict) -> str:
        values = []

        for sub_value in node['nodes']:
            sub_value_result = ''

            for value in sub_value:
                if isinstance(value, str):
                    sub_value_result += value
                elif value.get('type') == 'random_choice':
                    sub_value_result += self.render_random_choice_node(value)
                elif value.get('type') == 'random_mixing':
                    sub_value_result += self.render_random_mixing_node(value)
                elif value.get('type') == 'random_mixing_with_delimiter':
                    sub_value_result += self.render_random_mixing_with_delimiter_node(
                        value
                    )
            values.append(sub_value_result)

        return random.choice(values)

    def render_ast(self) -> str:
        render_result = ''

        for node in self.__ast['nodes']:
            if isinstance(node, str):
                render_result += node
            elif node['type'] == 'random_choice':
                render_result += self.render_random_choice_node(node)
            elif node['type'] == 'random_mixing':
                render_result += self.render_random_mixing_node(node)
            elif node['type'] == 'random_mixing_with_delimiter':
                render_result += self.render_random_mixing_with_delimiter_node(
                    node
                )
        return render_result
