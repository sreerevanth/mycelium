# mycelium/shared/types/genome.py
# Shared genome type definitions - used by backend API, worker, and frontend types

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..events.types import GenomeStatus, MutationType


class GenomeSpec(BaseModel):
    """
    The executable specification of a genome.
    Contains the actual code payload that gets executed in the sandbox.
    """

    language: str = "python"  # python | rust | js
    entrypoint: str  # filename of the entrypoint
    source_files: Dict[str, str]  # filename -> source code content
    dependencies: List[str] = Field(default_factory=list)  # pip/cargo/npm packages
    runtime_config: Dict[str, Any] = Field(default_factory=dict)
    interface_version: str = "1.0"  # protocol version for the genome interface


class FitnessVector(BaseModel):
    """
    Multi-dimensional fitness score for a genome.
    Each dimension is normalized to [0.0, 1.0].
    """

    correctness: float = 0.0    # passes test suite
    latency: float = 0.0        # lower latency → higher score
    memory: float = 0.0         # lower memory → higher score
    throughput: float = 0.0     # ops/sec normalized
    stability: float = 0.0      # crash-free ratio
    energy: float = 0.0         # cpu-time efficiency

    # Weighted composite score
    composite: float = 0.0

    # Raw measurements
    raw: Dict[str, Any] = Field(default_factory=dict)

    def calculate_composite(
        self,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Calculate weighted composite fitness score."""
        w = weights or {
            "correctness": 0.35,
            "latency": 0.20,
            "memory": 0.15,
            "throughput": 0.15,
            "stability": 0.10,
            "energy": 0.05,
        }
        self.composite = (
            self.correctness * w["correctness"]
            + self.latency * w["latency"]
            + self.memory * w["memory"]
            + self.throughput * w["throughput"]
            + self.stability * w["stability"]
            + self.energy * w["energy"]
        )
        return self.composite


class MutationDescriptor(BaseModel):
    """
    Describes a mutation operation applied to a genome.
    """

    mutation_type: MutationType
    description: str
    affected_files: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    parent_genome_id: str
    child_genome_id: Optional[str] = None


class GenomeWireFormat(BaseModel):
    """
    Complete genome representation for API/WebSocket transport.
    """

    id: str
    species_id: Optional[str] = None
    parent_id: Optional[str] = None
    generation: int = 0
    status: GenomeStatus
    spec: GenomeSpec
    fitness: Optional[FitnessVector] = None
    mutation_history: List[MutationDescriptor] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: float
    updated_at: float

    class Config:
        use_enum_values = True
