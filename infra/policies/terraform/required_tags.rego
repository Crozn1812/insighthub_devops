package main

import rego.v1

required_tags := {"project", "environment", "owner", "cost_center", "managed_by"}

is_managed_aws(resource) if {
    object.get(resource, "mode", "managed") == "managed"
    startswith(resource.type, "aws_")
}

deny contains message if {
    resource := input.resource_changes[_]
    is_managed_aws(resource)
    tags := object.get(resource.change.after, "tags", {})
    missing := required_tags - object.keys(tags)
    count(missing) > 0
    message := sprintf("required tags missing on %s.%s: %v", [resource.type, resource.name, sort(missing)])
}
