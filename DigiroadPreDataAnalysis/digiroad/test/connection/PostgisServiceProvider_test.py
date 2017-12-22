import os
import unittest

from digiroad.connection.PostgisServiceProvider import PostgisServiceProvider
from digiroad.util import CostAttributes, FileActions


class PostgisServiceProviderTest(unittest.TestCase):
    def setUp(self):
        self.postgisServiceProvider = PostgisServiceProvider()
        self.fileActions = FileActions()
        self.dir = os.getcwd()

    def test_givenAPairOfVertex_then_retrieveDijsktraOneToOneCostSummaryGeojson(self):
        dir = self.dir + '%digiroad%test%data%geojson%oneToOneCostSummary.geojson'.replace("%", os.sep)

        expectedSummary = self.fileActions.readJson(dir)
        summaryShortestPathCostOneToOne = self.postgisServiceProvider.getTotalShortestPathCostOneToOne(
            startVertexID=99080,
            endVertexID=49020,
            costAttribute=CostAttributes.DISTANCE
        )
        self.assertEqual(expectedSummary, summaryShortestPathCostOneToOne)

    def test_givenASetOfVertexesVsOneVertex_then_retrieveDijsktraManyToOneCostSummaryGeojson(self):
        dir = self.dir + '%digiroad%test%data%geojson%manyToOneCostSummary.geojson'.replace("%", os.sep)

        expectedSummary = self.fileActions.readJson(dir)
        summaryShortestPathCostManyToOne = self.postgisServiceProvider.getTotalShortestPathCostManyToOne(
            startVertexesID=[99080, 78618, 45174, 46020, 44823, 110372, 140220, 78317, 106993, 127209, 33861, 49020],
            endVertexID=99080,
            costAttribute=CostAttributes.DISTANCE
        )
        self.assertEqual(expectedSummary, summaryShortestPathCostManyToOne)

    def test_givenAVertexVsASetOfVertexes_then_retrieveDijsktraOneToManyCostSummaryGeojson(self):
        dir = self.dir + '%digiroad%test%data%geojson%oneToManyCostSummary.geojson'.replace("%", os.sep)

        expectedSummary = self.fileActions.readJson(dir)
        summaryShortestPathCostOneToMany = self.postgisServiceProvider.getTotalShortestPathCostOneToMany(
            startVertexID=99080,
            endVertexesID=[99080, 78618, 45174, 46020, 44823, 110372, 140220, 78317, 106993, 127209, 33861, 49020],
            costAttribute=CostAttributes.DISTANCE
        )
        self.assertEqual(expectedSummary, summaryShortestPathCostOneToMany)

    def test_givenASetOfVertexesVsASetOfVertexes_then_retrieveDijsktraManyToManyCostSummaryGeojson(self):
        dir = self.dir + '%digiroad%test%data%geojson%manyToManyCostSummary.geojson'.replace("%", os.sep)

        expectedSummary = self.fileActions.readJson(dir)
        summaryShortestPathCostManyToMany = self.postgisServiceProvider.getTotalShortestPathCostManyToMany(
            startVertexesID=[99080, 78618, 45174, 46020, 44823, 110372, 140220, 78317, 106993, 127209, 33861, 49020],
            endVertexesID=[99080, 78618, 45174, 46020, 44823, 110372, 140220, 78317, 106993, 127209, 33861, 49020],
            costAttribute=CostAttributes.DISTANCE
        )
        self.assertEqual(expectedSummary, summaryShortestPathCostManyToMany)
