from dataclasses import dataclass, field
from typing import Dict


@dataclass
class OntologyClass:
    name: str
    description: str
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class OntologyRelation:
    name: str
    domain: str
    range: str
    description: str
    attributes: Dict[str, str] = field(default_factory=dict)


def default_ontology():
    classes = [
        OntologyClass(
            name="component",
            description="Physical components; focus on cell, anode, cathode.",
            attributes={
                "id": "string",
                "componentType": "enum(cell|anode|cathode)",
                "ratedCapacity_Ah": "float",
                "ratedVoltage_V": "float",
                "anode": "string",
                "cathode": "string",
                "chemistry": "string",
                "manufacturer": "string",
                "formFactor": "string",
            },
        ),
        OntologyClass(
            name="context",
            description="Operational/environmental context of usage or test.",
            attributes={
                "temperature_C": "float",
                "testProfile": "string",
                "drivingScenario": "string",
                "lifeStage": "string",
                "operatingMode": "string",
                "deviceEnv": "string",
                "operatingPhase": "string",
                "operatingSubphase": "string",
                "summary": "string",
            },
        ),
        OntologyClass(
            name="measurement",
            description="Runtime time-series data or lab tables (e.g., OCV).",
            attributes={
                "dataType": "enum(timeseries|table)",
                "variables": "list[string]",
                "variableRanges": "map[string,string]",
                "filePath": "string",
                "sourceFile": "string",
                "sheet": "string",
                "rowRange": "string",
                "recordId": "string",
                "recordIndex": "int",
                "samplingRate_Hz": "float",
                "timeRange": "string",
                "summary": "string",
            },
        ),
        OntologyClass(
            name="state",
            description="SOC/SOH expressed via file-based metadata/summary.",
            attributes={
                "stateType": "enum(SOC|SOH)",
                "range": "string",
                "filePath": "string",
                "sourceFile": "string",
                "recordId": "string",
                "recordIndex": "int",
                "method": "string",
                "isGroundTruth": "bool",
                "errorRange": "string",
            },
        ),
    ]

    relations = [
        OntologyRelation("isPartOf", "component", "component", "Component hierarchy."),
        OntologyRelation("hasPart", "component", "component", "Inverse of isPartOf for component hierarchy."),
        OntologyRelation("isPartOf", "context", "context", "Context hierarchy."),
        OntologyRelation("isPartOf", "measurement", "measurement", "Measurement hierarchy."),
        OntologyRelation(
            "measures",
            "measurement",
            "component",
            "Measurement targets component.",
            attributes={"signal": "string"},
        ),
        OntologyRelation(
            "estimates",
            "measurement",
            "state",
            "Measurement estimates/provides a State (e.g., SOC/SOH).",
            attributes={"method": "string"},
        ),
        OntologyRelation(
            "supplies",
            "context",
            "measurement",
            "Context supplies/provides measurement (test/usage conditions).",
            attributes={
                "evidence": "string",
                "confidence": "float",
                "temperature_C": "float",
                "operatingMode": "string",
                "operatingSubphase": "string",
                "drivingScenario": "string",
                "lifeStage": "string",
            },
        ),
        OntologyRelation(
            "degrades",
            "context",
            "component",
            "Context degrades component (degradation risk/impact).",
            attributes={
                "drivers": "list[string]",
                "direction": "enum(accelerate_degradation|slow_degradation|unknown)",
                "expectedImpact": "string",
                "degradationRisk": "string",
                "confidence": "float",
                "temperature_C": "float",
                "avgC_rate": "float",
                "peakC_rate": "float",
                "operatingMode": "string",
                "operatingSubphase": "string",
                "drivingScenario": "string",
                "lifeStage": "string",
                "evidence": "string",
            },
        ),
    ]

    return {"classes": classes, "relations": relations}
