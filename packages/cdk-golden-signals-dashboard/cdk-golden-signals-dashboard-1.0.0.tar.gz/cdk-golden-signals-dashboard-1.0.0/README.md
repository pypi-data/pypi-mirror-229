# CloudWatch Golden Signals Dashboard AWS CDK Construct

Create Amazon CloudWatch Dashboards for monitoring CloudWatch Metrics of AWS Resources partitioned in golden signals. *Latency, Traffic, Errors, Saturation*

You can create tag based CloudWatch dashbord solution out of the box using this construct! [Here](https://github.com/cdklabs/cdk-golden-signals-dashboard/tree/main/dashboard-images) are some screen captures of CloudWatch dashboards created using this cdk construct.

# Supported Resource Types

* AWS::DynamoDB::Table
* AWS::Lambda::Function
* AWS::RDS::DBInstance
* AWS::SNS::Topic
* AWS::AutoScaling::AutoScalingGroup

# Usage

<summary>Including in a CDK application</summary>

```python
# Example automatically generated from non-compiling source. May contain errors.
from aws_cdk import App, Stack, StackProps
from constructs import Construct
from golden_signals_dashboard import GoldenSignalDashboard


class MyStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)
        GoldenSignalDashboard(self, "dynamodbDashboard",
            resource_type="AWS::DynamoDB::Table",
            dashboard_name="myGSDashboard",
            resource_dimensions=[{"resource_region": "us-east-1", "resources": ["Table1", "Table2"]}],
            create_alarms=True
        )
app = App()
MyStack(app, "golden-signals-sample-app-dev")
app.synth()
```

# Contributing

See [CONTRIBUTING](./CONTRIBUTING.md) for more information.

# License Summary

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for our project's licensing.
