import unittest

from unittest.mock import patch
from flowhigh.utils.converter import FlowHighSubmissionClass
from flowhigh.model import DBO


class ConverterTest(unittest.TestCase):
    _mock_response = {
        "version": "1.0",
        "status": "OK",
        "ts": "2023-08-22T21:04:38.703Z",
        "eltype": "parseql",
        "statement": [
            {
                "pos": "0-42",
                "ds": [
                    {
                        "pos": "0-42",
                        "type": "root",
                        "subType": "inline",
                        "out": {
                            "exprs": [
                                {
                                    "pos": "7-4",
                                    "oref": "C1",
                                    "eltype": "attr"
                                },
                                {
                                    "pos": "13-4",
                                    "oref": "C2",
                                    "eltype": "attr"
                                }
                            ],
                            "eltype": "out"
                        },
                        "in": {
                            "exprs": [
                                {
                                    "pos": "24-3",
                                    "oref": "T1",
                                    "eltype": "ds"
                                }
                            ],
                            "eltype": "in"
                        },
                        "modifiers": [
                            {
                                "type": "filtreg",
                                "op": {
                                    "pos": "34-8",
                                    "exprs": [
                                        {
                                            "pos": "34-4",
                                            "oref": "C1",
                                            "eltype": "attr"
                                        },
                                        {
                                            "value": 1,
                                            "eltype": "const"
                                        }
                                    ],
                                    "type": "EQ",
                                    "eltype": "op"
                                },
                                "eltype": "filter"
                            }
                        ],
                        "eltype": "ds"
                    }
                ],
                "rawInput": "select col1, col2 \nfrom tab\nwhere col1 = 1",
                "eltype": "statement"
            }
        ],
        "DBOHier": {
            "dbo": [
                {
                    "oid": "T1",
                    "type": "TABLE",
                    "name": "tab",
                    "dbo": [
                        {
                            "oid": "C1",
                            "type": "COLUMN",
                            "name": "col1",
                            "eltype": "dBO"
                        },
                        {
                            "oid": "C2",
                            "type": "COLUMN",
                            "name": "col2",
                            "eltype": "dBO"
                        }
                    ],
                    "eltype": "dBO"
                }
            ],
            "eltype": "dBOHier"
        }
    }

    def test_convert(self):
        def __init__(self, sql):
            self._parsed_tree = self._convert_node(sql)

        with patch.object(FlowHighSubmissionClass, '__init__', __init__):
            fh = FlowHighSubmissionClass(self._mock_response)
            self.assertEqual(len(fh.get_statements()), 1)

            statement = fh.get_statements()[-1]
            self.assertIsNotNone(statement.ds[-1].in_)
            self.assertIsNotNone(statement.ds[-1].out)

    def test_get_where_cols(self):
        def __init__(self, sql):
            self._parsed_tree = self._convert_node(sql)

        with patch.object(FlowHighSubmissionClass, '__init__', __init__):
            fh = FlowHighSubmissionClass(self._mock_response)
            stats = fh.get_statements()
            self.assertIsNotNone(stats)
            self.assertEqual(len(stats), 1)

            res = fh.get_where_cols(stats[0])
            self.assertEqual(len(res), 1)
            self.assertEqual([col.name for col in res], ["col1"])

    def test_get_tables(self):
        fh = FlowHighSubmissionClass(None)

        tab = DBO()
        tab.name = "tab"
        tab.type_ = "TABLE"

        fh.get_DBO_hierarchy = lambda: [tab]
        result = fh.get_tables()
        self.assertEqual([dbo.name for dbo in result], ["tab"])

    def test_get_table_columns(self):
        fh = FlowHighSubmissionClass(None)

        tab = DBO()
        tab.name = "tab"
        tab.type_ = "TABLE"
        col1 = DBO()
        col1.name = "col1"
        col1.type_ = "COLUMN"
        tab.dbo.append(col1)

        col2 = DBO()
        col2.name = "col2"
        col2.type_ = "COLUMN"
        tab.dbo.append(col2)

        fh.get_DBO_hierarchy = lambda: [tab]
        result = fh.get_table_columns(tab)
        self.assertEqual([dbo.name for dbo in result], ["col1", "col2"])

    if __name__ == '__main__':
        unittest.main()
