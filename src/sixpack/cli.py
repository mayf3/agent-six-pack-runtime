"""``sixpack`` command line interface.

Commands:
- ``init``       create a runtime workspace (ledger, queues, audit store)
- ``task``       create a task with its PREFLIGHT/profile record
- ``run``        admit + drive one task through the six stations
- ``resume``     crash recovery + deterministic tick
- ``status``     show tasks, workflows, queues, window phase
- ``verify``     run the terminal impact-and-coverage verifier
- ``host``       registry/scan/quiesce/recover control-plane commands

Cron and timers belong here (control plane only); the six stations are
woken by handoff completion, never by polling.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import AuditGate
from .controller import HostController, RegistryEntry
from .errors import SixPackError
from .ledger import Ledger, PreflightRecord, TaskRecord
from .model import Role
from .queue import QueueStore
from .roles import load_role_catalog, role_catalog_digest
from .runner import AgentAdapter, FakeAgentAdapter, ProcessAdapter, RoleRunner
from .verifier import TerminalVerifier


def _build_runtime(
    workspace: Path, provider: str = "fake"
) -> tuple[Ledger, QueueStore, RoleRunner, HostController]:
    root = workspace / "state"
    ledger = Ledger(root)
    queues = QueueStore(root / "queues")
    audit_gate = AuditGate(root / "audit", queues)
    adapter: AgentAdapter
    if provider == "fake":
        adapter = FakeAgentAdapter()
    else:
        adapter = ProcessAdapter(command_template=provider.split(" "))
    runner = RoleRunner(ledger, queues, audit_gate, {}, adapter)
    host_json = workspace / "host.json"
    if host_json.exists():
        overrides = json.loads(host_json.read_text(encoding="utf-8"))
        if overrides.get("worktree_root"):
            runner.default_worktree_root = (workspace / overrides["worktree_root"]).resolve()
    controller = HostController(workspace, ledger, queues, runner)
    return ledger, queues, runner, controller


def cmd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    _build_runtime(workspace)
    load_role_catalog()  # fail closed on invalid role definitions
    manifest = {
        "role_catalog_digest": role_catalog_digest(),
        "accepted_authority": {
            "AGENT_DEVELOPMENT_GOVERNANCE_V1": "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8",
            "AGENT_OPERATIONAL_LAYER_V1": "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8",
            "AGENT_SIX_PACK_DELIVERY_PROFILE_V1": "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8",
        },
    }
    (workspace / "runtime-manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=1), encoding="utf-8"
    )
    print(f"workspace ready: {workspace}")
    return 0


def cmd_task(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    ledger, _, _, controller = _build_runtime(workspace, args.provider)
    record = TaskRecord(
        task_id=args.task_id,
        repository=args.repository,
        repository_path=str(Path(args.repo_path).resolve()),
        goal=args.goal,
        done_when=args.done_when,
        task_source=args.source,
        base_head=args.base_head,
        surfaces=args.surface or [],
        affected_contracts=args.contract or [],
        accepted_authority_revisions=[args.authority_revision],
        requires_independent_review=not args.no_independent_review,
        preflight=PreflightRecord(
            authority_action=args.authority_action,
            plan_level=args.plan_level,
            assurance_level=args.assurance_level,
            product_authority_refs=[args.authority_revision],
            mandate_ref=args.mandate_ref,
            delivery_profile="SIX_PACK_V1" if args.profile_selected else "",
            completed=args.profile_selected,
        ),
    )
    ledger.create_task(record)
    ledger.save()
    controller.register(
        RegistryEntry(
            name=args.repository,
            path=str(Path(args.repo_path).resolve()),
            write_enabled=True,
        )
    )
    print(f"task created: {args.task_id} (profile_selected={args.profile_selected})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    _, _, _, controller = _build_runtime(workspace, args.provider)
    controller.admit(args.task_id)
    result = controller.drive(args.task_id)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    _, _, _, controller = _build_runtime(workspace, args.provider)
    report = controller.recover()
    tick = controller.tick()
    print(json.dumps({"recover": report, "tick": tick}, indent=1, sort_keys=True, default=str))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    ledger, queues, _, controller = _build_runtime(workspace, args.provider)
    status: dict[str, object] = {
        "window_phase": controller.window_phase(),
        "tasks": {key: task.to_dict() for key, task in ledger.tasks().items()},
        "workflows": {key: wf.to_dict() for key, wf in ledger.workflows().items()},
        "registry": {key: entry.to_dict() for key, entry in controller.registry.items()},
        "leases": {key: lease.to_dict() for key, lease in controller.leases.items()},
    }
    if args.queues:
        status["queues"] = {
            role.value: {
                "new": queues.queue(role.value).list_new(),
                "in_process": queues.queue(role.value).list_in_process(),
            }
            for role in Role.ordered()
        }
    print(json.dumps(status, indent=1, sort_keys=True))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    ledger, _, _, _ = _build_runtime(workspace, "fake")
    report = TerminalVerifier(ledger).verify(args.task_id)
    print(json.dumps(report.to_dict(), indent=1, sort_keys=True))
    return 0 if report.verdict == "PASS" else 1


def cmd_drive_all(args: argparse.Namespace) -> int:
    """Deterministic multi-task drive: tick until all tasks settle.

    Proves the shared worker pool: tasks in different repositories advance
    at different stations under MAX_IN_PROCESS_PER_ROLE=1.
    """
    workspace = Path(args.workspace).resolve()
    _, _, _, controller = _build_runtime(workspace, args.provider)
    from .model import WorkflowState

    # Deterministic admission of every task record that lacks a workflow.
    admitted: list[str] = []
    refused: list[dict[str, str]] = []
    for task_id in controller.ledger.tasks():
        if task_id in controller.ledger.workflows():
            continue
        try:
            controller.admit(task_id)
            admitted.append(task_id)
        except SixPackError as error:
            refused.append({"task_id": task_id, "code": error.code, "detail": str(error)})
    history: list[dict[str, object]] = [{"admitted": admitted, "refused": refused}]
    for _ in range(args.max_passes):
        before = {
            key: (wf.state.value, wf.stage_pointer.value)
            for key, wf in controller.ledger.workflows().items()
        }
        tick = controller.tick()
        dispatched = tick.get("dispatched") or []
        after = {
            key: (wf.state.value, wf.stage_pointer.value)
            for key, wf in controller.ledger.workflows().items()
        }
        history.append({"dispatched": dispatched})
        if not dispatched and before == after:
            break
        if all(
            wf.state
            in (WorkflowState.TERMINAL_BROADCAST, WorkflowState.CONVERGED)
            for wf in controller.ledger.workflows().values()
        ):
            break
    final = {
        key: {"state": wf.state.value, "pointer": wf.stage_pointer.value}
        for key, wf in controller.ledger.workflows().items()
    }
    print(json.dumps({"final": final, "passes": history}, indent=1, default=str))
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    """Record that the task record asserts DONE_WHEN satisfied (stop control)."""
    workspace = Path(args.workspace).resolve()
    ledger, _, _, _ = _build_runtime(workspace, "fake")
    instance = ledger.workflow(args.task_id)
    instance.done_when_met = True
    ledger.save()
    print(json.dumps({"task_id": args.task_id, "done_when_met": True}))
    return 0


def cmd_converge(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    _, _, _, controller = _build_runtime(workspace, "fake")
    report = controller.converge_terminal(args.task_id)
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0


def cmd_host(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    _, _, _, controller = _build_runtime(workspace, "fake")
    if args.host_command == "register":
        controller.register(
            RegistryEntry(
                name=args.name,
                path=str(Path(args.path).resolve()),
                base_branch=args.base_branch,
                write_enabled=args.writable,
            )
        )
        print(f"registered {args.name} @ {controller.registry[args.name].head[:12]}")
    elif args.host_command == "scan":
        print(json.dumps(controller.scan(), indent=1, sort_keys=True))
    elif args.host_command == "quiesce":
        print(json.dumps(controller.quiesce(), indent=1, sort_keys=True, default=str))
    elif args.host_command == "recover":
        print(json.dumps(controller.recover(), indent=1, sort_keys=True, default=str))
    elif args.host_command == "status":
        print(json.dumps({
            "window_phase": controller.window_phase(),
            "registry": {k: v.to_dict() for k, v in controller.registry.items()},
            "leases": {k: v.to_dict() for k, v in controller.leases.items()},
        }, indent=1, sort_keys=True, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sixpack", description="Six-Pack delivery runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="create a runtime workspace")
    init_p.add_argument("workspace")
    init_p.set_defaults(func=cmd_init)

    task_p = sub.add_parser("task", help="create a task with PREFLIGHT record")
    task_p.add_argument("workspace")
    task_p.add_argument("--task-id", dest="task_id", required=True)
    task_p.add_argument("--repository", required=True)
    task_p.add_argument("--repo-path", required=True)
    task_p.add_argument("--goal", required=True)
    task_p.add_argument("--done-when", dest="done_when", required=True)
    task_p.add_argument("--source", required=True, help="TASK_SOURCE binding")
    task_p.add_argument("--base-head", dest="base_head", required=True)
    task_p.add_argument("--authority-revision", dest="authority_revision", required=True)
    task_p.add_argument("--mandate-ref", dest="mandate_ref", default="")
    task_p.add_argument("--surface", action="append")
    task_p.add_argument("--contract", action="append")
    task_p.add_argument("--authority-action", dest="authority_action", default="REUSE")
    task_p.add_argument("--plan-level", dest="plan_level", default="BRIEF")
    task_p.add_argument("--assurance-level", dest="assurance_level", default="DURABLE")
    task_p.add_argument("--profile-selected", dest="profile_selected", action="store_true")
    task_p.add_argument(
        "--no-independent-review", dest="no_independent_review", action="store_true"
    )
    task_p.add_argument("--provider", default="fake")
    task_p.set_defaults(func=cmd_task)

    run_p = sub.add_parser("run", help="admit and drive one task through all six stations")
    run_p.add_argument("workspace")
    run_p.add_argument("--task-id", dest="task_id", required=True)
    run_p.add_argument("--provider", default="fake")
    run_p.set_defaults(func=cmd_run)

    resume_p = sub.add_parser("resume", help="crash recovery + deterministic tick")
    resume_p.add_argument("workspace")
    resume_p.add_argument("--provider", default="fake")
    resume_p.set_defaults(func=cmd_resume)

    status_p = sub.add_parser("status", help="show tasks/workflows/queues/window")
    status_p.add_argument("workspace")
    status_p.add_argument("--queues", action="store_true")
    status_p.add_argument("--provider", default="fake")
    status_p.set_defaults(func=cmd_status)

    verify_p = sub.add_parser("verify", help="terminal impact-and-coverage verification")
    verify_p.add_argument("workspace")
    verify_p.add_argument("--task-id", dest="task_id", required=True)
    verify_p.set_defaults(func=cmd_verify)

    drive_p = sub.add_parser(
        "drive-all", help="tick until every admitted task settles (shared pool)"
    )
    drive_p.add_argument("workspace")
    drive_p.add_argument("--provider", default="fake")
    drive_p.add_argument("--max-passes", dest="max_passes", type=int, default=24)
    drive_p.set_defaults(func=cmd_drive_all)

    done_p = sub.add_parser("done", help="record DONE_WHEN satisfied for a task")
    done_p.add_argument("workspace")
    done_p.add_argument("--task-id", dest="task_id", required=True)
    done_p.set_defaults(func=cmd_done)

    conv_p = sub.add_parser("converge", help="terminal broadcast convergence (merge-only)")
    conv_p.add_argument("workspace")
    conv_p.add_argument("--task-id", dest="task_id", required=True)
    conv_p.set_defaults(func=cmd_converge)

    host_p = sub.add_parser("host", help="multi-repo control plane")
    host_p.add_argument("workspace")
    host_p.add_argument(
        "host_command", choices=["register", "scan", "quiesce", "recover", "status"]
    )
    host_p.add_argument("--name")
    host_p.add_argument("--path")
    host_p.add_argument("--base-branch", dest="base_branch", default="main")
    host_p.add_argument("--writable", action="store_true")
    host_p.set_defaults(func=cmd_host)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SixPackError as error:
        print(json.dumps({"rejected": error.code, "detail": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
