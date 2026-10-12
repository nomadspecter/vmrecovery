# Testing with real VirtualBox (what to run and screenshot for Chapter Three)

The automated tests use a stand-in for VirtualBox. These steps prove the system works with real VMs.
**Use throwaway VMs only.**

## 0. Check VirtualBox from the terminal

```bash
VBoxManage --version
VBoxManage list vms                  # your VM names and UUIDs appear here
VBoxManage list runningvms
```
Run the system as the same user that created those VMs.

## 1. Start the system

```bash
python manage.py create-user admin admin
python run.py
```
Open http://127.0.0.1:5000, log in, and open **Virtual Machines**. Your real VMs should be in the dropdown.
Register two test VMs with an interval of 1 minute and keep 3 snapshots. **Screenshot: the registry page.**

## 2. Test checklist

| # | Test | How | Expected result | Screenshot |
|---|---|---|---|---|
| 1 | Scheduled snapshot | start a registered VM, wait 1 to 2 minutes | `VBoxManage snapshot <vm> list` shows `auto-...`; dashboard shows a last-snapshot time | dashboard + terminal |
| 2 | Retention | wait until more than 3 snapshots would exist | only 3 remain in VirtualBox and in the Snapshots page | snapshots page |
| 3 | Pre-session snapshot | click **Start session** for the VM's class group | a `pre-session-...` snapshot appears | dashboard + event log |
| 4 | Manual restore | change something inside the VM, then **Restore** an older snapshot | VM restarts without that change | snapshots page + event log |
| 5 | Crash recovery | kill the VM process (below), wait 1 to 2 minutes | status Crashed, then Running again; event log shows *crash detected* and *restore success* | dashboard (before/after) + event log |
| 6 | Frozen (paused) | `VBoxManage controlvm <vm> pause`, wait | detected as frozen, restored and running | event log |
| 7 | Powered off is not a crash | `VBoxManage controlvm <vm> poweroff` | stays *Powered off*, no restore | dashboard |
| 8 | Restore failure | delete the VM's snapshots in VirtualBox, then crash it | *no usable snapshot* alert on the dashboard | dashboard |
| 9 | Trainer role | log in as trainer, request a restore | admin dashboard shows the request | both dashboards |
| 10 | Reports | open **Reports** | counts match the event log | reports page |

**Simulating a crash (test 5):**
```bash
pgrep -af "VirtualBoxVM.*<your VM name>"     # find the process
pkill -9 -f "VirtualBoxVM.*<your VM name>"   # the VM goes to the 'aborted' state
```

## 3. Optional: catching a hung guest (heartbeat)

VirtualBox cannot tell that the OS *inside* a VM has hung. To detect that, run this inside the guest
(needs VirtualBox Guest Additions), for example every 15 seconds from a systemd timer or cron:
```bash
VBoxControl guestproperty set /Lab/Heartbeat "$(date +%s)"
```
Then enter `/Lab/Heartbeat` as the *Heartbeat guest property* when registering the VM. If the value stops
updating for 90 seconds (`VMR_HEARTBEAT_TIMEOUT`) the VM counts as frozen. The host and guest clocks must agree.

## 4. If something differs from the expected result

Copy the terminal output from `python run.py` (it logs every cycle) and the matching rows from the **Event Log** page.
The most likely differences are the `VBoxManage` output format on your VirtualBox version and VM-specific
settings (snapshot of a running VM with a lot of RAM is slow, so allow time).
