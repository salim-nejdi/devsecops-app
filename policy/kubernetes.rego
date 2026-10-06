package main

deny contains msg if {
    input.kind == "Deployment"

    container := input.spec.template.spec.containers[_]

    container.securityContext.privileged == true

    msg := sprintf(
        "Container %q is privileged",
        [container.name]
    )
}

deny contains msg if {
    input.kind == "Deployment"

    container := input.spec.template.spec.containers[_]

    not contains(container.image, "@sha256:")

    msg := sprintf(
        "Container %q does not use an immutable image digest: %q",
        [container.name, container.image]
    )
}

deny contains msg if {
    input.kind == "Deployment"

    not input.spec.template.spec.securityContext.runAsNonRoot == true

    msg := "Pod securityContext.runAsNonRoot must be true"
}

deny contains msg if {
    input.kind == "Deployment"

    container := input.spec.template.spec.containers[_]

    not container.securityContext.allowPrivilegeEscalation == false

    msg := sprintf(
        "Container %q must set allowPrivilegeEscalation to false",
        [container.name]
    )
}
