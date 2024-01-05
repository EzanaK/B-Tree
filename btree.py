from __future__ import annotations
import json
from typing import List
import math

# Node Class.
# You may make minor modifications.
class Node():
    def  __init__(self,
                  keys     : List[int]  = None,
                  values   : List[str] = None,
                  children : List[Node] = None,
                  parent   : Node = None):
        self.keys     = keys
        self.values   = values
        self.children = children
        self.parent   = parent

# DO NOT MODIFY THIS CLASS DEFINITION.
class Btree():
    def  __init__(self,
                  m    : int  = None,
                  root : Node = None):
        self.m    = m
        self.root = root

    # DO NOT MODIFY THIS CLASS METHOD.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            return {
                "keys": node.keys,
                "values": node.values,
                "children": [(_to_dict(child) if child is not None else None) for child in node.children]
            }
        if self.root == None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert.
    def insert(self, key: int, value: str):
        if self.root == None:
            node = Node(keys=[key], values=[value], children=[None, None], parent=None)
            self.root = node
        else:
            cur = self.root

            # get to leaf node
            while cur.children[0] is not None:
                cur = cur.children[get_index_in_children_list(cur.keys, key)]
            
            # add key and value to node
            cur.keys.append(key)
            cur.keys.sort()
            cur.values.insert(cur.keys.index(key), value)
            cur.children.append(None)

            # check for number of keys
            while len(cur.keys) == self.m:
                # Overfull node!

                # 1. First see if a left sibling exists and has space. If so then let T be the total number of keys in the overfull
                # node plus the left sibling and left rotate until the overfull node is down to ceil(T/2) keys.
                left_sib: Node = left_sibling(cur)
                if left_sib and (len(left_sib.keys) < self.m - 1):
                    # left sibling exists and has enough space
                    t = self.m + len(left_sib.keys)
                    while len(cur.keys) > math.ceil(t/2):
                        left_rotate(cur, left_sib)
                    return

                # 2. Second see if a right sibling exists and has space. If so then let T be the total number of keys in the overfull
                # node plus the right sibling and right rotate until the overfull node is down to ceil(T/2) keys.
                right_sib: Node = right_sibling(cur)
                if right_sib and (len(right_sib.keys) < self.m - 1):
                    # right sibling exists and has enough space
                    t = self.m + len(right_sib.keys)
                    while len(cur.keys) > math.ceil(t/2):
                        right_rotate(cur, right_sib)
                    return

                # 3. Split
                cur = split(self, cur)

            return

    # Delete.
    def delete(self, key: int):
        # Use in-order successor
        cur = self.root
        while cur:
            if key in cur.keys:
                break
            cur = cur.children[get_index_in_children_list(cur.keys, key)]
        delete_node = cur
        index_to_delete = delete_node.keys.index(key)
        cur = delete_node.children[index_to_delete + 1]
        if cur is None:
            delete_node.keys.remove(key)
            delete_node.values.pop(index_to_delete)
            delete_node.children.pop(index_to_delete)
        else:
            while cur.children[0]:
                cur = cur.children[0]
            delete_node.keys[index_to_delete] = cur.keys.pop(0)
            delete_node.values[index_to_delete] = cur.values.pop(0)
            cur.children.pop(0)
            delete_node = cur
        
        # check if delete_node is underfull
        while delete_node != self.root and len(delete_node.keys) < math.ceil(self.m/2) - 1:
            # 1. First see if a left sibling exists and has space. If so then let T be the total number of keys in
            # the underfull node plus the left sibling and right rotate until the underfull node is up to floor(T/2) keys.
            left_sib: Node = left_sibling(delete_node)
            if left_sib and (len(left_sib.keys) > math.ceil(self.m/2) - 1):
                # left sibling exists and has enough space
                t = len(delete_node.keys) + len(left_sib.keys)
                while len(delete_node.keys) != math.floor(t/2):
                    right_rotate(left_sib, delete_node)
                return

            # 2. Second see if a right sibling exists and has space. If so then let T be the total number of keys 
            # in the underfull node plus the right sibling and left rotate until the underfull node is up to floor(T/2) keys.
            right_sib: Node = right_sibling(delete_node)
            if right_sib and (len(right_sib.keys) > math.ceil(self.m/2) - 1):
                # right sibling exists and has enough space
                t = len(delete_node.keys) + len(right_sib.keys)
                while len(delete_node.keys) != math.floor(t/2):
                    left_rotate(right_sib, delete_node)
                return

            # 3. Merge with left sibling if possible.
            if left_sib:
                delete_node = merge(self, left_sib, delete_node)
            elif right_sib:
            # 4. Merge with right sibling if possible.
                delete_node = merge(self, delete_node, right_sib)

        return

    # Search
    def search(self,key) -> str:
        cur = self.root
        lst = []
        while cur:
            if key in cur.keys:
                return json.dumps(lst + [cur.values[cur.keys.index(key)]])
            child_index = get_index_in_children_list(cur.keys, key)
            lst.append(child_index)
            cur = cur.children[get_index_in_children_list(cur.keys, key)]
        return json.dumps(lst)

# Merge
def merge(btree :Btree, left: Node, right: Node) -> Node:
    parent = left.parent
    parent_key_index = parent.children.index(left)
    parent_key = parent.keys.pop(parent_key_index)
    parent_val = parent.values.pop(parent_key_index)

    merged_node = Node(keys=left.keys+[parent_key]+right.keys,
                       values=left.values+[parent_val]+right.values,
                       children=left.children+right.children,
                       parent=parent)

    for child in merged_node.children:
        if child:
            child.parent = merged_node

    parent.children[parent_key_index] = merged_node
    parent.children.pop(parent_key_index + 1)

    if parent == btree.root and len(parent.keys) == 0:
        btree.root = merged_node
        merged_node.parent = None
        return btree.root

    return parent


# Split
def split(btree: Btree, node: Node) -> Node:
    num_of_keys = len(node.keys)
    median_key_index = math.ceil(num_of_keys / 2) - 1

    # create left node
    left_node = Node(keys=node.keys[:median_key_index],
                     values=node.values[:median_key_index],
                     children=node.children[:median_key_index + 1], 
                     parent=node.parent)
    
    for child in left_node.children:
        if child:
            child.parent = left_node

    # create right node
    right_node = Node(keys=node.keys[median_key_index+1:],
                      values=node.values[median_key_index+1:],
                      children=node.children[median_key_index+1:],
                      parent=node.parent)

    for child in right_node.children:
        if child:
            child.parent = right_node

    parent = node.parent
    key = node.keys[median_key_index]
    value = node.values[median_key_index]
    if parent:
        parent_key_index = parent.children.index(node)
        parent.keys.insert(parent_key_index, key)
        parent.keys.sort()
        parent.values.insert(parent.keys.index(key), value)
        left_child_index = parent.children.index(node)
        right_child_index = left_child_index + 1
        parent.children[left_child_index] = left_node
        parent.children.insert(right_child_index, right_node)
    else:
        parent = Node(keys=[key],
                      values=[value],
                      children=[left_node, right_node],
                      parent=None)
        left_node.parent = parent
        right_node.parent = parent
        btree.root = parent

    return parent

# Left rotate
def left_rotate(node: Node, left_sib: Node):
    node_key = node.keys.pop(0)
    node_value = node.values.pop(0)
    node_left_child = node.children.pop(0)

    parent = node.parent
    parent_key_index = parent.children.index(node) - 1
    parent_key = parent.keys[parent_key_index]
    parent.keys[parent_key_index] = node_key
    parent_value = parent.values[parent_key_index]
    parent.values[parent_key_index] = node_value

    left_sib.keys.append(parent_key)
    left_sib.values.append(parent_value)
    left_sib.children.append(node_left_child)
    if node_left_child:
        node_left_child.parent = left_sib

# Right rotate
def right_rotate(node: Node, right_sib: Node):
    node_key = node.keys.pop()
    node_value = node.values.pop()
    node_right_child = node.children.pop()

    parent = node.parent
    parent_key_index = parent.children.index(node)
    parent_key = parent.keys[parent_key_index]
    parent.keys[parent_key_index] = node_key
    parent_value = parent.values[parent_key_index]
    parent.values[parent_key_index] = node_value

    right_sib.keys.insert(0, parent_key)
    right_sib.values.insert(0, parent_value)
    right_sib.children.insert(0, node_right_child)
    if node_right_child:
        node_right_child.parent = right_sib

# Returns left sibling if it exists
def left_sibling(node: Node) -> Node:
    parent = node.parent
    if parent:
        index_of_node = parent.children.index(node)
        if index_of_node != 0:
            return parent.children[index_of_node - 1]
    return None

# Returns right sibling if it exists
def right_sibling(node: Node) -> Node:
    parent = node.parent
    if parent:
        index_of_node = parent.children.index(node)
        if index_of_node < len(parent.children) - 1:
            return parent.children[index_of_node + 1]
    return None

# Return the index that x would be located in if added to the list
def get_index_in_children_list(keys: List[int], key: int) -> int:
    if key < keys[0]:
        return 0
    for i in range(1,len(keys)):
        if key < keys[i]:
            return i
    return len(keys)