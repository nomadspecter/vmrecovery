"""The only module that talks to VirtualBox.

VBoxController runs real VBoxManage commands. SimulatedVBox has the same
methods but keeps everything in memory, so the system can be demonstrated
and tested on a machine without VirtualBox. Everything else in the project
uses whichever one it is given.
"""
import logging
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path


log = logging.getLogger("vmrecovery")


class VBoxError(Exception):
    """A VBoxManage command failed or VirtualBox is not reachable."""


# VirtualBox states that mean "something is changing, do not judge the VM yet".
#
# This is the union of the state words VirtualBox 7.x actually reports, and
# the spellings differ between the command line ("onlinesnapshotting") and the
# SDK ("OnlinSnapshotting"), so both are listed. A state missing from this list
# is worse than useless: the machine looks settled when it is not, and the
# recovery then acts on a machine VirtualBox considers locked.
BUSY_STATES = {"starting", "stopping", "saving", "restoring", "restoringsnapshot",
               "takingsnapshot", "deletingsnapshot", "onlinesnapshotting", "onlinsnapshotting",
               "livesnapshotting", "teleporting", "settingup", "probing", "meteringunsupported"}

# States that mean the machine died rather than being switched off.
CRASHED_STATES = {"aborted", "gurumeditation", "stuck", "aborted-saved"}

# States that mean the machine is there but not doing anything.
PAUSED_STATES = {"paused"}
SAVED_STATES = {"saved"}
POWERED_OFF_STATES = {"poweroff", "off"}


def state_is_busy(state: str) -> bool:
    """True when VirtualBox is busy with the machine and it must not be judged yet."""
    return (state or "").strip().lower() in BUSY_STATES


class VBoxController:
    def __init__(self, vboxmanage: str = "VBoxManage", timeout: int = 1800,
                 query_timeout: int = 60, snapshot_timeout: int = 120,
                 action_timeout: int = 180, restore_timeout: int = 600):
        self.exe = shutil.which(vboxmanage) or vboxmanage
        # Every command has its own bound. A command that hangs holds the
        # global VirtualBox lock, and a lock held for half an hour freezes the
        # dashboard and stops the worker, so the short commands get a short
        # timeout and only export and clone get the long one.
        self.timeout = timeout                # long operations: export, clone, import
        self.query_timeout = query_timeout    # reads: state, uuid, snapshot list
        self.snapshot_timeout = snapshot_timeout   # snapshot take and delete
        self.action_timeout = action_timeout  # power, suspend, start, rename
        self.restore_timeout = restore_timeout    # snapshot restore

    # ---- low level -------------------------------------------------------
    def _run(self, *args: str, check: bool = True, timeout: float | None = None) -> str:
        log.debug("VBoxManage %s", " ".join(args))
        try:
            proc = subprocess.run([self.exe, *args], capture_output=True, text=True,
                                  timeout=timeout or self.timeout)
        except FileNotFoundError:
            raise VBoxError(f"VBoxManage not found ('{self.exe}'). Is VirtualBox installed?")
        except subprocess.TimeoutExpired:
            raise VBoxError(f"VBoxManage timed out: {' '.join(args[:3])}")
        if check and proc.returncode != 0:
            raise VBoxError(self._error_message(proc))
        return proc.stdout

    @staticmethod
    def _error_message(proc) -> str:
        """The most useful line of a failed VBoxManage run.

        VirtualBox's first "error:" line is often just a summary — "Clone VM
        failed" — and another line carries the code that says why
        (VBOX_E_INVALID_OBJECT_STATE, for instance). Both are kept, because
        the summary alone is not enough to act on.

        The code is looked for anywhere in the output, because VirtualBox
        writes it in several shapes: "Code: VBOX_E_...", "Details: Error:
        VBOX_E_...", and always behind its own "VBoxManage: error: " prefix.
        """
        lines = [line.strip() for line in (proc.stderr or proc.stdout).splitlines() if line.strip()]
        summary = None
        code = None
        for line in lines:
            if summary is None and "error:" in line and "Context:" not in line and "Details:" not in line:
                summary = line
            if code is None:
                m = re.search(r"Code:\s*(VBOX_E_[A-Z0-9_]+)", line)
                if not m:
                    m = re.search(r"\b(VBOX_E_[A-Z0-9_]+)\b", line)
                if m:
                    code = m.group(1)
        if summary is None and lines:
            summary = lines[-1] if not any("error:" in l for l in lines) else lines[0]
        summary = summary or f"VBoxManage exit code {proc.returncode}"
        return f"{summary} ({code})" if code else summary

    # ---- queries ---------------------------------------------------------
    def list_vms(self, timeout: float | None = None) -> list[tuple[str, str]]:
        """Return [(name, uuid)] for every VM known to VirtualBox."""
        out = self._run("list", "vms", timeout=timeout or self.query_timeout)
        return [(m.group(1), m.group(2))
                for m in re.finditer(r'^"(.*)" \{([0-9a-fA-F-]+)\}\s*$', out, re.M)]

    def get_state(self, vm: str) -> str:
        """VirtualBox's own state word: running, poweroff, aborted, paused, ..."""
        out = self._run("showvminfo", vm, "--machinereadable", timeout=self.query_timeout)
        m = re.search(r'^VMState="([^"]+)"', out, re.M)
        if not m:
            raise VBoxError("could not read VMState")
        return m.group(1)

    def list_snapshots(self, vm: str) -> list[str]:
        out = self._run("snapshot", vm, "list", "--machinereadable", check=False,
                        timeout=self.query_timeout)
        return re.findall(r'^SnapshotName(?:-[\d-]+)?="(.*)"$', out, re.M)

    def get_guest_property(self, vm: str, prop: str) -> str | None:
        out = self._run("guestproperty", "get", vm, prop, check=False, timeout=self.query_timeout)
        m = re.search(r'^Value:\s*(.*)$', out, re.M)
        if m:
            return m.group(1).strip()
        return None

    def get_uuid(self, vm: str) -> str:
        out = self._run("showvminfo", vm, "--machinereadable", timeout=self.query_timeout)
        m = re.search(r'^UUID="([^"]+)"', out, re.M)
        if not m:
            raise VBoxError("could not read VM UUID")
        return m.group(1)

    def base_folder(self, vm: str) -> str:
        """The folder VirtualBox keeps this VM in (the base of every file it owns)."""
        out = self._run("showvminfo", vm, "--machinereadable", timeout=self.query_timeout)
        m = re.search(r'^BaseFolder="([^"]+)"', out, re.M)
        return m.group(1) if m else ""

    def get_version(self, timeout: float | None = None) -> str:
        return self._run("--version", timeout=timeout).strip()

    def wait_until_ready(self, vm: str, timeout: float = 60.0, poll: float = 1.0) -> str:
        """Block until VirtualBox has left a changing state. Returns the settled state.

        Taking a snapshot while VirtualBox is still writing the previous one fails
        with "machine state: LiveSnapshotting", so callers wait here first. A
        machine that stays in a changing state for the whole timeout is stuck
        and needs an administrator, so the error says so.
        """
        deadline = time.monotonic() + timeout
        while True:
            state = self.get_state(vm)
            if not state_is_busy(state):
                return state
            if time.monotonic() >= deadline:
                raise VBoxError(f"VirtualBox is still busy with this machine (state "
                                f"'{state}') after {timeout:.0f}s. It looks stuck and "
                                f"needs an administrator.")
            time.sleep(poll)

    def wait_for_state(self, vm: str, states, timeout: float = 60.0, poll: float = 0.5,
                       settle: float = 1.0) -> str:
        """Wait until the machine is in one of the given states, and has settled.

        VirtualBox changes a machine's state in several steps, and a command
        issued in the middle of that change is refused — "Current object state
        prohibits operation". Saving a running machine's state and cloning it
        straight afterwards used to fail for exactly that reason, so the state
        is not just reached but has to stay put for a moment.
        """
        wanted = {s.lower() for s in states}
        deadline = time.monotonic() + timeout
        stable_since = None
        while True:
            state = self.get_state(vm)
            if state.lower() in wanted:
                if stable_since is None:
                    stable_since = time.monotonic()
                elif time.monotonic() - stable_since >= settle:
                    return state
            else:
                stable_since = None
            if time.monotonic() >= deadline:
                raise VBoxError(f"The machine is in the state '{state}' and did not reach "
                                f"{' or '.join(sorted(wanted))} within {timeout:.0f}s.")
            time.sleep(poll)

    # ---- actions ---------------------------------------------------------
    def take_snapshot(self, vm: str, name: str, live: bool = False, description: str = "") -> None:
        args = ["snapshot", vm, "take", name]
        if description:
            args += ["--description", description]
        if live:
            args.append("--live")
        # A live snapshot of a guest that does not support them never returns,
        # so the call is bounded instead of waiting for the long timeout.
        self._run(*args, timeout=self.snapshot_timeout)

    def delete_snapshot(self, vm: str, name: str) -> None:
        self._run("snapshot", vm, "delete", name, timeout=self.snapshot_timeout)

    def power_off(self, vm: str) -> None:
        self._run("controlvm", vm, "poweroff", timeout=self.action_timeout)

    def resume_vm(self, vm: str) -> None:
        """Resume a paused VM without power-cycling it."""
        self._run("controlvm", vm, "resume", timeout=self.action_timeout)

    def pause_vm(self, vm: str) -> None:
        """Pause a running VM without shutting it down."""
        self._run("controlvm", vm, "pause", timeout=self.action_timeout)

    def _find_vm_pids(self, vm_uuid: str) -> list[int]:
        """Locate running VBoxHeadless/VirtualBoxVM process IDs for this VM UUID."""
        target = vm_uuid.strip().lower().strip("{}")
        pids: list[int] = []
        proc_dir = Path("/proc")
        if not proc_dir.is_dir():
            return pids
        for entry in proc_dir.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                raw = (entry / "cmdline").read_bytes()
            except OSError:
                continue
            if not raw:
                continue
            parts = [p.decode("utf-8", errors="ignore") for p in raw.split(b"\x00") if p]
            if not parts:
                continue
            exe_name = Path(parts[0]).name.lower()
            if exe_name not in ("vboxheadless", "virtualboxvm"):
                continue
            for idx, arg in enumerate(parts):
                if arg == "--startvm" and idx + 1 < len(parts):
                    if parts[idx + 1].strip().lower().strip("{}") == target:
                        pids.append(int(entry.name))
                        break
        return pids

    def crash(self, vm: str) -> None:
        """Simulate an abrupt VM crash by terminating its running VirtualBox process.

        Sending SIGKILL to the VM's VBoxHeadless/VirtualBoxVM process forces
        VirtualBox into the 'aborted' state, matching a genuine hypervisor or
        host-process crash so the recovery worker detects and restores it.
        """
        state = self.wait_until_ready(vm).lower()
        if state in CRASHED_STATES:
            return
        if state not in ("running", "paused"):
            raise VBoxError(f"Cannot simulate a crash while the machine is '{state}'. Start the VM first.")
        uuid = self.get_uuid(vm)
        pids = self._find_vm_pids(uuid)
        if not pids:
            raise VBoxError("Could not locate the running VirtualBox VM process to simulate a crash.")
        killed = False
        last_err = None
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
                killed = True
            except OSError as exc:
                last_err = exc
        if not killed:
            raise VBoxError(f"Could not terminate VirtualBox VM process: {last_err}")
        self.wait_for_state(vm, ("aborted", "poweroff"), timeout=15.0, poll=0.5, settle=0.5)

    def freeze(self, vm: str) -> None:
        """Simulate a guest OS freeze by pausing the running VM in VirtualBox."""
        state = self.wait_until_ready(vm).lower()
        if state == "paused":
            return
        if state != "running":
            raise VBoxError(f"Cannot simulate a freeze while the machine is '{state}'. Start the VM first.")
        self.pause_vm(vm)
        self.wait_for_state(vm, ("paused",), timeout=15.0, poll=0.5, settle=0.5)

    def save_state(self, vm: str) -> None:
        """Suspend to disk. export/clone refuse a running VM; a saved one is fine."""
        self._run("controlvm", vm, "savestate", timeout=self.action_timeout)

    def discard_state(self, vm: str) -> None:
        """Throw away a saved state so the VM can be restored or started cleanly."""
        self._run("discardstate", vm, timeout=self.action_timeout)

    def restore_snapshot(self, vm: str, name: str) -> None:
        self._run("snapshot", vm, "restore", name, timeout=self.restore_timeout)

    def start_vm(self, vm: str) -> None:
        self._run("startvm", vm, "--type", "headless", timeout=self.action_timeout)

    def rename_vm(self, vm: str, new_name: str) -> None:
        self._run("modifyvm", vm, "--name", new_name, timeout=self.action_timeout)

    def clone_vm(self, source_vm: str, new_name: str, linked: bool = True,
                 snapshot: str | None = None) -> tuple[str, str]:
        args = ["clonevm", source_vm, "--name", new_name, "--register"]
        if linked:
            if not snapshot:
                raise VBoxError("A linked clone needs a snapshot. Take a snapshot of the "
                                "template first (auto or manual), then clone again.")
            args += ["--options", "link", "--snapshot", snapshot]
        else:
            args += ["--mode", "all"]
        self._run(*args)
        return new_name, self.get_uuid(new_name)

    def export_vm(self, vm: str, output_path: str) -> None:
        self._run("export", vm, "-o", output_path)

    def import_vm(self, appliance_path: str, new_name: str = "",
                  base_folder: str = "") -> tuple[str, str]:
        args = ["import", appliance_path]
        if new_name:
            args += ["--vsys", "0", "--vmname", new_name]
        if base_folder:
            args += ["--basefolder", base_folder]
        self._run(*args)
        target = new_name or "Imported-VM"
        return target, self.get_uuid(target)

    def unregister_and_delete(self, vm: str) -> None:
        self._run("unregistervm", vm, "--delete")

    def default_machine_folder(self) -> str:
        """The folder VirtualBox keeps new machines in."""
        out = self._run("list", "systemproperties", timeout=self.query_timeout)
        m = re.search(r"^Default machine folder:\s*(.+)$", out, re.M)
        return m.group(1).strip() if m else ""

    def list_media(self) -> list[dict]:
        """Every disk VirtualBox knows about: its path, type and whether it is still there."""
        out = self._run("list", "hdds", timeout=self.query_timeout)
        media, cur = [], {}
        for line in out.splitlines():
            m = re.match(r"^(UUID|Location|State|Type):\s*(.*)$", line)
            if m:
                cur[m.group(1)] = m.group(2).strip()
            elif not line.strip() and cur:
                media.append(cur)
                cur = {}
        if cur:
            media.append(cur)
        return media

    def close_medium(self, path: str, delete: bool = True) -> None:
        """Take a disk out of VirtualBox's registry, and its file with it.

        A medium whose file has already been deleted cannot be closed the
        usual way — VirtualBox answers "Could not find file for the medium" —
        so an empty placeholder is created for it first. That is the only way
        to get a stale entry out of the registry, and a stale entry is what
        makes the next clone of the same name fail.
        """
        p = Path(path)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()
        args = ["closemedium", "disk", path]
        if delete:
            args.append("--delete")
        self._run(*args, check=False, timeout=self.action_timeout)


class SimulatedVBox:
    """In-memory stand-in for VirtualBox. Thread-safe enough for the demo."""

    def __init__(self, demo_vms: bool = False):
        self._lock = threading.RLock()
        self.vms: dict[str, dict] = {}
        self.heartbeats: dict[tuple[str, str], str] = {}
        self.fail_next: set[str] = set()      # operations that should fail, for tests
        if demo_vms:
            for i, (name, state) in enumerate([("DEV-LAB-01", "running"), ("DEV-LAB-02", "running"),
                                                ("NET-LAB-03", "running"), ("NET-LAB-04", "running"),
                                                ("SEC-LAB-05", "poweroff")], start=1):
                self.add_vm(name, f"00000000-0000-4000-8000-00000000000{i}", state)

    def add_vm(self, name: str, uuid: str, state: str = "running") -> None:
        with self._lock:
            self.vms[uuid] = {"name": name, "state": state, "snapshots": []}

    def _find(self, vm: str) -> dict:
        with self._lock:
            for uuid, data in self.vms.items():
                if vm in (uuid, data["name"]):
                    return data
        raise VBoxError(f"Could not find a registered machine named '{vm}'")

    def _maybe_fail(self, op: str) -> None:
        if op in self.fail_next:
            self.fail_next.discard(op)
            raise VBoxError(f"simulated {op} failure")

    # test and demo helpers
    def crash(self, vm: str) -> None:
        self._find(vm)["state"] = "aborted"

    def freeze(self, vm: str) -> None:
        self._find(vm)["state"] = "paused"

    # same interface as VBoxController
    def list_vms(self, timeout=None):
        with self._lock:
            return [(d["name"], u) for u, d in self.vms.items()]

    def get_state(self, vm):
        return self._find(vm)["state"]

    def get_uuid(self, vm):
        with self._lock:
            for u, d in self.vms.items():
                if vm in (u, d["name"]):
                    return u
        raise VBoxError(f"Could not find a registered machine named '{vm}'")

    def list_snapshots(self, vm):
        return list(self._find(vm)["snapshots"])

    def get_guest_property(self, vm, prop):
        data = self._find(vm)
        for uuid, d in self.vms.items():
            if d is data:
                return self.heartbeats.get((uuid, prop))
        return None

    def base_folder(self, vm):
        self._find(vm)
        return ""

    def get_version(self, timeout=None):
        return "simulated"

    def wait_until_ready(self, vm, timeout=60.0, poll=1.0):
        state = self.get_state(vm)
        if state_is_busy(state):
            raise VBoxError(f"VirtualBox is still busy with this machine (state "
                            f"'{state}') after {timeout:.0f}s. It looks stuck and "
                            f"needs an administrator.")
        return state

    def wait_for_state(self, vm, states, timeout=60.0, poll=0.5, settle=1.0):
        """The simulator changes state instantly, so this always succeeds."""
        wanted = {s.lower() for s in states}
        state = self.get_state(vm)
        if state.lower() not in wanted:
            raise VBoxError(f"The machine is in the state '{state}' and did not reach "
                            f"{' or '.join(sorted(wanted))} within {timeout:.0f}s.")
        return state

    def take_snapshot(self, vm, name, live=False, description=""):
        self._maybe_fail("take_snapshot")
        d = self._find(vm)
        if name in d["snapshots"]:
            raise VBoxError("Snapshot name already exists")
        d["snapshots"].append(name)

    def delete_snapshot(self, vm, name):
        self._maybe_fail("delete_snapshot")
        d = self._find(vm)
        if name not in d["snapshots"]:
            raise VBoxError("Snapshot not found")
        d["snapshots"].remove(name)

    def power_off(self, vm):
        self._maybe_fail("power_off")
        self._find(vm)["state"] = "poweroff"

    def resume_vm(self, vm):
        self._maybe_fail("resume_vm")
        d = self._find(vm)
        if d["state"] != "paused":
            raise VBoxError("Cannot resume a machine that is not paused")
        d["state"] = "running"

    def pause_vm(self, vm):
        self._maybe_fail("pause_vm")
        d = self._find(vm)
        if d["state"] != "running":
            raise VBoxError("Cannot pause a machine that is not running")
        d["state"] = "paused"

    def save_state(self, vm):
        self._maybe_fail("save_state")
        d = self._find(vm)
        if d["state"] not in ("running", "paused"):
            raise VBoxError("Cannot save the state of a machine that is not running")
        d["state"] = "saved"

    def discard_state(self, vm):
        self._maybe_fail("discard_state")
        d = self._find(vm)
        if d["state"] not in ("saved", "aborted-saved"):
            raise VBoxError("Machine has no saved state to discard")
        d["state"] = "poweroff"

    def restore_snapshot(self, vm, name):
        self._maybe_fail("restore_snapshot")
        d = self._find(vm)
        if name not in d["snapshots"]:
            raise VBoxError("Snapshot not found")
        if d["state"] in ("running", "paused", "saved"):
            raise VBoxError("Cannot restore a snapshot while the machine is running")
        d["state"] = "poweroff"

    def start_vm(self, vm):
        self._maybe_fail("start_vm")
        self._find(vm)["state"] = "running"

    def rename_vm(self, vm, new_name):
        self._maybe_fail("rename_vm")
        with self._lock:
            d = self._find(vm)
            if any(o["name"] == new_name for o in self.vms.values()):
                raise VBoxError(f"Machine named '{new_name}' already exists")
            d["name"] = new_name

    def clone_vm(self, source_vm, new_name, linked=True, snapshot=None):
        self._maybe_fail("clone_vm")
        with self._lock:
            source = self._find(source_vm)
            if linked and not (snapshot or source["snapshots"]):
                raise VBoxError("Linked clone can only be created from a snapshot")
            if any(d["name"] == new_name for d in self.vms.values()):
                raise VBoxError(f"Machine named '{new_name}' already exists")
            new_uuid = f"00000000-0000-4000-8000-{len(self.vms) + 1:012d}"
            # A real clone of a suspended machine is suspended as well: it
            # inherits the saved state of the machine it was made from.
            state = "saved" if source["state"] in ("saved", "aborted-saved") else "poweroff"
            self.add_vm(new_name, new_uuid, state=state)
            return new_name, new_uuid

    def export_vm(self, vm, output_path):
        self._maybe_fail("export_vm")
        d = self._find(vm)
        if d["state"] not in ("poweroff", "aborted", "saved", "aborted-saved"):
            raise VBoxError("Cannot export a machine that is running. Save its state first.")
        from pathlib import Path
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("SIMULATED_OVA_BACKUP")

    def import_vm(self, appliance_path, new_name="", base_folder=""):
        self._maybe_fail("import_vm")
        with self._lock:
            name = new_name or f"Imported-VM-{len(self.vms) + 1}"
            if any(d["name"] == name for d in self.vms.values()):
                raise VBoxError(f"Machine named '{name}' already exists")
            new_uuid = f"00000000-0000-4000-8000-{len(self.vms) + 1:012d}"
            self.add_vm(name, new_uuid, state="poweroff")
            return name, new_uuid

    def unregister_and_delete(self, vm):
        self._maybe_fail("unregister_and_delete")
        with self._lock:
            found_u = None
            for u, d in self.vms.items():
                if vm in (u, d["name"]):
                    found_u = u
                    break
            if found_u:
                del self.vms[found_u]

    def default_machine_folder(self):
        return ""

    def list_media(self):
        return []

    def close_medium(self, path, delete=True):
        """The simulator has no registry, so there is nothing to take out of it."""
        return None


def make_vbox(settings):
    if settings.simulate:
        return SimulatedVBox(demo_vms=True)
    return VBoxController(settings.vboxmanage,
                          timeout=getattr(settings, "vbox_timeout", 1800),
                          query_timeout=getattr(settings, "vbox_query_timeout", 60),
                          action_timeout=getattr(settings, "vbox_action_timeout", 180),
                          restore_timeout=getattr(settings, "vbox_restore_timeout", 600))
