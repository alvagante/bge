#!/usr/bin/env python3
"""Process the next BGE episode's missing geek portraits.

Run with PyYAML and cwebp installed. New portraits also need an authenticated
Codex CLI with image generation, yt-dlp, FFmpeg, and ClamAV with signatures.
"""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile, TemporaryDirectory

import yaml


IMAGES = Path("assets/images/geeks")
PROVENANCE = IMAGES / "provenance"
MODEL = "gpt-6.1-terra"
DEFAULT_HOST = "Alessandro Franceschi"
ADAM = "Adam Jacob"
RESULT_FIELDS = (
    "status", "source_episode_number", "video_url", "timestamp",
    "identity_evidence", "generation_prompt", "reason",
)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_file(path, content, *, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as staged:
        temporary = Path(staged.name)
        try:
            staged.write(content)
            staged.close()
            temporary.chmod(0o644)
            if replace:
                temporary.replace(path)
            else:
                try:
                    os.link(temporary, path)
                except FileExistsError:
                    pass
        finally:
            temporary.unlink(missing_ok=True)


def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---[ \t]*\n(.*?)^---[ \t]*(?:\n|\Z)", text, re.M | re.S)
    if match:
        fields = yaml.safe_load(match[1])
        if isinstance(fields, dict):
            return fields
    raise ValueError(f"{path}: missing or invalid frontmatter")


def video_url(episode):
    video_id = episode.get("youtube")
    if isinstance(video_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return f"https://www.youtube.com/watch?v={video_id}"
    return ""


def command_log(command, cwd, reason, result):
    logfile = Path.home() / ".agents/logs/bge.jsonl"
    logfile.parent.mkdir(parents=True, exist_ok=True)
    for key, value in os.environ.items():
        if value and re.search(r"KEY|TOKEN|SECRET|PASSWORD", key, re.I):
            command = command.replace(value, "***")
    entry = dict(ts=now(), agent="codex", actor="agent", cwd=str(cwd),
                 cmd=command, reason=reason, result=result)
    with logfile.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run(args, scratch, reason, *, timeout=120, prompt=None):
    result = "fail"
    try:
        process = subprocess.run(args, cwd=scratch, input=prompt, text=True,
                                 stdout=subprocess.PIPE, check=False, timeout=timeout)
        result = "ok" if process.returncode == 0 else "fail"
    finally:
        command_log(shlex.join(args), scratch, reason, result)
    return process


def encode(source, target, side, quality, scratch):
    encoded = scratch / f"{side}.webp"
    result = run(["cwebp", "-quiet", "-q", str(quality), "-m", "6", "-resize",
                  str(side), str(side), str(source.resolve()), "-o", encoded.name],
                 scratch, f"Encode the {side} pixel WebP.")
    result.check_returncode()
    return target, encoded.read_bytes()


def generate(name, geek_path, episode_path, sources, style, scratch):
    shutil.copyfile(geek_path, scratch / "geek.md")
    shutil.copyfile(episode_path, scratch / "episode.md")
    if style:
        shutil.copyfile(style, scratch / f"style{style.suffix}")
    job = dict(name=name, episode_number=episode_path.stem, recordings=sources,
               style_reference=f"style{style.suffix}" if style else None)
    (scratch / "job.json").write_text(json_text(job), encoding="utf-8")
    schema = dict(type="object", required=RESULT_FIELDS, additionalProperties=False,
                  properties={key: {"type": "string"} for key in RESULT_FIELDS})
    schema["properties"]["status"]["enum"] = ["accepted", "identity_blocked", "retry"]
    (scratch / "schema.json").write_text(json_text(schema), encoding="utf-8")

    prompt = Path("bin/prompts/geek_portrait.md").read_text(encoding="utf-8")
    process = run([
        "codex", "exec", "--model", MODEL, "--enable", "image_generation",
        "--sandbox", "workspace-write", "--skip-git-repo-check", "--ephemeral",
        "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=true",
        "-c", 'web_search="live"', "--json", "--output-schema", "schema.json",
        "--output-last-message", "result.json", "-",
    ], scratch, "Verify identity and generate a portrait with Terra.", timeout=1800, prompt=prompt)
    for line in process.stdout.splitlines():
        event = json.loads(line)
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") == "command_execution":
            outcome = "ok" if item.get("exit_code") == 0 else "fail"
            command_log(item["command"], scratch, "Run a portrait worker command.", outcome)
    process.check_returncode()

    result = read_json(scratch / "result.json", {})
    if (not isinstance(result, dict) or set(result) != set(RESULT_FIELDS)
            or not all(isinstance(value, str) for value in result.values())
            or result["status"] not in schema["properties"]["status"]["enum"]):
        raise ValueError("Portrait worker returned an invalid result")
    if result["status"] != "accepted":
        if not result["reason"].strip():
            raise ValueError("Portrait worker did not explain the blocker")
        return result
    if (not result["video_url"].startswith("https://")
            or not all(result[key].strip() for key in ("timestamp", "identity_evidence", "generation_prompt"))
            or (result["source_episode_number"]
                and sources.get(result["source_episode_number"]) != result["video_url"])):
        raise ValueError("Portrait worker did not provide verifiable source details")

    candidate = scratch / "candidate.png"
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError("Portrait worker did not save the accepted image")
    dimensions = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                      "-show_entries", "stream=width,height", "-of", "csv=p=0",
                      candidate.name], scratch, "Check the generated portrait dimensions.")
    dimensions.check_returncode()
    width, height = (int(n) for n in dimensions.stdout.strip().split(","))
    if width != height or width < 512:
        raise ValueError("Generated portrait must be square and at least 512 pixels")
    return result


def process_geek(name, geek_path, episode_path, sources, style, known_blockers):
    stem = geek_path.stem
    profile = IMAGES / "profile" / f"{stem}.webp"
    icon = IMAGES / "icons" / f"{stem}.webp"
    if profile.exists() and icon.exists():
        return "existing", None

    legacy = next((p for p in (profile, IMAGES / f"{stem}.png",
                               IMAGES / "profile" / f"{stem}.png") if p.is_file()), None)
    if name == ADAM and not legacy:
        legacy = style
    if not legacy and (icon.exists() or name == ADAM):
        reason = "Only the icon exists" if icon.exists() else "Approved Adam Jacob portrait unavailable"
        return "record", reason

    fingerprint = hashlib.sha256(
        geek_path.read_bytes() + json_text(dict(sorted(sources.items()))).encode()
    ).hexdigest()
    if not legacy:
        for blocker in reversed(known_blockers):
            same_legacy_source = (not blocker.get("fingerprint")
                                  and str(blocker.get("episode_number")) == episode_path.stem
                                  and blocker.get("video_url") == sources.get(episode_path.stem))
            if (blocker.get("geek_record") == geek_path.as_posix()
                    and blocker.get("type") == "identity_attribution"
                    and (blocker.get("fingerprint") == fingerprint or same_legacy_source)):
                return "blocked", blocker["reason"]

    with TemporaryDirectory(prefix="bge-portrait-", dir="/tmp") as directory:
        scratch = Path(directory)
        if legacy:
            source = legacy
            metadata = dict(video_url=sources.get(episode_path.stem),
                            timestamp=None, identity_evidence=None, generation_prompt=None,
                            source_image=source.as_posix(),
                            method=("Converted the approved Adam Jacob portrait without regeneration."
                                    if name == ADAM else "Converted an existing portrait without regeneration."))
            if name == ADAM:
                metadata["identity_evidence"] = (
                    "User-approved Adam Jacob portrait. Original frame, timestamp and prompt unavailable."
                )
        else:
            tools = [tool for tool in ("codex", "yt-dlp", "ffmpeg", "ffprobe", "clamscan", "cwebp")
                     if not shutil.which(tool)]
            if tools:
                raise ValueError(f"Missing runtime commands: {', '.join(tools)}")
            result = generate(name, geek_path, episode_path, sources, style, scratch)
            if result["status"] == "retry":
                return "retry", result["reason"]
            if result["status"] == "identity_blocked":
                return "identity_attribution", (result["reason"], fingerprint)
            source = scratch / "candidate.png"
            metadata = {key: value for key, value in result.items() if key not in ("status", "reason")}
            if metadata["source_episode_number"] in ("", episode_path.stem):
                del metadata["source_episode_number"]
            metadata.update(method="Built-in image generation through Codex",
                            model=MODEL, style_reference=style.as_posix() if style else None)

        outputs = [encode(source, path, side, quality, scratch)
                   for path, side, quality in ((profile, 512, 85), (icon, 128, 82))
                   if not path.exists()]
        metadata.update(geek_record=geek_path.as_posix(), episode_number=episode_path.stem,
                        output_filename=profile.as_posix(),
                        output_filenames=[profile.as_posix(), icon.as_posix()])
        save_file(PROVENANCE / f"{stem}.json", json_text(metadata).encode())
        for path, content in outputs:
            save_file(path, content)
    return "added", None


def process_episode():
    episode_paths = {path.stem: path for path in Path("_episodes").glob("*.md")
                     if re.fullmatch(r"[0-9]+", path.stem)}
    progress_path = PROVENANCE / "episode-progress.json"
    blockers_path = PROVENANCE / "blockers.json"
    progress = read_json(progress_path, {"version": 1, "episodes": {}})
    blockers = read_json(blockers_path, {"version": 1, "blockers": []})
    episodes = progress["episodes"]
    order = sorted(episode_paths, key=int)
    number = next((n for n in order if episodes.get(n, {}).get("status")
                   not in ("processed", "retry")), None)
    if number is None:
        number = min((n for n in order if episodes[n]["status"] == "retry"),
                     key=lambda n: (episodes[n]["processed_at"], int(n)), default=None)
    if number is None:
        print("No unchecked episodes or portrait retries.")
        return 0

    episode_path = episode_paths[number]
    record = read_frontmatter(episode_path)
    url = video_url(record)
    added, skipped, issues, blocked, retry = [], [], [], [], []
    guests = record.get("guests", [])
    if not isinstance(guests, list):
        issues.append("guests: expected a list")
        guests = []
    if not url:
        issues.append("youtube: missing or invalid video ID")

    geeks = {}
    for path in Path("_geeks").glob("*.md"):
        try:
            data = read_frontmatter(path)
        except (ValueError, yaml.YAMLError):
            continue
        if isinstance(data.get("nome"), str):
            geeks.setdefault(data["nome"], []).append((path, data))

    style = next((p for p in (PROVENANCE / "adam-jacob-screenprint.png",
                              IMAGES / f"{ADAM}.png", IMAGES / "profile" / f"{ADAM}.webp")
                  if p.is_file()), None)
    names = [record.get("host", DEFAULT_HOST), *guests]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        issues.append("host or guests: invalid participant name")
    for name in dict.fromkeys(name for name in names if isinstance(name, str) and name.strip()):
        matches = geeks.get(name, [])
        if len(matches) != 1:
            issues.append(f"{name}: {'ambiguous' if matches else 'missing'} exact geek record")
            continue
        path, data = matches[0]
        linked = data.get("episodi")
        linked = {str(n) for n in linked} if isinstance(linked, list) else set()
        if number not in linked:
            issues.append(f"{name}: geek record does not list episode {number}")
            skipped_if_complete = all((IMAGES / kind / f"{path.stem}.webp").is_file()
                                      for kind in ("profile", "icons"))
            if skipped_if_complete:
                skipped.append(name)
            continue

        sources = {number: url} if url else {}
        for other in sorted(linked & episode_paths.keys(), key=int):
            if other != number:
                try:
                    linked_url = video_url(read_frontmatter(episode_paths[other]))
                except (ValueError, yaml.YAMLError):
                    continue
                if linked_url:
                    sources[other] = linked_url
        try:
            status, detail = process_geek(name, path, episode_path, sources, style, blockers["blockers"])
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            status, detail = "retry", str(exc)

        if status == "identity_attribution":
            reason, fingerprint = detail
            blockers["blockers"].append(dict(type=status, geek_record=path.as_posix(),
                                             episode_number=number, video_url=url, reason=reason,
                                             fingerprint=fingerprint, checked_at=now()))
            save_file(blockers_path, json_text(blockers).encode(), replace=True)
            blocked.append(f"{name}: {reason}")
        elif status == "added":
            added.append(name)
        elif status == "existing":
            skipped.append(name)
        else:
            bucket = {"record": issues, "retry": retry, "blocked": blocked}[status]
            bucket.append(f"{name}: {detail}")

    previous = episodes.get(number, {})
    all_added = list(dict.fromkeys([*previous.get("portraits_added", []), *added]))
    episodes[number] = dict(previous, status="retry" if retry else "processed",
                            video_url=url, portraits_added=all_added,
                            existing_portraits_skipped=[name for name in skipped if name not in all_added],
                            record_inconsistencies=issues, blockers=blocked, retry=retry,
                            processed_at=now())
    save_file(progress_path, json_text(progress).encode(), replace=True)
    print(f"Episode {number}")
    for label, items in (("Added", added), ("Existing", skipped), ("Record issues", issues),
                         ("Identity blockers", blocked), ("Retry", retry)):
        print(f"  {label}: {'; '.join(items) or 'none'}")
    return int(bool(retry))


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    lock_dir = Path.home() / ".cache/bge"
    lock_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(os.fsencode(root)).hexdigest()[:16]
    with (lock_dir / f"geek-portraits-{key}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return process_episode()


if __name__ == "__main__":
    sys.exit(main())
