import os
import questionary
import requests
from flipt_migrate.models.flipt import (
    Collection,
    Document,
    Flag,
    FlagType,
    Variant,
    Segment,
    SegmentMatchType,
    Constraint,
    ConstraintOperator,
    ConstraintComparisonType,
    Rule,
    Distribution,
)


def transformer():
    api_key = os.getenv("LAUNCHDARKLY_API_KEY")
    if not api_key:
        api_key = questionary.password("LaunchDarkly API Key:").ask() or ""

    project_key = os.getenv("LAUNCHDARKLY_PROJECT_KEY")
    if not project_key:
        project_key = questionary.text("LaunchDarkly Project Key:", "default").ask()

    return Transformer(api_key, project_key)


class Transformer:
    BASE_URL = "https://app.launchdarkly.com/api/v2"

    # LaunchDarkly API uses different operators for constraints
    # We dont support all of them, so we will map them to the closest match
    OPS = {
        "endsWith": ConstraintOperator.suffix,
        "startsWith": ConstraintOperator.prefix,
        "contains": ConstraintOperator.equals,
    }

    def __init__(self, api_key, project_key=None):
        self.api_key = api_key
        self.project_key = project_key or "default"

    def transform(self) -> Collection:
        out = Collection(namespaces={})

        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}

        # TODO: support pagination
        response = requests.get(
            f"{self.BASE_URL}/projects/{self.project_key}/environments", headers=headers
        )
        if response.status_code != 200:
            raise Exception(
                f"Request to LaunchDarkly API failed with status code: {response.status_code}"
            )

        environment_data = response.json()
        # environment loop
        for environment in environment_data["items"]:
            env_key = environment["key"]
            out.namespaces[env_key] = Document(flags=[], segments=[])

            # get all global segments for this environment
            # TODO: support pagination
            response = requests.get(
                f"{self.BASE_URL}/segments/{self.project_key}/{env_key}",
                headers=headers,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Request to LaunchDarkly API failed with status code: {response.status_code}"
                )

            segment_data = response.json()

            for s in segment_data["items"]:
                segment = Segment(
                    key=s["key"],
                    name=s["name"],
                    description=s["description"] if "description" in s else "",
                    match_type=SegmentMatchType.all,
                    constraints=[],
                )

                for rule in s["rules"]:
                    for clause in rule["clauses"]:
                        segment.constraints.append(
                            Constraint(
                                type=ConstraintComparisonType.string,
                                property=clause["attribute"],
                                operator=self.OPS[clause["op"]]
                                if clause["op"] in self.OPS
                                else clause["op"],
                                value=clause["values"][0],
                            )
                        )

                # add global segment to namespace
                out.namespaces[env_key].segments.append(segment)

        # get all flags
        # TODO: support pagination
        response = requests.get(
            f"{self.BASE_URL}/flags/{self.project_key}", headers=headers
        )
        if response.status_code != 200:
            raise Exception(
                f"Request to LaunchDarkly API failed with status code: {response.status_code}"
            )

        flags_data = response.json()
        # flag loop
        for f in flags_data["items"]:
            response = requests.get(
                f"{self.BASE_URL}/flags/{self.project_key}/{f['key']}", headers=headers
            )
            if response.status_code != 200:
                raise Exception(
                    f"Request to LaunchDarkly API failed with status code: {response.status_code}"
                )

            flag_data = response.json()

            # We do not support percentage based rollouts on segmentation for "boolean"
            # but LaunchDarkly does. So we will use the VARIANT_FLAG_TYPE for all flags.
            flag = Flag(
                key=flag_data["key"],
                name=flag_data["name"],
                description=flag_data["description"],
                enabled=False,
                type=FlagType.variant,
                variants=[],
                rules=[],
            )

            # variant loop
            for v in flag_data["variations"]:
                flag.variants.append(
                    Variant(
                        key=str(v["value"]),
                        name=str(
                            v["value"]
                        ),  # LaunchDarkly does not support names for variants
                        description=v["description"] if "description" in v else "",
                    )
                )

            environment_data = flag_data["environments"]
            # environment loop per flag
            for env_key, environment in environment_data.items():
                flag_segment_count = 0

                # rule loop per environment
                for rule in environment["rules"]:
                    segment = Segment(
                        key=f"{flag.key}-{flag_segment_count}",
                        name=f"{flag.name}-{flag_segment_count}",
                        description="",
                        constraints=[],
                    )
                    flag_segment_count += 1

                    # clause loop per rule
                    for clause in rule["clauses"]:
                        if clause["contextKind"] != "user":
                            # TODO: support segment matching
                            continue

                        segment.constraints.append(
                            Constraint(
                                type=ConstraintComparisonType.string,
                                property=clause["attribute"],
                                operator=self.OPS[clause["op"]]
                                if clause["op"] in self.OPS
                                else clause["op"],
                                value=clause["values"][0],
                            )
                        )

                    # add segment to namespace
                    out.namespaces[env_key].segments.append(segment)

                    # add rule to flag with segment
                    distributions: list[Distribution] = []
                    if "rollout" in rule:
                        for rollout in rule["rollout"]["variations"]:
                            distributions.append(
                                Distribution(
                                    variant=flag.variants[rollout["variation"]].key,
                                    rollout=float(rollout["weight"] / 1000),
                                )
                            )
                    else:
                        distributions.append(
                            Distribution(
                                variant=flag.variants[rule["variation"]].key,
                                rollout=100.0,
                            )
                        )

                    flag.rules.append(
                        Rule(
                            segment=segment.key,
                            rank=flag_segment_count,
                            distributions=distributions,
                        )
                    )

                # add flag to namespace
                out.namespaces[env_key].flags.append(flag)

        return out
