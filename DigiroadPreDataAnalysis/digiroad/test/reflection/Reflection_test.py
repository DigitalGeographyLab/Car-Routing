import os
import unittest

from digiroad.additionalOperations import AbstractAdditionalLayerOperation
from digiroad.reflection import Reflection


class ReflectionTest(unittest.TestCase):
    def setUp(self):
        self.dir = os.getcwd()
        self.reflection = Reflection()

    def test_givenADirectory_retrieveAllDefinedAbstractOperation(self):
        mainPythonModulePath = "digiroad.additionalOperations"
        additionalOperationsList = self.reflection.getClasses(
            self.dir,
            mainPythonModulePath,
            AbstractAdditionalLayerOperation
        )

        self.assertGreater(len(additionalOperationsList), 0)
        for the_object in additionalOperationsList:
            self.assertIsInstance(the_object, AbstractAdditionalLayerOperation)

    @unittest.SkipTest  # Deprecated
    def test_givenTheAdditionalOperationsModuleDirectory_retrieveAllOrderedAbstractOperation(self):
        additionalOperationsList = self.reflection.getAbstractAdditionalLayerOperationObjects()
        self.assertGreater(len(additionalOperationsList), 0)
        counter = 1
        for the_object in additionalOperationsList:
            self.assertEqual(counter, the_object.getExecutionOrder())
            counter = counter + 1
            self.assertIsInstance(the_object, AbstractAdditionalLayerOperation)

    def test_givenAbstractAdditionalLayerOperation_then_returnALinkedListWithAllTheAvailableOperations(self):
        additionalLayerOperationLinkedList = self.reflection.getLinkedAbstractAdditionalLayerOperation()
        counter = 0
        while additionalLayerOperationLinkedList.hasNext():
            additionalLayerOperation = additionalLayerOperationLinkedList.next()
            counter = counter + 1
            self.assertIsInstance(additionalLayerOperation, AbstractAdditionalLayerOperation)

        self.assertEqual(4, counter)
