# Getting runtime evidence

Getting logs, screenshots, recordings and attachments is environment-specific. Whether you drive a browser or call an API directly, which library and which path to take, is decided by the project adapter, the skill does not hardcode it. But a set of pitfalls is mechanism-independent, you hit them no matter how you fetch. They are listed here.

## Seven pitfalls

1. Before starting automation, check there is no already-open browser of the same kind occupying the session. Close it or switch to a separate user directory, otherwise automation fights the open window.
2. Leave enough timeout for slow pages. The default timeout is often not enough, do not treat slow as hung.
3. Download attachments serially, not concurrently. Concurrent downloads fight over the session, files come down incomplete.
4. A failed download and a missing attachment are two different things. A failure only means you did not get it, never that the evidence does not exist. Only when the list truly has none can you say there is none.
5. Large attachments may live in an external object store, not in the tracker's API response. Look for the storage link in the page, not finding it in the API does not mean it does not exist.
6. Credentials never go into scripts. Reuse a logged-in session instead of logging in every time, the login step itself is error-prone.
7. When the evidence mechanism breaks, run a minimal reproduction first, do not analyze a whole batch with a broken mechanism.

## How it lands

The mechanism layer lives in the project adapter, follow the template in `scripts/adapters/example_api.py`. Check against the pitfall list during analysis. Change the environment or the mechanism, the pitfalls remain.
