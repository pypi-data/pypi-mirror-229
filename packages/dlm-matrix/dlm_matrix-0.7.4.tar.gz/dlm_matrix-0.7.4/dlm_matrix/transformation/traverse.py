from typing import Callable, List
from dlm_matrix.transformation.tree import CoordinateTree
from dlm_matrix.transformation.coordinate import Coordinate


class CoordinateTreeTraverser:
    def __init__(self, tree: CoordinateTree):
        self.tree = tree

    def traverse_depth_first(
        self, predicate: Callable[[Coordinate], bool]
    ) -> Coordinate:
        return CoordinateTree.depth_first_search(self.tree, predicate)

    def traverse_breadth_first(
        self, predicate: Callable[[Coordinate], bool]
    ) -> Coordinate:
        return CoordinateTree.breadth_first_search(self.tree, predicate)

    def traverse_depth_first_all(
        self, predicate: Callable[[Coordinate], bool]
    ) -> List[Coordinate]:
        return CoordinateTree.depth_first_search_all(self.tree, predicate)
