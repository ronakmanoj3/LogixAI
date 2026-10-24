# ReStock Enhanced — local inventory simulation

This bundle extends the supplied ReStock calculator with a multi-tab browser interface. It preserves the original Python reference engine and `/api/evaluate` endpoint.

## Run on Windows

1. Extract `ReStock_Enhanced.zip` to a folder such as `Documents\ReStock_Enhanced`.
2. Confirm that the `web` folder is beside `serve.py` and contains `index.html`, `app.js`, and `style.css`.
3. Open that folder in File Explorer.
4. Click the address bar, type `cmd`, and press Enter.
5. Run:

   ```bat
   python serve.py --open
   ```

   If `python` is not recognised but Python Launcher is installed, use `py serve.py --open`.
6. The browser should open `http://localhost:8000/`. If it does not, enter that address manually.
7. Keep the Command Prompt open while using ReStock. Press `Ctrl+C` in that window to stop it.

If port 8000 is occupied, run `python serve.py --port 8001 --open` and open `http://localhost:8001/`.

## Tabs included

- **Overview:** recommendation, headline metrics, inventory chart and sample risk alerts.
- **Stock simulator:** original scenario inputs, presets, option comparison, daily trace, JSON export.
- **Demand forecast:** configurable seven-day forecast with weekend uplift, trend and uncertainty range. Illustrative, not trained on sales history.
- **Replenishment planner:** reorder point, days of cover and suggested order quantity using a transparent heuristic.
- **Store network:** sample donor/receiver stores and indicative transfer matches with assumed distances and costs.
- **Suppliers:** editable illustrative supplier on-time rate, lead time and premium with a simple ranking score.
- **Financial impact:** opportunity cost of no action, response cost, modeled contribution gain and service level.
- **Product portfolio:** sample supermarket and fashion SKU risk register.
- **Reorder point model:** normal, demand spike, delayed delivery and reduced-budget comparisons.
- **Decision assistant:** rule-based explanations derived from the calculator results and a checklist before taking action.

## Run tests

From this folder:

```bat
python -m unittest -v test_reference_engine.py
```

The original eight calculator tests should pass. The app has also been checked locally for Python syntax, JavaScript syntax, static page delivery, defaults API and evaluation API.

## Important limitations

- The original inventory calculator remains deterministic and uses synthetic data.
- The forecast is a configurable illustrative pattern; it is not a trained machine-learning model.
- Store distances and supplier records are synthetic.
- The replenishment planner uses a basic reorder-point and coverage heuristic, not a full optimisation solver.
- The decision assistant is a local rule-based explanation layer, **not a connected LLM/AI agent**. Live availability checks, tool-calling orchestration, database persistence and real ERP/POS/supplier integrations are not implemented.
- No orders or transfers are placed. Human review is required before real-world action.
- The local server binds to `127.0.0.1`; it is for local use, not public deployment.
