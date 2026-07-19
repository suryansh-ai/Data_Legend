import databricks.sdk as sdk
print('sdk', getattr(sdk, '__version__', 'unknown'))
client = sdk.DatabricksClient()
print('client', type(client))
print('has apps', hasattr(client, 'apps'))
if hasattr(client, 'apps'):
    print('apps methods:', [m for m in dir(client.apps) if not m.startswith('_')])
