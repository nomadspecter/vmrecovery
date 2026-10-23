"""Checks the real VBoxController's command lines and output parsing.

A small fake `VBoxManage` script prints output in VirtualBox's real formats and
records the arguments it receives, so no VirtualBox is needed to run these.
"""
import stat
import textwrap

import pytest

from app.vbox import VBoxController, VBoxError

FAKE = textwrap.dedent('''\
    #!/bin/bash
    echo "$@" >> "$FAKE_LOG"
    case "$1 $2 $3" in
      "--version "*)
        echo "7.0.12r159484" ;;
      "list vms "*)
        echo '"DEV-LAB-01" {11111111-1111-4111-8111-111111111111}'
        echo '"My VM with spaces" {22222222-2222-4222-8222-222222222222}' ;;
      "showvminfo "*)
        echo 'name="DEV-LAB-01"'
        echo 'UUID="11111111-1111-4111-8111-111111111111"'
        echo 'BaseFolder="/home/lab/VirtualBox VMs"'
        echo "VMState=\\"$FAKE_STATE\\"" ;;
      "snapshot DEV-LAB-01 list")
        if [ "$FAKE_SNAPS" = "none" ]; then echo "This machine does not have any snapshots" >&2; exit 1; fi
        echo 'SnapshotName="auto-1"'
        echo 'SnapshotUUID="aaa"'
        echo 'SnapshotName-1="auto-2"'
        echo 'SnapshotName-1-1="auto-3"'
        echo 'CurrentSnapshotName="auto-3"' ;;
      "guestproperty get DEV-LAB-01")
        if [ "$FAKE_PROP" = "none" ]; then echo "No value set!"; else echo "Value: 1780000000"; fi ;;
      "snapshot DEV-LAB-01 restore")
        if [ "$FAKE_FAIL" = "1" ]; then echo "VBoxManage: error: Snapshot not found" >&2; exit 1; fi ;;
      "clonevm "*)
        if [ "$FAKE_CLONE_FAIL" = "1" ]; then
          echo "VBoxManage: error: Clone VM failed" >&2
          echo "VBoxManage: error: Code: VBOX_E_INVALID_OBJECT_STATE" >&2
          echo "VBoxManage: error: Details: Error: object state prohibits operation" >&2
          exit 1
        fi ;;
    esac
    exit 0
''')


@pytest.fixture
def ctl(tmp_path, monkeypatch):
    script = tmp_path / "VBoxManage"
    script.write_text(FAKE)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.log"
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("FAKE_STATE", "running")
    monkeypatch.setenv("FAKE_SNAPS", "some")
    monkeypatch.setenv("FAKE_PROP", "some")
    monkeypatch.setenv("FAKE_FAIL", "0")
    monkeypatch.setenv("FAKE_CLONE_FAIL", "0")
    c = VBoxController(str(script))
    c.calls = lambda: log.read_text().strip().splitlines()
    return c


def test_list_vms_parses_names_with_spaces(ctl):
    assert ctl.list_vms() == [("DEV-LAB-01", "11111111-1111-4111-8111-111111111111"),
                              ("My VM with spaces", "22222222-2222-4222-8222-222222222222")]


@pytest.mark.parametrize("state", ["running", "poweroff", "aborted", "paused", "gurumeditation"])
def test_get_state(ctl, monkeypatch, state):
    monkeypatch.setenv("FAKE_STATE", state)
    assert ctl.get_state("DEV-LAB-01") == state


def test_list_snapshots_reads_nested_names_but_not_current_marker(ctl):
    assert ctl.list_snapshots("DEV-LAB-01") == ["auto-1", "auto-2", "auto-3"]


def test_machine_without_snapshots_gives_empty_list(ctl, monkeypatch):
    monkeypatch.setenv("FAKE_SNAPS", "none")
    assert ctl.list_snapshots("DEV-LAB-01") == []


def test_guest_property(ctl, monkeypatch):
    assert ctl.get_guest_property("DEV-LAB-01", "/Lab/Heartbeat") == "1780000000"
    monkeypatch.setenv("FAKE_PROP", "none")
    assert ctl.get_guest_property("DEV-LAB-01", "/Lab/Heartbeat") is None


def test_command_lines_are_exactly_what_virtualbox_expects(ctl):
    ctl.take_snapshot("DEV-LAB-01", "snapA", live=True, description="d")
    ctl.take_snapshot("DEV-LAB-01", "snapB")
    ctl.delete_snapshot("DEV-LAB-01", "snapA")
    ctl.power_off("DEV-LAB-01")
    ctl.restore_snapshot("DEV-LAB-01", "snapB")
    ctl.start_vm("DEV-LAB-01")
    assert ctl.calls() == [
        "snapshot DEV-LAB-01 take snapA --description d --live",
        "snapshot DEV-LAB-01 take snapB",
        "snapshot DEV-LAB-01 delete snapA",
        "controlvm DEV-LAB-01 poweroff",
        "snapshot DEV-LAB-01 restore snapB",
        "startvm DEV-LAB-01 --type headless",
    ]


def test_failed_command_raises_with_virtualbox_message(ctl, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")
    with pytest.raises(VBoxError, match="Snapshot not found"):
        ctl.restore_snapshot("DEV-LAB-01", "x")


def test_the_failure_message_carries_the_virtualbox_code(ctl, monkeypatch):
    """The first "error:" line only says "Clone VM failed". The code on the
    next line says why — VBOX_E_INVALID_OBJECT_STATE means the machine was
    running — and that is what makes the message actionable.

    VirtualBox writes the code behind its own "VBoxManage: error: " prefix,
    so it has to be looked for inside the line, not at the start of it.
    """
    monkeypatch.setenv("FAKE_CLONE_FAIL", "1")
    with pytest.raises(VBoxError) as exc:
        ctl.clone_vm("DEV-LAB-01", "LAB-CS-002", linked=False)
    msg = str(exc.value)
    assert "Clone VM failed" in msg
    assert "VBOX_E_INVALID_OBJECT_STATE" in msg


def test_missing_vboxmanage_gives_clear_error():
    with pytest.raises(VBoxError, match="not found"):
        VBoxController("/nonexistent/VBoxManage").list_vms()


def test_names_with_shell_characters_are_not_interpreted(ctl, tmp_path):
    ctl.take_snapshot("DEV-LAB-01", "a; touch pwned")      # arguments go straight to the program
    assert not (tmp_path / "pwned").exists()
    assert ctl.calls()[-1] == "snapshot DEV-LAB-01 take a; touch pwned"


def test_base_folder_and_version_are_read(ctl):
    assert ctl.base_folder("DEV-LAB-01") == "/home/lab/VirtualBox VMs"
    assert ctl.get_version() == "7.0.12r159484"


def test_wait_until_ready_returns_a_settled_state(ctl):
    assert ctl.wait_until_ready("DEV-LAB-01", timeout=1) == "running"


def test_wait_until_ready_times_out_on_a_busy_machine(ctl, monkeypatch):
    monkeypatch.setenv("FAKE_STATE", "liveSnapshotting")
    with pytest.raises(VBoxError, match="still busy"):
        ctl.wait_until_ready("DEV-LAB-01", timeout=0.05, poll=0.01)


def test_wait_until_ready_knows_the_state_word_virtualbox_7_uses(ctl, monkeypatch):
    """A live snapshot leaves the machine in 'onlinesnapshotting'.

    It used to be missing from the list of busy states, so a machine that was
    stuck mid-snapshot was reported as "powered off" and the recovery tried to
    act on a machine VirtualBox had locked.
    """
    monkeypatch.setenv("FAKE_STATE", "onlinesnapshotting")
    with pytest.raises(VBoxError, match="still busy"):
        ctl.wait_until_ready("DEV-LAB-01", timeout=0.05, poll=0.01)
