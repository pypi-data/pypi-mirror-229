from typing import Dict, List, Tuple
from dlm_matrix.models import ChainTreeIndex, ChainTree, ChainMap, Chain
from tqdm import tqdm


class TreeMerger:
    def combine_conversations_in_batches(
        self, conversation_trees: List[ChainTreeIndex], batch_size: int = 1000
    ) -> List[ChainTreeIndex]:
        batched_trees = []
        for i in tqdm(
            range(0, len(conversation_trees), batch_size), desc="Processing batches"
        ):
            batch = conversation_trees[i : i + batch_size]
            combined_tree = self.combine_conversations(batch)
            batched_trees.append(combined_tree)
        return batched_trees

    def retrieve_mappings(
        self, conversation_trees: List[ChainTreeIndex]
    ) -> List[ChainMap]:
        print("Retrieving mappings from conversations...")
        mappings = []
        for tree in tqdm(conversation_trees):
            mappings.extend(list(tree.conversation.mapping.values()))
        return mappings

    def update_parent_child(self, mappings: List[ChainMap]) -> Dict[str, str]:
        print("Creating new IDs for mappings...")

        # If mappings is None or empty, return an empty dictionary
        if not mappings:
            return {}

        new_mapping_ids = {}
        parent_child_map = {}

        for mapping in tqdm(mappings):
            if mapping.message is not None:
                # Still retain the message ID mapping, as you did before
                new_mapping_ids[mapping.message.id] = mapping.message.id

                # Check for parent and establish a parent-child relationship
                parent_id = mapping.parent
                if parent_id:
                    # Store children IDs in a list against their parent
                    if parent_id not in parent_child_map:
                        parent_child_map[parent_id] = []
                    parent_child_map[parent_id].append(mapping.message.id)

        # Now, update the children information for each mapping based on the parent_child_map
        for mapping in mappings:
            if mapping.message and mapping.message.id in parent_child_map:
                mapping.children = parent_child_map[mapping.message.id]

        return new_mapping_ids

    def extract_and_sort_messages(
        self, mappings: List[ChainMap], new_mapping_ids: Dict[str, str]
    ) -> List[Chain]:
        print("Extracting and sorting messages...")
        sorted_messages = []

        for mapping in tqdm(mappings):
            if mapping.message is not None:
                mapping.message.id = new_mapping_ids[mapping.message.id]
                sorted_messages.append(mapping.message)

        # Sort the messages based on their creation time
        sorted_messages.sort(key=lambda m: (m.create_time is None, m.create_time))

        return sorted_messages

    def create_linked_list(
        self, sorted_messages: List[Chain]
    ) -> Tuple[Dict[str, str], List[Chain]]:
        print("Creating linked list...")
        id_mapping = {}
        for i, message in tqdm(enumerate(sorted_messages)):
            # For each message, determine its previous and next based on its position in the sorted list
            message.prev = sorted_messages[i - 1].id if i > 0 else None
            message.next = (
                sorted_messages[i + 1].id if i < len(sorted_messages) - 1 else None
            )
            id_mapping[message.id] = message.id
        return sorted_messages

    def update_mappings(
        self, sorted_messages: List[Chain], conversation_trees: List[ChainTreeIndex]
    ) -> List[ChainMap]:
        print("Updating mappings...")
        combined_mappings = []

        # Create a message_id to ChainMap dictionary for quick look-up
        existing_mappings = {
            mapping.message.id: mapping
            for tree in conversation_trees
            for mapping in tree.conversation.mapping.values()
            if mapping.message is not None
        }

        # Initialize previous message variable
        prev_message = None

        for message in tqdm(sorted_messages):
            if message.id in existing_mappings:
                mapping = existing_mappings[message.id]
                mapping.message = message
            else:
                mapping = ChainMap(id=message.id, message=message)

            # Check if message is by system
            if message.author.role == "system":
                # If message is by system, check if it is a prompt
                related_conversation = None
                for index, conv in enumerate(conversation_trees):
                    if conv.conversation.mapping.get(message.id):
                        related_conversation = conv
                        break

                if related_conversation:
                    # If message is a prompt, update the message content
                    message.content.text = f"Conversation {index + 1}: {related_conversation.conversation.title}"
                    message.content.parts = [message.content.text]
                    message.create_time = related_conversation.conversation.create_time

                if prev_message:
                    mapping.parent = prev_message.id
                    prev_mapping = existing_mappings.get(
                        prev_message.id,
                        ChainMap(id=prev_message.id, message=prev_message),
                    )
                    if prev_mapping.children:
                        prev_mapping.children.append(message.id)
                    else:
                        prev_mapping.children = [message.id]

            combined_mappings.append(mapping)
            prev_message = message

        return combined_mappings

    def combine_conversations(
        self, filtered_trees: List[ChainTreeIndex], title: str = "Combined Conversation"
    ) -> ChainTreeIndex:
        try:
            mappings = self.retrieve_mappings(filtered_trees)
            new_mapping_ids = self.update_parent_child(mappings)
            sorted_messages = self.extract_and_sort_messages(mappings, new_mapping_ids)
            sorted_messages = self.create_linked_list(sorted_messages)
            combined_mappings = self.update_mappings(sorted_messages, filtered_trees)
            print("Creating combined conversation...")
            # convert the combined mappings to a dictionary
            combined_mappings = {mapping.id: mapping for mapping in combined_mappings}
            # sort the combined mappings by create_time
            combined_mappings = dict(
                sorted(
                    combined_mappings.items(),
                    key=lambda item: item[1].message.create_time,
                )
            )

            combined_conversation = ChainTree(
                title=title,
                create_time=sorted_messages[0].create_time,
                update_time=sorted_messages[-1].create_time,
                mapping=combined_mappings,
                moderation_results=[],
                current_node="",
            )
            # convert the combined tree to a dictionary
            combined_tree = [ChainTreeIndex(conversation=combined_conversation)]
            return combined_tree

        except Exception as e:
            print(e)
            return None
