# Kaltura Analytics Report Types Guide

This comprehensive guide documents all available Kaltura analytics report types, their use cases, and implementation examples.

## Overview

Kaltura provides over 150 different report types for analyzing content performance, user engagement, quality of experience, and system usage. Each report type serves specific analytical needs and provides unique insights into your media platform.

## Report Categories

### 1. Content Performance Reports

#### TOP_CONTENT (1)
**Description**: Shows the most viewed/played content in your account  
**Use Case**: Identify your most popular videos, understand content performance  
**Key Metrics**: Views, plays, unique viewers, engagement rate, completion rate  
**Example**: Find top 10 most watched videos in the last month

#### CONTENT_DROPOFF (2)
**Description**: Analyzes where viewers stop watching videos  
**Use Case**: Identify problematic sections in videos, optimize content length  
**Key Metrics**: Drop-off points, viewer retention curve, engagement timeline  
**Example**: See at which timestamp most viewers leave a training video

#### CONTENT_INTERACTIONS (3)
**Description**: Tracks user interactions with video content  
**Use Case**: Measure engagement features usage (likes, shares, comments)  
**Key Metrics**: Interaction counts, interaction types, user participation  
**Example**: Count how many users shared or downloaded a video

#### USER_ENGAGEMENT_TIMELINE (34) ⭐
**Description**: Shows detailed engagement metrics throughout video timeline  
**Use Case**: Analyze which parts of videos get most engagement/replays  
**Key Metrics**: Timeline heatmap, replay segments, skip patterns  
**Example**: Find the most replayed moments in a product demo video  
**Note**: This is the report type for analyzing engagement throughout the video timeline

#### CONTENT_REPORT_REASONS (44)
**Description**: Tracks why content was reported by users  
**Use Case**: Content moderation, policy compliance monitoring  
**Key Metrics**: Report reasons, frequency, reporter demographics  
**Example**: Monitor inappropriate content reports

### 2. User Analytics Reports

#### USER_ENGAGEMENT (11)
**Description**: Overall user engagement metrics across all content  
**Use Case**: Understand user behavior patterns, measure platform stickiness  
**Key Metrics**: Session duration, content consumed, return frequency  
**Example**: Track average viewing time per user segment

#### SPECIFIC_USER_ENGAGEMENT (12)
**Description**: Detailed engagement metrics for specific users  
**Use Case**: Personalized analytics, VIP user tracking  
**Key Metrics**: Individual viewing history, preferences, engagement score  
**Example**: Analyze viewing patterns of premium subscribers

#### USER_TOP_CONTENT (13)
**Description**: Most popular content among specific user groups  
**Use Case**: Content recommendations, segment-specific insights  
**Key Metrics**: Views by segment, preferences by demographics  
**Example**: Find most watched videos by geography or user type

#### USER_CONTENT_DROPOFF (14)
**Description**: Drop-off analysis segmented by user groups  
**Use Case**: Identify content issues for specific audiences  
**Key Metrics**: Segment-specific retention, dropout patterns  
**Example**: Compare video completion rates between mobile and desktop users

#### USER_CONTENT_INTERACTIONS (15)
**Description**: User interaction patterns by segment  
**Use Case**: Engagement strategy optimization by audience  
**Key Metrics**: Interaction rates by user type, feature adoption  
**Example**: Measure comment rates for different user roles

#### USER_USAGE (17)
**Description**: Platform usage statistics by users  
**Use Case**: User adoption tracking, license utilization  
**Key Metrics**: Active users, usage frequency, feature adoption  
**Example**: Track monthly active users and their activity levels

#### UNIQUE_USERS_PLAY (35)
**Description**: Unique viewer counts and patterns  
**Use Case**: Reach measurement, audience growth tracking  
**Key Metrics**: Unique viewers, new vs returning, growth rate  
**Example**: Measure unique audience reach for marketing campaigns

### 3. Geographic & Demographic Reports

#### MAP_OVERLAY (4)
**Description**: Geographic distribution of viewers (general)  
**Use Case**: Global content strategy, CDN optimization  
**Key Metrics**: Views by location, geographic spread  
**Example**: Visualize worldwide audience distribution

#### MAP_OVERLAY_COUNTRY (36)
**Description**: Country-level geographic analytics  
**Use Case**: Country-specific content planning  
**Key Metrics**: Views by country, top countries, growth by region  
**Example**: Identify top 5 countries for your content

#### MAP_OVERLAY_REGION (37)
**Description**: Regional/state-level geographic data  
**Use Case**: Regional marketing campaigns, localized content  
**Key Metrics**: State/province breakdown, regional preferences  
**Example**: Analyze content performance by US states

#### MAP_OVERLAY_CITY (30)
**Description**: City-level viewer analytics  
**Use Case**: Local event planning, city-specific content  
**Key Metrics**: Top cities, urban vs rural distribution  
**Example**: Find which cities have highest engagement

### 4. Platform & Technology Reports

#### PLATFORMS (21)
**Description**: Device platform breakdown (mobile, desktop, TV)  
**Use Case**: Cross-platform strategy, app development priorities  
**Key Metrics**: Platform distribution, platform-specific behavior  
**Example**: Compare mobile vs desktop viewing patterns

#### OPERATING_SYSTEM (22)
**Description**: Operating system distribution  
**Use Case**: Technical compatibility planning  
**Key Metrics**: OS versions, OS-specific issues  
**Example**: Track Windows vs Mac vs Linux usage

#### OPERATING_SYSTEM_FAMILIES (32)
**Description**: OS family groupings (Windows, Apple, Android)  
**Use Case**: High-level platform strategy  
**Key Metrics**: Major OS family distribution  
**Example**: iOS vs Android mobile usage

#### BROWSERS (23)
**Description**: Web browser usage analytics  
**Use Case**: Browser compatibility testing priorities  
**Key Metrics**: Browser versions, browser-specific metrics  
**Example**: Identify most used browsers for optimization

#### BROWSERS_FAMILIES (33)
**Description**: Browser family groupings (Chrome, Firefox, Safari)  
**Use Case**: Browser support strategy  
**Key Metrics**: Major browser family usage  
**Example**: Chrome vs Safari vs Firefox distribution

### 5. Creator & Contributor Reports

#### TOP_CONTRIBUTORS (5)
**Description**: Most active content uploaders  
**Use Case**: Recognize top creators, incentive programs  
**Key Metrics**: Upload count, content performance by creator  
**Example**: Identify top 10 content contributors

#### TOP_CREATORS (20)
**Description**: Content creators ranked by performance  
**Use Case**: Creator partnerships, content quality tracking  
**Key Metrics**: Views generated, engagement rates by creator  
**Example**: Find creators generating most engagement

#### TOP_CONTENT_CREATOR (38)
**Description**: Top content pieces by specific creators  
**Use Case**: Creator portfolio analysis  
**Key Metrics**: Best performing content per creator  
**Example**: Showcase creator's most successful videos

#### TOP_CONTENT_CONTRIBUTORS (39)
**Description**: Contributors to specific content pieces  
**Use Case**: Collaboration tracking, credit attribution  
**Key Metrics**: Multi-contributor content performance  
**Example**: Track team-created content success

### 6. Distribution & Syndication Reports

#### TOP_SYNDICATION (6)
**Description**: Content distribution channel performance  
**Use Case**: Distribution strategy optimization  
**Key Metrics**: Views by distribution channel, embed performance  
**Example**: Compare owned site vs syndicated partner performance

#### TOP_PLAYBACK_CONTEXT (25)
**Description**: Context where content is played  
**Use Case**: Embed strategy, player optimization  
**Key Metrics**: Playback environment, context-specific metrics  
**Example**: In-app vs web vs embed performance

#### TOP_SOURCES (41)
**Description**: Traffic source analytics  
**Use Case**: Marketing channel optimization  
**Key Metrics**: Referrer data, source quality metrics  
**Example**: Track which sites drive most traffic

### 7. Usage & Infrastructure Reports

#### PARTNER_USAGE (201)
**Description**: Overall account usage statistics  
**Use Case**: Billing, capacity planning, usage trends  
**Key Metrics**: Storage, bandwidth, transcoding usage  
**Example**: Monitor monthly bandwidth consumption

#### VAR_USAGE (19)
**Description**: Value-added reseller usage metrics  
**Use Case**: Reseller account management  
**Key Metrics**: Sub-account usage, reseller performance  
**Example**: Track usage across reseller accounts

#### VPAAS_USAGE (26)
**Description**: Video Platform as a Service usage  
**Use Case**: API usage tracking, service utilization  
**Key Metrics**: API calls, service consumption  
**Example**: Monitor API usage patterns

#### ENTRY_USAGE (27)
**Description**: Individual entry (video) usage details  
**Use Case**: Content-specific resource tracking  
**Key Metrics**: Storage, bandwidth per video  
**Example**: Find most resource-intensive videos

#### CDN_BANDWIDTH_USAGE (64)
**Description**: Content Delivery Network bandwidth details  
**Use Case**: CDN cost optimization  
**Key Metrics**: Bandwidth by region, CDN efficiency  
**Example**: Optimize CDN configuration

### 8. Quality of Experience (QoE) Reports

#### QOE_OVERVIEW (30001)
**Description**: Overall quality metrics summary  
**Use Case**: Platform health monitoring  
**Key Metrics**: Error rates, buffering, quality scores  
**Example**: Dashboard for video quality KPIs

#### QOE_EXPERIENCE (30002)
**Description**: Detailed user experience metrics  
**Use Case**: Identify and fix quality issues  
**Key Metrics**: Startup time, buffering ratio, bitrate  
**Example**: Track video loading performance

#### QOE_ENGAGEMENT (30014)
**Description**: How quality affects engagement  
**Use Case**: Understand quality impact on viewing  
**Key Metrics**: Engagement vs quality correlation  
**Example**: Prove ROI of quality improvements

#### QOE_STREAM_QUALITY (30026)
**Description**: Technical stream quality metrics  
**Use Case**: Engineering optimization  
**Key Metrics**: Resolution distribution, bitrate adaptation  
**Example**: Monitor 4K vs HD vs SD usage

#### QOE_ERROR_TRACKING (30038)
**Description**: Error occurrence and patterns  
**Use Case**: Troubleshooting, reliability improvement  
**Key Metrics**: Error types, frequency, impact  
**Example**: Track most common playback errors

### 9. Interactive & Advanced Reports

#### USER_INTERACTIVE_VIDEO (49)
**Description**: Interactive video element usage  
**Use Case**: Measure interactive feature adoption  
**Key Metrics**: Interaction points, path analysis  
**Example**: Track quiz completion in training videos

#### INTERACTIVE_VIDEO_TOP_NODES (50)
**Description**: Most visited interactive video nodes  
**Use Case**: Optimize interactive video flow  
**Key Metrics**: Node visits, path popularity  
**Example**: Find most clicked hotspots

#### PLAYBACK_RATE (46)
**Description**: Video playback speed usage  
**Use Case**: Content pacing insights  
**Key Metrics**: Speed settings distribution  
**Example**: See how many users watch at 2x speed

#### PLAYER_RELATED_INTERACTIONS (45)
**Description**: Player control usage analytics  
**Use Case**: UI/UX optimization  
**Key Metrics**: Control usage frequency  
**Example**: Track fullscreen vs normal viewing

### 10. Real-time Reports

#### MAP_OVERLAY_COUNTRY_REALTIME (10001)
**Description**: Live geographic viewer data  
**Use Case**: Live event monitoring  
**Key Metrics**: Current viewers by country  
**Example**: Monitor live stream audience

#### USERS_OVERVIEW_REALTIME (10005)
**Description**: Real-time user activity  
**Use Case**: Live platform monitoring  
**Key Metrics**: Active users, current sessions  
**Example**: Track concurrent viewers

#### QOS_OVERVIEW_REALTIME (10006)
**Description**: Real-time quality metrics  
**Use Case**: Live quality monitoring  
**Key Metrics**: Current error rates, quality scores  
**Example**: Monitor live broadcast quality

### 11. Business Intelligence Reports

#### HIGHLIGHTS_WEBCAST (40001)
**Description**: Webcast performance highlights  
**Use Case**: Webinar success metrics  
**Key Metrics**: Peak attendance, engagement highlights  
**Example**: Post-webinar executive summary

#### ENGAGEMENT_TIMELINE_WEBCAST (40011)
**Description**: Detailed webcast engagement over time  
**Use Case**: Optimize webinar content flow  
**Key Metrics**: Minute-by-minute engagement  
**Example**: Find when attendees were most engaged

#### SELF_SERVE_USAGE (60)
**Description**: Self-service feature utilization  
**Use Case**: Feature adoption tracking  
**Key Metrics**: Feature usage rates  
**Example**: Track upload tool usage

## Implementation Examples

### Example 1: Finding Most Engaging Video Segments

To analyze which parts of a video get the most engagement:

```javascript
// Use USER_ENGAGEMENT_TIMELINE report
const reportRequest = {
  reportType: "34", // USER_ENGAGEMENT_TIMELINE
  fromDate: "2024-01-01",
  toDate: "2024-01-31",
  objectIds: "1_abc123", // specific video entry ID
  metrics: ["engagement_timeline", "replay_segments", "skip_patterns"]
};
```

### Example 2: Geographic Performance Analysis

To understand global content reach:

```javascript
// Use multiple geographic reports
const reports = [
  { reportType: "36", name: "Country Distribution" },
  { reportType: "37", name: "Regional Breakdown" },
  { reportType: "30", name: "City Hotspots" }
];
```

### Example 3: Cross-Platform User Behavior

To compare user behavior across devices:

```javascript
// Combine platform and engagement reports
const crossPlatformAnalysis = {
  reports: [
    { reportType: "21", filter: "platform" },
    { reportType: "11", filter: "platform", segment: true }
  ],
  compareMetrics: ["viewing_time", "completion_rate", "interactions"]
};
```

## Best Practices

1. **Choose the Right Report Type**: Match report type to your specific question
2. **Use Appropriate Date Ranges**: Some reports need longer periods for meaningful data
3. **Combine Reports**: Use multiple report types for comprehensive insights
4. **Consider Performance**: Some reports are resource-intensive
5. **Segment Analysis**: Use filters to drill down into specific audiences
6. **Regular Monitoring**: Set up automated reports for KPIs

## Report Type Selection Guide

| If you want to know... | Use these report types |
|------------------------|------------------------|
| Which videos are most popular | TOP_CONTENT (1) |
| Where viewers stop watching | CONTENT_DROPOFF (2), USER_ENGAGEMENT_TIMELINE (34) |
| Which parts get replayed most | USER_ENGAGEMENT_TIMELINE (34) |
| Geographic audience distribution | MAP_OVERLAY variants (4, 30, 36, 37) |
| Device/platform breakdown | PLATFORMS (21), BROWSERS (23) |
| User behavior patterns | USER_ENGAGEMENT (11), SPECIFIC_USER_ENGAGEMENT (12) |
| Content creator performance | TOP_CREATORS (20), TOP_CONTRIBUTORS (5) |
| Video quality impact | QOE reports (30001-30064) |
| Real-time metrics | REALTIME reports (10001-10015) |
| Resource usage/costs | PARTNER_USAGE (201), CDN_BANDWIDTH_USAGE (64) |