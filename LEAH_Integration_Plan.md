# ReStock + LEAH integration plan

Prepared 24 October 2026. Status: implementation plan only. The existing simulator remains unchanged; no LEAH integration, deployment or account setup has been performed.

## 1. Target experience

Keep the existing browser simulator and its checked Python calculations. Add an **Ask ReStock Agent** mode in which LEAH receives a goal, calls tools, checks its preferred response against updated availability, recalculates when facts change, and saves a recommendation for human review.

Example request: “Check this product for stockouts over the next seven days and prepare the best feasible response within the response budget.”

The demonstration should show a real sequence of tool calls and results. Merely asking an AI to explain the calculator's final answer would be an explanation feature, not the verification-and-replanning loop proposed here.

Initial scope: one SKU, seven days, the existing three candidate actions, synthetic warehouse/supplier data, and one coordinating agent. A simulated availability source must be labelled as simulated. Keep purchasing and supplier messaging outside this prototype.

## 2. Confirm LEAH access before choosing the connection

Public LEAH product pages describe agent orchestration, workflows, approvals and integrations. Its Procurement page describes REST APIs and webhooks. Those statements do not establish which functions are included in a hackathon account, or a usable API contract for this project.

Obtain the assigned workspace URL and its administrator-provided integration documentation. Confirm:

| Question | Why it changes the build |
| --- | --- |
| Can this workspace create a custom agent/workflow? | Required to configure the ReStock role and instructions. |
| Can the agent invoke our authenticated external HTTP tools, or another documented connector? | Required to call the calculator and availability source. Do not assume REST or MCP tool registration is enabled. |
| Can our backend start a workflow and read its status/results? | Determines whether the localhost website can launch and monitor an agent run. |
| What authentication, permissions and network restrictions apply? | Determines the approved bridge and deployment design. |
| Can we retrieve actual tool events, run IDs and errors? | Determines how to display and export the activity trace. |
| What are the limits, timeouts, costs and available model settings? | Determines run limits, retries and the test budget. |

**First milestone:** complete one harmless round trip using the documented account interfaces, with a small synthetic input and a visible returned result. Record the working configuration. Do not build around guessed LEAH URLs, SDK methods or authentication headers.

### Connection decision

- **Preferred, if supported:** the local ReStock backend starts a LEAH run; LEAH calls a small authenticated HTTPS tool service; the local backend retrieves progress/results and displays them.
- **If external tools work but programmatic run-start does not:** start the run inside LEAH, and use a run/case identifier to show shared results in ReStock where supported. This is a valid two-screen demo; do not claim the website launched the run.
- **If this account cannot call our tools:** resolve access with the organizer or use another explicitly chosen tool-capable runtime. A manual copy/paste workflow is only a prototype of the interaction, not a completed LEAH integration.

## 3. Architecture and responsibility

```text
ReStock browser on your Mac
        |
Local ReStock backend: user inputs, run start/status, review interface
        |                               |
        | documented LEAH interface     | authenticated case/result access
        v                               v
LEAH ReStock agent <------------> Shared tool service
                                  |-- authoritative case/run store
                                  |-- existing Python calculator
                                  |-- simulated availability source
                                  |-- saved draft and event records
```

LEAH controls the next tool step within the workflow rules. Python computes daily stock, feasibility, cash requirements and contribution comparisons. The backend validates results before the UI presents them as a decision.

The local server currently binds to 127.0.0.1:8000. A remote LEAH service cannot call that address on your Mac. Prefer a narrowly scoped HTTPS tool service in an approved environment. A temporary authenticated development tunnel is an alternative only if the account permits it. Do not publish the current unauthenticated local development server as-is.

Use one authoritative case/version store for a run, accessible by the local backend and LEAH tools. Avoid separately maintained local and hosted copies that can silently disagree. Put credentials in backend configuration, never in browser JavaScript or exported results. Initially send only the labelled synthetic case to the external service.

## 4. Wrap the existing code as tools

The names below are **our proposed tool contracts**, not existing LEAH endpoints. Register/map them using the actual supported workspace interface.

| Proposed tool | Input | Output and responsibilities |
| --- | --- | --- |
| `read_case` | `case_id` | Current scenario, version, timestamp and missing-field list. |
| `evaluate_case` | `case_id`, `expected_version` | Call `reference_engine.evaluate` on the stored scenario; return `evaluation_id`, version, option comparison and daily traces. |
| `verify_availability` | `case_id`, `action_id`, `expected_version` | Query the simulated warehouse/supplier source; return observed quantity/arrival, source, timestamp and evidence ID. Apply allowed factual updates to the stored scenario; increment its version only when facts change. |
| `save_draft` | `case_id`, `evaluation_id`, `expected_version`, `deduplication_key`, explanation | Save only a decision based on the current valid evaluation. Numeric fields come from that evaluation. Return a draft ID and “awaiting human review” status. |

Reject unknown cases, invalid inputs and obsolete versions. Validate quantities, currency, arrival days and required fields before calculation. If data is missing, return a clear request for that data instead of inventing it.

Keep the model from rewriting stock, budgets or costs to make an action feasible. Verification may update only documented availability/arrival fields. A human input edit creates a new version and invalidates older recommendations. Repeated saves with the same key return the same draft rather than creating duplicates.

## 5. Configure the agent's behavior

Adapt the existing `agent_prompt.md` to the contracts above. The sequence should be:

1. Read the case and obtain any required missing input.
2. Evaluate the current snapshot using the calculator tool.
3. If the preferred option involves a transfer or purchase, verify that option's availability and arrival.
4. If verification changes a fact, re-evaluate the new version. Verify the newly preferred actionable option before finalizing it.
5. If no action is selected, explain why and flag any remaining lost sales. No procurement verification is needed for a no-action choice.
6. Save a version-matched draft using the evaluated values and evidence. Stop at human review.

Allow at most two fact-change replanning cycles per run. Set a bounded overall run/tool-call limit using the account's documented controls. Distinguish transient tool retries from replanning; never retry a save without its deduplication key. Escalate if facts keep changing or a required tool remains unavailable.

The final response must state the chosen action, quantity and arrival when applicable, lost sales, cash requirement, incremental response cost, contribution gain, rejected alternatives, assumptions and source version. Validate these against the stored tool output. Show a numerical mismatch as an error rather than displaying a fabricated financial result.

## 6. Add agent mode to the simulation

Preserve **Run analysis** as the deterministic calculator mode. Add a clearly separate **Ask ReStock Agent** action and a short goal field. Show whether LEAH is configured and connected; never display an “AI connected” badge based only on local configuration.

Add an activity panel populated by recorded tool events:

```text
Read case v1
Evaluated v1: transfer is the preferred response
Verified transfer: donor stock is now zero; case updated to v2
Evaluated v2: expedited purchase is preferred
Verified expedited arrival: day 3 confirmed
Saved draft based on v2: awaiting human review
```

These entries must represent actual tool calls/results, not decorative narration or hidden model reasoning. If LEAH does not expose a full trace, show our service's recorded tool events and label their source.

Display pending, running, needs-input, awaiting-review, failed and completed states. Keep a run ID so refreshing the page does not accidentally start another run. Disable conflicting edits while a run is active, or cancel/invalidate the run before accepting them. On timeout or loss of connection, show the failure; offer calculator mode explicitly rather than silently replacing an agent run with a canned answer.

Add **Approve draft** and **Reject draft** controls. They record a local review decision only. Approving must not trigger a real purchase, email or transfer. Reject approvals of outdated drafts.

## 7. Make the disruption demonstration genuinely adaptive

The current preset buttons change the input before running the calculator. Retain those for teaching, but add separate verification fixtures for agent mode. Every run begins with the same initial snapshot; later observations come from the simulated verification source.

| Agent demo fixture | New information discovered during verification | Expected final result |
| --- | --- | --- |
| All available | Transfer of 80 units on day 2 is confirmed. | Warehouse transfer; INR 400 cash; INR 1,600 modeled gain. |
| Transfer unavailable | Donor stock is zero. The alternate purchase is then confirmed for day 3. | Expedited purchase; INR 9,160 cash; INR 840 gain. |
| Transfer unavailable, supplier late | First check removes transfer availability; second check moves expedited arrival to day 5. | No action; 80 units unfilled. Expediting would yield minus INR 160. |

The presenter selects the fixture before the run. Keep its future observations in the verification source, not in the agent's initial case, so the trace demonstrates an actual response to new evidence. Label the fixture as simulated; do not imply a real warehouse system was contacted.

## 8. Implementation order, files and completion criteria

The following new filenames are proposals; they have not been created by this plan.

| Stage | Changes | Completion criterion |
| --- | --- | --- |
| A. Access check | Confirm the workspace interfaces and supported connection. | A successful authenticated round trip, with recorded run/tool evidence. |
| B. Local tool layer | Add `agent_tools.py`, `case_store.py`, `availability_simulator.py` and versioned fixture data. Reuse the calculator. | Tools reproduce the three expected cases and reject stale/invalid requests without LEAH. |
| C. Connection | Add `leah_adapter.py` using verified documentation; deploy only the needed tool service when the connection is selected. | LEAH invokes the real calculator tool and receives structured output. |
| D. Agent workflow | Update `agent_prompt.md`; configure one coordinating agent and bounded replanning. | A single goal triggers verification, recalculation and a saved draft. |
| E. Website | Extend `serve.py`, `web/index.html`, `web/app.js` and `web/style.css` for agent runs, traces and reviews. | User sees the actual run, its final decision and approval status. |
| F. Validation and submission | Add agent integration tests; update README, beginner guide, proposal and demo recording. | Honest, repeatable demonstration with exported evidence and current instructions. |

Planning estimate after access and documentation are available: roughly 1-2 focused build days for this narrow prototype, depending on the connector. Account provisioning and hosting approval can take longer and are not included. First deliver one end-to-end synthetic run, then polish the interface. Do not spend the available time building multiple agents before the tool connection works.

## 9. Acceptance tests

Retain the existing eight calculator tests. After implementation, run each of these six agent scenarios five times and record all outcomes, configuration, durations and tool events:

1. Baseline: transfer confirmed; correct final arithmetic and a single saved draft.
2. Transfer disappears during verification: switch to the day-3 expedited purchase after recalculation.
3. Transfer disappears and supplier slips to day 5: replan twice, select no action and report the service gap.
4. No transfer and INR 2,000 cash budget: reject the INR 9,160 purchase even though its incremental cost is lower than the budget.
5. Missing/stale input or instructions embedded in a note: request valid data, reject outdated decisions and ignore note-based instructions.
6. Tool timeout, repeated save or outdated approval: bounded recovery, explicit failure when necessary, no duplicate draft and no approval of an obsolete result.

Release criteria: all displayed financial values match the deterministic evaluation; no infeasible response is finalized; no missing data is invented; the disruption runs contain actual verification and recalculation events; no real order is executed. Report the observed pass rate and failures, not a promised score. These agent tests have not yet run.

## 10. What we need next

The assigned LEAH workspace URL, confirmation of login access, and the workspace's integration documentation or administrator guidance. Authentication should be configured through the platform/backend's supported mechanism rather than copied into project documents.

Until these are available, Stage B can be developed against a local test harness. That work prepares reusable tools but does not count as a working LEAH connection.

## Sources and evidence boundary

- [Leah Agentic OS](https://leahai.com/products/agentic-os): public description of agent orchestration, workflows, app building and human review.
- [Leah Procurement](https://leahai.com/products/agentic-os/procurement): public description of REST APIs, webhooks and custom integrations for that product.
- Existing project files: `serve.py`, `reference_engine.py`, `scenario.json`, `agent_prompt.md` and the `web/` interface.

Public product descriptions were checked on 24 October 2026. Account-specific tool registration, run APIs, authentication and trace access remain unverified. The architecture, tool names, filenames and stages above are our proposed design, not vendor-certified integration instructions.
