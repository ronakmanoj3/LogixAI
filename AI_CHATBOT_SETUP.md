# ReStock AI Chatbot — Windows setup

The Decision Assistant now includes a connected chatbot interface. The rest of ReStock can still run without an API key; the chatbot requires an OpenAI API key and internet access.

## 1. Install the chatbot dependency

Open Command Prompt in this folder and run:

```cmd
python -m pip install -r requirements.txt
```

## 2. Set your API key for this terminal session

Create/manage an API key from the OpenAI API platform. API access and billing are separate from a ChatGPT subscription, and API usage may incur charges.

In the same Command Prompt window, run the following, replacing the placeholder with your own key:

```cmd
set "OPENAI_API_KEY=YOUR_API_KEY_HERE"
```

Optional: choose another model available to your API account:

```cmd
set "OPENAI_MODEL=gpt-4.1-mini"
```

Do not paste your key into `index.html`, `app.js`, `serve.py`, screenshots, or source control. Do not share it in chat. This `set` command applies only to the current Command Prompt window.

## 3. Start ReStock from this same terminal

```cmd
python serve.py --open
```

Keep the terminal open while using the app. If port 8000 is already occupied, stop the old server with Ctrl+C or use `python serve.py --port 8001 --open`.

## 4. Try the chatbot

Open the Decision Assistant tab. The status badge should say `AI ready`. Run the Stock Simulator first, then ask questions about the current case, such as:

- What should I do and why?
- Compare all available actions and their financial impact.
- When will a stockout happen if I do nothing?
- What assumptions should I verify before acting?

The browser sends the question and the current scenario/result to the local Python server. The server calls the OpenAI API. The key is not sent to browser JavaScript. If no key is configured, the regular simulator and rule-based explanation still work.

## Limitations and safety

- Uses synthetic teaching data, not live store or supplier systems.
- The AI explains the current calculation; it does not independently execute the simulation for arbitrary what-if assumptions. Change the simulator inputs and run it to calculate new results.
- It does not check live stock, route distances, supplier availability or real delivery times.
- It cannot place orders or transfers. Review any recommendation before taking action.
- Do not submit confidential or personally identifiable business data.
- API availability, model access, and charges depend on your API account.
