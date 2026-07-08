from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    hcp_name: str = Field("", description="Healthcare Professional name")
    interaction_type: str = Field("", description="Type of interaction: Call, Email, Meeting, Other")
    interaction_date: Optional[str] = Field("", description="Date of interaction (YYYY-MM-DD)")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    sentiment: Optional[str] = Field("", description="Sentiment: Positive, Neutral, Negative")
    specialty: Optional[str] = Field("", description="HCP specialty")
    region: Optional[str] = Field("", description="HCP region/location")
    products_discussed: Optional[str] = Field("", description="Products discussed")
    key_discussion_points: Optional[str] = Field("", description="Key discussion points")
    action_items: Optional[str] = Field("", description="Action items")
    follow_up_date: Optional[str] = Field("", description="Follow-up date (YYYY-MM-DD)")
    additional_notes: Optional[str] = Field("", description="Additional notes")


class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[str] = None
    duration_minutes: Optional[int] = None
    sentiment: Optional[str] = None
    specialty: Optional[str] = None
    region: Optional[str] = None
    products_discussed: Optional[str] = None
    key_discussion_points: Optional[str] = None
    action_items: Optional[str] = None
    follow_up_date: Optional[str] = None
    additional_notes: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_name: str
    interaction_type: str
    interaction_date: date
    duration_minutes: Optional[int] = None
    sentiment: Optional[str] = None
    specialty: Optional[str] = None
    region: Optional[str] = None
    products_discussed: Optional[str] = None
    key_discussion_points: Optional[str] = None
    action_items: Optional[str] = None
    follow_up_date: Optional[date] = None
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    interaction: InteractionCreate
    tool_called: str
    conversation_id: str


class ValidationResult(BaseModel):
    is_valid: bool
    missing_fields: list[str]
    suggestions: list[str]


class HcpSearchResult(BaseModel):
    name: str
    specialty: str
    region: str
    last_interaction: Optional[str] = None


class NextStepsSuggestion(BaseModel):
    suggestion: str
    priority: str
    timeframe: str
