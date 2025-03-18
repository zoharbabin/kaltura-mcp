"""
Reporting prompts for the Kaltura-MCP Server intelligent prompting library.

This module provides prompts for reporting and analytics tasks such as content performance analysis,
user engagement reporting, trend identification, and recommendation generation.
"""

from .base import BasePrompt


class ReportingPrompts:
    """Collection of reporting prompts."""

    @staticmethod
    def trend_identification() -> BasePrompt:
        """Create a prompt for trend identification."""
        prompt = BasePrompt(
            name="trend_identification",
            description="Identify and analyze significant trends in platform usage and content performance",
        )

        prompt.set_system_message(
            """
You are a trend analysis specialist for a video platform. Your task is to identify
and analyze significant trends in platform usage, content performance, and user behavior.

When identifying and analyzing trends:
1. Look for meaningful patterns across different metrics and time periods
2. Distinguish between short-term fluctuations and long-term trends
3. Identify correlations between different metrics and potential causal relationships
4. Consider external factors that might influence the observed trends
5. Assess the implications of trends for content strategy and platform development
6. Provide actionable insights based on the identified trends

Your analysis should be data-driven, insightful, and focused on actionable recommendations.
"""
        )

        prompt.set_user_message_template(
            """
Please identify and analyze trends in the following data:

Time Period: {time_period}
Data Scope: {data_scope}

Usage Metrics Over Time:
{usage_metrics}

Content Metrics Over Time:
{content_metrics}

User Behavior Metrics Over Time:
{user_behavior_metrics}

External Factors:
{external_factors}

Additional context: {additional_context}

Please provide a comprehensive trend analysis with insights and recommendations.
"""
        )

        prompt.add_example(
            user_message="""
Please identify and analyze trends in the following data:

Time Period: Last 12 Months (April 2024 - March 2025)
Data Scope: Enterprise Learning Platform (Corporate Training)

Usage Metrics Over Time:
- Monthly Active Users:
  Apr: 8,450 | May: 8,620 | Jun: 9,150 | Jul: 9,340 | Aug: 9,280 | Sep: 10,120
  Oct: 10,580 | Nov: 10,890 | Dec: 10,450 | Jan: 11,240 | Feb: 12,180 | Mar: 12,650
- Average Weekly Sessions per User:
  Apr: 2.1 | May: 2.2 | Jun: 2.3 | Jul: 2.2 | Aug: 2.1 | Sep: 2.4
  Oct: 2.5 | Nov: 2.6 | Dec: 2.3 | Jan: 2.7 | Feb: 2.8 | Mar: 2.9
- Average Session Duration (minutes):
  Apr: 18.4 | May: 18.2 | Jun: 17.9 | Jul: 17.5 | Aug: 17.2 | Sep: 16.8
  Oct: 16.5 | Nov: 16.2 | Dec: 15.9 | Jan: 15.5 | Feb: 15.2 | Mar: 14.8
- Mobile Usage (%):
  Apr: 22% | May: 23% | Jun: 24% | Jul: 26% | Aug: 27% | Sep: 29%
  Oct: 31% | Nov: 33% | Dec: 34% | Jan: 36% | Feb: 38% | Mar: 40%

Content Metrics Over Time:
- Monthly Content Uploads:
  Apr: 1,240 | May: 1,320 | Jun: 1,380 | Jul: 1,290 | Aug: 1,350 | Sep: 1,520
  Oct: 1,640 | Nov: 1,720 | Dec: 1,580 | Jan: 1,840 | Feb: 1,920 | Mar: 2,050
- Average Video Length (minutes):
  Apr: 22.5 | May: 21.8 | Jun: 20.4 | Jul: 19.6 | Aug: 18.7 | Sep: 17.5
  Oct: 16.8 | Nov: 15.9 | Dec: 15.2 | Jan: 14.5 | Feb: 13.8 | Mar: 12.9
- Interactive Content (% of uploads):
  Apr: 12% | May: 14% | Jun: 15% | Jul: 18% | Aug: 21% | Sep: 24%
  Oct: 28% | Nov: 32% | Dec: 35% | Jan: 39% | Feb: 42% | Mar: 46%
- Content Categories (% of uploads):
  * Technical Skills:
    Apr: 35% | May: 36% | Jun: 36% | Jul: 37% | Aug: 38% | Sep: 38%
    Oct: 39% | Nov: 39% | Dec: 40% | Jan: 40% | Feb: 41% | Mar: 41%
  * Soft Skills:
    Apr: 25% | May: 26% | Jun: 27% | Jul: 28% | Aug: 29% | Sep: 30%
    Oct: 30% | Nov: 31% | Dec: 31% | Jan: 32% | Feb: 32% | Mar: 33%
  * Compliance:
    Apr: 30% | May: 28% | Jun: 27% | Jul: 25% | Aug: 23% | Sep: 22%
    Oct: 21% | Nov: 20% | Dec: 19% | Jan: 18% | Feb: 17% | Mar: 16%
  * Onboarding:
    Apr: 10% | May: 10% | Jun: 10% | Jul: 10% | Aug: 10% | Sep: 10%
    Oct: 10% | Nov: 10% | Dec: 10% | Jan: 10% | Feb: 10% | Mar: 10%

User Behavior Metrics Over Time:
- Content Completion Rate:
  Apr: 62% | May: 63% | Jun: 64% | Jul: 65% | Aug: 66% | Sep: 67%
  Oct: 68% | Nov: 69% | Dec: 70% | Jan: 71% | Feb: 72% | Mar: 73%
- Quiz Participation Rate:
  Apr: 45% | May: 48% | Jun: 51% | Jul: 54% | Aug: 57% | Sep: 60%
  Oct: 63% | Nov: 66% | Dec: 68% | Jan: 71% | Feb: 74% | Mar: 76%
- Social Features Usage (comments, shares):
  Apr: 8% | May: 9% | Jun: 10% | Jul: 12% | Aug: 14% | Sep: 16%
  Oct: 18% | Nov: 20% | Dec: 22% | Jan: 24% | Feb: 26% | Mar: 28%
- Peak Usage Times:
  * Q2 2024: Weekdays 1-3pm (65%), Evenings 7-9pm (25%), Other (10%)
  * Q3 2024: Weekdays 1-3pm (60%), Evenings 7-9pm (28%), Other (12%)
  * Q4 2024: Weekdays 1-3pm (55%), Evenings 7-9pm (32%), Other (13%)
  * Q1 2025: Weekdays 1-3pm (50%), Evenings 7-9pm (35%), Other (15%)

External Factors:
- Platform Updates:
  * May 2024: Enhanced analytics dashboard released
  * August 2024: Mobile app redesign launched
  * November 2024: Interactive content creation tools released
  * February 2025: Social learning features expanded
- Industry Events:
  * June 2024: Major industry conference with platform showcase
  * October 2024: Learning technology awards (platform won "Best Enterprise Solution")
  * January 2025: Annual HR technology report recommending the platform
- Market Factors:
  * Ongoing hybrid work policies across client organizations
  * Increasing emphasis on microlearning in corporate training
  * Growing demand for mobile learning solutions
  * Rising competition in enterprise learning platforms

Additional context: The platform serves primarily large enterprises (1000+ employees) for employee training and development. The company has been actively promoting mobile learning and interactive content features over the past year. Customer feedback has indicated growing interest in shorter, more engaging content formats and social learning capabilities.
""",
            assistant_message="""
# Enterprise Learning Platform Trend Analysis: April 2024 - March 2025

## Executive Summary

Analysis of the past 12 months reveals five transformative trends reshaping enterprise learning: (1) significant platform growth with 50% increase in active users, (2) fundamental shift toward mobile and after-hours learning, (3) dramatic evolution in content format preferences toward shorter, interactive content, (4) changing content focus from compliance to skills development, and (5) increasing social engagement. These trends align with broader market shifts toward microlearning, mobile accessibility, and social learning. Strategic recommendations focus on accelerating mobile optimization, expanding interactive content capabilities, and developing a comprehensive social learning framework.

## Key Trend Analysis

### 1. Platform Growth & Engagement Transformation

**User Base Expansion**
- **Monthly Active Users**: Increased from 8,450 to 12,650 (+50% YoY)
- **Growth Pattern**: Consistent upward trajectory with two notable acceleration periods:
  * Jun-Sep 2024: +10.6% (following industry conference)
  * Jan-Mar 2025: +20.1% (following HR technology report)

**Engagement Intensity**
- **Session Frequency**: Increased from 2.1 to 2.9 weekly sessions per user (+38%)
- **Total Platform Sessions**: Increased by ~107% (combining user growth and session frequency)
- **Session Duration**: Decreased from 18.4 to 14.8 minutes (-19.6%)
- **Net Engagement Time**: Despite shorter sessions, total engagement time increased by ~66% due to more frequent sessions

**Correlation Analysis**
- Strong positive correlation (r=0.92) between interactive content availability and session frequency
- Strong negative correlation (r=-0.89) between video length and session duration
- Moderate correlation (r=0.76) between platform updates and user growth spikes

### 2. Mobile Learning Revolution

**Mobile Usage Trajectory**
- **Adoption Rate**: Increased from 22% to 40% of all sessions (+82% YoY)
- **Growth Pattern**: Steady month-over-month growth with acceleration following:
  * August 2024 mobile app redesign: +7% over next three months
  * February 2025 social features: +6% over next two months

**Usage Pattern Shift**
- **Peak Usage Times**: Significant shift from workday to evening hours
  * Workday usage (1-3pm): Decreased from 65% to 50% of sessions
  * Evening usage (7-9pm): Increased from 25% to 35% of sessions
  * Other times: Increased from 10% to 15% of sessions

**Implications**
- Learning increasingly occurring outside traditional work hours
- Mobile becoming primary access method for evening/flexible learning
- Trend toward "learning in the flow of life" rather than just "learning in the flow of work"

### 3. Content Format Evolution

**Video Length Transformation**
- **Average Duration**: Decreased from 22.5 to 12.9 minutes (-42.7%)
- **Trend Consistency**: Steady month-over-month reduction without plateauing
- **Correlation**: Coincides with increasing completion rates (62% → 73%)

**Interactive Content Surge**
- **Adoption Rate**: Increased from 12% to 46% of all uploads (+283%)
- **Acceleration Point**: Significant uptick following November 2024 interactive tools release
- **Impact**: Strong correlation with increased quiz participation (45% → 76%)

**Content Volume Growth**
- **Monthly Uploads**: Increased from 1,240 to 2,050 (+65.3%)
- **Growth Pattern**: Consistent upward trend with seasonal fluctuation (December dip)

### 4. Content Focus Rebalancing

**Category Shift Analysis**
- **Technical Skills**: Steady increase from 35% to 41% (+6 percentage points)
- **Soft Skills**: Moderate increase from 25% to 33% (+8 percentage points)
- **Compliance**: Significant decrease from 30% to 16% (-14 percentage points)
- **Onboarding**: Remained constant at 10%

**Trend Implications**
- Strategic pivot from mandatory compliance training to skill development
- Growing emphasis on balanced technical and soft skills development
- Stable onboarding content suggests consistent new employee processes

### 5. Social Learning Emergence

**Social Engagement Growth**
- **Social Feature Usage**: Increased from 8% to 28% of users (+250%)
- **Growth Pattern**: Consistent month-over-month growth with acceleration following February 2025 social features expansion

**Correlation Analysis**
- Strong correlation between social feature usage and:
  * Quiz participation rates (r=0.91)
  * Content completion rates (r=0.87)
  * Session frequency (r=0.84)

## Strategic Implications & Recommendations

### 1. Mobile-First Strategy Acceleration

**Current State Assessment**
- Mobile usage trending toward becoming primary access method
- Evening learning becoming increasingly significant
- Mobile app redesign showing positive impact

**Strategic Recommendations**
- **Mobile Content Optimization** (High Priority)
  * Develop mobile-first content templates optimized for smaller screens
  * Implement auto-formatting for existing content
  * Create mobile-specific interactive elements

- **Mobile Learning Pathways** (Medium Priority)
  * Design learning journeys specifically for mobile consumption
  * Implement "micro-moments" learning approach for fragmented mobile sessions
  * Develop offline capabilities for commuter learning scenarios

### 2. Content Strategy Realignment

**Current State Assessment**
- Shorter, interactive content showing superior engagement metrics
- Technical and soft skills content growing in importance
- Compliance content decreasing but still necessary

**Strategic Recommendations**
- **Microlearning Framework** (High Priority)
  * Establish 5-10 minute standard for new content development
  * Create templates for converting existing longer content
  * Develop microlearning instructional design guidelines

- **Interactive Content Expansion** (High Priority)
  * Extend interactive capabilities beyond quizzes (simulations, branching scenarios)
  * Create interactive templates for different learning objectives
  * Implement interactive elements in at least 60% of new content

- **Balanced Content Portfolio** (Medium Priority)
  * Maintain 40/30/20/10 ratio for Technical/Soft/Compliance/Onboarding
  * Develop integrated pathways combining technical and soft skills
  * Create more engaging approaches to compliance content

### 3. Social Learning Ecosystem Development

**Current State Assessment**
- Social features showing strong correlation with engagement metrics
- Recent expansion demonstrating positive early results
- Significant growth potential based on current trajectory

**Strategic Recommendations**
- **Community-Based Learning** (High Priority)
  * Implement learning cohorts and peer groups
  * Develop discussion-based learning activities
  * Create expert networks and mentoring frameworks

- **Social Content Creation** (Medium Priority)
  * Enable collaborative content development
  * Implement user-generated content workflows with quality controls
  * Create peer review and social curation mechanisms

- **Recognition Framework** (Medium Priority)
  * Develop social recognition for learning achievements
  * Implement contribution badges and expertise indicators
  * Create leaderboards and team-based learning competitions

### 4. Analytics & Personalization Enhancement

**Current State Assessment**
- Rich data available but limited evidence of personalization
- Engagement patterns showing distinct user segments
- Content preferences becoming increasingly differentiated

**Strategic Recommendations**
- **Advanced Analytics Implementation** (High Priority)
  * Develop predictive models for learning outcomes
  * Implement content effectiveness scoring
  * Create engagement risk identification system

- **Personalization Engine** (Medium Priority)
  * Develop AI-driven content recommendations
  * Implement adaptive learning pathways
  * Create personalized learning goals and tracking

## Implementation Roadmap

### Immediate Actions (Next 30 Days)
1. Conduct mobile user experience audit
2. Develop microlearning templates for content conversion
3. Implement basic social learning features in high-engagement courses
4. Begin compliance content redesign as microlearning modules

### Short-Term Initiatives (60-90 Days)
1. Launch mobile content optimization project
2. Implement interactive content templates
3. Develop social learning community guidelines and structure
4. Create analytics dashboard for content effectiveness

### Medium-Term Strategy (4-6 Months)
1. Implement personalization engine for content recommendations
2. Develop comprehensive social learning ecosystem
3. Complete conversion of high-priority content to microlearning format
4. Launch advanced mobile features (offline learning, mobile notifications)

## Conclusion

The enterprise learning platform is undergoing a fundamental transformation from traditional e-learning to a mobile-friendly, interactive, social learning ecosystem. The data shows clear user preference for shorter, more engaging content consumed in flexible time periods across multiple devices. By accelerating the platform's evolution toward microlearning, mobile optimization, and social engagement, the company can capitalize on these trends to drive further growth and deeper learning impact.
""",
        )

        prompt.add_required_tool("kaltura.media.list")
        prompt.add_required_tool("kaltura.user.list")
        prompt.add_required_resource("kaltura://media/list")
        prompt.add_required_resource("kaltura://users/list")

        return prompt

    @staticmethod
    def recommendation_generation() -> BasePrompt:
        """Create a prompt for generating recommendations based on analytics."""
        prompt = BasePrompt(
            name="recommendation_generation",
            description="Generate data-driven recommendations for content strategy and platform optimization",
        )

        prompt.set_system_message(
            """
You are a strategic recommendations specialist for a video platform. Your task is to analyze
platform data and generate actionable recommendations to improve content strategy, user engagement,
and overall platform performance.

When generating recommendations:
1. Base your recommendations on the data provided, not assumptions
2. Prioritize recommendations based on potential impact and feasibility
3. Be specific and actionable, avoiding vague suggestions
4. Consider different stakeholder perspectives (content creators, users, administrators)
5. Provide clear rationales for each recommendation
6. Suggest metrics to measure the success of each recommendation

Your recommendations should be practical, data-driven, and aligned with business objectives.
"""
        )

        prompt.set_user_message_template(
            """
Please generate strategic recommendations based on the following data:

Business Context:
- Platform Type: {platform_type}
- Primary Objectives: {primary_objectives}
- Target Audience: {target_audience}

Performance Data:
{performance_data}

Current Challenges:
{current_challenges}

Previous Initiatives:
{previous_initiatives}

Resource Constraints:
{resource_constraints}

Additional context: {additional_context}

Please provide comprehensive, prioritized recommendations with implementation guidance.
"""
        )

        prompt.add_required_tool("kaltura.media.list")
        prompt.add_required_tool("kaltura.user.list")
        prompt.add_required_resource("kaltura://media/list")
        prompt.add_required_resource("kaltura://users/list")

        return prompt
