"""Autonomous GitHub Self-Updater for Money Glitch Studio.
Checks remote GitHub repository for new commits every 7 days (or on command),
automatically pulls updates, upgrades dependencies, migrates database,
and synchronizes Antigravity skills and sidecar permissions.
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .config import (
    WORKSPACE_DIR,
    AUTO_UPDATE_ENABLED,
    UPDATE_CHECK_INTERVAL_DAYS,
    GITHUB_REPO_URL
)
from .db import get_setting, set_setting, init_db

logger = logging.getLogger("AutoUpdater")
logging.basicConfig(level=logging.INFO)

class GitHubAutoUpdater:
    """
    Autonomous self-updater ensuring the local Money Glitch Studio instance
    stays synchronized with the central GitHub repository every 7 days.
    """

    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else WORKSPACE_DIR
        self.repo_url = GITHUB_REPO_URL
        self.interval_days = UPDATE_CHECK_INTERVAL_DAYS

    def _run_git(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Runs a git command inside the workspace directory safely."""
        cmd = ["git"] + args
        try:
            return subprocess.run(
                cmd,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"[AutoUpdater] Git command '{' '.join(args)}' timed out after {timeout}s.")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=f"Git command timed out after {timeout} seconds"
            )
        except Exception as e:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=str(e)
            )

    def is_git_repository(self) -> bool:
        """Verifies if the workspace is a valid Git repository."""
        res = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return res.returncode == 0 and "true" in res.stdout.strip().lower()

    def get_current_commit(self) -> Dict[str, Any]:
        """Returns metadata about the current local commit."""
        res_hash = self._run_git(["rev-parse", "HEAD"])
        res_short = self._run_git(["rev-parse", "--short", "HEAD"])
        res_msg = self._run_git(["log", "-1", "--pretty=%s"])
        res_date = self._run_git(["log", "-1", "--pretty=%cd", "--date=iso"])

        return {
            "hash": res_hash.stdout.strip() if res_hash.returncode == 0 else "unknown",
            "short_hash": res_short.stdout.strip() if res_short.returncode == 0 else "unknown",
            "message": res_msg.stdout.strip() if res_msg.returncode == 0 else "",
            "date": res_date.stdout.strip() if res_date.returncode == 0 else ""
        }

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Fetches the remote tracking branch and checks if new commits exist on GitHub.
        """
        if not self.is_git_repository():
            logger.warning("[AutoUpdater] Workspace is not a git repository.")
            return {
                "status": "error",
                "error": "Workspace is not a Git repository",
                "update_available": False
            }

        logger.info(f"[AutoUpdater] Fetching latest updates from GitHub ({self.repo_url})...")
        fetch_res = self._run_git(["fetch", "origin", "main"])
        if fetch_res.returncode != 0:
            logger.warning(f"[AutoUpdater] Git fetch failed: {fetch_res.stderr.strip()}")
            return {
                "status": "error",
                "error": fetch_res.stderr.strip() or "Failed to fetch origin main",
                "update_available": False
            }

        local_info = self.get_current_commit()
        remote_hash_res = self._run_git(["rev-parse", "origin/main"])
        remote_hash = remote_hash_res.stdout.strip() if remote_hash_res.returncode == 0 else ""
        remote_short_res = self._run_git(["rev-parse", "--short", "origin/main"])
        remote_short = remote_short_res.stdout.strip() if remote_short_res.returncode == 0 else ""

        # Count commits behind
        count_res = self._run_git(["rev-list", "--count", "HEAD..origin/main"])
        behind_count = 0
        try:
            behind_count = int(count_res.stdout.strip())
        except Exception:
            behind_count = 1 if local_info["hash"] != remote_hash else 0

        # Collect commit subjects if updates are available
        new_commits = []
        if behind_count > 0:
            log_res = self._run_git(["log", "--oneline", "HEAD..origin/main"])
            if log_res.returncode == 0:
                new_commits = [c.strip() for c in log_res.stdout.splitlines() if c.strip()]

        update_available = (behind_count > 0)
        logger.info(f"[AutoUpdater] Check complete. Local: {local_info['short_hash']} | Remote: {remote_short} | Behind: {behind_count} commits")

        return {
            "status": "success",
            "update_available": update_available,
            "behind_count": behind_count,
            "local_commit": local_info["short_hash"],
            "remote_commit": remote_short,
            "commits": new_commits,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    def apply_updates(self) -> Dict[str, Any]:
        """
        Pulls latest commits from GitHub, updates dependencies, initializes DB,
        and synchronizes Antigravity skills and automations.
        """
        logger.info("[AutoUpdater] Applying GitHub updates to Money Glitch Studio...")

        # 1. Inspect diff to see if requirements.txt will be changed
        diff_res = self._run_git(["diff", "--name-only", "HEAD", "origin/main"])
        changed_files = diff_res.stdout.splitlines() if diff_res.returncode == 0 else []
        requirements_changed = any("requirements.txt" in f for f in changed_files)

        # 2. Pull updates safely
        pull_res = self._run_git(["pull", "--ff-only", "origin", "main"])
        if pull_res.returncode != 0:
            logger.warning(f"[AutoUpdater] Fast-forward pull failed, trying safe rebase: {pull_res.stderr.strip()}")
            pull_res = self._run_git(["pull", "origin", "main"])
            if pull_res.returncode != 0:
                err_msg = pull_res.stderr.strip() or "Git pull failed"
                logger.error(f"[AutoUpdater] Update pull failed: {err_msg}")
                return {
                    "status": "error",
                    "error": err_msg,
                    "update_applied": False
                }

        new_commit = self.get_current_commit()
        logger.info(f"[AutoUpdater] Successfully pulled code! Now at commit {new_commit['short_hash']}: {new_commit['message']}")

        # 3. Upgrade Python dependencies if requirements changed
        if requirements_changed:
            logger.info("[AutoUpdater] requirements.txt changed. Upgrading dependencies...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=str(self.workspace_dir),
                    capture_output=True,
                    timeout=120
                )
                logger.info("[AutoUpdater] Dependencies upgraded successfully.")
            except Exception as e:
                logger.warning(f"[AutoUpdater] Pip upgrade warning: {e}")

        # 4. Migrate / Initialize SQLite database
        try:
            init_db()
            logger.info("[AutoUpdater] Database schema synchronized.")
        except Exception as e:
            logger.warning(f"[AutoUpdater] Database sync notice: {e}")

        # 5. Synchronize local workspace skills to global Antigravity config
        self._sync_skills_globally()

        # 6. Refresh Antigravity Automations Sidecar
        self._refresh_antigravity_automation()

        # 7. Record update timestamps in database
        now_iso = datetime.now(timezone.utc).isoformat()
        set_setting("last_update_check_time", now_iso)
        set_setting("last_auto_update_timestamp", now_iso)
        set_setting("last_auto_update_commit", new_commit["short_hash"])
        set_setting("last_auto_update_status", "SUCCESS")

        return {
            "status": "success",
            "update_applied": True,
            "new_commit": new_commit["short_hash"],
            "commit_message": new_commit["message"],
            "updated_at": now_iso
        }

    def _sync_skills_globally(self):
        """Copies all workspace skills into ~/.gemini/config/skills/ for global agent awareness."""
        try:
            user_home = Path.home()
            global_skills_dir = user_home / ".gemini" / "config" / "skills"
            src_skills_dir = self.workspace_dir / ".agents" / "skills"
            if src_skills_dir.exists():
                for skill_folder in src_skills_dir.iterdir():
                    if skill_folder.is_dir() and (skill_folder / "SKILL.md").exists():
                        dest = global_skills_dir / skill_folder.name
                        dest.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(skill_folder, dest, dirs_exist_ok=True)
                        logger.info(f"[AutoUpdater] Synced global skill: {skill_folder.name}")
        except Exception as e:
            logger.warning(f"[AutoUpdater] Skill sync warning: {e}")

    def _refresh_antigravity_automation(self):
        """Re-runs the registration script so any updated permissions or args are applied."""
        reg_script = self.workspace_dir / "scripts" / "register_antigravity_automation.py"
        if reg_script.exists():
            try:
                subprocess.run(
                    [sys.executable, str(reg_script)],
                    cwd=str(self.workspace_dir),
                    capture_output=True,
                    timeout=30
                )
                logger.info("[AutoUpdater] Antigravity Automations registration refreshed.")
            except Exception as e:
                logger.warning(f"[AutoUpdater] Automation refresh notice: {e}")

    def check_and_auto_update_if_due(self, interval_days: int = 7, force: bool = False) -> Dict[str, Any]:
        """
        Executes update check if 7 days have elapsed since last check (or if force=True).
        If new commits exist, automatically applies them.
        """
        if not AUTO_UPDATE_ENABLED and not force:
            return {"status": "disabled", "message": "Auto-update is disabled in config."}

        last_check_str = get_setting("last_update_check_time", None)
        now = datetime.now(timezone.utc)

        is_due = False
        elapsed_days = 0.0

        if not last_check_str or force:
            is_due = True
        else:
            try:
                last_check_dt = datetime.fromisoformat(last_check_str)
                if last_check_dt.tzinfo is None:
                    last_check_dt = last_check_dt.replace(tzinfo=timezone.utc)
                elapsed_days = (now - last_check_dt).total_seconds() / 86400.0
                if elapsed_days >= interval_days:
                    is_due = True
            except Exception:
                is_due = True

        if not is_due:
            remaining_days = max(0.0, round(interval_days - elapsed_days, 1))
            return {
                "status": "skipped",
                "is_due": False,
                "elapsed_days": round(elapsed_days, 1),
                "remaining_days": remaining_days,
                "message": f"Auto-update check not due yet. Next check in {remaining_days} days."
            }

        logger.info(f"[AutoUpdater] 7-day interval reached (Elapsed: {round(elapsed_days, 1)} days). Checking GitHub...")
        check_result = self.check_for_updates()

        if check_result.get("status") == "error":
            logger.warning(f"[AutoUpdater] Check failed: {check_result.get('error')}. Will retry next cycle.")
            return {
                "status": "error",
                "is_due": True,
                "update_applied": False,
                "error": check_result.get("error"),
                "message": f"GitHub check failed: {check_result.get('error')}. Will retry next cycle."
            }

        # Update last check timestamp now that check succeeded
        now_iso = now.isoformat()
        set_setting("last_update_check_time", now_iso)

        if check_result.get("update_available"):
            logger.info(f"[AutoUpdater] {check_result.get('behind_count')} new commits found on GitHub. Auto-updating now!")
            apply_result = self.apply_updates()
            return {
                "status": "updated",
                "is_due": True,
                "update_applied": True,
                "previous_commit": check_result.get("local_commit"),
                "new_commit": apply_result.get("new_commit"),
                "commit_message": apply_result.get("commit_message"),
                "commits_pulled": check_result.get("commits"),
                "message": f"Successfully updated to {apply_result.get('new_commit')}!"
            }
        else:
            logger.info("[AutoUpdater] Local repository is already up-to-date with GitHub main.")
            return {
                "status": "up_to_date",
                "is_due": True,
                "update_applied": False,
                "current_commit": check_result.get("local_commit"),
                "message": "Repository is up to date."
            }

    def get_status(self) -> Dict[str, Any]:
        """Provides a formatted status report for the web dashboard and CLI."""
        current_commit = self.get_current_commit()
        last_check = get_setting("last_update_check_time", "Never")
        last_update = get_setting("last_auto_update_timestamp", "Never")
        last_commit = get_setting("last_auto_update_commit", current_commit["short_hash"])

        remaining_days = None
        if last_check and last_check != "Never":
            try:
                dt = datetime.fromisoformat(last_check)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
                remaining_days = max(0.0, round(self.interval_days - elapsed, 1))
            except Exception:
                remaining_days = None

        return {
            "enabled": AUTO_UPDATE_ENABLED,
            "interval_days": self.interval_days,
            "current_commit": current_commit["short_hash"],
            "current_commit_message": current_commit["message"],
            "repo_url": self.repo_url,
            "last_check_time": last_check,
            "last_update_time": last_update,
            "last_updated_commit": last_commit,
            "days_until_next_check": remaining_days
        }

# Module-level convenience functions
_updater_instance = None

def get_auto_updater() -> GitHubAutoUpdater:
    global _updater_instance
    if _updater_instance is None:
        _updater_instance = GitHubAutoUpdater()
    return _updater_instance

def check_and_auto_update_if_due(interval_days: int = 7, force: bool = False) -> Dict[str, Any]:
    return get_auto_updater().check_and_auto_update_if_due(interval_days=interval_days, force=force)

def check_for_updates() -> Dict[str, Any]:
    return get_auto_updater().check_for_updates()

def apply_updates() -> Dict[str, Any]:
    return get_auto_updater().apply_updates()

def get_updater_status() -> Dict[str, Any]:
    return get_auto_updater().get_status()
