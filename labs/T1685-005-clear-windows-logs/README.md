# T1685.005-clear-windows-logs

**Tactique** : Defense Impairment

**Technique**: T1685

**Sub-technique**: T1685.005

When attackers clear Windows logs, they are able to hide their intrusive or malicious activities, as every action taken on a Windows system is recorded or noted within Windows log files.
For more information on this subject, please refer to the link [here](https://attack.mitre.org/techniques/T1685/005/).

## Repo structure

`file_delete_win_evtx_deletion.yml` [file](labs/T1070.001-clear-windows-logs/file_delete_win_evtx_deletion.yml), use to detect any activity involving the deletion of .ectx files.
`proc_creation_win_wevtutil_clear_log.yml` [file](labs/T1070.001-clear-windows-logs/proc_creation_win_wevtutil_clear_log.yml), used to detect the execution of Windows log-clearing processes.
`win_security_clear_event_log_service_shutdown.yml` [file](labs/T1070.001-clear-windows-logs/win_security_clear_event_log_service_shutdown.yml), use to detect the termination of the log service.
`win_security_eventlog_cleared.yml` [file](labs/T1070.001-clear-windows-logs/win_security_eventlog_cleared.yml), use to detect log-clearing activities, using the relevant **EventID**, which is **1102**.
`win_system_eventlog_cleared.yml` [file](labs/T1070.001-clear-windows-logs/win_system_eventlog_cleared.yml), Use this to detect log-clearing activities within Windows logs by looking for **EventID 104**.

Samples click [here](labs/T1070.001-clear-windows-logs/samples)

___
> Sebastien Xia
