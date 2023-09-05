import os
import json

from typing import Union

from shulker.components.Block import Block
from shulker.components.BlockCoordinates import BlockCoordinates
from shulker.components.BlockState import BlockState
from shulker.components.BlockHandler import BlockHandler
from shulker.components.BlockZone import BlockZone
from shulker.functions.base_functions import *
from shulker.functions.default import meta_set_block, meta_set_zone

# TODO: Make clear zone works with scaling
# TODO: orientation
# TODO: vertical text (like japanese)
# TODO: Remove digit skip and encode them
# TODO: handle '\n'
# TODO: flatten scale for every number to usable (but translates to odd numbers)

path = os.path.dirname(os.path.abspath(__file__))
with open(f"{path}/mc_data/set_text_data.json", "r") as file:
    set_text_data = json.load(file)

letters_repr = set_text_data["letters"]
block_palette = set_text_data["block_palette"]

def meta_set_text(
    message: str,
    coords: BlockCoordinates,
    palette: list,
    style: str,
    orientation: str,
    replace: Union[bool, None],
    scale: int,
    filler: Union[Block, None],
    namespace: bool,
) -> dict:

    if replace is not None:
      handler = BlockHandler("replace" if replace else "keep")
    else:
      handler = None
    
    offset = 0
    instructions = {"cmds": [], "zone": None}

    # Can't use enumerate(message) because I don't want
    # to count spaces
    letter_index = 0

    # First we iterate over each letter of the string that
    # was passed
    for index, letter in enumerate(message):

        # If the letter is a space, we skip the loop
        # but add an offset of 2 to the next letter placement
        if letter == " " or letter == "\n":
            offset += 2 + scale
            continue

        try:
            # This condition makes the style "mixed"
            # set the first letter of a string as an uppercase
            if style == "mixed":

                if letter.isupper():
                    letter = letter.lower()
                    representation = letters_repr[letter]["uppercase"]
                else:
                    representation = letters_repr[letter]["lowercase"]

            # Otherwise, it fetches the "representation" (e.g.: 000-421-etc.)
            # of the current letter in the string.
            # The representations are at the bottom of this file.
            else:
                letter = letter.lower()
                representation = letters_repr[letter][style]
        except KeyError:
            offset += 2 + scale
            print("Couldn't find representation for " + letter)
            continue

        # Here we reverse the representation to read it
        # from the bottom left corner to the top right corner
        representation = representation.split("-")
        representation.reverse()

        # This handles when multiple palettes were provided as a list
        # using a modulo based on the length of the palette.
        if len(palette) > 1:
            mod = letter_index % len(palette)
        else:
            mod = 0

        # Then it starts looping through each digit in
        # the representation (e.g.: ["000"], ["414"], etc.)
        y = 0
        for line in representation:

            # After each line it resets the X position to the left
            x = 0 + offset

            for digit in line:

                # This variable stores the computed coordinates at
                # which the current block should be placed
                new_coords = BlockCoordinates(coords.x + x, coords.y + y, coords.z)

                # After which we move the cursor
                x += 1 + scale

                # And finally, this is the part where the block is set
                # depending on whether a scale was specified or not
                if scale == 0:
                      
                    block = fetch_block(digit, orientation, palette[mod], filler)

                    if block:
                      cmd = meta_set_block(new_coords, block, handler)
                      
                      if not namespace:
                        cmd = cmd.replace("minecraft:", "")
                        
                      instructions["cmds"].append(cmd)

                # In case it was, it creates "zones" instead
                # of placing blocks
                else:
                    zones = construct_zones(new_coords, digit, scale)

                    for zone in zones:

                        # A letter scaled up can be represented by multiple zones
                        # with the slabs for instance, it's half filler(/air),
                        # half solid, so we have to adjust which block
                        # is used per sub zone
                        if zone["filler"] == "air":
                            block = filler
                        elif zone["filler"] == "block":
                            temp_digit = "0" if digit == "0" else "1"
                            block = fetch_block(
                                temp_digit, orientation, palette[mod], filler
                            )

                        cmd = meta_set_zone(zone["coords"], block, handler)
                        instructions["cmds"].append(cmd)

            # After a line has been printed, the Y level is increased
            y += 1 + scale

        # This increases the offset after a letter has been printed
        # by computing the length of any 'line' representing
        # the current letter, and adding one block space
        offset += len(representation[0]) * (scale + 1) + 1 * (scale + 1)
        letter_index += 1

    # Y is being re-declared to be used in the return value
    # of the function
    else:
        try:
            y = representation.count("-")
        except UnboundLocalError:
            y = 0
            new_coords = BlockCoordinates(coords.x, coords.y, coords.z)

    new_coords.y += y
    instructions["zone"] = BlockZone(coords, new_coords)

    # The functions returns the "instructions" dictionary
    # containing all the commands to .post() as well
    # as the zone representing the text that was created
    # for later clean-up
    return instructions


def set_text(
    message: str,
    coords: Union[BlockCoordinates, tuple],
    palette: Union[list, str] = "blackstone",
    style: str = "mixed",
    orientation: str = "east",
    replace: bool = True,
    scale: int = 0,
    filler: Union[Block, str] = "air",
    namespace: bool = True,
) -> dict:

    """
    Returns a BlockZone representing the area used by the text
    to be represented

    The given coords should represent the block that is
    lower northwest corner of the structure

    Available styles:
    - smallcaps
    - lowercase
    - uppercase
    - mixed (alternate between lowercase/uppercase by respecting case)

    The availables palettes are listed at the bottom of this file.

    Orientation can be either east(/west) or north(/south)

    Replace is a boolean which defines whether the 'empty' part of
    the text should be replaced by air blocks or left as is

    Scale is the amount of block to "add" to the size of a default block (1)
    e.g: if scale is set to 1, a block will be represented by a 2x2 zone

    Filler represents the block to use in the empty area of the letter
    representation if Replace is set to True
    """

    check_output_channel()

    coords = format_arg(coords, BlockCoordinates)
    filler = format_arg(filler, Block)

    if type(palette) is not list:
        palette = [palette]

    if scale != 0 and (scale % 2) == 0:
        raise ValueError(f"Scale must be an odd number")

    # TODO: Handle this
    """if orientation == "south":
        orientation = "north"
    elif orientation == "east":
        orientation = "west"
    elif orientation != "west" and orientation != "north":
        raise ValueError(f"Orientation must be either north or west for set_text()")"""

    instructions = meta_set_text(
        message, coords, palette, style, orientation, replace, scale, filler, namespace
    )

    status = {
      "cmd": [],
      "zone": instructions["zone"]
    }
    
    for cmd in instructions["cmds"]:
        ret = post(cmd)
        if ret and ret != '':
          status['cmd'].append(ret)

    return status


def construct_zones(coords: BlockCoordinates, digit: str, scale: int) -> list:

    zones = []

    if digit in ["0", "1"]:
        new_coords1 = BlockCoordinates(coords.x, coords.y, coords.z)

        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale, coords.z + scale
        )

        zones.append({"coords": BlockZone(new_coords1, new_coords2), "filler": "block"})

    elif digit in ["2", "3"]:

        new_coords1 = BlockCoordinates(coords.x, coords.y + ((scale / 2) + 1), coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "2" else "air",
            }
        )

        new_coords1 = BlockCoordinates(coords.x, coords.y, coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale / 2, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "3" else "air",
            }
        )

    elif digit in ["4", "5"]:

        new_coords1 = BlockCoordinates(coords.x, coords.y, coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale / 2, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block",
            }
        )

        new_coords1 = BlockCoordinates(
            coords.x + ((scale / 2) + 1), coords.y + ((scale / 2) + 1), coords.z
        )
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "4" else "air",
            }
        )

        new_coords1 = BlockCoordinates(coords.x, coords.y + ((scale / 2) + 1), coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale / 2, coords.y + scale, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "5" else "air",
            }
        )

    elif digit in ["6", "7"]:

        new_coords1 = BlockCoordinates(coords.x, coords.y + ((scale / 2) + 1), coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block",
            }
        )

        new_coords1 = BlockCoordinates(coords.x + ((scale / 2) + 1), coords.y, coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale, coords.y + scale / 2, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "6" else "air",
            }
        )

        new_coords1 = BlockCoordinates(coords.x, coords.y, coords.z)
        new_coords2 = BlockCoordinates(
            coords.x + scale / 2, coords.y + scale / 2, coords.z + scale
        )

        zones.append(
            {
                "coords": BlockZone(new_coords1, new_coords2),
                "filler": "block" if digit == "7" else "air",
            }
        )

    else:
        zones = []

    return zones


def fetch_block(digit: str, orientation: str, palette: str, filler: Block) -> Block:

    counter_orientation = "west" if orientation == "east" else "south"

    if digit == "1":
        block = block_palette[palette]["block"]

    elif digit == "2":
        block = block_palette[palette]["slab"]
        block.blockstate = BlockState({"type": "top"})

    elif digit == "3":
        block = block_palette[palette]["slab"]
        block.blockstate = BlockState({"type": "bottom"})

    elif digit == "4":
        block = block_palette[palette]["stairs"]
        block.blockstate = BlockState(
            {"facing": orientation, "shape": "straight", "half": "bottom"}
        )

    elif digit == "5":
        block = block_palette[palette]["stairs"]
        block.blockstate = BlockState(
            {"facing": counter_orientation, "shape": "straight", "half": "bottom"}
        )

    elif digit == "6":
        block = block_palette[palette]["stairs"]
        block.blockstate = BlockState(
            {"facing": orientation, "shape": "straight", "half": "top"}
        )

    elif digit == "7":
        block = block_palette[palette]["stairs"]
        block.blockstate = BlockState(
            {"facing": counter_orientation, "shape": "straight", "half": "top"}
        )

    else:
        block = filler

    return block
