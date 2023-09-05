import os
import sys
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..'))
import unittest
import pandas as pd
import numpy as np
import pytest
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from src.bert import BertCircles


BERT_COMPONENT_ID = 165
BERT_COMPONENT_NAME = 'bert-local-python-package'

logger_code_init = {
    'component_id': BERT_COMPONENT_ID,
    'component_name': BERT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'tal@circlez.ai'
}
logger = Logger.create_logger(object=logger_code_init)

class TestBertCircles(unittest.TestCase):
    def setUp(self):
        self.bert = BertCircles()
        self.csv_table = pd.DataFrame({'field2': ['data science', 'software engineering', 'database management'],
                                       'field1': [1, 2, 3]})

    def test_get_sentence_embedding(self):
        logger.start(object={})
        sentence = 'This is a sample sentence for testing'
        embedding = self.bert.get_sentence_embedding(sentence)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (1, 768))
        logger.end("Test succeeded", object={})

    def test_classify(self):
        logger.start(object={})
        # Test when best match is the first row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Data Scientist',self.csv_table)
        self.assertEqual(result, ['data science', 1])

        # Test when best match is the second row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Software Engineering Job',self.csv_table)
        self.assertEqual(result, ['software engineering', 2])

        # Test when best match is the third row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Database Administrator', self.csv_table)
        self.assertEqual(result, ['database management', 3])
        
        logger.end("Test succeeded", object={})


if __name__ == '__main__':
    unittest.main()
