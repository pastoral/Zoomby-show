"""Flow image batch runner: one job at a time, profile failover, "unusual activity" rule.

Usage: python run_batch.py [max_jobs]     (jobs come from batch_manifest.J: (out_rel, refs_rel, prompt))

Profiles come from a private JSON file, never from this repo:
  $GFLOW_PROFILES, else ~/.gflow/profiles.json   (format: see profiles.example.json)
Only entries with "enabled": true are used, in file order.

Unusual-activity rule:
 1. A profile raises "unusual activity" -> switch to the next profile.
 2. If the new profile also raises it within 3 min of that switch -> cool down 20 min.
 3. After the cool-down, resume on the next unflagged profile.
 4. A flagged profile rests 3 h from its flag (kept in flags.json across restarts).
 5. Every profile flagged/resting -> stop (exit 2) and report.
"""
import json, os, re, subprocess, sys, time, tempfile
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # the video folder
sys.path.insert(0, str(HERE))
import importlib
J = importlib.import_module(os.environ.get("MANIFEST", "batch_manifest")).J


def load_profiles():
    path = Path(os.environ.get("GFLOW_PROFILES") or Path.home() / ".gflow" / "profiles.json")
    if not path.exists():
        sys.exit(f"No profiles file at {path}. Copy profiles.example.json there and fill in your own gflow profiles.")
    data = json.loads(path.read_text(encoding="utf-8"))
    profiles = [(p["profile"], p["project"]) for p in data["profiles"] if p.get("enabled", True)]
    if not profiles:
        sys.exit(f"{path} has no enabled profiles.")
    return profiles


PROFILES = load_profiles()
LOG = HERE / "batch_log.txt"
FLAGS = HERE / "flags.json"
GAP = 18
REST_S = 3 * 3600
SWITCH_WINDOW_S = 180
COOLDOWN_S = 1200
FLAG_RE = re.compile(r"UNUSUAL_ACTIVITY|unusual activity|WAF|\b403\b")


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class FlagState:
    """Tracks flags per profile and the time of the last flag-driven switch."""
    def __init__(self, path=FLAGS, clock=time.time, sleeper=time.sleep):
        self.path, self.clock, self.sleep = path, clock, sleeper
        self.flags = json.loads(path.read_text()) if path and path.exists() else {}
        self.last_switch = None  # time of the last flag-driven switch

    def save(self):
        if self.path:
            self.path.write_text(json.dumps(self.flags, indent=1))

    def resting(self, profile):
        t = self.flags.get(profile)
        return t is not None and self.clock() - t < REST_S

    def available(self):
        return [p for p in PROFILES if not self.resting(p[0])]

    def on_flag(self, profile):
        """Record a flag; returns True if a cool-down was taken."""
        now = self.clock()
        self.flags[profile] = now
        self.save()
        cooled = False
        if self.last_switch is not None and now - self.last_switch < SWITCH_WINDOW_S:
            log(f"FLAG on {profile} within 3 min of the last switch: cooling down 20 min")
            self.sleep(COOLDOWN_S)
            cooled = True
        else:
            log(f"FLAG on {profile}: resting it 3 h, switching to the next profile")
        self.last_switch = self.clock()
        return cooled


def run(prompt, refs, profile, project, aspect):
    tmp = Path(tempfile.mkdtemp(prefix="gf_"))
    cmd = ["gflow", "image", "gen", prompt, "--profile", profile, "--project", project,
           "--aspect", aspect, "--out", str(tmp), "--json"]
    for r in refs:
        cmd += ["--ref", r]
    env = dict(os.environ, GFLOW_CLI_UPDATE_CHECK="0")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=600)
    except subprocess.TimeoutExpired:
        return [], "TIMEOUT after 600 s"
    files = sorted(tmp.glob("*.png")) + sorted(tmp.glob("*.jpg")) + sorted(tmp.glob("*.webp"))
    return files, (p.stdout[-1500:] + " | " + p.stderr[-800:]).replace("\n", " ")


def missing():
    return [o for o, _, _ in J if not (ROOT / o).exists()]


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
    st = FlagState()
    resting = [p for p, _ in PROFILES if st.resting(p)]
    if resting:
        log(f"START: resting from earlier flags: {resting}")
    done = 0
    for out, refs, prompt in J:
        dest = ROOT / out
        if dest.exists():
            continue
        if done >= limit:
            break
        dest.parent.mkdir(parents=True, exist_ok=True)
        ok_refs = [str(ROOT / r) for r in refs if (ROOT / r).exists()]
        if len(ok_refs) < len(refs):
            log(f"WARN {out}: missing refs {[r for r in refs if not (ROOT / r).exists()]}")
        aspect = "1:1" if "/props/" in out else "9:16"
        got, tried = False, set()
        while not got:
            avail = [p for p in st.available() if p[0] not in tried]
            if not st.available():
                log(f"STOPPED: all profiles flagged/resting. Missing {len(missing())}: {missing()}")
                sys.exit(2)
            if not avail:
                break  # every available profile failed this job for non-flag reasons
            profile, project = avail[0]
            tried.add(profile)
            for attempt in (1, 2):
                files, tail = run(prompt, ok_refs, profile, project, aspect)
                if files:
                    Image.open(files[0]).convert("RGB").save(dest, quality=93)
                    log(f"OK   {out} [{profile}]")
                    got = True
                    break
                log(f"FAIL {out} [{profile} try {attempt}] {tail[-500:]}")
                time.sleep(GAP)
                if FLAG_RE.search(tail):
                    st.on_flag(profile)
                    tried.discard(profile)  # it is resting now; available() drops it
                    break
        if not got:
            log(f"GAVE UP {out}: failed on every available profile")
        done += 1
        time.sleep(GAP)
    m = missing()
    log(f"BATCH END: {len(J) - len(m)}/{len(J)} present; missing: {m}")


if __name__ == "__main__":
    main()
