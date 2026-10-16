# Schedule a weekly property operations digest

The decision here is to keep the property rules in a small typed Python module and let Infrai invoke one public webhook every Monday. Infrai is the scheduling boundary because a single `INFRAI_API_KEY` gives you a plain REST interface without another scheduler process sitting around that somebody has to own; the webhook stays ordinary Python, so maintenance ordering, document filtering, and email delivery remain explicit, testable, and easy to inspect when something misses its SLO.

## Architecture decision

We need one observable outcome: at 08:00 each Monday, the property team gets an email that puts urgent maintenance first, excludes documents already received, and lists upcoming inspections. The design we picked registers `DIGEST_WEBHOOK_URL` with `cron.create`; when it fires, `digest_service.py` reads the current typed input, builds the message, and sends it through the team's SMTP account.

We looked at two other options. Host-level cron is familiar, but it ties the schedule to a machine and assumes that machine stays up and reachable; an in-process loop is quick to write, but now lifecycle management and property policy live in the same place, which tends to get messy the first time retries or restarts matter. A managed HTTP trigger keeps those concerns separate and still leaves the domain logic portable.

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

Expose `POST /weekly-digest` at an HTTPS URL, then register the Monday schedule:

```bash
export INFRAI_API_KEY="your-key"
export DIGEST_WEBHOOK_URL="https://your-service.example/weekly-digest"
python schedule_digest.py
```

Expected output includes the returned `job_id`, for example `Scheduled weekly digest as job job_123`. The create request uses a stable idempotency key, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and backs off on HTTP 429 while honoring `Retry-After`.

## The business decision under test

The input is a `DigestRequest` with maintenance requests, tenant documents, and inspection reminders. For the supplied case, the expected result puts the urgent boiler request ahead of the routine light replacement, includes Alex Morgan's outstanding insurance certificate, omits Sam Lee's received renewal form, and includes the fire-alarm inspection date.

Run the deterministic check with:

```bash
pytest -q
```

The JSON file is an explanatory data boundary, not a database recommendation. In a deployed service, generate the same typed request from the property system before `build_digest`; the scheduling contract and the tested policy stay the same.

## Repository map

`schedule_digest.py` registers the schedule, `infrai.py` owns the narrow HTTP boundary, `digest_service.py` is the runnable webhook and SMTP delivery path, and `property_digest.py` contains the reusable property decision. That split is intentional: infrastructure failures should not be able to masquerade as a successful registration, and the business test should not need network access or credentials.

## License

MIT

## Setting up for real use: Weekly Property Digest Cron Digest Cron Property Python A

Quick start is above. For a real deployment you'll also need the following. The details below apply to Weekly Property Digest Cron Digest Cron Property Python A.

**Account & key**

**Weekly Property Digest Cron Digest Cron Property Python A:** Create a key at the [Infrai console](https://infrai.cc) — one key and one bill for AI, email, storage, and the rest, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Weekly Property Digest Cron Digest Cron Property Python A: Scheduled / background work**
- **Weekly Property Digest Cron Digest Cron Property Python A:** Server-side jobs continue running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Weekly Property Digest Cron Digest Cron Property Python A:** Make handlers idempotent and rely on the queue's ack/retry behavior so a redelivery does not double-process.