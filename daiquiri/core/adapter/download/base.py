class DownloadAdapter(object):

    def generate(self, schema_name, table_name, format):
        raise NotImplementedError()

    def _get_fmt_list(self, columns):
        fmt_list = []
        null_value_list = []
        for column in columns:
            if column['arraysize'] is not None:
                if column['datatype'] == 'char':
                    # this is a string!
                    fmt_list.append(str(column['arraysize']) + 's')
                else:
                    fmt_list.append(str(column['arraysize']) + self.FORMATS[column['datatype']])

                null_value_list.append('')
            else:
                fmt_list.append(self.FORMATS[column['datatype']])
                null_value_list.append(self.NULL_VALUES[column['datatype']])

        return fmt_list, null_value_list

    def _parse_line(self, line):
        insert_result = self.insert_pattern.match(line.decode())
        if insert_result:
            row = insert_result.group(1)
            reader = csv.reader([row], quotechar="'")
            return six.next(reader)
        else:
            return None

    def _get_binary_values(self, parsed_line, fmt_list, null_value_list):
        values = []
        null_mask = ''

        for i, cell in enumerate(parsed_line):
            if cell == 'NULL':
                null_mask += '1'
                values.append(null_value_list[i])

            else:
                null_mask += '0'

                if fmt_list[i] in ['B', 'h', 'i', 'q']:
                    values.append(int(cell))

                elif fmt_list[i] in ['f', 'd']:
                    values.append(float(cell))

                else:  # char
                    values.append(cell)

        return values, null_mask
