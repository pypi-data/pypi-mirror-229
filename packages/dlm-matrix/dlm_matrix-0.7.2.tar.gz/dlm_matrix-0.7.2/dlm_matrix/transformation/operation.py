from typing import List, Dict, Union, Callable
from dlm_matrix.transformation.base import BaseOperations
import numpy as np
from datetime import datetime
from collections import deque


class Operations(BaseOperations):
    def get_traversed_path(self):
        """Get the path traversed using historical data."""
        return list(self.history)

    def to_human_readable(self) -> str:
        """Convert the coordinate to a human-readable string."""
        return f"Depth: {self.x}, Sibling Position: {self.y}, Child Position: {self.z}, Timestamp: {self.t}"

    def compare_depth(self, other: "Operations") -> int:
        """
        Compare the depth of this coordinate with another.

        Args:
            other (Operations): Another coordinate object.

        Returns:
            int: Positive if this coordinate is deeper, negative if shallower, and zero if same depth.
        """
        if other is None:
            raise ValueError("The 'other' parameter cannot be None")
        return self.x - other.x

    def compare_time(self, other: "Operations") -> float:
        """
        Compare the time of this coordinate with another.

        Args:
            other (Operations): Another coordinate object.

        Returns:
            float: Positive if this coordinate is after, negative if before, and zero if at the same time.
        """
        if other is None:
            raise ValueError("The 'other' parameter cannot be None")
        return self.t - other.t

    # Comparison Methods
    def is_deeper_than(self, other: "Operations") -> bool:
        """Check if this coordinate is deeper than another."""
        return self.compare_depth(other) > 0

    def is_shallower_than(self, other: "Operations") -> bool:
        """Check if this coordinate is shallower than another."""
        return self.compare_depth(other) < 0

    def is_same_depth_as(self, other: "Operations") -> bool:
        """Check if this coordinate is at the same depth as another."""
        return self.compare_depth(other) == 0

    def is_before(self, other: "Operations") -> bool:
        """Check if this coordinate was created before another."""
        return self.compare_time(other) < 0

    def is_after(self, other: "Operations") -> bool:
        """Check if this coordinate was created after another."""
        return self.compare_time(other) > 0

    def is_next_sibling_of(self, other: "Operations") -> bool:
        """Check if this coordinate is the immediate next sibling of another."""
        return self.is_same_depth_as(other) and (self.y == other.y + 1)

    def is_previous_sibling_of(self, other: "Operations") -> bool:
        """Check if this coordinate is the immediate previous sibling of another."""
        return self.is_same_depth_as(other) and (self.y == other.y - 1)

    @staticmethod
    def is_conversation_progressing(
        coord_old: "Operations", coord_new: "Operations"
    ) -> bool:
        """Determine if the conversation is progressing based on comparing two coordinates in time."""
        return coord_new.is_after(coord_old)

    @staticmethod
    def get_relative_depth(coord1: "Operations", coord2: "Operations") -> int:
        """Get the relative depth difference between two conversation nodes."""
        return coord1.compare_depth(coord2)

    @staticmethod
    def is_sibling(coord1: "Operations", coord2: "Operations") -> bool:
        """Determine if two coordinates are siblings."""
        return coord1.is_same_depth_as(coord2) and abs(coord1.y - coord2.y) == 1

    @staticmethod
    def is_parent_child_relation(parent: "Operations", child: "Operations") -> bool:
        """Determine if there is a parent-child relationship between two nodes."""
        return parent.is_previous_sibling_of(child) and parent.y == child.y

    @staticmethod
    def conversation_temporal_gap(coord1: "Operations", coord2: "Operations") -> float:
        """Calculate the temporal gap between two messages in a conversation."""
        return abs(coord1.compare_time(coord2))

    def _difference(self, other: "Operations", exclude_t: bool = False) -> np.ndarray:
        """
        Compute the difference between two coordinates as a numpy array.

        Args:
            other (Operations): Another coordinate object.
            exclude_t (bool, optional): If True, the 't' value will not be included. Defaults to False.

        Returns:
            np.ndarray: The difference array.
        """
        if other is None:
            raise ValueError("The 'other' parameter cannot be None")

        return self.to_reduced_array(exclude_t) - other.to_reduced_array(exclude_t)

    def euclidean_distance(self, other: "Operations", exclude_t: bool = False) -> float:
        """Computes the Euclidean distance between two coordinates."""
        diff = self._difference(other, exclude_t)
        return np.linalg.norm(diff)

    @staticmethod
    def calculate_distance(
        coord1: "Operations", coord2: "Operations", exclude_t: bool = False
    ) -> float:
        """Calculate the Euclidean distance between two coordinates."""
        return coord1.euclidean_distance(coord2, exclude_t)

    @staticmethod
    def calculate_distance_matrix(
        coordinates: List["Operations"], exclude_t: bool = False
    ) -> np.ndarray:
        """Calculate a distance matrix for a list of coordinates."""
        coords_array = np.array(
            [coord.to_reduced_array(exclude_t) for coord in coordinates]
        )

        # Vectorized Euclidean distance calculation
        distances = np.sqrt(
            np.sum(
                (coords_array[:, np.newaxis, :] - coords_array[np.newaxis, :, :]) ** 2,
                axis=-1,
            )
        )
        return distances

    def assess_conversation_density(
        self,
        coordinates: List["Operations"],
        metrics: List[str] = ["mean", "std_dev"],
        weight_decay: float = None,
    ) -> Dict[str, Union[float, np.ndarray]]:
        result = {}

        if not coordinates or len(coordinates) == 1:
            for metric in metrics:
                result[metric] = 0 if metric != "distance_matrix" else np.array([])
            return result

        distance_matrix = Operations.calculate_distance_matrix(coordinates)
        np.fill_diagonal(distance_matrix, 0)
        distances = distance_matrix[np.tril_indices_from(distance_matrix, k=-1)]

        # Apply optional weighting if weight_decay is provided
        if weight_decay is not None:
            weights = np.power(weight_decay, np.arange(len(distances)))
            distances = distances * weights

        # Calculate and return specified metrics
        if "mean" in metrics:
            result["mean"] = np.mean(distances)
        if "std_dev" in metrics:
            result["std_dev"] = np.std(distances)
        if "distance_matrix" in metrics:
            result["distance_matrix"] = distance_matrix

        return result
