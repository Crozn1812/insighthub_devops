package main

import rego.v1

deny contains message if {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    object.get(resource.change.after, "storage_encrypted", false) != true
    message := sprintf("database encryption required on %s", [resource.name])
}

deny contains message if {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    object.get(resource.change.after, "publicly_accessible", true) != false
    message := sprintf("public database forbidden on %s", [resource.name])
}
