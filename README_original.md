# ReStock submission starter kit

ReStock is a proposed inventory exception agent for the Operations Management evaluation area. This kit prepares the concept, teaching exercise, demo and implementation. It is not a completed live-agent submission.

## Run the browser interface

A local browser interface is now included. Double-click `Start ReStock.command`, or run these commands in Terminal:

```sh
cd "/Users/daiitya/Documents/Academics/output/hackathon/restock"
python3 serve.py --open
```

Open http://localhost:8000/ and keep the server's Terminal window open. Press Ctrl+C to stop it. If port 8000 is already in use, use `python3 serve.py --port 8001 --open` and visit http://localhost:8001/.

The interface provides editable scenario inputs, three scenario presets, option comparisons, an inventory chart, a daily trace and a downloadable result. Run analysis after manual edits; preset buttons reset all inputs and run automatically. Everything runs locally with Python's standard library. No account, API key or package installation is required. It is a deterministic calculator; an AI model is not connected.

This interface was added after the original PDF and submission draft. Their descriptions of the interface as pending reflect the earlier preparation stage; the live-agent features remain pending.

## Read first

- `LEAH_Integration_Plan.md`: staged plan for connecting LEAH to the simulator, including account capability checks, tool contracts, adaptive scenarios and acceptance tests. Integration is not yet implemented.
- `ReStock_Beginners_Guide.pdf`: illustrated beginner instructions for starting the website yourself, running simulations, understanding the folder, saving results and troubleshooting.
- `ReStock_Hackathon_Submission_Pack.pdf`: readable seven-page preparation pack (included in the ZIP).
- `submission_draft.md`: editable version, including proposal abstract, rubric mapping, architecture, curriculum exercise, evidence plan, demo script and sprint plan.
- `agent_prompt.md`: proposed instructions and tool contracts for a portable agent implementation.

## Try the synthetic reference case

Python 3 is the only dependency. From this directory:

```sh
python3 reference_engine.py
python3 reference_engine.py --no-transfer
python3 reference_engine.py --no-transfer --express-day 5
python3 -m unittest -v test_reference_engine.py
```

The three commands recommend warehouse transfer, expedited purchase and no action respectively. `scenario.json` contains all assumptions. The three `*_result.json` files contain saved outputs and daily traces. `reference_test_results.txt` records the eight passing acceptance tests.

The baseline loses 80 units of sales. Transfer produces INR 1,600 modeled contribution gain relative to the baseline. If transfer is unavailable, expedited purchase produces INR 840 gain, requires INR 9,160 cash and incurs INR 1,160 incremental response cost. These are synthetic calculations, not observed savings.

## What still needs implementation

The calculator compares three fixed candidate actions for one SKU; it is not an optimizer or an LLM agent. The local interface and decision display are implemented. Connect the calculator to a model, implement the read/verify/save tools, and add persistent scenario version checks and deduplication. Then run the agent acceptance matrix and record a working demo. A simulated verification connector is acceptable for the concept demo only if disclosed.

Do not claim user benefits, live integrations, curriculum adoption or agent test results before collecting evidence. Confirm current course/module placement with faculty. The supplied brief lists 25 October without a year and does not specify the final cutoff time or upload format.

## Complete before submission

Add team/mentor details, confirm the official evaluation-area label and organizer requirements, insert working prototype and video links, and update the writeup to distinguish implemented features from planned ones. Nothing has been uploaded or sent on your behalf.

## Sources

The requirements and weights come from the user's `Agentic AI Hackathon.pdf` and `Hackathon Evaluation.pdf`. Course-title evidence comes from the historical [IIMV PGP 2022-24 listing](https://iimv.ac.in/programs/pgp/pgp2022-24); this does not verify current module coverage. All demo data and project design choices were created for this preparation kit.
