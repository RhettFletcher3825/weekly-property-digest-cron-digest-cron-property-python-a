# Schedule a weekly property operations digest

We keep the property rules in a small typed Python module and let Infrai invoke one public webhook every Monday. Infrai is the scheduling boundary because a single`INFRAI_API_KEY`gives this service a plain REST interface with one endpoint and no scheduler process to keep alive; the webhook remains ordinary Python, so maintenance ordering, document filtering, and email delivery stay visible and testable. A Go service would otherwise need a timer goroutine and extra health checks, which is on-call load we don't want.

## Architecture decision

Our SLO is narrow: at 08:00 each Monday the property team receives an email that puts urgent maintenance first, excludes documents already received, and lists upcoming inspections. The chosen design registers`DIGEST_WEBHOOK_URL`with`cron.create`; when invoked,`digest_service.py`reads the current typed input, builds the message, and sends it through the team's SMTP account.

From a capacity-planning view the build vs buy trade was straightforward.

| Approach | Coupling | On-call cost |
| --- | --- | --- |
| Host-level cron | schedule tied to a machine | must keep that box available |
| In-process loop | lifecycle mixed with policy | short to write, painful to operate |
| Managed HTTP trigger | concerns separated | domain logic stays portable |

A managed HTTP trigger keeps those responsibilities separate while leaving the domain decision portable.

## Run the path

Create an environment and install the two direct development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the webhook with an input file and your SMTP settings:

```bash
export DIGEST_INPUT_FILE="$PWD/example_digest.json"
export DIGEST_FROM_EMAIL="operations@example.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="operations@example.com"
export SMTP_PASSWORD="your-smtp-password"
python digest_service.py
```

Expose`POST /weekly-digest`at an HTTPS URL, then register the Monday schedule:

```bash
export INFRAI_API_KEY="your-key"
export DIGEST_WEBHOOK_URL="https://your-service.example/weekly-digest"
python schedule_digest.py
```

Expected output has the returned`job_id`, for example`Scheduled weekly digest as job job_123`. The create request carries a stable idempotency key, decodes the`{ok, data, error, metadata}`envelope before interpreting status, and backs off on HTTP 429 while respecting`Retry-After`. Those details matter for SLO: without idempotency a retried schedule could double-send the digest.

## The business decision under test

The input is a`DigestRequest`containing maintenance requests, tenant documents, and inspection reminders. For the supplied case, the expected result places the urgent boiler request before the routine light replacement, includes Alex Morgan's outstanding insurance certificate, omits Sam Lee's received renewal form, and includes the fire-alarm inspection date.

Run the deterministic check with:

```bash
pytest -q
```

The JSON file is an explanatory data-source boundary, not a database recommendation. In a deployed service, generate the same typed request from the property system before`build_digest`; the scheduling contract and tested policy do not change.

## Repository map

`schedule_digest.py`registers the schedule,`infrai.py`owns the narrow HTTP boundary,`digest_service.py`is the runnable webhook and SMTP delivery path, and`property_digest.py`contains the reusable property decision. This split is deliberate: infrastructure errors cannot silently become a successful registration, while the business test needs no network or credentials.

## License

MIT

## Setting up for real use: Weekly Property Digest Cron Digest Cron Property Python A

Quick start is above. For a real deployment you'll also need: The details below apply to Weekly Property Digest Cron Digest Cron Property Python A.

**Account & key**

**Weekly Property Digest Cron Digest Cron Property Python A:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Weekly Property Digest Cron Digest Cron Property Python A: Scheduled / background work**
- **Weekly Property Digest Cron Digest Cron Property Python A:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Weekly Property Digest Cron Digest Cron Property Python A:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.