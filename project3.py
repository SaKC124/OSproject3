#!/usr/bin/env python3
import sys
import os
import csv

BLOCK_SIZE = 512
MAGIC = b"4348PRJ3"
T = 10                       # minimal degree
MAX_KEYS = 2*T - 1           # 19
MAX_CHILDREN = 2*T           # 20

# -----------------------------
# Helper functions
# -----------------------------

def u64(num):
    """Convert int → big endian 8 bytes."""
    return num.to_bytes(8, "big", signed=False)

def read_u64(data, pos):
    """Read big endian 8-byte number from bytes."""
    return int.from_bytes(data[pos:pos+8], "big", signed=False), pos + 8


# -----------------------------
# Node structure in memory
# -----------------------------
class Node:
    def __init__(self, block_id):
        self.block_id = block_id
        self.parent = 0
        self.num_keys = 0
        self.keys = [0]*MAX_KEYS
        self.values = [0]*MAX_KEYS
        self.children = [0]*MAX_CHILDREN


# -----------------------------
# B-Tree Index File Manager
# -----------------------------
class BTree:
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, "r+b")
        self.root_id, self.next_id = self.read_header()

    # -----------------------------
    # Header
    # -----------------------------
    def read_header(self):
        self.f.seek(0)
        block = self.f.read(BLOCK_SIZE)
        if block[:8] != MAGIC:
            raise RuntimeError("Not a valid index file.")

        pos = 8
        root, pos = read_u64(block, pos)
        next_id, pos = read_u64(block, pos)
        return root, next_id

    def write_header(self):
        buf = bytearray(BLOCK_SIZE)
        pos = 0
        buf[pos:pos+8] = MAGIC; pos += 8
        buf[pos:pos+8] = u64(self.root_id); pos += 8
        buf[pos:pos+8] = u64(self.next_id); pos += 8

        self.f.seek(0)
        self.f.write(buf)

    # -----------------------------
    # Node read/write
    # -----------------------------
    def read_node(self, block_id):
        if block_id == 0:
            return None
        self.f.seek(block_id * BLOCK_SIZE)
        data = self.f.read(BLOCK_SIZE)

        node = Node(block_id)
        pos = 0

        node.block_id, pos = read_u64(data, pos)
        node.parent, pos = read_u64(data, pos)
        node.num_keys, pos = read_u64(data, pos)

        # read keys
        for i in range(MAX_KEYS):
            node.keys[i], pos = read_u64(data, pos)

        # read values
        for i in range(MAX_KEYS):
            node.values[i], pos = read_u64(data, pos)

        # read children
        for i in range(MAX_CHILDREN):
            node.children[i], pos = read_u64(data, pos)

        return node

    def write_node(self, node):
        buf = bytearray(BLOCK_SIZE)
        pos = 0

        def put(num):
            nonlocal pos
            buf[pos:pos+8] = u64(num)
            pos += 8

        put(node.block_id)
        put(node.parent)
        put(node.num_keys)

        for k in node.keys: put(k)
        for v in node.values: put(v)
        for c in node.children: put(c)

        self.f.seek(node.block_id * BLOCK_SIZE)
        self.f.write(buf)

    # -----------------------------
    # B-TREE INSERT IMPLEMENTATION
    # -----------------------------
    def is_leaf(self, node):
        return all(c == 0 for c in node.children)

    def split_child(self, parent, index, full_child):
        """Split a full child node into 2 nodes."""
        t = T

        # Create new right node
        new_id = self.next_id
        self.next_id += 1
        right = Node(new_id)
        right.parent = parent.block_id

        # Move t-1 keys to right node
        right.num_keys = t - 1
        for j in range(t-1):
            right.keys[j] = full_child.keys[j+t]
            right.values[j] = full_child.values[j+t]

        # Move t children if not leaf
        if not self.is_leaf(full_child):
            for j in range(t):
                right.children[j] = full_child.children[j+t]

        # Reduce left child
        full_child.num_keys = t - 1

        # Shift parent's children
        for j in range(parent.num_keys, index, -1):
            parent.children[j+1] = parent.children[j]
        parent.children[index+1] = right.block_id

        # Shift parent's keys
        for j in range(parent.num_keys - 1, index - 1, -1):
            parent.keys[j+1] = parent.keys[j]
            parent.values[j+1] = parent.values[j]

        # Move middle key into parent
        parent.keys[index] = full_child.keys[t-1]
        parent.values[index] = full_child.values[t-1]

        parent.num_keys += 1

        # Clear moved keys from full_child
        full_child.keys[t-1] = 0
        full_child.values[t-1] = 0

        # Write nodes
        self.write_node(full_child)
        self.write_node(right)
        self.write_node(parent)
        self.write_header()

    def insert(self, key, value):
        if self.root_id == 0:
            # Create root
            rid = self.next_id
            self.next_id += 1
            root = Node(rid)
            root.num_keys = 1
            root.keys[0] = key
            root.values[0] = value
            self.root_id = rid
            self.write_node(root)
            self.write_header()
            return

        root = self.read_node(self.root_id)

        # If root is full, split it
        if root.num_keys == MAX_KEYS:
            new_root_id = self.next_id
            self.next_id += 1
            new_root = Node(new_root_id)
            new_root.children[0] = root.block_id
            root.parent = new_root_id

            self.root_id = new_root_id
            self.write_node(root)
            self.write_node(new_root)
            self.write_header()

            self.split_child(new_root, 0, root)
            root = new_root

        # Insert in non-full node
        self.insert_nonfull(root, key, value)

    def insert_nonfull(self, node, key, value):
        i = node.num_keys - 1

        if self.is_leaf(node):
            # Shift keys to make room
            while i >= 0 and key < node.keys[i]:
                node.keys[i+1] = node.keys[i]
                node.values[i+1] = node.values[i]
                i -= 1

            node.keys[i+1] = key
            node.values[i+1] = value
            node.num_keys += 1
            self.write_node(node)
            return
        else:
            # Find child to descend
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            child = self.read_node(node.children[i])

            if child.num_keys == MAX_KEYS:
                self.split_child(node, i, child)
                # After split, decide which child to descend into
                if key > node.keys[i]:
                    i += 1
                child = self.read_node(node.children[i])

            self.insert_nonfull(child, key, value)

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search(self, key):
        node_id = self.root_id

        while node_id != 0:
            node = self.read_node(node_id)
            i = 0
            while i < node.num_keys and key > node.keys[i]:
                i += 1

            if i < node.num_keys and key == node.keys[i]:
                return (node.keys[i], node.values[i])

            if self.is_leaf(node):
                return None

            node_id = node.children[i]

        return None

    # -----------------------------
    # PRINT/EXTRACT – load all nodes
    # -----------------------------
    def all_pairs(self):
        arr = []
        for bid in range(1, self.next_id):
            node = self.read_node(bid)
            for i in range(node.num_keys):
                arr.append((node.keys[i], node.values[i]))
        return sorted(arr)

    def close(self):
        self.f.close()


# -----------------------------
# COMMAND HANDLERS
# -----------------------------
def create_index(name):
    if os.path.exists(name):
        print("error: file exists")
        return
    f = open(name, "wb")
    buf = bytearray(BLOCK_SIZE)
    buf[0:8] = MAGIC
    # root=0, next block=1
    buf[8:16] = u64(0)
    buf[16:24] = u64(1)
    f.write(buf)
    f.close()


def main():
    if len(sys.argv) < 2:
        print("usage: project3 <command> ...")
        return

    cmd = sys.argv[1]

    try:
        if cmd == "create":
            create_index(sys.argv[2])

        elif cmd == "insert":
            idx = BTree(sys.argv[2])
            k = int(sys.argv[3])
            v = int(sys.argv[4])
            idx.insert(k, v)
            idx.close()

        elif cmd == "search":
            idx = BTree(sys.argv[2])
            k = int(sys.argv[3])
            res = idx.search(k)
            if res is None:
                print("key not found")
            else:
                print(f"{res[0]},{res[1]}")
            idx.close()

        elif cmd == "load":
            idx = BTree(sys.argv[2])
            with open(sys.argv[3]) as f:
                reader = csv.reader(f)
                for row in reader:
                    k = int(row[0])
                    v = int(row[1])
                    idx.insert(k, v)
            idx.close()

        elif cmd == "print":
            idx = BTree(sys.argv[2])
            for k, v in idx.all_pairs():
                print(f"{k},{v}")
            idx.close()

        elif cmd == "extract":
            idx = BTree(sys.argv[2])
            outfile = sys.argv[3]
            if os.path.exists(outfile):
                print("error: file exists")
                return
            with open(outfile, "w") as f:
                for k, v in idx.all_pairs():
                    f.write(f"{k},{v}\n")
            idx.close()

        else:
            print("unknown command")

    except Exception as e:
        print("error:", e)


if __name__ == "__main__":

