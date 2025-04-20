from __future__ import annotations
import traceback
from collections.abc import Callable
from typing import override

import adsk.core, adsk.fusion
from .helpers import message_box, value_input
from .command_values import load_command_values, store_command_values


# Dummy list of the event handlers to prevent them from being garbage collected.

# We can not use the type adsk.core.EventHandler directly here
# because adsk.core.EventHandler does not exists at runtime.
# AttributeError: module 'adsk.core' has no attribute 'EventHandler' will be raised.
# _handlers: list[adsk.core.EventHandler] = []
type EventHandler = (
    adsk.core.ApplicationCommandEventHandler
    | adsk.core.CommandCreatedEventHandler
    | adsk.core.CommandEventHandler
    | adsk.core.InputChangedEventHandler
    | adsk.core.ValidateInputsEventHandler
    | adsk.core.KeyboardEventHandler
    | adsk.core.MouseEventHandler
)
_handlers: list[EventHandler] = []

# Universal event handlers that handle events with given callback function.


class CommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self, handler: Callable[[adsk.core.CommandEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    @override
    def notify(
        self, args: adsk.core.CommandEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, handler: Callable[[adsk.core.InputChangedEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    @override
    def notify(
        self, args: adsk.core.InputChangedEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class ValidateInputsEventHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self, handler: Callable[[adsk.core.ValidateInputsEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    @override
    def notify(
        self, args: adsk.core.ValidateInputsEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, handler: Callable[[adsk.core.CommandCreatedEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    @override
    def notify(
        self, args: adsk.core.CommandCreatedEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class KeyboardEventHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, handler: Callable[[adsk.core.KeyboardEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    def notify(
        self, args: adsk.core.KeyboardEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class MouseEventHandler(adsk.core.MouseEventHandler):
    def __init__(self, handler: Callable[[adsk.core.MouseEventArgs], None]):
        super().__init__()
        _handlers.append(self)
        self.handler = handler

    def notify(
        self, args: adsk.core.MouseEventArgs
    ):  # pylint: disable=arguments-renamed
        try:
            self.handler(args)
        except:  # pylint: disable=bare-except
            message_box(traceback.format_exc())


class Command:
    """Universal command class for Fusion 360 add-ins.
    It handles the command lifecycle events by its methods
    providing a simple interface for creating user commands."""

    processing = False
    default_values: dict[str, str]

    def __init__(
        self, _id: str, name: str, tooltip: str = "", resource_folder: str = ""
    ):
        ui = adsk.core.Application.get().userInterface
        self.cmd_def = ui.commandDefinitions.itemById(_id)
        if not self.cmd_def:  # create if not exists
            self.cmd_def = ui.commandDefinitions.addButtonDefinition(
                _id, name, tooltip, resource_folder
            )

        def command_created(args: adsk.core.CommandCreatedEventArgs):
            command = args.command
            command.inputChanged.add(InputChangedHandler(self.on_changed))
            command.validateInputs.add(
                ValidateInputsEventHandler(self.on_validate_inputs)
            )
            command.activate.add(CommandEventHandler(self.on_activate))
            command.deactivate.add(CommandEventHandler(self.on_deactivate))
            command.execute.add(CommandEventHandler(self.on_execute))
            command.executePreview.add(CommandEventHandler(self.on_preview))
            command.destroy.add(CommandEventHandler(self.on_destroy))
            command.keyDown.add(KeyboardEventHandler(self.on_key_down))
            command.keyUp.add(KeyboardEventHandler(self.on_key_up))
            command.mouseMove.add(MouseEventHandler(self.on_mouse_move))
            command.mouseDown.add(MouseEventHandler(self.on_mouse_down))
            command.mouseUp.add(MouseEventHandler(self.on_mouse_up))
            command.mouseClick.add(MouseEventHandler(self.on_mouse_click))
            command.mouseDoubleClick.add(MouseEventHandler(self.on_mouse_double_click))
            command.mouseDragBegin.add(MouseEventHandler(self.on_mouse_drag_begin))
            command.mouseDrag.add(MouseEventHandler(self.on_mouse_drag))
            command.mouseDragEnd.add(MouseEventHandler(self.on_mouse_drag_end))
            command.mouseWheel.add(MouseEventHandler(self.on_mouse_wheel))
            self.on_created(args)

            # restore input values from design attributes
            # save default values, too
            self.default_values = load_command_values(command)
            self.on_changed(None)

        self.cmd_def.commandCreated.add(CommandCreatedEventHandler(command_created))
        self.cmd_def.execute()
        adsk.autoTerminate(False)

    def on_created(self, args: adsk.core.CommandCreatedEventArgs):
        pass  # to be overridden

    def on_validate_inputs(self, args: adsk.core.ValidateInputsEventArgs):
        pass  # to be overridden

    def on_changed(self, args: adsk.core.InputChangedEventArgs | None):
        pass  # to be overridden

    def on_execute_or_preview(
        self, args: adsk.core.CommandEventArgs, is_preview: bool = False
    ):
        pass  # to be overridden

    def on_execute(self, args: adsk.core.CommandEventArgs):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        timeline_start = design.timeline.markerPosition
        try:
            self.processing = True
            self.on_execute_or_preview(args, False)
        except:
            message_box(traceback.format_exc())
        finally:
            self.processing = False
            if design.timeline.markerPosition > timeline_start + 1:
                if design.timeline.item(timeline_start).parentGroup is None:
                    design.timeline.timelineGroups.add(
                        timeline_start, design.timeline.markerPosition - 1
                    )
            adsk.terminate()

    def on_preview(self, args: adsk.core.CommandEventArgs):
        try:
            self.processing = True
            self.on_execute_or_preview(args, True)
        except:
            # message_box(traceback.format_exc())
            pass
        finally:
            self.processing = False

    def on_destroy(self, _: adsk.core.CommandEventArgs):
        if not self.processing:
            adsk.terminate()

    def on_activate(self, args: adsk.core.CommandEventArgs):
        pass  # to be overridden

    def on_deactivate(self, args: adsk.core.CommandEventArgs):
        pass  # to be overridden

    def on_key_down(self, args: adsk.core.KeyboardEventArgs):
        pass  # to be overridden

    def on_key_up(self, args: adsk.core.KeyboardEventArgs):
        pass  # to be overridden

    def on_mouse_move(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_down(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_up(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_click(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_double_click(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_drag_begin(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_drag(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_drag_end(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden

    def on_mouse_wheel(self, args: adsk.core.MouseEventArgs):
        pass  # to be overridden


class TabInput[Parent]:
    """Each tab of a TabbedCommand should be derived from this class.
    It provides a simple interface for creating tabbed commands."""

    tab: adsk.core.TabCommandInput
    id = ""
    name = ""

    def __init__(
        self,
        args: adsk.core.CommandCreatedEventArgs,
        inputs: adsk.core.CommandInputs,
        parent: Parent,
    ):
        self.parent = parent
        if self.id == "" or self.name == "":
            raise NotImplementedError("Give id and name for the tab.")
        self.tab = inputs.addTabCommandInput(self.id, self.name)
        self.on_created(args, self.tab.children)

    def on_created(
        self, args: adsk.core.CommandCreatedEventArgs, inputs: adsk.core.CommandInputs
    ):
        pass  # to be overridden

    def on_changed(self, args: adsk.core.InputChangedEventArgs | None):
        pass  # to be overridden

    def on_execute_or_preview(
        self, args: adsk.core.CommandEventArgs, is_preview: bool = False
    ):
        pass  # to be overridden


class TabbedCommand(Command):
    """Command with tabs. Each tab has its own execution context.
    Each tab should be derived from TabInput class."""

    tabs: list[TabInput] = []

    def __init__(
        self,
        _id: str,
        name: str,
        tooltip: str = "",
        tab_classes: list[type[TabInput]] | None = None,
    ):
        self.tab_classes = tab_classes if tab_classes is not None else []
        super().__init__(_id, name, tooltip)

    @override
    def on_created(self, args: adsk.core.CommandCreatedEventArgs):
        # remove references to the old objects
        self.tabs.clear()

        # initialize tabs
        for tab_class in self.tab_classes:
            self.tabs.append(tab_class(args, args.command.commandInputs, self))

        # then initialize other command inputs

    @override
    def on_changed(self, args: adsk.core.InputChangedEventArgs | None):
        for tab in self.tabs:
            tab.on_changed(args)

    @override
    def on_execute_or_preview(
        self, args: adsk.core.CommandEventArgs, is_preview: bool = False
    ):
        if not is_preview:
            # store the parameters into design attributes
            store_command_values(args.command)

        # execute the active tab
        for tab in self.tabs:
            if tab.tab.isActive:
                tab.on_execute_or_preview(args, is_preview)
                break


def value_control(
    parent: adsk.core.CommandInputs,
    id: str,
    name: str,
    unit: str,
    value: str,
    # @pylint: disable=redefined-builtin
    min: float | None = None,
    max: float | None = None,
    min_exclusive: float | None = None,
    max_exclusive: float | None = None,
    is_visible: bool = True,
    is_enabled: bool = True,
    is_full_width: bool | None = None,
    tooltip: str | None = None,
):
    """Create a ValueCommandInput in parent CommandInputs."""

    result = parent.addValueInput(id, name, unit, value_input(value))
    if min is not None:
        result.minimumValue = min
        result.isMinimumInclusive = True
        result.isMinimumLimited = True
    if min_exclusive is not None:
        result.minimumValue = min_exclusive
        result.isMinimumInclusive = False
        result.isMinimumLimited = True
    if max is not None:
        result.maximumValue = max
        result.isMaximumInclusive = True
        result.isMaximumLimited = True
    if max_exclusive is not None:
        result.maximumValue = max_exclusive
        result.isMaximumInclusive = False
        result.isMaximumLimited = True
    if tooltip is not None:
        result.tooltip = tooltip
    result.isVisible = is_visible
    result.isEnabled = is_enabled
    if is_full_width is not None:
        result.isFullWidth = is_full_width
    return result
