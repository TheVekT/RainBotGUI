def get_btns_style_settings(ui):
    return {
        ui.terminal_btn: {"default": ":/MainIcons/icons/terminalW.png", "hover": ":/MainIcons/icons/terminalB.png", "checkable": True},
        ui.menuButton: {"default": ":/MainIcons/icons/sideBarW.png", "hover": ":/MainIcons/icons/sideBarB.png", "checkable": False},
        ui.Settings_btn: {"default": ":/MainIcons/icons/settingsW.png", "hover": ":/MainIcons/icons/settingsB.png", "checkable": True},
        ui.wbsocket_btn: {"default": ":/MainIcons/icons/websocketW.png", "hover": ":/MainIcons/icons/websocketB.png", "checkable": True},
        ui.logs_btn: {"default": ":/MainIcons/icons/logsW.png", "hover": ":/MainIcons/icons/logsB.png", "checkable": True},
        ui.stats_btn: {"default": ":/MainIcons/icons/statsW.png", "hover": ":/MainIcons/icons/statsB.png", "checkable": True},
        ui.com_help_btn: {"default": ":/MainIcons/icons/command_helpW.png", "hover": ":/MainIcons/icons/command_helpB.png", "checkable": False},
        ui.send_btn: {"default": ":/MainIcons/icons/sendW.png", "hover": ":/MainIcons/icons/sendB.png", "checkable": False},
        ui.server_btn: {"default": ":/MainIcons/icons/serverW.png", "hover": ":/MainIcons/icons/serverB.png", "checkable": True},
        ui.download_log_btn: {"default": ":/MainIcons/icons/download_W.png", "hover": ":/MainIcons/icons/download_B.png", "checkable": False},
    }