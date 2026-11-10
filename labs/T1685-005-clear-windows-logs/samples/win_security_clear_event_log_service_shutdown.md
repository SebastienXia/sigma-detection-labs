## Chainsaw Test
* `win_security_clear_event_log_service_shutdown.yml` Chainsaw Test

**No Chainsaw test for this rule.** Chainsaw needs a `.evtx` file, and I did not find any public `.evtx` sample containing Event ID 1100 (the EVTX-ATTACK-SAMPLES repository used for the other rules of this lab does not provide one).

The only sample available is a single event in XML format. An XML event cannot be converted back to `.evtx` (the `.evtx` format is a binary format that only Windows writes), so this rule is only tested in Splunk.

A `.evtx` sample could be generated later on a Windows test VM: Event ID 1100 is written at every normal shutdown, so restarting the VM and exporting the Security log (`wevtutil epl Security C:\temp\security_1100.evtx`) would be enough to run a Chainsaw test.


## Splunk Test
* `win_security_clear_event_log_service_shutdown.yml` Splunk Test

The sample is an XML event, not a `.evtx` file. It is converted to JSON Lines with the same structure as the `.evtx` conversions of the other rules, so the `evtx:json` sourcetype and the custom pipeline are reused unchanged:

```
.xml   ──(xml2jsonl.py)──>  .jsonl  ──(Upload)──>  Splunk, sourcetype evtx:json
.yml   ──(sigma convert + custom pipeline)──>  SPL query  ──>  run in Splunk
```

### Prerequisites

```bash
python3 -m venv ~/venv-evtx
source ~/venv-evtx/bin/activate
pip install sigma-cli
sigma plugin install splunk
```

`xml2jsonl.py` only uses the Python standard library.

### Step 1: convert the XML event to JSON Lines

Sample: [`labs/T1685-005-clear-windows-logs/samples/rss/security_1100.xml`](labs/T1685-005-clear-windows-logs/samples/rss/security_1100.xml)

source: [Data Source: Windows Event Log Security 1100](https://research.splunk.com/sources/2a25dafa-691e-4cb2-ae59-07a48867ed9a/)

```bash
python tools/xml2jsonl.py \
  labs/T1685-005-clear-windows-logs/samples/security_1100.xml \
  security_1100.jsonl
```

The script keeps the structure produced by the EVTX parser (`Event.System.EventID`, attributes under `#attributes`). It also truncates `SystemTime` to 7 decimals: the XML event has 9 (`2024-03-13T05:20:11.937418700Z`), while the `evtx:json` sourcetype expects 7 (`%7N`), like the `.evtx` conversions.

### Step 2: ingest the file in Splunk

In *Settings → Add Data → Upload*, select `security_1100.jsonl`, then select the `evtx:json` sourcetype (created during the `win_system_eventlog_cleared.yml` test). If it does not exist yet, create it from `Structured → _json` with these settings and *Save As* → `evtx:json`:

| Setting | Value |
|---|---|
| Timestamp → Extraction | Advanced |
| Time zone | UTC / GMT (the timestamp ends with `Z`) |
| Timestamp format | `%Y-%m-%dT%H:%M:%S.%7NZ` |
| Timestamp fields | `Event.System.TimeCreated.#attributes.SystemTime` |
| Advanced → `MAX_DAYS_AGO` | `10951` |

Check that `_time` shows the original date of the event (13/03/2024 05:20:11 UTC), then submit.

### Step 3: convert the Sigma rule with the custom pipeline

The rule only uses `EventID`, which is already mapped by the pipeline [`pipelines/evtx_json.yml`](pipelines/evtx_json.yml):

| Sigma field | Field in Splunk (`evtx:json`) |
|---|---|
| `EventID` | `Event.System.EventID` |

```bash
sigma convert -t splunk -p pipelines/evtx_json.yml \
  labs/T1685-005-clear-windows-logs/win_security_clear_event_log_service_shutdown.yml
```

Output:

```
sourcetype="evtx:json" Event.System.EventID=1100
```

The rule has no `fields` section, so the query has no `| table` command.

> Do not add `-p splunk_windows`: it renames `EventID` to `EventCode` before the custom pipeline runs, and the mapping no longer applies.

> **Limitation:** the custom pipeline does not use the `logsource` section, so `service: security` does not filter anything in Splunk. The query matches every Event ID 1100, whatever its log. Adding `Channel: Security` and `Provider_Name: Microsoft-Windows-Eventlog` to the detection would restrict it to the Event Log service shutdown.

### Step 4: run the query in Splunk

Paste the query in *Search & Reporting* with the time range set to **All time** (add `index=<your_index>` at the beginning if the file was not indexed in `main`). The query returns the shutdown event of the `EC2AMAZ-M3380E5` host.

Event 1100 contains no user information (its `UserData.ServiceShutdown` element is empty): only the host and the time of the shutdown can be investigated. A 1100 event preceded by an Event ID 1074 in the System log corresponds to a normal shutdown, which is the main false positive of this rule.

![splunk_win_security_clear_event_log_service_shutdown](rss/splunk_win_security_clear_event_log_service_shutdown.png)
