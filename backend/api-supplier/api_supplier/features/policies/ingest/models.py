from pydantic import BaseModel, Field


class IngestPolicyRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1)
    policy_type: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=50)
    effective_date: str = Field(min_length=1, max_length=50)


class IngestPolicyResponse(BaseModel):
    document_id: str
    chunks_indexed: int
    embedding_dimensions: int
