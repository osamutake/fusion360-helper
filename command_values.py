"""Utility functions to store and retrieve command values
in design attributes.
load_command_values(cmd) - load command values from design attributes
store_command_values(cmd) - store command values in design attributes
"""

from __future__ import annotations
from typing import cast

import adsk.core, adsk.fusion


def load_command_values(cmd: adsk.core.Command):
    """Load command values from design attributes and
    fill the input fields of the command.
    It returns a dictionary with the default values of the command inputs.
    """
    design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    command_name = cmd.parentCommandDefinition.id
    default_values = get_command_values(cmd.commandInputs)
    for key in default_values:
        attr = design.attributes.itemByName(command_name, key)
        if attr:
            set_command_value(cmd.commandInputs, key, attr.value)
    return default_values


def store_command_values(cmd: adsk.core.Command):
    """Store command values in design attributes."""

    design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    command_name = cmd.parentCommandDefinition.id
    values = get_command_values(cmd.commandInputs)
    for key, value in values.items():
        design.attributes.add(command_name, key, value)


def get_command_values(
    items: adsk.core.CommandInputs, prepend: str = ""
) -> dict[str, str]:
    """Create a dictionary with the command values.
    The key is prepend + item.id and the value is the command value.
    """
    result: dict[str, str] = {}
    for item in items:
        if item.commandInputs != items:
            continue
        key = prepend + item.id
        match item.objectType:
            case "adsk::core::TabCommandInput":
                result[key] = (
                    "1" if cast(adsk.core.TabCommandInput, item).isActive else "0"
                )
                result.update(
                    get_command_values(
                        cast(adsk.core.TabCommandInput, item).children, key + "."
                    )
                )
            case "adsk::core::GroupCommandInput":
                result[key] = (
                    "1" if cast(adsk.core.GroupCommandInput, item).isExpanded else "0"
                )
                result.update(
                    get_command_values(
                        cast(adsk.core.GroupCommandInput, item).children, key + "."
                    )
                )
            # case "adsk::core::ImageCommandInput":
            #     cast(adsk.core.ImageCommandInput, item).imageFile = str(value)
            #     cast(adsk.core.ImageCommandInput, item).scaleFactor = str(value)
            # case "adsk::core::TableCommandInput":
            #     cast(adsk.core.TableCommandInput, item).commandInputs
            case "adsk::core::TriadCommandInput":
                result[key] = ",".join(
                    str(f)
                    for f in cast(adsk.core.TriadCommandInput, item).transform.asArray()
                )
            case "adsk::core::ValueCommandInput":
                result[key] = str(cast(adsk.core.ValueCommandInput, item).value)
            case "adsk::core::BoolValueCommandInput":
                result[key] = (
                    "1" if cast(adsk.core.BoolValueCommandInput, item).value else "0"
                )
            case "adsk::core::TextBoxCommandInput":
                result[key] = cast(adsk.core.TextBoxCommandInput, item).text
            # case "adsk::core::BrowserCommandInput":
            #     cast(adsk.core.BrowserCommandInput, item).htmlFileURL
            case "adsk::core::DropDownCommandInput":
                result[key] = str(
                    cast(adsk.core.DropDownCommandInput, item).selectedItem.index
                )
            # case "adsk::core::ButtonRowCommandInput":
            #     cast(adsk.core.ButtonRowCommandInput, item).listItems
            # case "adsk::core::DirectionCommandInput":
            #     result[key] = str(
            #         vector.Vector(cast(adsk.core.DirectionCommandInput, item).manipulatorDirection)
            #     )
            # case "adsk::core::SelectionCommandInput":
            #     cast(adsk.core.SelectionCommandInput, item).selectionCount
            # case "adsk::core::SeparatorCommandInput":
            #     cast(adsk.core.SeparatorCommandInput, item).isVisible
            case "adsk::core::AngleValueCommandInput":
                result[key] = str(cast(adsk.core.AngleValueCommandInput, item).value)
            case "adsk::core::StringValueCommandInput":
                result[key] = cast(adsk.core.StringValueCommandInput, item).value
            case "adsk::core::FloatSliderCommandInput":
                float_slider = cast(adsk.core.FloatSliderCommandInput, item)
                result[key] = str(float_slider.valueOne)
                if float_slider.hasTwoSliders:
                    result[key] += "," + str(float_slider.valueTwo)
            case "adsk::core::FloatSpinnerCommandInput":
                result[key] = str(cast(adsk.core.FloatSpinnerCommandInput, item).value)
            # case "adsk::core::DistanceValueCommandInput":
            #     result[key] = str(cast(adsk.core.DistanceValueCommandInput, item).value)
            case "adsk::core::IntegerSliderCommandInput":
                integer_slider = cast(adsk.core.IntegerSliderCommandInput, item)
                result[key] = str(integer_slider.valueOne)
                if integer_slider.hasTwoSliders:
                    result[key] += "," + str(integer_slider.valueTwo)
            case "adsk::core::IntegerSpinnerCommandInput":
                result[key] = str(
                    cast(adsk.core.IntegerSpinnerCommandInput, item).value
                )
            case "adsk::core::RadioButtonGroupCommandInput":
                result[key] = str(
                    cast(
                        adsk.core.RadioButtonGroupCommandInput, item
                    ).selectedItem.index
                )
    return result


def set_command_value(items: adsk.core.CommandInputs, key: str, value: str):
    """Set the value of a CommandInput corresponding to the given key."""
    name, *children = key.split(".", 2)
    item = items.itemById(name)
    if item is None:
        return
    if len(children):
        match item.objectType:
            case "adsk::core::TabCommandInput":
                set_command_value(
                    cast(adsk.core.TabCommandInput, item).children, children[0], value
                )
            case "adsk::core::GroupCommandInput":
                set_command_value(
                    cast(adsk.core.GroupCommandInput, item).children, children[0], value
                )
        return

    match item.objectType:
        case "adsk::core::TabCommandInput":
            if int(value):
                cast(adsk.core.TabCommandInput, item).activate()
        case "adsk::core::GroupCommandInput":
            cast(adsk.core.GroupCommandInput, item).isExpanded = bool(int(value))
        # case "adsk::core::ImageCommandInput":
        #     cast(adsk.core.ImageCommandInput, item).imageFile = str(value)
        #     cast(adsk.core.ImageCommandInput, item).scaleFactor = str(value)
        # case "adsk::core::TableCommandInput":
        #     cast(adsk.core.TableCommandInput, item).commandInputs
        case "adsk::core::TriadCommandInput":
            cast(adsk.core.TriadCommandInput, item).transform.setWithArray(
                [float(s) for s in value.split(",")]
            )
        case "adsk::core::ValueCommandInput":
            cast(adsk.core.ValueCommandInput, item).value = float(value)
        case "adsk::core::BoolValueCommandInput":
            cast(adsk.core.BoolValueCommandInput, item).value = bool(int(value))
        case "adsk::core::TextBoxCommandInput":
            cast(adsk.core.TextBoxCommandInput, item).text = value
        # case "adsk::core::BrowserCommandInput":
        #     cast(adsk.core.BrowserCommandInput, item).htmlFileURL
        case "adsk::core::DropDownCommandInput":
            cast(adsk.core.DropDownCommandInput, item).listItems[
                int(value)
            ].isSelected = True
        # case "adsk::core::ButtonRowCommandInput":
        #     cast(adsk.core.ButtonRowCommandInput, item).listItems
        # case "adsk::core::DirectionCommandInput":
        #     result[key] = str(
        #         vector.Vector(cast(adsk.core.DirectionCommandInput, item).manipulatorDirection)
        #     )
        # case "adsk::core::SelectionCommandInput":
        #     cast(adsk.core.SelectionCommandInput, item).selectionCount
        # case "adsk::core::SeparatorCommandInput":
        #     cast(adsk.core.SeparatorCommandInput, item).isVisible
        case "adsk::core::AngleValueCommandInput":
            cast(adsk.core.AngleValueCommandInput, item).value = float(value)
        case "adsk::core::StringValueCommandInput":
            cast(adsk.core.StringValueCommandInput, item).value = value
        case "adsk::core::FloatSliderCommandInput":
            values = value.split(",", 2)
            float_slider = cast(adsk.core.FloatSliderCommandInput, item)
            float_slider.valueOne = float(values[0])
            if len(values) == 2:
                float_slider.valueTwo = float(values[1])
        case "adsk::core::FloatSpinnerCommandInput":
            cast(adsk.core.FloatSpinnerCommandInput, item).value = float(value)
        # case "adsk::core::DistanceValueCommandInput":
        #     result[key] = str(cast(adsk.core.DistanceValueCommandInput, item).value)
        case "adsk::core::IntegerSliderCommandInput":
            values = value.split(",", 2)
            integer_slider = cast(adsk.core.IntegerSliderCommandInput, item)
            integer_slider.valueOne = int(values[0])
            if len(values) == 2:
                integer_slider.valueTwo = int(values[1])
        case "adsk::core::IntegerSpinnerCommandInput":
            cast(adsk.core.IntegerSpinnerCommandInput, item).value = int(value)
        case "adsk::core::RadioButtonGroupCommandInput":
            cast(adsk.core.RadioButtonGroupCommandInput, item).listItems[
                int(value)
            ].isSelected = True
