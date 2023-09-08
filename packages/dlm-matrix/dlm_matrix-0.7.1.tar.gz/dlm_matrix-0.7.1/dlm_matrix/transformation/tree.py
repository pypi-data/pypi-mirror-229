from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from dlm_matrix.transformation.coordinate import Coordinate
from pydantic import Field
import numpy as np
from collections import defaultdict


class CoordinateTree(Coordinate):  # Inherits from Coordinate
    children: List["CoordinateTree"] = Field(
        default_factory=list, description="The children of the node."
    )

    tree_structure: Dict[str, Any] = Field(
        default_factory=dict,
        description="The tree structure representing the messages.",
    )

    coordinates: Dict[str, Union[Coordinate, Dict[str, np.ndarray]]] = Field(
        default_factory=dict,
        description="A dictionary mapping node IDs to their corresponding message nodes.",
    )
    message_info: Any = Field(None)  # or a more specific type if you have one

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @classmethod
    def from_tree_structure(
        cls, message_id: str, tree_structure: Dict[str, Dict[str, Any]]
    ) -> "CoordinateTree":
        node_info = tree_structure.get(message_id, {})
        children = [
            cls.from_tree_structure(child_id, tree_structure)
            for child_id in node_info.get("children", [])
        ]
        message_info = node_info.get("message", {})
        return cls(id=message_id, children=children, message_info=message_info)

    @staticmethod
    def tree_to_tetra_dict(
        tree: "CoordinateTree",
    ) -> Dict[str, Tuple[float, float, float, float, int]]:
        """
        Converts a CoordinateTree into a dictionary where each key is a node id,
        and the value is a tuple containing (x, y, z, t, n_parts) for that node.

        Parameters:
            tree (CoordinateTree): The root of the CoordinateTree.

        Returns:
            Dict[str, Tuple[float, float, float, float, int]]: A dictionary mapping node IDs to tuples of coordinates.
        """

        tetra_dict = {}
        stack = [tree]

        while stack:
            node = stack.pop()

            if not node.id:
                continue

            # Validate the coordinates
            if any(
                val is None for val in [node.x, node.y, node.z, node.t, node.n_parts]
            ):
                continue

            # Add to tetra_dict
            tetra_dict[node.id] = (node.x, node.y, node.z, node.t, node.n_parts)

            # Add children to stack
            stack.extend(node.children)

        return tetra_dict

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

    def find_node_by_id(self, node_id: str) -> Optional["CoordinateTree"]:
        for node in self:
            if node.id == node_id:
                return node
        return None

    def add_child(self, parent: str, child: "CoordinateTree"):
        if parent not in self.coordinates:
            raise ValueError(f"No parent coordinate with id: {parent}")

        child_id = child.id
        self.tree_structure.setdefault(parent, []).append(child_id)
        self.coordinates[child_id] = child
        self.children.append(child)

    def remove_child(self, node_id: str):
        if node_id not in self.coordinates:
            raise ValueError(f"No node with id: {node_id}")

        del self.coordinates[node_id]
        for children in self.tree_structure.values():
            if node_id in children:
                children.remove(node_id)

    def get_branch(self, branch_id: str) -> List[Coordinate]:
        if branch_id not in self.tree_structure:
            raise ValueError(f"No branch with id: {branch_id}")

        branch = [self.coordinates[branch_id]]
        for child_id in self.tree_structure[branch_id]:
            branch.extend(self.get_branch(child_id))
        return branch

    def add_branch(self, parent_id: str, branch: List[Coordinate]):
        """Adds a list of Coordinates as a branch under a given parent ID."""
        if parent_id not in self.coordinates:
            raise ValueError(f"No parent coordinate with id: {parent_id}")

        for node in branch:
            self.add_child(parent_id, node)

    def remove_branch(self, branch_id: str):
        """Removes a branch rooted at the given ID from the tree."""
        if branch_id not in self.tree_structure:
            raise ValueError(f"No branch with id: {branch_id}")

        children = self.tree_structure.get(branch_id, [])
        for child_id in children:
            self.remove_branch(child_id)

        self.remove_child(branch_id)
        del self.tree_structure[branch_id]

    def get_branches(self) -> List[List[Coordinate]]:
        branches = []
        for node_id in self.tree_structure:
            branches.append(self.get_branch(node_id))
        return branches

    @classmethod
    def build_from_dict(cls, d: Dict[str, Any]) -> "CoordinateTree":
        return cls(
            id=d["id"],
            x=d["x"],
            y=d["y"],
            z=d["z"],
            t=d["t"],
            n_parts=d["n_parts"],
            children=[cls.build_from_dict(child) for child in d["children"]],
            tree_structure=d["tree_structure"],
            coordinates=d["coordinates"],
        )

    def classify_by_depth(
        self,
    ) -> Dict[float, Dict[str, Union[List["CoordinateTree"], float]]]:
        """
        Classify the nodes by their depth and compute the density of nodes at each depth.

        :return: Dictionary where keys are depths, and values are another dictionary containing nodes at that depth and the density.
        """

        # Group nodes by their depth
        nodes_by_depth = defaultdict(list)
        total_nodes = 0

        for node in self:
            depth = self.fetch_value("x")
            nodes_by_depth[depth].append(node)
            total_nodes += 1

        # Compute the density for each depth and restructure the result
        depth_density_data = {}

        for depth, nodes in nodes_by_depth.items():
            density = len(nodes) / total_nodes
            depth_density_data[depth] = {"nodes": nodes, "density": density}

        return depth_density_data

    def compute_sibling_sequences(
        self, nodes: List["CoordinateTree"]
    ) -> List[List["CoordinateTree"]]:
        """
        Compute sequences of uninterrupted siblings while considering chronology.

        :param nodes: List of CoordinateTree objects to sequence.
        :return: List of sequenced CoordinateTree objects based on y and t values.
        """

        # First, sort nodes by their y-coordinate. In case of a tie (same y-coordinate), sort by t-coordinate
        nodes.sort(key=lambda node: (node.fetch_value("y"), node.fetch_value("t")))

        sequences = [[nodes[0]]]

        for i in range(1, len(nodes)):
            # Check if the y-coordinate of the current node is consecutive to the previous node
            is_consecutive_y = (
                nodes[i].fetch_value("y") == nodes[i - 1].fetch_value("y") + 1
            )

            # If nodes have the same y-coordinate, they should be sequenced based on t-values
            is_same_y = nodes[i].fetch_value("y") == nodes[i - 1].fetch_value("y")
            is_earlier_t = nodes[i].fetch_value("t") < nodes[i - 1].fetch_value("t")

            if is_consecutive_y or (is_same_y and not is_earlier_t):
                sequences[-1].append(nodes[i])
            else:
                sequences.append([nodes[i]])
        return sequences

    def check_homogeneity(
        self, sequence: List["CoordinateTree"]
    ) -> List[Dict[str, Any]]:
        """
        Check homogeneity within a sequence with depth-based importance score.

        :param sequence: List of CoordinateTree objects to check for homogeneity.
        :return: List of dictionaries containing homogeneous groups and their importance scores.
        """

        # Lists to keep track of homogeneous groups and their corresponding importance scores
        homogeneous_groups = []
        importance_scores = []

        # Calculate the initial importance score for the first coordinate in the sequence
        importance_scores.append(
            sequence[0].fetch_value("x") * len(sequence[0].children)
        )

        current_group = [sequence[0]]
        for i in range(1, len(sequence)):
            if sequence[i].fetch_value("z") == sequence[i - 1].fetch_value("z"):
                current_group.append(sequence[i])
                importance_scores[-1] += sequence[i].fetch_value("x") * len(
                    sequence[i].children
                )
            else:
                homogeneous_groups.append(
                    {
                        "group": current_group,
                        "importance_score": importance_scores[-1] / len(current_group),
                    }
                )
                current_group = [sequence[i]]
                importance_scores.append(
                    sequence[i].fetch_value("x") * len(sequence[i].children)
                )

        # Add the last group to the result
        if current_group:
            homogeneous_groups.append(
                {
                    "group": current_group,
                    "importance_score": importance_scores[-1] / len(current_group),
                }
            )

        return homogeneous_groups

    def compute_group_sizes(self) -> Dict[float, float]:
        """Compute the depth-adjusted size of each homogeneous group in the tree."""
        group_sizes = defaultdict(float)

        for node in self:
            z_value = node.fetch_value("z")
            adjustment_factor = 1 / (1 + node.fetch_value("x"))
            group_sizes[z_value] += adjustment_factor

        return group_sizes

    def get_group_characteristics(
        self, groups: List[List["CoordinateTree"]]
    ) -> List[Dict[str, Union[float, List["CoordinateTree"]]]]:
        """
        Extracts key characteristics: size, mean depth, temporal range, spatial density,
        and time consistency of the groups.
        """
        group_characteristics = []

        for group in groups:
            depths = [node.fetch_value("x") for node in group]
            times = [node.fetch_value("t") for node in group]

            size = len(group)
            mean_depth = sum(depths) / size
            temporal_range = max(times) - min(times)

            spatial_density = sum(node.fetch_value("y") for node in group) / (
                size * mean_depth
            )
            time_consistency = 1 / (1 + temporal_range)

            characteristics = {
                "size": size,
                "mean_depth": mean_depth,
                "temporal_range": temporal_range,
                "spatial_density": spatial_density,
                "time_consistency": time_consistency,
                "group": group,
            }
            group_characteristics.append(characteristics)

        return group_characteristics

    def find_maximus_triangle(self) -> List["CoordinateTree"]:
        """
        Discovers the Maximus Triangle prioritizing balanced triangular structures.
        Uses a weighted scoring system for metrics.
        """
        nodes_by_depth = self.classify_by_depth()
        maximus_triangle = []
        max_score = 0

        WEIGHTS = {
            "size": 1.0,
            "mean_depth": 0.5,
            "spatial_density": 1.5,
            "time_consistency": 1.2,
        }

        for nodes in nodes_by_depth.values():
            sequences = self.compute_sibling_sequences(nodes)
            for sequence in sequences:
                homogeneous_groups = self.check_homogeneity(sequence)
                group_characteristics = self.get_group_characteristics(
                    homogeneous_groups
                )

                for characteristics in group_characteristics:
                    score = sum(WEIGHTS[key] * characteristics[key] for key in WEIGHTS)

                    if score > max_score:
                        max_score = score
                        maximus_triangle = characteristics["group"]

        return maximus_triangle

    def rotate_subtree(self, subtree_id: str, angle_degree: float):
        """
        Rotates a given subtree by the specified angle (in degrees)
        around its root node. This can be a simulation of shifting a conversation topic.
        """
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return

        for node in subtree:
            # Just a simple rotation around the 'y' axis (can be extended to other axes)
            x, y = node.fetch_value("x"), node.fetch_value("y")
            angle_rad = np.radians(angle_degree)
            new_x = x * np.cos(angle_rad) - y * np.sin(angle_rad)
            new_y = x * np.sin(angle_rad) + y * np.cos(angle_rad)
            if isinstance(node, Coordinate):
                node.x = new_x
                node.y = new_y
            else:
                node[0], node[1] = new_x, new_y

    def subtree_by_node_id(self, node_id: str) -> Optional["CoordinateTree"]:
        """Fetches a subtree starting from the provided node id."""
        for subtree in self:
            if subtree.root_id == node_id:
                return subtree
        return None

    def get_subtree_coordinates(self, subtree_id: str) -> List[Coordinate]:
        """Fetches the coordinates of a subtree."""
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return []

        return [node for node in subtree]

    def get_subtree_coordinates_by_depth(
        self, subtree_id: str
    ) -> Dict[float, List[Coordinate]]:
        """Fetches the coordinates of a subtree by depth."""
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return {}

        coordinates_by_depth = defaultdict(list)
        for node in subtree:
            depth = node.fetch_value("x")
            coordinates_by_depth[depth].append(node)
        return coordinates_by_depth

    def visualize_tree(self, level=0, prefix="--> ") -> str:
        """
        Enhanced tree visualization using ASCII characters.
        """
        tree_str = "|   " * (level - 1) + prefix + str(self) + "\n"
        for child in self.children:
            tree_str += child.visualize_tree(level + 1)
        return tree_str

    @staticmethod
    def depth_first_search(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> Optional["CoordinateTree"]:
        if predicate(tree):
            return tree
        else:
            for child in tree.children:
                result = CoordinateTree.depth_first_search(child, predicate)
                if result is not None:
                    return result
            return None

    @staticmethod
    def breadth_first_search(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> Optional["CoordinateTree"]:
        queue = [tree]
        while queue:
            node = queue.pop(0)
            if predicate(node):
                return node
            else:
                queue.extend(node.children)
        return None

    @staticmethod
    def depth_first_search_all(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> List["CoordinateTree"]:
        results = []
        if predicate(tree):
            results.append(tree)
        for child in tree.children:
            results.extend(CoordinateTree.depth_first_search_all(child, predicate))
        return results
