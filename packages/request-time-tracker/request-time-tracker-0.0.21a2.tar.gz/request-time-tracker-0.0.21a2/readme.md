# Queue time tracker
Reads time when request was processed by nginx & send time spent in queue before it was handled by wsgi.  
Designed mostly for autoscaling. Instance cpu is not trustworthy enough, sometimes there can be external bottlenecks, 
so even if instance cpu is fine, application can hang in queue between nginx(for example) and gunicorn or another wsgi processor.  

## Configuration
1. Add header with request timestamp.

   nginx:
    ```
   proxy_set_header X-RequestTime $msec;
   ```

2. Read header value & send metric value

### Django application
1. Configure django settings:

aws:
   - QUEUE_TIME_TRACKER_NOTIFY_EVERY_SECONDS = 10
   - QUEUE_TIME_TRACKER_HEADER = 'HTTP_X_REQUESTTIME'
   - QUEUE_TIME_TRACKER_CACHE_NAME = 'default'
   - QUEUE_TIME_TRACKER_CACHE_KEY_PREFIX = 'foobar'
   - QUEUE_TIME_TRACKER_CLOUDWATCH_NAMESPACE = 'FooBar Web'
   - QUEUE_TIME_TRACKER_CLOUDWATCH_ACCESS_KEY = 'AK****A'
   - QUEUE_TIME_TRACKER_CLOUDWATCH_SECRET_KEY = 'so******BS'
   - QUEUE_TIME_TRACKER_CLOUDWATCH_REGION = 'us-west-1'

azure:
   - QUEUE_TIME_TRACKER_AZURE_REGION = 'eastus' 
   - QUEUE_TIME_TRACKER_AZURE_SUBSCRIPTION_ID = '*****'  
   - QUEUE_TIME_TRACKER_AZURE_RESOURCE_GROUP_NAME = 'example_group' 
   - QUEUE_TIME_TRACKER_AZURE_PROVIDER_NAME = 'Microsoft.ContainerService' 
   - QUEUE_TIME_TRACKER_AZURE_RESOURCE_TYPE = 'managedClusters' 
   - QUEUE_TIME_TRACKER_AZURE_RESOURCE_ID = 'example-k8s-cluster'

2. Wrap wsgi application with time tracker:
aws:
```python

from request_time_tracker.wsgi_django.cloudwatch import CloudWatchQueueTimeTracker

application = get_wsgi_application()

application = CloudWatchQueueTimeTracker(application)
```

azure:
```python

from request_time_tracker.wsgi_django.azure import AzureMonitoringQueueTimeTracker

application = get_wsgi_application()

application = AzureMonitoringQueueTimeTracker(application)
```

### Non-django application
1. Wrap wsgi application with time tracker. Example:
```python
from functools import partial
from request_time_tracker.trackers.cache.redis import RedisCacheQueueTimeTracker
from request_time_tracker.notifiers.cloudwatch import CloudWatchNotifier

tracker = partial(
    RedisCacheQueueTimeTracker, 
    queue_time_header_name='HTTP_X_REQUESTTIME',
    redis_url='redis://localhost:6379/0',
    notifier=CloudWatchNotifier(
        namespace='FooBar Web',
        aws_access_key='AK****A',
        aws_secret_key='so******BS',
        aws_region='us-west-1',
    ),
)

wsgi_application = tracker(wsgi_application)
```


## Cloudwatch role policy:
```
{
    “Version”: “2012-10-17",
    “Statement”: [
        {
            “Sid”: “VisualEditor0”,
            “Effect”: “Allow”,
            “Action”: [“cloudwatch:PutMetricData”],
            “Resource”: “*”
        }
    ]
}
```

## Azure
role definition: Monitoring Metrics Publisher
https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#monitoring-metrics-publisher