from onur_drive.probe import READ_COMMANDS

def test_only_preapproved_read_commands():
    permitted={'getprop','ls','dumpsys','service'}
    assert all(cmd[0] in permitted for cmd in READ_COMMANDS.values())
    all_parts=' '.join(' '.join(x) for x in READ_COMMANDS.values())
    for forbidden in ('setprop','chmod','root','remount','am broadcast','settings put','pm install'):
        assert forbidden not in all_parts
