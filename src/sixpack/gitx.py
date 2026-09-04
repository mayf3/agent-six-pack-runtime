"""Git integration: exact commit/tree verification and isolated worktrees.

Implements the write-isolation contracts:

- every writing role gets its own isolated worktree bound to an exact parent
  commit and an isolated ref (CTR-SIX-003, DEC-SIX-004);
- the active main checkout is never mutated (CTR-GOV1-006);
- head movement without revalidation aborts instead of being adopted
  (``HeadDrift``);
- candidates are verified as full SHAs with their exact trees.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .canonical import require_full_sha
from .errors import HeadDrift, MainCheckoutWrite, WorktreeError


def _run(
    args: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise WorktreeError(
            f"git command failed ({result.returncode}): {' '.join(args)}\n"
            f"stderr: {result.stderr.strip()}"
        )
    return result


def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    """Run ``git`` and return stripped stdout."""
    result = _run(["git", *args], cwd=cwd, check=check)
    return result.stdout.strip()


@dataclass(frozen=True)
class WorktreeInfo:
    path: Path
    branch: str
    base_head: str


class WorktreeManager:
    """Creates and verifies per-role isolated worktrees for one repository."""

    def __init__(self, repo_path: Path, worktree_root: Path) -> None:
        self.repo_path = repo_path.resolve()
        self.worktree_root = worktree_root.resolve()
        self._main_toplevel = Path(
            git("rev-parse", "--show-toplevel", cwd=self.repo_path)
        ).resolve()

    # -- exact verification --------------------------------------------------

    def head(self, ref: str = "HEAD") -> str:
        """Full 40-hex SHA of ``ref``."""
        return require_full_sha(git("rev-parse", ref, cwd=self.repo_path), f"ref {ref}")

    def tree_of(self, head: str) -> str:
        """Exact tree SHA committed at ``head``."""
        require_full_sha(head, "head")
        return require_full_sha(
            git("rev-parse", f"{head}^{{tree}}", cwd=self.repo_path), f"tree of {head}"
        )

    def object_exists(self, sha: str) -> bool:
        return _run(["git", "cat-file", "-t", sha], cwd=self.repo_path, check=False).returncode == 0

    def verify_candidate(self, head: str, tree: str) -> None:
        """Fail unless ``head`` exists and its exact tree is ``tree``."""
        require_full_sha(head, "head")
        require_full_sha(tree, "tree")
        if not self.object_exists(head):
            raise WorktreeError(f"candidate head {head} does not exist in repository")
        actual_tree = self.tree_of(head)
        if actual_tree != tree:
            raise WorktreeError(
                f"candidate tree mismatch for {head}: recorded {tree}, actual {actual_tree}"
            )

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        result = _run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=self.repo_path,
            check=False,
        )
        return result.returncode == 0

    def changed_files(self, base: str, head: str) -> list[str]:
        out = git("diff", "--name-only", base, head, cwd=self.repo_path)
        return [line for line in out.splitlines() if line.strip()]

    # -- main checkout protection ---------------------------------------------

    def ensure_not_main_checkout(self, path: Path) -> None:
        resolved = path.resolve()
        if resolved == self._main_toplevel:
            raise MainCheckoutWrite(
                f"{resolved} is the active main checkout; profile roles must never write it"
            )

    # -- worktree lifecycle ------------------------------------------------------

    def branch_ref(self, task_id: str, role: str) -> str:
        return f"sixpack/{task_id}/{role}"

    def worktree_path(self, task_id: str, role: str) -> Path:
        return self.worktree_root / f"{task_id}__{role}"

    def ensure_worktree(self, task_id: str, role: str, base_head: str) -> WorktreeInfo:
        """Create or verify the role worktree bound to the exact ``base_head``.

        An existing worktree whose HEAD is not exactly ``base_head`` raises
        :class:`HeadDrift`; movement is never silently adopted.
        """
        require_full_sha(base_head, "base_head")
        if not self.object_exists(base_head):
            raise HeadDrift(
                f"stage base {base_head} not found in repository; exact parent must be revalidated"
            )
        branch = self.branch_ref(task_id, role)
        path = self.worktree_path(task_id, role)
        self.ensure_not_main_checkout(path)
        if path.exists():
            current = git("rev-parse", "HEAD", cwd=path)
            if current != base_head:
                raise HeadDrift(
                    f"worktree {path} HEAD {current} != expected base {base_head}; "
                    "head drift must be revalidated before proceeding"
                )
            return WorktreeInfo(path=path, branch=branch, base_head=base_head)
        self.worktree_root.mkdir(parents=True, exist_ok=True)
        branch_result = _run(
            ["git", "rev-parse", "--verify", branch], cwd=self.repo_path, check=False
        )
        if branch_result.returncode == 0:
            git("worktree", "add", str(path), branch, cwd=self.repo_path)
        else:
            git("worktree", "add", "-b", branch, str(path), base_head, cwd=self.repo_path)
        current = git("rev-parse", "HEAD", cwd=path)
        if current != base_head:
            raise HeadDrift(
                f"fresh worktree {path} sits at {current}, expected {base_head}"
            )
        return WorktreeInfo(path=path, branch=branch, base_head=base_head)

    def commit_all(self, worktree: Path, message: str) -> tuple[str, str]:
        """Stage every change in the worktree and commit; return (head, tree)."""
        self.ensure_not_main_checkout(worktree)
        status = git("status", "--porcelain", cwd=worktree)
        if not status:
            raise WorktreeError("no changes to commit; a stage must produce its candidate")
        git("add", "-A", cwd=worktree)
        git("commit", "-m", message, cwd=worktree)
        head = require_full_sha(git("rev-parse", "HEAD", cwd=worktree), "committed head")
        tree = self.tree_of(head)
        return head, tree

    def fast_forward_ref(self, task_id: str, role: str, target_head: str) -> bool:
        """Merge-only state convergence: fast-forward a role ref to ``target``.

        Returns False when the role ref is not an ancestor (divergent role
        state must be resolved by replay/correction, never a silent merge).
        When the role worktree exists locally its index and tree are moved
        together with the branch so the surface stays consistent.
        """
        require_full_sha(target_head, "target_head")
        branch = self.branch_ref(task_id, role)
        result = _run(
            ["git", "rev-parse", "--verify", branch], cwd=self.repo_path, check=False
        )
        if result.returncode != 0:
            git("branch", branch, target_head, cwd=self.repo_path)
            return True
        current = result.stdout.strip()
        if current == target_head:
            return True
        if not self.is_ancestor(current, target_head):
            return False
        worktree = self.worktree_path(task_id, role)
        if worktree.exists():
            git("reset", "--hard", target_head, cwd=worktree)
        else:
            git("branch", "-f", branch, target_head, cwd=self.repo_path)
        return True

    def prune_worktree(self, task_id: str, role: str) -> None:
        path = self.worktree_path(task_id, role)
        if path.exists():
            _run(
                ["git", "worktree", "remove", "--force", str(path)],
                cwd=self.repo_path, check=False,
            )
        _run(["git", "worktree", "prune"], cwd=self.repo_path, check=False)
