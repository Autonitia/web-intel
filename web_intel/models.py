"""
Pydantic models that define the extraction schema.

These models serve double duty:
  1. OpenAI structured outputs uses .model_json_schema() to enforce the shape
  2. The response is parsed directly into typed Python objects via .model_validate()

To add a new field: just add it here. No prompt changes needed.
"""

from pydantic import BaseModel, Field


class Founder(BaseModel):
    name: str = Field(description="Full name of the founder or team member")
    role: str = Field(description="Their title or role at the company")
    linkedin: str = Field(default="", description="LinkedIn profile URL if found on the page")


class SocialLinks(BaseModel):
    linkedin: str = ""
    twitter: str = ""
    github: str = ""
    discord: str = ""
    reddit: str = ""
    medium: str = ""
    youtube: str = ""
    website: str = ""
    crunchbase: str = ""


class PricingPlan(BaseModel):
    plan: str = Field(description="Name of the pricing tier")
    price: str = Field(description="Price as displayed, e.g. '$17/mo'")
    features: list[str] = Field(default_factory=list)


class Contact(BaseModel):
    email: str = ""
    phone: str = ""
    address: str = ""


class CompanyIntel(BaseModel):
    """The full extraction schema. OpenAI structured outputs guarantees this shape."""
    company_name: str = ""
    description: str = Field(default="", description="What the company does, products, value proposition")
    founders: list[Founder] = Field(default_factory=list)
    social_media_links: SocialLinks = Field(default_factory=SocialLinks)
    pricing: list[PricingPlan] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    contact: Contact = Field(default_factory=Contact)
    year_founded: str = ""
    headquarters: str = ""
    is_open_source: bool = False
