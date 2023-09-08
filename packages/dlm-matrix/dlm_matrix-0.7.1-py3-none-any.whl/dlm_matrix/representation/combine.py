from typing import Dict, List, Optional, Tuple, Any
from dlm_matrix.representation.chain import ChainRepresentation
from dlm_matrix.services.filters import ChainFilter
from dlm_matrix.services.helper import compute_and_combine
from dlm_matrix.embedding.spatial import SpatialSimilarity
from dlm_matrix.builder import ChainTreeBuilder
from dlm_matrix.context import MultiLevelContext, DataFrameStore, JsonStore, NumpyStore
from dlm_matrix.models import DocumentEmbeddings
from dlm_matrix.context import get_file_paths, DEFAULT_PERSIST_DIR
import pandas as pd
import numpy as np


class ChainCombiner(ChainTreeBuilder):
    def __init__(
        self,
        use_embeddings: bool = False,
        target_number: int = 10,
        combine: bool = False,
        path: Optional[str] = None,
        api_key: Optional[str] = None,
        output_name: Optional[str] = None,
        chain_filter: Optional[ChainFilter] = None,
        spatial_similarity: Optional[SpatialSimilarity] = None,
        base_persist_dir: Optional[str] = DEFAULT_PERSIST_DIR,
        db_path: Optional[str] = None,
        table: Optional[str] = None,
        
    ):
        super().__init__(
            path=path,
            base_persist_dir=base_persist_dir,
            db_path=db_path,
            table=table,
            target_num=target_number,
            combine=combine,
        )
        self.chain_filter = chain_filter if chain_filter else ChainFilter()
        self.base_persist_dir = base_persist_dir
        self.output_name = output_name
        self.api_key = api_key
        self.use_embeddings = use_embeddings

        if api_key:
            self.spatial_similarity = SpatialSimilarity(api_key=api_key)
        else:
            self.spatial_similarity = spatial_similarity if spatial_similarity else SpatialSimilarity()

    def _validate_use_graph_index(self, use_graph_index):
        if use_graph_index is not None and not isinstance(use_graph_index, int):
            raise ValueError("use_graph_index should be an integer or None.")

    def _process_tree_range(self, tree_range):
        start, end = tree_range
        if end is None:
            end = len(self.conversations)
        return start, end

    def _filter_conversation_trees(self, start, end, skip_indexes):
        if skip_indexes is not None:
            filtered_trees = [
                ct
                for i, ct in enumerate(self.conversations[start:end])
                if i not in skip_indexes
            ]
        else:
            filtered_trees = self.conversations[start:end]
        return filtered_trees

    def process_and_filter_trees(
        self, tree_range: Tuple[int, int], use_graph_index: int, skip_indexes: List[int]
    ):
        self._validate_use_graph_index(use_graph_index)
        start, end = self._process_tree_range(tree_range)
        filtered_trees = self._filter_conversation_trees(start, end, skip_indexes)

        return filtered_trees, start

    def process_trees(
        self,
        use_graph: bool = False,
        use_graph_index: Optional[int] = None,
        tree_range: Optional[Tuple[int, int]] = (0, None),
        skip_indexes: Optional[List[int]] = None,
        pre_computed_embeddings: bool = True,
        animate: bool = False,
    ) -> pd.DataFrame:
        """
        Main method to process trees and return a DataFrame.

        Args:
            use_graph: Whether to use a graph representation.
            use_graph_index: Index of the graph to use, if any.
            tree_range: Tuple specifying the range of trees to process.
            skip_indexes: List of tree indexes to skip.
            animate: Whether to animate the process.

        Returns:
            A DataFrame containing the processed information.
        """

        # Automatically set pre_computed_embeddings based on use_openai

        filtered_trees, start = self.process_and_filter_trees(
            tree_range, use_graph_index, skip_indexes
        )
        main_dfs = []

        for start_count, conversation_tree in enumerate(filtered_trees, start=start):
            tetra = self.initialize_conversation_tree(conversation_tree)
            (
                tree_docs,
                relationship_df,
                embeddings,
            ) = self.process_coordinates_and_features(
                tetra, use_graph, animate, pre_computed_embeddings
            )

            if tree_docs is not None:
                self.update_mapping_with_features(tetra, tree_docs)
                main_df = pd.DataFrame.from_records(tree_docs)

            main_df = self.create_and_save_dataframes(
                tetra, main_df, relationship_df, embeddings
            )
            main_dfs.append(main_df)

        mean_n_neighbors, combined_df = compute_and_combine(main_dfs)

        df = self.format_as_dataframe(
            data=combined_df,
            neighbors=mean_n_neighbors,
            embedding_model=self.spatial_similarity,
            path=self.output_name,
            use_embeddings=self.use_embeddings,
        )

        print(f"Mean n_neighbors: {mean_n_neighbors}")
        return df

    def initialize_conversation_tree(
        self,
        conversation_tree: Dict[str, Any],
    ) -> ChainRepresentation:
        """
        Initialize a conversation tree and print its title.

        Args:
            conversation_tree: The conversation tree to initialize.

        Returns:
            Initialized ChainRepresentation object.
        """
        tetra = ChainRepresentation(
            conversation_tree=conversation_tree,
            spatial_similarity=self.spatial_similarity,
        )
        title = tetra.conversation.conversation.title
        print(f"Processing conversation {title}.")
        return tetra

    def process_coordinates_and_features(
        self,
        tetra: ChainRepresentation,
        use_graph: bool,
        animate: bool,
        pre_computed_embeddings=False,
    ) -> Tuple[List, pd.DataFrame]:
        """
        Process the coordinates and features of the conversation tree.

        Args:
            tetra: The initialized ChainRepresentation object.
            use_graph: Whether to use a graph representation.
            animate: Whether to animate the process.

        Returns:
            A tuple containing the processed tree documents and the relationship DataFrame.
        """
        tree_docs, embeddings , coordinate_tree = tetra._procces_coordnates(
            use_graph=use_graph, animate=animate
        )
        relationship_df = tetra.create_prompt_response_df(
            pre_computed_embeddings,
        )
        return tree_docs, relationship_df, embeddings

    def update_mapping_with_features(
        self, tetra: ChainRepresentation, tree_docs: List[dict]
    ) -> None:
        """
        Update the mapping of the conversation tree with new features.

        Args:
            tetra: The initialized ChainRepresentation object.
            tree_docs: The processed tree documents containing new features.

        Returns:
            None
        """
        # Inside update_mapping_with_features
        for doc in tree_docs:
            message = tetra.conversation.conversation.mapping.get(doc["id"])
            if message is not None:
                attributes_to_update = [
                    "umap_embeddings",
                    "cluster_label",
                    "n_neighbors",
                ]
                for embedding in message.message.embedding:  # Assuming this is a list
                    if isinstance(embedding, DocumentEmbeddings):  # Type check
                        for attribute in attributes_to_update:
                            setattr(embedding, attribute, doc[attribute])

    def create_and_save_dataframes(
        self,
        tetra: ChainRepresentation,
        tree_docs: List,
        relationship_df: pd.DataFrame,
        embeddings: List[np.array] = None,
    ) -> pd.DataFrame:
        """
        Create and save DataFrames for the conversation tree.

        Args:
            tetra: The initialized ChainRepresentation object.
            tree_docs: The processed tree documents.
            relationship_df: The DataFrame containing relationships among messages.

        Returns:
            The main DataFrame.
        """
        mapping_dict = tetra.conversation.conversation.dict()
        (
            persist_dir,

        ) = get_file_paths(self.base_persist_dir, tetra.conversation.conversation.title)

        main_df = self.create_and_persist_dataframes(
            persist_dir,
            mapping_dict,
            tree_docs,
            relationship_df,
            embeddings,
        )
        return main_df

    def create_and_persist_dataframes(
        self,
        persist_dir: str,
        conversation_tree: dict,
        tree_docs: List[dict],
        relationship_df: pd.DataFrame = pd.DataFrame,
        embeddings: List[np.array] = None,
    ):
        try:
            # Create the main_df DataFrame

            # Initialize storage context with main_df
            storage_context = self.initialize_storage_context(
                tree_docs, conversation_tree, relationship_df, embeddings
            )
            # Persist the storage context
            storage_context.persist(
                persist_dir=persist_dir,
            )
            return storage_context.main_df_store.df

        except Exception as e:
            # Handle any exceptions that might occur and return None
            print("An error occurred while creating and persisting dataframes:", str(e))
            return None

    def initialize_storage_context(
        self,
        main_df: pd.DataFrame,
        conversation_tree: dict,
        relationship_df=pd.DataFrame,
        embeddings: List[np.array] = None,
    ):
        return MultiLevelContext.from_defaults(
            main_df_store=DataFrameStore(main_df),
            conversation_tree_store=JsonStore(conversation_tree),
            relationship_store=DataFrameStore(relationship_df),
            global_embedding_store=NumpyStore(embeddings),
        )
