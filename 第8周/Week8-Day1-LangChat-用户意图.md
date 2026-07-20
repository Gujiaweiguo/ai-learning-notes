# Week 8 Day 1: Who Calls LangChat?

## Today’s Question

**Why is LangChat not an Agent Host?**

## 1. Start with the request journey

A practical request begins with a user talking to an Agent Host. The Agent Host understands the intent, plans any cross-system work, chooses a governed business capability, and calls LangChat through controlled HTTP or MCP access. LangChat then authorizes the call, resolves a published SkillRelease, executes it through the appropriate runtime path, and returns a structured result.

```text
User
  -> Agent Host
  -> controlled HTTP/MCP
  -> LangChat capability platform
  -> governed SkillRelease
  -> internal workflow / provider capability
  -> structured result
```

This boundary is the first rule for understanding the product. If LangChat is treated as another Agent Host, it duplicates intent understanding and cross-system planning. The call chain becomes “Agent Host calls Agent Host”, while neither product has a crisp responsibility.

## 2. What ADR-001 decides

ADR-001 defines LangChat as an **Enterprise Capability Platform**, not a mandatory orchestrator. It freezes several important decisions:

- Agent Hosts call LangChat directly through controlled HTTP or MCP access.
- An orchestrator is an optional, replaceable role; it is not a required system.
- The historical `OrchestratorAgent` was never put into production and is not part of the target architecture.
- LangChat owns capability discovery, authorization, versioning, approval, traceability, and governed execution.
- LangChat does not own user-intent interpretation, cross-system replanning, or provider-level business-data authorization.

The difference is subtle but essential. An Agent Host is responsible for deciding *what the user needs*. LangChat is responsible for providing *what enterprise capability can be used safely and reproducibly*.

## 3. The code that exists today

The boundary already has concrete code, although it is not yet at the full v2 target state.

### SkillRelease API

`/root/langchat/apps/backend/langchat/skill_release/routes.py` exposes the controlled access surface. The API supports discovery, invocation, and approval-related flows for SkillRelease instances. This is the practical entry point through which an Agent Host can discover and invoke governed enterprise capabilities.

### Six-dimensional identity

`/root/langchat/apps/backend/langchat/server/auth/six_dim_middleware.py` validates the request context. The architecture requires six dimensions:

| Dimension | Question answered |
|---|---|
| client | Which Agent Host or client is calling? |
| actor | Who initiated the work? |
| tenant | Which tenant owns the request? |
| workspace | Which workspace is the scope? |
| scope | Which actions are authorized? |
| delegation | Which delegated authority chain applies? |

This is why “direct call” does not mean “uncontrolled call.” An Agent Host may call LangChat directly, but it must do so with an attributable identity and explicit authorization context.

### SkillRelease descriptor

`/root/langchat/apps/backend/langchat/skill_release/descriptor.py` contains `SkillReleaseDescriptor`, a frozen Pydantic model that describes a release. Its meaningful fields include `skill_id`, `version`, lifecycle state, effect policy, human-review gate, workflow binding, visibility, and scopes.

### Existing bindings

`/root/langchat/apps/backend/langchat/skill_release/bindings/` contains W01-W09 bindings. They show that the code already publishes specific workflow-backed capabilities such as operational anomaly detection and internal policy Q&A. A caller should see a governed release, not an internal workflow implementation detail.

## 4. Current state versus v2 target state

The present system has a real foundation:

- SkillRelease discovery and invocation APIs exist.
- Six-dimensional request identity exists.
- Workflow-backed SkillRelease bindings exist.
- Human approval workflows already exist.

The v2 strategy adds an artifact and deployment model that is not implemented yet:

- SkillRelease should become a signed OCI artifact with a digest.
- A Blueprint should be compiled into an `ExecutionPlanIR`, rather than a release binding directly to a workflow.
- `ApplicationContract` should be a first-class contract between the Agent Host and LangChat.
- `Deployment`, `DeploymentRevision`, `ReleaseChannel`, and `TrafficPolicy` should govern how releases reach production.

The gap is therefore significant, but it is not a blank slate. The architecture must evolve a working governed release system into a reproducible artifact-and-deployment chain.

## 5. The mental-model correction

**Before:** LangChat is an AI runtime that should orchestrate everything.

**Now:** LangChat is an enterprise capability platform. Agent Hosts understand user goals and plan work; LangChat makes enterprise capabilities discoverable, authorized, versioned, reviewable, and executable in a controlled way.

## 6. Test your understanding

Try to explain this in your own words:

> OpenClaw is an Agent Host. It understands user intent, decides what work to do, and selects a governed capability. LangChat is the enterprise capability platform that exposes a SkillRelease through controlled HTTP or MCP. LangChat does not become a second Agent Host or a mandatory orchestration layer; it makes enterprise execution safe, attributable, and repeatable.

## 7. Design challenge

If you redesigned LangChat today, would you still keep the Agent Host and Capability Platform separate? What responsibility would force you to change the boundary?

## 8. Boundary examples

### Example A: “Summarize this tenant’s monthly operations and recommend actions.”

The Agent Host interprets the request and decides whether it needs one or several enterprise capabilities. It may call LangChat for an approved operational-analysis SkillRelease, then call another business system for a separate action. LangChat does not become the global planner; it executes the capability it governs and returns a traceable result.

### Example B: “Publish a new version of a business analysis skill.”

The Agent Host can request publication, but the release decision belongs to LangChat governance. LangChat applies the release lifecycle, approval gate, scope checks, audit trail, and eventually the deployment policy. This is precisely the distinction between *asking for an action* and *governing whether that action is allowed*.

### Why direct access still needs a platform

A direct HTTP or MCP call without identity, versioning, review, and audit is merely an API call. LangChat turns that call into an enterprise capability invocation. The caller can discover only approved releases, invoke only the scopes it holds, and receive an outcome tied to a request identity and trace. That is the product value; it should not be hidden behind a fictional mandatory orchestrator.

## 9. Alternatives considered

| Alternative | Why it is not the target design |
|---|---|
| Make LangChat a full Agent Host | Duplicates goal understanding and cross-system planning; blurs the boundary. |
| Require one central Orchestrator | Creates a mandatory hop and an availability/ownership bottleneck; the historical component was never productionized. |
| Let Agent Hosts call provider systems directly | Bypasses capability discovery, release lifecycle, review, audit, and consistent governance. |
| Expose internal workflows directly | Couples callers to implementation details and makes versioning and rollout hard to control. |

The chosen architecture is therefore not “less orchestration.” It is **explicit separation of orchestration from governed enterprise execution**.

## 10. Today’s engineering log

| Item | Record |
|---|---|
| Confirmed | LangChat is positioned as an Enterprise Capability Platform by ADR-001. |
| Confirmed | The existing code has direct SkillRelease invocation and six-dimensional identity enforcement. |
| Gap | The v2 artifact chain, `ExecutionPlanIR`, and deployment constructs are not yet first-class in code. |
| Technical risk | Workflow bindings may leak implementation coupling until an artifact/plan boundary is introduced. |
| Next step | Study `ApplicationContract`: how an Agent Host describes a request without exposing LangChat internals. |

## References

- ADR-001: LangChat direct-to-Agent-Host capability platform positioning, especially the decision and boundary sections.
- `/root/langchat/apps/backend/langchat/skill_release/routes.py`
- `/root/langchat/apps/backend/langchat/server/auth/six_dim_middleware.py`
- `/root/langchat/apps/backend/langchat/skill_release/descriptor.py`
- `/root/langchat/apps/backend/langchat/skill_release/bindings/`
