from __future__ import annotations
import importlib, os
from collections.abc import Iterable
import json
from typing import cast

import adsk.core, adsk.fusion


def message_box(
    s: str,
    title: str = "",
    buttons: adsk.core.MessageBoxButtonTypes | int = adsk.core.MessageBoxButtonTypes.OKButtonType,
    icon: adsk.core.MessageBoxIconTypes | int = adsk.core.MessageBoxIconTypes.NoIconIconType,
    terminate: bool = False,
):
    result = adsk.core.Application.get().userInterface.messageBox(
        s,
        title,
        cast(adsk.core.MessageBoxButtonTypes, buttons),
        cast(adsk.core.MessageBoxIconTypes, icon),
    )
    if terminate and result == adsk.core.DialogResults.DialogCancel:
        raise ValueError("Terminated by user")
    return result


def read_script_manifest(file: str) -> dict:
    """read information from the manifest file"""
    with open(file.removesuffix(".py") + ".manifest", "r", encoding="utf-8") as f:
        return json.load(f)

def value_input(v: str | float | bool | int | adsk.core.Base):
    if isinstance(v, str):
        return adsk.core.ValueInput.createByString(v)
    if isinstance(v, bool):
        return adsk.core.ValueInput.createByBoolean(v)
    if isinstance(v, float) or isinstance(v, int):
        return adsk.core.ValueInput.createByReal(v)
    return adsk.core.ValueInput.createByObject(v)

def collection(arg: adsk.core.Base | Iterable[adsk.core.Base]):
    if isinstance(arg, Iterable):
        return adsk.core.ObjectCollection.createWithArray(list(arg))
    return adsk.core.ObjectCollection.createWithArray([arg])


def app_refresh():
    adsk.doEvents()
    adsk.core.Application.get().activeViewport.refresh()


def pip_install(modules: Iterable[str]):
    result = []
    for mod in modules:
        try:
            result.append(importlib.import_module(mod))
        except ImportError as exc:
            if (
                message_box(
                    f"Do you want to install pip package '{mod}'?\n",
                    buttons=adsk.core.MessageBoxButtonTypes.YesNoButtonType,
                    icon=adsk.core.MessageBoxIconTypes.WarningIconType,
                )
                != adsk.core.DialogResults.DialogYes
            ):
                raise exc

            # program will run in the webdeployed folder like
            # C:\Users\(user)\AppData\Local\Autodesk\webdeploy\production\xxxxxx
            # So, we can run python from the folder
            install_command = f"Python\\python.exe -m pip install {mod}"
            os.system(f'cmd /C "{install_command}"')

            # 再度試す
            try:
                result.append(importlib.import_module(mod))
            except:
                raise exc from exc

    importlib.invalidate_caches()
    return result
