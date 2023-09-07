from collections import defaultdict
from typing import List

from deadcode.actions.merge_overlaping_file_parts import merge_overlaping_file_parts
from deadcode.actions.remove_file_parts_from_content import remove_file_parts_from_content
from deadcode.data_types import Part
from deadcode.visitor.code_item import CodeItem


def fix_unused_code(unused_items: List[CodeItem]) -> None:
    # Reading and writing should be patched in this file.

    # Group unused_names by filenames
    # For each filename find file parts, which have to be fixed.
    # And fix those file parts.
    #
    # TODO: trailing commas, trailing white spaces and empty lines

    filename_to_unused_items = defaultdict(list)
    for unused_item in unused_items:
        filename_to_unused_items[str(unused_item.filename)].append(unused_item)

    for filename, unused_items in filename_to_unused_items.items():
        file_parts = [
            Part(item.first_lineno, item.last_lineno, item.first_column, item.last_column or 0) for item in unused_items
        ]

        unused_file_parts = merge_overlaping_file_parts(file_parts)

        with open(filename) as f:
            file_content_lines = f.readlines()

        updated_file_content_lines = remove_file_parts_from_content(file_content_lines, unused_file_parts)

        with open(filename, "w") as f:
            # TODO: is there a method writelines?
            f.write("".join(updated_file_content_lines))

    # TODO: update this one: solution is to use read and write operations.
    #
    # Solution is to open file for reading and then for writing.
