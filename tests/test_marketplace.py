"""Tests run against real git repositories in a temp directory: XBERG_MARKETPLACE_REMOTE_BASE points validate.py at them."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import marketplace as mp  # noqa: E402
import staleness  # noqa: E402
import validate  # noqa: E402

spec = importlib.util.spec_from_file_location("bump_ref", SCRIPTS / "bump-ref.py")
bump_ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bump_ref)

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "tag.gpgsign=false", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        env=GIT_ENV,
    )


def make_repo(base, repo, name, tags, plugin_dir="plugin"):
    path = Path(base) / repo
    manifest = path / plugin_dir / ".claude-plugin"
    manifest.mkdir(parents=True)
    (manifest / "plugin.json").write_text(json.dumps({"name": name}))
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "init")
    for tag in tags:
        git(path, "tag", tag)


def write_marketplaces(root, plugins, overrides=None):
    """plugins: list of (name, repo, path, ref); overrides: {format key: modifier(data)}."""
    for fmt in mp.FORMATS:
        entries = []
        for name, repo, path, ref in plugins:
            entry = {"name": name, "source": mp.make_source(fmt, repo, path, ref)}
            if fmt.key == "codex":
                entry["policy"] = {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
                entry["category"] = "x"
            entries.append(entry)
        data = {"name": "test", "owner": {"name": "o"}, "plugins": entries}
        if fmt.key == "codex":
            data = {"name": "test", "interface": {"displayName": "T"}, "plugins": entries}
        if overrides and fmt.key in overrides:
            overrides[fmt.key](data)
        target = Path(root) / fmt.file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(mp.dump(data))


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.remotes = Path(self._tmp.name) / "remotes"
        self.root = Path(self._tmp.name) / "root"
        make_repo(self.remotes, "acme/alpha", "alpha", ["v1.0.0", "v1.1.0"])
        make_repo(self.remotes, "acme/beta", "beta", ["v2.0.0"])
        os.environ["XBERG_MARKETPLACE_REMOTE_BASE"] = f"file://{self.remotes}"
        self.addCleanup(os.environ.pop, "XBERG_MARKETPLACE_REMOTE_BASE", None)
        self.good = [("alpha", "acme/alpha", "plugin", "v1.0.0"), ("beta", "acme/beta", "plugin", "v2.0.0")]


class ValidateTests(Base):
    def test_valid_marketplaces_pass(self):
        write_marketplaces(self.root, self.good)
        self.assertEqual(validate.validate(self.root), [])

    def test_unknown_tag_fails(self):
        write_marketplaces(self.root, [("alpha", "acme/alpha", "plugin", "v9.9.9")])
        errs = validate.validate(self.root)
        self.assertTrue(any("ref 'v9.9.9' is not an existing tag" in e for e in errs), errs)

    def test_branch_name_is_not_accepted_as_a_tag(self):
        write_marketplaces(self.root, [("alpha", "acme/alpha", "plugin", "main")])
        errs = validate.validate(self.root)
        self.assertTrue(any("not an existing tag" in e for e in errs), errs)

    def test_missing_path_fails(self):
        write_marketplaces(self.root, [("alpha", "acme/alpha", "nope", "v1.0.0")])
        errs = validate.validate(self.root)
        self.assertTrue(any("path 'nope' does not exist" in e for e in errs), errs)

    def test_missing_repo_fails(self):
        write_marketplaces(self.root, [("ghost", "acme/ghost", "plugin", "v1.0.0")])
        errs = validate.validate(self.root)
        self.assertTrue(any("cannot list tags" in e for e in errs), errs)

    def test_entry_name_must_match_plugin_json(self):
        write_marketplaces(self.root, [("renamed", "acme/alpha", "plugin", "v1.0.0")])
        errs = validate.validate(self.root)
        self.assertTrue(any("differs from plugin.json name 'alpha'" in e for e in errs), errs)

    def test_mismatched_refs_across_files_fail(self):
        write_marketplaces(
            self.root,
            self.good,
            {"factory": lambda d: d["plugins"][0]["source"].__setitem__("ref", "v1.1.0")},
        )
        errs = validate.validate(self.root, offline=True)
        self.assertTrue(any(e.startswith("drift:") and "'alpha'" in e for e in errs), errs)

    def test_missing_plugin_in_one_file_fails(self):
        write_marketplaces(self.root, self.good, {"copilot": lambda d: d["plugins"].pop()})
        errs = validate.validate(self.root, offline=True)
        self.assertTrue(any("'beta' is in claude but not in copilot" in e for e in errs), errs)

    def test_version_in_entry_fails(self):
        write_marketplaces(self.root, self.good, {"claude": lambda d: d["plugins"][0].update(version="1.0.0")})
        errs = validate.validate(self.root, offline=True)
        self.assertTrue(any("version must not be set" in e for e in errs), errs)

    def test_invalid_json_fails(self):
        write_marketplaces(self.root, self.good)
        (self.root / mp.FORMATS[1].file).write_text("{not json")
        errs = validate.validate(self.root, offline=True)
        self.assertTrue(any("invalid JSON" in e for e in errs), errs)

    def test_missing_file_fails(self):
        write_marketplaces(self.root, self.good)
        (self.root / mp.FORMATS[3].file).unlink()
        errs = validate.validate(self.root, offline=True)
        self.assertTrue(any("file is missing" in e for e in errs), errs)

    def test_offline_skips_remote_checks(self):
        write_marketplaces(self.root, [("alpha", "acme/alpha", "plugin", "v9.9.9")])
        self.assertEqual(validate.validate(self.root, offline=True), [])


class BumpTests(Base):
    def test_bump_rewrites_every_file_and_result_validates(self):
        write_marketplaces(self.root, self.good)
        changed = bump_ref.bump("alpha", "v1.1.0", self.root)
        self.assertEqual(sorted(changed), sorted(f.file for f in mp.FORMATS))
        for fmt in mp.FORMATS:
            refs = {e.name: e.ref for e in mp.entries(fmt, mp.load(fmt, self.root))}
            self.assertEqual(refs, {"alpha": "v1.1.0", "beta": "v2.0.0"})
        self.assertEqual(validate.validate(self.root), [])

    def test_bump_accepts_owner_repo(self):
        write_marketplaces(self.root, self.good)
        bump_ref.bump("acme/alpha", "v1.1.0", self.root)
        self.assertEqual(mp.entries(mp.FORMATS[0], mp.load(mp.FORMATS[0], self.root))[0].ref, "v1.1.0")

    def test_bump_unknown_target_changes_nothing(self):
        write_marketplaces(self.root, self.good)
        before = {f.file: (self.root / f.file).read_text() for f in mp.FORMATS}
        with self.assertRaises(mp.MarketplaceError):
            bump_ref.bump("zeta", "v1.0.0", self.root)
        self.assertEqual(before, {f.file: (self.root / f.file).read_text() for f in mp.FORMATS})

    def test_bump_to_current_ref_is_a_noop(self):
        write_marketplaces(self.root, self.good)
        self.assertEqual(bump_ref.bump("alpha", "v1.0.0", self.root), [])


class StalenessTests(Base):
    def test_behind_is_reported(self):
        write_marketplaces(self.root, self.good)
        latest = {"acme/alpha": "v1.1.0", "acme/beta": "v2.0.0"}
        stale = staleness.find_stale(self.root, latest.__getitem__)
        self.assertEqual(stale, [{"name": "alpha", "repo": "acme/alpha", "pinned": "v1.0.0", "latest": "v1.1.0"}])
        self.assertIn("`v1.1.0`", staleness.report(stale))

    def test_up_to_date_is_empty(self):
        write_marketplaces(self.root, self.good)
        latest = {"acme/alpha": "v1.0.0", "acme/beta": "v2.0.0"}
        self.assertEqual(staleness.find_stale(self.root, latest.__getitem__), [])


if __name__ == "__main__":
    unittest.main()
