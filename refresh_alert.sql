-- The purpose is to refresh the alert setting to see whether the alert works as expected.
-- Should not use this in a production server b/c all the alert will be triggered again
DELETE FROM emerge4cuimclocalredcap.redcap_alerts_sent
where alert_id in
(SELECT alert_id FROM emerge4cuimclocalredcap.redcap_alerts
where project_id = 33
);

DELETE FROM emerge4cuimclocalredcap.redcap_alerts_recurrence
where alert_id in
(SELECT alert_id FROM emerge4cuimclocalredcap.redcap_alerts
where project_id = 33
);

DELETE FROM emerge4cuimclocalredcap.redcap_alerts_sent_log
WHERE alert_sent_id in 
(
SELECT alert_sent_id FROM emerge4cuimclocalredcap.redcap_alerts_sent
where alert_id in
(SELECT alert_id FROM emerge4cuimclocalredcap.redcap_alerts
where project_id = 33
)
);
