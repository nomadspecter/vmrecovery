"""The only module that talks to VirtualBox.

VBoxController runs real VBoxManage commands. SimulatedVBox has the same
methods but keeps everything in memory, so the system can be demonstrated
and tested on a machine without VirtualBox. Everything else in the project
uses whichever one it is given.
"""
import re
import shutil
import subprocess
import threading


class VBoxError(Exception):
    """A VBoxManage command failed or VirtualBox is not reachable."""


# VirtualBox states that mean "something is changing, do not judge the VM yet".
BUSY_STATES = {"starting", "stopping", "saving", "restoring", "restoringsnapshot",
               "takingsnapshot", "deletingsnapshot", "liveSnapshotting", "livesnapshotting",
               "teleporting", "settingup", "meteringunsupported"}


class VBoxController:
    def __init__(self, vboxmanage: str = "VBoxManage", timeout: int = 600):
        self.exe = shutil.which(vboxmanage) or vboxmanage
        self.timeout = timeout

    # ---- low level -------------------------------------------------------
    def _run(self, *args: str, check: bool = True) -> str:
        try:
            proc = subprocess.run([self.exe, *args], capture_output=True, text=True,
                                  timeout=self.timeout)
        except FileNotFoundError:
            raise VBoxError(f"VBoxManage not found ('{self.exe}'). Is VirtualBox installed?")
        except subprocess.TimeoutExpired:
            raise VBoxError(f"VBoxManage timed out: {' '.join(args[:3])}")
        if check and proc.returncode != 0:
            lines = [line.strip() for line in (proc.stderr or proc.stdout).splitlines() if line.strip()]
            err_line = None
            for l in lines:
                if "error:" in l and "Context:" not in l and "Details:" not in l:
                    err_line = l
                    break
            if not err_line and lines:
                err_line = lines[-1] if not any("error:" in l for l in lines) else lines[0]
            raise VBoxError(err_line or f"VBoxManage exit code {proc.returncode}")
        return proc.stdout

    # ---- queries ---------------------------------------------------------
    def list_vms(self) -> list[tuple[str, str]]:
        """Return [(name, uuid)] for every VM known to VirtualBox."""
        out = self._run("list", "vms")
        return [(m.group(1), m.group(2))
                for m in re.finditer(r'^"(.*)" \{([0-9a-fA-F-]+)\}\s*$', out, re.M)]

    def get_state(self, vm: str) -> str:
        """VirtualBox's own state word: running, poweroff, aborted, paused, ..."""
        out = self._run("showvminfo", vm, "--machinereadable")
        m = re.search(r'^VMState="([^"]+)"', out, re.M)
        if not m:
            raise VBoxError("could not read VMState")
        return m.group(1)

    def list_snapshots(self, vm: str) -> list[str]:
        out = self._run("snapshot", vm, "list", "--machinereadable", check=False)
        return re.findall(r'^SnapshotName(?:-[\d-]+)?="(.*)"$', out, re.M)

    def get_guest_property(self, vm: str, prop: str) -> str | None:
        out = self._run("guestproperty", "get", vm, prop, check=False)
        m = re.search(r'^Value:\s*(.*)$', out, re.M)
        if m:
            return m.group(1).strip()
        return None

    # ---- actions ---------------------------------------------------------
    def take_snapshot(self, vm: str, name: str, live: bool = False, description: str = "") -> None:
        args = ["snapshot", vm, "take", name]
        if description:
            args += ["--description", description]
        if live:
            args.append("--live")
        self._run(*args)

    def delete_snapshot(self, vm: str, name: str) -> None:
        self._run("snapshot", vm, "delete", name)

    def power_off(self, vm: str) -> None:
        self._run("controlvm", vm, "poweroff")

    def restore_snapshot(self, vm: str, name: str) -> None:
        self._run("snapshot", vm, "restore", name)

    def start_vm(self, vm: str) -> None:
        self._run("startvm", vm, "--type", "headless")


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
    def list_vms(self):
        with self._lock:
            return [(d["name"], u) for u, d in self.vms.items()]

    def get_state(self, vm):
        return self._find(vm)["state"]

    def list_snapshots(self, vm):
        return list(self._find(vm)["snapshots"])

    def get_guest_property(self, vm, prop):
        data = self._find(vm)
        for uuid, d in self.vms.items():
            if d is data:
                return self.heartbeats.get((uuid, prop))
        return None

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

    def restore_snapshot(self, vm, name):
        self._maybe_fail("restore_snapshot")
        d = self._find(vm)
        if name not in d["snapshots"]:
            raise VBoxError("Snapshot not found")
        if d["state"] in ("running", "paused"):
            raise VBoxError("Cannot restore a snapshot while the machine is running")
        d["state"] = "poweroff"

    def start_vm(self, vm):
        self._maybe_fail("start_vm")
        self._find(vm)["state"] = "running"


def make_vbox(settings):
    if settings.simulate:
        return SimulatedVBox(demo_vms=True)
    return VBoxController(settings.vboxmanage)
