"""
Auto-generated Pydantic models for atlassian-rovo's MCP. Supported tools are:
getTeamworkGraphContext : Retrieves connected context from Teamwork Graph for any Atlassian entity. Returns all relationships and linked objects within one traversal – including cross-product and third-party connections. Use when the answer requires connections between entities, not just a single entity's fields.

Supported entry points:

Jira: issues, projects, sprints, versions, comments

Confluence: pages, blogposts, whiteboards, databases, spaces

Goals, Projects, Focus Areas, Tags and updates

People: users, teams, organisations

DevOps: PRs, repos, deployments, services, builds, designs

Loom: videos, meetings

Compass: components

Incidents, conversations, calendar events, external documents

After calling this tool, call getTeamworkGraphObject on returned ARIs to get full content.
getTeamworkGraphObject : Fetches the entire available data for one or more objects (Atlassian or third-party) using their ARIs or URLs. Use for the objects gathered from getTeamworkGraphContext tool.
addTeamworkGraphContext : Adds a relationship between two entities in the Teamwork Graph (e.g. linking two Jira work items, marking one as blocking another, attaching a remote link, or connecting a Jira work item to an Atlas project or goal).

Example BoundMCPAgentConfig (JSON) for this provider:
 {
   "server": {
     "type": "http",
     "url": "https://mcp.atlassian.com/v1/mcp/authv2"
   },
   "tools": [
     {
       "name": "getTeamworkGraphContext",
       "input_class_name": "rustic_ai.mcp.connectors.atlassian-rovo.GetteamworkgraphcontextInput"
     },
     {
       "name": "getTeamworkGraphObject",
       "input_class_name": "rustic_ai.mcp.connectors.atlassian-rovo.GetteamworkgraphobjectInput"
     },
     {
       "name": "addTeamworkGraphContext",
       "input_class_name": "rustic_ai.mcp.connectors.atlassian-rovo.AddteamworkgraphcontextInput"
     }
   ]
 }

"""  # noqa

from enum import Enum
from typing import Annotated, Optional

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel


class ObjectType(Enum):
    """
    Type of object to fetch context for.
    """

    ATLASSIAN_GOAL = "AtlassianGoal"
    ATLASSIAN_GOAL_UPDATE = "AtlassianGoalUpdate"
    ATLASSIAN_HOME_COMMENT = "AtlassianHomeComment"
    ATLASSIAN_HOME_TAG = "AtlassianHomeTag"
    ATLASSIAN_PROJECT = "AtlassianProject"
    ATLASSIAN_PROJECT_UPDATE = "AtlassianProjectUpdate"
    ATLASSIAN_TEAM = "AtlassianTeam"
    ATLASSIAN_USER = "AtlassianUser"
    COMPASS_COMPONENT = "CompassComponent"
    CONFLUENCE_BLOG_POST = "ConfluenceBlogPost"
    CONFLUENCE_COMMENT = "ConfluenceComment"
    CONFLUENCE_DATABASE = "ConfluenceDatabase"
    CONFLUENCE_PAGE = "ConfluencePage"
    CONFLUENCE_SPACE = "ConfluenceSpace"
    CONFLUENCE_WHITEBOARD = "ConfluenceWhiteboard"
    EXTERNAL_CALENDAR_EVENT = "ExternalCalendarEvent"
    EXTERNAL_CONVERSATION = "ExternalConversation"
    EXTERNAL_DEPLOYMENT = "ExternalDeployment"
    EXTERNAL_DESIGN = "ExternalDesign"
    EXTERNAL_DOCUMENT = "ExternalDocument"
    EXTERNAL_ORGANISATION = "ExternalOrganisation"
    EXTERNAL_POSITION = "ExternalPosition"
    EXTERNAL_PULL_REQUEST = "ExternalPullRequest"
    EXTERNAL_REPOSITORY = "ExternalRepository"
    EXTERNAL_SERVICE = "ExternalService"
    FOCUS_FOCUS_AREA = "FocusFocusArea"
    JIRA_SPACE = "JiraSpace"
    JIRA_SPRINT = "JiraSprint"
    JIRA_VERSION = "JiraVersion"
    JIRA_WORK_ITEM = "JiraWorkItem"
    JIRA_WORK_ITEM_COMMENT = "JiraWorkItemComment"
    LOOM_MEETING = "LoomMeeting"
    LOOM_MEETING_RECURRENCE = "LoomMeetingRecurrence"
    LOOM_VIDEO = "LoomVideo"


class DetailLevel(Enum):
    """
    'summary' (counts/metadata) or 'full' (detailed content).
    """

    SUMMARY = "summary"
    FULL = "full"


class RelationshipType(RootModel[str]):
    root: Annotated[str, Field(max_length=200)]


class TargetObjectType(RootModel[str]):
    root: Annotated[str, Field(max_length=200)]


class TimeRange(BaseModel):
    """
    Optional time range to filter relationships by creation or update time.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    from_: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="from",
            description='ISO 8601 date-time string for the start of the time range (e.g. "2025-01-01T00:00:00Z").',
        ),
    ] = None
    to: Annotated[
        Optional[AwareDatetime],
        Field(description='ISO 8601 date-time string for the end of the time range (e.g. "2025-12-31T23:59:59Z").'),
    ] = None


class GetTeamworkGraphContextInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    cloudId: Annotated[str, Field(description="Cloud ID (UUID or site URL)")]
    objectType: Annotated[ObjectType, Field(description="Type of object to fetch context for.")]
    objectIdentifier: Annotated[
        str,
        Field(
            description=(
                "Identifier for the object. It could be a key (e.g. ENG-1234), ID, ARI, or full URL; format depends on"
                " objectType."
            ),
            max_length=500,
        ),
    ]
    detailLevel: Annotated[
        Optional[DetailLevel], Field(description="'summary' (counts/metadata) or 'full' (detailed content).")
    ] = DetailLevel.SUMMARY
    relationshipTypes: Annotated[
        Optional[list[RelationshipType]],
        Field(
            description=(
                "Filter full results to specific relationship types to save tokens (e.g."
                " 'jira-work-item-links-external-build' for Jira work items)."
            ),
            max_length=20,
        ),
    ] = None
    targetObjectTypes: Annotated[
        Optional[list[TargetObjectType]],
        Field(
            description=(
                "Filter results to only include relationships targeting specific object types (e.g. AtlassianUser,"
                " ConfluenceComment)."
            ),
            max_length=20,
        ),
    ] = None
    timeRange: Annotated[
        Optional[TimeRange],
        Field(description="Optional time range to filter relationships by creation or update time."),
    ] = None
    first: Annotated[Optional[int], Field(description="Max number of related items to return.", le=50)] = 50
    after: Annotated[Optional[str], Field(description="Pagination cursor for fetching the next page of results.")] = (
        None
    )


class Object(RootModel[str]):
    root: Annotated[str, Field(max_length=500)]


class GetTeamworkGraphObjectInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    cloudId: Annotated[str, Field(description="Cloud ID (UUID or site URL)")]
    objects: Annotated[
        list[Object],
        Field(
            description=(
                "A list of object identifiers to hydrate. Supports both ARIs (e.g., 'ari:cloud:jira::issue/123') and"
                " full browser URLs (e.g., 'https://mysite.atlassian.net/browse/PROJ-1')."
            ),
            max_length=25,
        ),
    ]


class RelationshipType1(Enum):
    """
    Type of relationship to create. Determines which entity types 'objectIdentifier' and 'targetObjectIdentifier' must resolve to.
    """

    JIRA_WORK_ITEM_LINKS_JIRA_WORK_ITEM = "jira-work-item-links-jira-work-item"
    JIRA_WORK_ITEM_BLOCKS_JIRA_WORK_ITEM = "jira-work-item-blocks-jira-work-item"
    JIRA_WORK_ITEM_LINKS_JIRA_WORK_ITEM_REMOTE_LINK = "jira-work-item-links-jira-work-item-remote-link"
    JIRA_WORK_ITEM_TRACKS_ATLASSIAN_PROJECT = "jira-work-item-tracks-atlassian-project"
    JIRA_WORK_ITEM_CONTRIBUTES_TO_ATLASSIAN_GOAL = "jira-work-item-contributes-to-atlassian-goal"


class AddTeamworkGraphContextInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    cloudId: Annotated[str, Field(description="Cloud ID (UUID or site URL)")]
    relationshipType: Annotated[
        RelationshipType1,
        Field(
            description=(
                "Type of relationship to create. Determines which entity types 'objectIdentifier' and"
                " 'targetObjectIdentifier' must resolve to."
            )
        ),
    ]
    objectIdentifier: Annotated[
        str,
        Field(
            description=(
                "Identifier of the source entity. Accepts an ARI, a full URL, or a stable key (e.g. ENG-123 for a Jira"
                " work item). Format depends on relationshipType."
            ),
            max_length=500,
        ),
    ]
    targetObjectIdentifier: Annotated[
        str,
        Field(
            description=(
                "Identifier of the target entity. Accepts an ARI, a full URL, or a stable key (e.g. ATLAS-20426 for an"
                " Atlas project). Format depends on relationshipType."
            ),
            max_length=500,
        ),
    ]
    title: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional display label for the target. Used by relationships that surface a title (e.g. remote links);"
                " ignored otherwise."
            ),
            max_length=500,
        ),
    ] = None
