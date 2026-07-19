# Databricks permissions JSON examples

Use `databricks apps set-permissions APP_NAME --json @filename.json` to apply.

1) Grant a specific user `CAN_USE`:

```json
{
  "access_control_list": [
    {
      "user_name": "user@example.com",
      "permission_level": "CAN_USE"
    }
  ]
}
```

2) Grant a workspace group `CAN_USE` (replace group name):

```json
{
  "access_control_list": [
    {
      "group_name": "All Users",
      "permission_level": "CAN_USE"
    }
  ]
}
```

3) Grant a service principal `CAN_MANAGE` (use the app's service principal name):

```json
{
  "access_control_list": [
    {
      "service_principal_name": "app-33ksvr data-legend-v3",
      "permission_level": "CAN_MANAGE"
    }
  ]
}
```

Notes:
- `CAN_USE` lets users invoke/run the app.
- The CLI call requires a token with `access-management` scope (workspace admin).
