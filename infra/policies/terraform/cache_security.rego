package main

import rego.v1

is_cache(resource) if {
    resource.type == "aws_elasticache_replication_group"
}

deny contains message if {
    resource := input.resource_changes[_]
    is_cache(resource)
    object.get(resource.change.after, "at_rest_encryption_enabled", false) != true
    message := sprintf("cache at-rest encryption required on %s", [resource.name])
}

deny contains message if {
    resource := input.resource_changes[_]
    is_cache(resource)
    object.get(resource.change.after, "transit_encryption_enabled", false) != true
    message := sprintf("cache in-transit encryption required on %s", [resource.name])
}

deny contains message if {
    resource := input.resource_changes[_]
    is_cache(resource)
    object.get(resource.change.after, "publicly_accessible", false) == true
    message := sprintf("public cache network forbidden on %s", [resource.name])
}
