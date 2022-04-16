import sys
import time
import re


def load_data(filename):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    transaction = []

    for i in range(0, len(content)):
        transaction.append(content[i].split(','))

    return transaction


def transfer_2_frozen_data_set(data_set):
    frozen_data_set = {}
    for elem in data_set:
        frozen_data_set[frozenset(elem)] = 1
    return frozen_data_set


class TreeNode:
    def __init__(self, node_name, count, node_parent):
        self.node_name = node_name
        self.count = count
        self.node_parent = node_parent
        self.next_similar_item = None
        self.children = {}

    def increase_c(self, count):
        self.count += count


def create_fp_tree(frozen_data_set, min_support):

    head_point_table = {}
    for items in frozen_data_set:
        for item in items:
            head_point_table[item] = head_point_table.get(item, 0) + frozen_data_set[items]
    head_point_table = {k: v for k, v in head_point_table.items()
                        if v >= min_support}
    frequent_items = set(head_point_table.keys())
    if len(frequent_items) == 0:
        return None, None

    for k in head_point_table:
        head_point_table[k] = [head_point_table[k], None]
    fp_tree = TreeNode("null", 1, None)

    for items, count in frozen_data_set.items():
        frequent_items_in_record = {}
        for item in items:
            if item in frequent_items:
                frequent_items_in_record[item] = head_point_table[item][0]
        if len(frequent_items_in_record) > 0:
            ordered_frequent_items = [v[0] for v in sorted(
                frequent_items_in_record.items(), key=lambda v:v[1], reverse=True)]
            update_fp_tree(fp_tree, ordered_frequent_items, head_point_table, count)

    return fp_tree, head_point_table


def update_fp_tree(fp_tree, ordered_frequent_items, head_point_table, count):
    if ordered_frequent_items[0] in fp_tree.children:
        fp_tree.children[ordered_frequent_items[0]].increase_c(count)
    else:
        fp_tree.children[ordered_frequent_items[0]] = TreeNode(ordered_frequent_items[0], count, fp_tree)

        if head_point_table[ordered_frequent_items[0]][1] is None:
            head_point_table[ordered_frequent_items[0]][1] = fp_tree.children[ordered_frequent_items[0]]
        else:
            update_head_point_table(head_point_table[ordered_frequent_items[0]][1],
                                    fp_tree.children[ordered_frequent_items[0]])
    if len(ordered_frequent_items) > 1:
        update_fp_tree(fp_tree.children[ordered_frequent_items[0]],
                       ordered_frequent_items[1::], head_point_table, count)


def update_head_point_table(head_point_begin_node, target_node):
    while head_point_begin_node.next_similar_item is not None:
        head_point_begin_node = head_point_begin_node.next_similar_item
    head_point_begin_node.next_similar_item = target_node


def ascend_tree(tree_node):
    prefixs = []

    while(tree_node.node_parent is not None) and (tree_node.node_parent.node_name != 'null'):
        tree_node = tree_node.node_parent
        prefixs.append(tree_node.node_name)
    return prefixs


def get_prefix_path(head_point_table, head_point_item):

    prefix_path = {}
    begin_node = head_point_table[head_point_item][1]
    prefixs = ascend_tree(begin_node)
    if prefixs is not []:
        prefix_path[frozenset(prefixs)] = begin_node.count

    while begin_node.next_similar_item is not None:
        begin_node = begin_node.next_similar_item
        prefixs = ascend_tree(begin_node)
        if prefixs is not []:
            prefix_path[frozenset(prefixs)] = begin_node.count
    return prefix_path


def mine_fp_tree(fp_tree, head_point_table, prefix, frequent_patterns, min_support):

    head_point_items = [v[0] for v in sorted(head_point_table.items(), key=lambda v:v[1][0])]
    if len(head_point_items) == 0:
        return

    for head_point_item in head_point_items:
        new_prefix = prefix.copy()
        new_prefix.add(head_point_item)
        support = head_point_table[head_point_item][0]
        frequent_patterns[frozenset(new_prefix)] = support

        prefix_path = get_prefix_path(head_point_table, head_point_item)
        if prefix_path != {}:
            conditional_fp_tree, conditional_head_point_table = create_fp_tree(
                prefix_path, min_support)
            if conditional_head_point_table is not None:
                mine_fp_tree(conditional_fp_tree, conditional_head_point_table, new_prefix,
                             frequent_patterns, min_support)


if __name__ == '__main__':

    filename = load_data(sys.argv[2])
    total_lines = sum(1 for line in filename)

    min_support = float(sys.argv[1])*total_lines

    frozen_data_set = transfer_2_frozen_data_set(filename)
    start = time.time()
    fp_tree, head_point_table = create_fp_tree(frozen_data_set, min_support)
    frequent_patterns = {}
    prefix = set([])
    mine_fp_tree(fp_tree, head_point_table, prefix, frequent_patterns, min_support)
    end = time.time()

    output_filename = open(sys.argv[3], "w")

    print("執行時間:")
    print(end-start)
    characters = "frozenset(){}''"
    for i in frequent_patterns:
        print(re.sub("[frozenst(){} ']", '', str(i))+":"+str(format(round(frequent_patterns[i]/total_lines, 4), '0<6')), file=output_filename)
    output_filename.close()

    if len(sys.argv) < 4:
        print('too few arguments')
        sys.exit()
    min_support = float(sys.argv[1])
    filename = str(sys.argv[2])
    output_filename = str(sys.argv[3])
