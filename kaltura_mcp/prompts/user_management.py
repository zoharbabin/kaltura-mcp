"""
User management prompts for the Kaltura-MCP Server intelligent prompting library.

This module provides prompts for user management tasks such as role assignment,
permission management, user activity analysis, and user engagement strategies.
"""

from .base import BasePrompt


class UserManagementPrompts:
    """Collection of user management prompts."""

    @staticmethod
    def role_assignment() -> BasePrompt:
        """Create a prompt for user role assignment."""
        prompt = BasePrompt(
            name="user_role_assignment",
            description="Recommend appropriate user roles based on responsibilities and requirements",
        )

        prompt.set_system_message(
            """
You are a user management assistant for a video platform. Your task is to recommend
appropriate user roles and permissions based on the user's responsibilities and requirements.

When recommending user roles:
1. Consider the user's job function and responsibilities
2. Analyze the specific tasks they need to perform on the platform
3. Apply the principle of least privilege (users should have only the permissions they need)
4. Consider organizational hierarchy and reporting relationships
5. Balance security concerns with usability and efficiency
6. Provide clear justification for your recommendations

Recommend roles that align with the user's needs while maintaining appropriate security boundaries.
"""
        )

        prompt.set_user_message_template(
            """
Please recommend appropriate user roles for the following user:

User Information:
- Name/ID: {user_id}
- Job Title: {job_title}
- Department: {department}
- Primary Responsibilities: {responsibilities}

Platform Access Requirements:
- Content Creation: {content_creation}
- Content Publishing: {content_publishing}
- User Management: {user_management}
- Analytics Access: {analytics_access}
- System Administration: {system_administration}

Available Roles:
{available_roles}

Additional context: {additional_context}

Please provide role recommendations with justification for each recommendation.
"""
        )

        prompt.add_example(
            user_message="""
Please recommend appropriate user roles for the following user:

User Information:
- Name/ID: sarah.johnson
- Job Title: Content Marketing Manager
- Department: Marketing
- Primary Responsibilities: Creating and managing video content for marketing campaigns, coordinating with creative team, publishing content on schedule

Platform Access Requirements:
- Content Creation: Yes - needs to upload and edit videos
- Content Publishing: Yes - needs to publish and schedule content
- User Management: Limited - needs to add contributors to specific projects
- Analytics Access: Yes - needs to view performance metrics for marketing content
- System Administration: No

Available Roles:
- Administrator: Full system access, all permissions
- Manager: Can create/edit/publish content, manage users in their group, view analytics
- Contributor: Can create and edit content, cannot publish
- Publisher: Can publish and schedule content, cannot create/edit
- Analyst: View-only access to content and analytics
- Viewer: View-only access to published content

Additional context: Sarah is leading a team of 3 content creators and needs to coordinate publishing across multiple channels. She reports to the Marketing Director who has Manager access.
""",
            assistant_message="""
# User Role Recommendations for sarah.johnson

## Primary Recommendation: Manager

The Manager role is most appropriate for Sarah Johnson based on her position as Content Marketing Manager and her specific needs. This role would provide:

- **Content creation and editing capabilities** needed for her primary responsibilities
- **Publishing and scheduling permissions** required for managing marketing campaigns
- **Limited user management** to add contributors to specific projects
- **Analytics access** to track performance of marketing content

### Justification:
1. **Job alignment**: The Manager role aligns with her position overseeing a team of content creators
2. **Responsibility match**: Covers all her required functions (creation, publishing, team management, analytics)
3. **Hierarchical consistency**: Appropriate for someone who reports to a Marketing Director who also has Manager access
4. **Security balance**: Provides necessary permissions without granting unnecessary system administration access

## Alternative Consideration: Custom Role (if available)

If your system supports custom roles, consider creating a "Marketing Manager" role with:
- Full content creation/editing permissions
- Full publishing permissions
- User management limited to contributor assignment only
- Full analytics access for marketing content
- No system administration permissions

This would follow the principle of least privilege more precisely than the standard Manager role.

## Not Recommended

- **Administrator**: Excessive permissions for Sarah's needs, violating the principle of least privilege
- **Contributor**: Insufficient permissions (lacks publishing capabilities)
- **Publisher**: Insufficient permissions (lacks content creation capabilities)
- **Analyst/Viewer**: Severely insufficient permissions (lacks content creation and publishing)

## Implementation Notes

When assigning the Manager role to Sarah, consider:
1. Limiting her user management scope to only her team of 3 content creators
2. Setting up appropriate content categories/channels to define where she has publishing rights
3. Configuring analytics access to focus on marketing-related metrics
4. Documenting the role assignment and reviewing permissions quarterly as responsibilities may change
""",
        )

        prompt.add_required_tool("kaltura.user.get")
        prompt.add_required_tool("kaltura.user.update")
        prompt.add_required_resource("kaltura://users/{user_id}")

        return prompt

    @staticmethod
    def permission_management() -> BasePrompt:
        """Create a prompt for permission management."""
        prompt = BasePrompt(
            name="permission_management",
            description="Analyze and optimize user permissions for security and efficiency",
        )

        prompt.set_system_message(
            """
You are a permission management specialist for a video platform. Your task is to analyze
user permissions and recommend optimizations for security and efficiency.

When analyzing permissions:
1. Identify potential security risks from excessive permissions
2. Detect permission gaps that may hinder user productivity
3. Recommend permission adjustments based on user activity patterns
4. Consider role-based access control best practices
5. Balance security requirements with usability
6. Provide clear, actionable recommendations

Your analysis should help maintain the principle of least privilege while ensuring users can perform their required tasks efficiently.
"""
        )

        prompt.set_user_message_template(
            """
Please analyze the permissions for the following user:

User Information:
- Name/ID: {user_id}
- Current Role: {current_role}
- Department: {department}

Current Permissions:
{current_permissions}

User Activity (Last 30 Days):
{user_activity}

Permission Usage Statistics:
{permission_usage}

Security Policies:
{security_policies}

Additional context: {additional_context}

Please provide a permission analysis with specific recommendations for optimization.
"""
        )

        prompt.add_example(
            user_message="""
Please analyze the permissions for the following user:

User Information:
- Name/ID: alex.rodriguez
- Current Role: Content Editor
- Department: Production

Current Permissions:
- CONTENT_MANAGE_BASE: Yes
- CONTENT_MODERATE: Yes
- CONTENT_MANAGE_METADATA: Yes
- CONTENT_MANAGE_ASSIGN_CATEGORIES: Yes
- CONTENT_MANAGE_THUMBNAIL: Yes
- CONTENT_MANAGE_SCHEDULE: Yes
- CONTENT_MANAGE_ACCESS_CONTROL: Yes
- CONTENT_MANAGE_CUSTOM_DATA: Yes
- CONTENT_MANAGE_DELETE: Yes
- CONTENT_MANAGE_RECONVERT: Yes
- CONTENT_MANAGE_EDIT_CATEGORIES: Yes
- CONTENT_MANAGE_ANNOTATION: Yes
- CONTENT_MANAGE_SHARE: Yes
- CONTENT_MANAGE_DOWNLOAD: Yes
- CONTENT_MANAGE_EMBED_CODE: Yes
- PLAYLIST_BASE: Yes
- PLAYLIST_ADD: Yes
- PLAYLIST_UPDATE: Yes
- PLAYLIST_DELETE: Yes
- PLAYLIST_EMBED_CODE: Yes
- ANALYTICS_BASE: Yes
- INTEGRATION_UPDATE_SETTINGS: Yes
- ADMIN_USER_UPDATE: Yes
- ADMIN_USER_ADD: Yes

User Activity (Last 30 Days):
- Content uploads: 15
- Content edits: 47
- Content deletions: 0
- Category assignments: 32
- Thumbnail changes: 28
- Playlist creation: 2
- Playlist edits: 3
- User management actions: 0
- Analytics views: 1
- Integration setting changes: 0

Permission Usage Statistics:
- CONTENT_MANAGE_BASE: Used frequently
- CONTENT_MODERATE: Never used
- CONTENT_MANAGE_METADATA: Used frequently
- CONTENT_MANAGE_ASSIGN_CATEGORIES: Used frequently
- CONTENT_MANAGE_THUMBNAIL: Used frequently
- CONTENT_MANAGE_SCHEDULE: Used occasionally
- CONTENT_MANAGE_ACCESS_CONTROL: Never used
- CONTENT_MANAGE_CUSTOM_DATA: Used occasionally
- CONTENT_MANAGE_DELETE: Never used
- CONTENT_MANAGE_RECONVERT: Never used
- CONTENT_MANAGE_EDIT_CATEGORIES: Never used
- CONTENT_MANAGE_ANNOTATION: Used occasionally
- CONTENT_MANAGE_SHARE: Used occasionally
- CONTENT_MANAGE_DOWNLOAD: Used occasionally
- CONTENT_MANAGE_EMBED_CODE: Never used
- PLAYLIST_BASE: Used occasionally
- PLAYLIST_ADD: Used occasionally
- PLAYLIST_UPDATE: Used occasionally
- PLAYLIST_DELETE: Never used
- PLAYLIST_EMBED_CODE: Never used
- ANALYTICS_BASE: Used rarely
- INTEGRATION_UPDATE_SETTINGS: Never used
- ADMIN_USER_UPDATE: Never used
- ADMIN_USER_ADD: Never used

Security Policies:
- Principle of least privilege should be applied to all users
- Content deletion requires manager approval
- User management restricted to HR and IT departments
- Integration settings restricted to IT department
- Content moderation restricted to the Compliance team

Additional context: Alex is a content editor responsible for preparing and organizing video content. He works with the production team to ensure content meets quality standards before publication. He does not have direct reports and is not involved in user management.
""",
            assistant_message="""
# Permission Analysis for alex.rodriguez

## Summary of Findings
After analyzing Alex Rodriguez's permissions and activity patterns, I've identified several security concerns and optimization opportunities. Alex currently has multiple permissions that:
1. He never uses
2. Violate security policies
3. Exceed his role requirements as a Content Editor

## Critical Security Issues

### User Management Permissions
- **ADMIN_USER_UPDATE** and **ADMIN_USER_ADD**: These permissions violate your security policy restricting user management to HR and IT departments
- **Risk Level**: High
- **Evidence**: No user management actions in the past 30 days
- **Recommendation**: Remove immediately

### Integration Settings Permission
- **INTEGRATION_UPDATE_SETTINGS**: Violates security policy restricting these settings to IT department
- **Risk Level**: High
- **Evidence**: No integration setting changes in the past 30 days
- **Recommendation**: Remove immediately

### Content Deletion Permission
- **CONTENT_MANAGE_DELETE**: Violates security policy requiring manager approval for content deletion
- **Risk Level**: Medium
- **Evidence**: No content deletions in the past 30 days
- **Recommendation**: Remove and implement workflow for requesting deletions

## Unused Permissions to Remove

The following permissions have never been used and should be removed to align with the principle of least privilege:
- CONTENT_MODERATE (restricted to Compliance team per policy)
- CONTENT_MANAGE_ACCESS_CONTROL
- CONTENT_MANAGE_RECONVERT
- CONTENT_MANAGE_EDIT_CATEGORIES
- CONTENT_MANAGE_EMBED_CODE
- PLAYLIST_DELETE
- PLAYLIST_EMBED_CODE

## Permissions to Retain

Based on usage patterns, these permissions align with Alex's role and should be retained:
- CONTENT_MANAGE_BASE
- CONTENT_MANAGE_METADATA
- CONTENT_MANAGE_ASSIGN_CATEGORIES
- CONTENT_MANAGE_THUMBNAIL
- CONTENT_MANAGE_SCHEDULE
- CONTENT_MANAGE_CUSTOM_DATA
- CONTENT_MANAGE_ANNOTATION
- CONTENT_MANAGE_SHARE
- CONTENT_MANAGE_DOWNLOAD
- PLAYLIST_BASE
- PLAYLIST_ADD
- PLAYLIST_UPDATE

## Permission for Review

- **ANALYTICS_BASE**: Rarely used (only once in 30 days)
  - **Recommendation**: Discuss with Alex whether this is necessary for his role or if he can use reports shared by managers

## Recommended Permission Profile

I recommend creating an optimized "Content Editor" role with only the necessary permissions listed in the "Permissions to Retain" section. This would:
1. Reduce security risks by removing 12 unnecessary permissions
2. Maintain all functionality needed for Alex's actual work
3. Align with security policies and least privilege principle
4. Serve as a template for other Content Editors

## Implementation Plan

1. Create the new optimized Content Editor role
2. Migrate Alex to this role
3. Monitor for any workflow disruptions for 2 weeks
4. Apply the optimized role to other Content Editors if successful
5. Document the permission changes for compliance purposes
""",
        )

        prompt.add_required_tool("kaltura.user.get")
        prompt.add_required_tool("kaltura.user.update")
        prompt.add_required_resource("kaltura://users/{user_id}")

        return prompt

    @staticmethod
    def user_activity_analysis() -> BasePrompt:
        """Create a prompt for user activity analysis."""
        prompt = BasePrompt(
            name="user_activity_analysis",
            description="Analyze user activity patterns and provide insights",
        )

        prompt.set_system_message(
            """
You are a user activity analyst for a video platform. Your task is to analyze user activity
patterns and provide insights that can help improve user engagement, identify potential issues,
and optimize the platform experience.

When analyzing user activity:
1. Identify patterns and trends in user behavior
2. Compare activity against benchmarks or historical data
3. Detect anomalies that may indicate problems or opportunities
4. Segment users based on activity patterns
5. Provide actionable recommendations based on the analysis
6. Consider both individual user patterns and aggregate trends

Your analysis should be data-driven, insightful, and focused on actionable recommendations.
"""
        )

        prompt.set_user_message_template(
            """
Please analyze the following user activity data:

User Information:
- User ID/Group: {user_id}
- Role: {role}
- Time Period: {time_period}

Activity Metrics:
{activity_metrics}

Historical Comparison:
{historical_comparison}

Platform Benchmarks:
{platform_benchmarks}

Additional context: {additional_context}

Please provide an analysis of the user activity with insights and recommendations.
"""
        )

        prompt.add_example(
            user_message="""
Please analyze the following user activity data:

User Information:
- User ID/Group: marketing_team (12 users)
- Role: Content Publishers
- Time Period: Q1 2025 (Jan-Mar)

Activity Metrics:
- Content Created: 87 videos (avg 7.25 per user)
- Content Published: 64 videos (73.6% of created content)
- Average Time to Publish: 8.3 days from creation
- Average Video Duration: 4.2 minutes
- Total Upload Size: 15.8 GB
- Content Categories Used: Product (45%), Tutorial (30%), Promotional (15%), Other (10%)
- Average Views per Video: 342
- Average Engagement Rate: 24% (percentage of video watched)
- Peak Upload Days: Mondays (32% of uploads)
- Peak Publishing Days: Thursdays (41% of publishing)
- Failed Uploads: 23 (21% of attempts)
- Metadata Completeness: 78% (percentage of optional fields completed)
- Tag Usage: 3.2 tags per video (avg)
- Custom Thumbnail Usage: 52% of videos

Historical Comparison:
- Content Created: +15% vs Q4 2024
- Content Published: +5% vs Q4 2024
- Average Time to Publish: +2.1 days vs Q4 2024
- Average Video Duration: -0.8 minutes vs Q4 2024
- Average Views per Video: -12% vs Q4 2024
- Average Engagement Rate: -3% vs Q4 2024
- Failed Uploads: +8% vs Q4 2024
- Metadata Completeness: -5% vs Q4 2024

Platform Benchmarks:
- Average Content Created per Marketing Team: 72 videos per quarter
- Average Time to Publish (Marketing Teams): 5.7 days
- Average Video Duration (Marketing Content): 3.5 minutes
- Average Views per Marketing Video: 520
- Average Engagement Rate (Marketing Content): 31%
- Average Failed Upload Rate: 12%
- Average Metadata Completeness: 85%

Additional context: The marketing team has been focusing on a new product launch this quarter. Two new team members joined in February with limited platform experience. The team reported some technical issues with the upload process in January.
""",
            assistant_message="""
# Marketing Team Activity Analysis: Q1 2025

## Executive Summary
The marketing team showed increased content production (+15%) but is experiencing concerning trends in publishing efficiency, content performance, and technical issues. While output exceeds benchmarks, quality metrics and workflow efficiency have declined, suggesting a need for targeted interventions in training, workflow optimization, and technical support.

## Key Findings

### Strengths
1. **Above-Average Production**: 87 videos created vs. benchmark of 72 (+21%)
2. **Increased Output**: 15% increase in content creation compared to Q4 2024
3. **Diverse Content Mix**: Good distribution across product, tutorial, and promotional categories

### Concerns
1. **Publishing Bottleneck**: 
   - 26.4% of created content remains unpublished
   - 8.3 days to publish vs. benchmark of 5.7 days (+46%)
   - Publishing delay increased by 2.1 days compared to Q4

2. **Declining Performance Metrics**:
   - Views per video down 12% from Q4 and 34% below benchmark
   - Engagement rate down 3% from Q4 and 7% below benchmark

3. **Technical Issues**:
   - 21% failed upload rate (benchmark: 12%)
   - 8% increase in failed uploads from Q4

4. **Metadata Quality Decline**:
   - Metadata completeness down 5% from Q4
   - 7% below platform benchmark

## Root Cause Analysis

The data suggests three primary factors affecting performance:

1. **Onboarding Gaps**: New team members in February likely contributing to efficiency and quality issues
2. **Technical Barriers**: January upload issues created workflow disruptions
3. **Content Strategy Shift**: Longer videos (+20% vs benchmark) with less engagement suggests potential mismatch with audience preferences

## Segment Analysis

The team appears to have two distinct user segments:

1. **Experienced Publishers**: Maintaining higher efficiency and quality metrics
2. **New/Struggling Users**: Facing technical challenges and workflow inefficiencies

## Recommendations

### Immediate Actions (Next 30 Days)
1. **Technical Support Intervention**:
   - Investigate and resolve upload failures (priority)
   - Schedule technical refresher session focused on upload process
   - Create troubleshooting guide for common upload issues

2. **Targeted Training**:
   - Conduct metadata best practices workshop (focus on completeness)
   - Provide custom thumbnail creation training (only 52% utilization)

### Short-Term Improvements (60 Days)
1. **Workflow Optimization**:
   - Implement approval workflow templates to reduce publishing delays
   - Create pre-publishing checklist to improve metadata completeness
   - Shift some uploads to lower-volume days (reduce Monday bottleneck)

2. **Content Strategy Adjustment**:
   - Test shorter video formats (closer to 3.5 minute benchmark)
   - A/B test different content types to identify highest engagement formats
   - Review tag strategy to improve discoverability (current: 3.2 tags/video)

### Monitoring Metrics
1. **Primary KPIs to Track**:
   - Time to publish (target: reduce to 6 days by end of Q2)
   - Failed upload rate (target: reduce to platform average of 12%)
   - Engagement rate (target: increase to 28% by end of Q2)
   - Metadata completeness (target: increase to 85% by end of Q2)

## Opportunity Assessment

Despite current challenges, the marketing team's increased production volume presents significant opportunities:

1. **Performance Potential**: If videos achieved benchmark views (520 vs. current 342), total quarterly views would increase by ~11,400
2. **Efficiency Gains**: Reducing publishing time to benchmark could release ~165 person-hours per quarter for other activities
3. **Quality Improvement**: Addressing metadata and thumbnail usage could significantly improve content discoverability and performance

## Conclusion

The marketing team is producing content at an impressive volume but needs targeted support to address quality, efficiency, and technical challenges. With focused interventions in training, workflow, and technical support, the team could significantly improve performance metrics while maintaining their above-benchmark production levels.
""",
        )

        prompt.add_required_tool("kaltura.user.get")
        prompt.add_required_resource("kaltura://users/{user_id}")

        return prompt

    @staticmethod
    def user_engagement_strategy() -> BasePrompt:
        """Create a prompt for user engagement strategies."""
        prompt = BasePrompt(
            name="user_engagement_strategy",
            description="Develop strategies to improve user engagement and adoption",
        )

        prompt.set_system_message(
            """
You are a user engagement strategist for a video platform. Your task is to develop
strategies to improve user engagement, increase platform adoption, and enhance the
overall user experience.

When developing engagement strategies:
1. Analyze current usage patterns and identify opportunities
2. Consider different user segments and their specific needs
3. Recommend targeted interventions to address engagement gaps
4. Suggest communication and training approaches
5. Propose metrics to measure success
6. Consider both short-term tactics and long-term strategic initiatives

Your recommendations should be practical, actionable, and tailored to the specific context of the organization.
"""
        )

        prompt.set_user_message_template(
            """
Please develop a user engagement strategy for the following scenario:

Organization Context:
- Organization Type: {organization_type}
- Platform Usage: {platform_usage}
- User Base: {user_base}

Current Engagement Metrics:
{engagement_metrics}

User Segments:
{user_segments}

Engagement Goals:
{engagement_goals}

Previous Initiatives:
{previous_initiatives}

Additional context: {additional_context}

Please provide a comprehensive user engagement strategy with specific recommendations.
"""
        )

        prompt.add_example(
            user_message="""
Please develop a user engagement strategy for the following scenario:

Organization Context:
- Organization Type: Higher Education Institution (University with 15,000 students, 2,000 faculty/staff)
- Platform Usage: Learning content management, lecture capture, student assignments, faculty training
- User Base: 8,500 active users (4,200 students, 950 faculty, 350 staff, 3,000 occasional viewers)

Current Engagement Metrics:
- Active Users: 45% of potential user base
- Content Creation: 320 faculty/staff creating content (24% of potential creators)
- Average Session Duration: 18 minutes
- Average Sessions per Week per User: 2.3
- Content Upload Frequency: 1,200 videos per month
- Mobile Access: 35% of sessions
- Feature Utilization: Basic features (85%), Advanced features (22%)
- Help Desk Tickets: 85 per month (mostly upload issues and permissions)
- Training Attendance: 15% of users attended at least one training session
- User Satisfaction: 3.6/5 based on last survey

User Segments:
- Power Users (10%): Regular content creators, use advanced features, high engagement
- Standard Users (35%): Regular viewers, occasional uploaders, basic feature usage
- Occasional Users (30%): Infrequent usage, mainly for specific courses or events
- Inactive Users (25%): Have accounts but rarely or never log in
- By Role: Students (50%), Faculty (11%), Staff (4%), External Viewers (35%)
- By Department: Highest usage in Business, Engineering, Medicine; Lowest in Arts, Humanities

Engagement Goals:
- Increase active user percentage to 60% within 6 months
- Increase content creator percentage to 35% of faculty/staff
- Improve user satisfaction score to 4.2/5
- Increase advanced feature utilization to 40%
- Reduce help desk tickets by 25%
- Increase mobile usage to 50% of sessions

Previous Initiatives:
- Monthly training webinars (low attendance)
- Help documentation portal (low utilization)
- Email newsletters (25% open rate)
- Department champion program (inconsistent results)
- New user onboarding email sequence (implemented 3 months ago)

Additional context: The university recently upgraded the platform with new features including automatic captioning, analytics dashboard, and integration with the learning management system. The academic year starts in 4 weeks, which is typically when usage spikes. Budget is available for engagement initiatives but requires justification based on expected outcomes.
""",
            assistant_message="""
# User Engagement Strategy: University Video Platform

## Executive Summary
This strategy leverages the upcoming academic year start and recent platform upgrades to drive a significant increase in engagement across all user segments. By implementing a multi-faceted approach combining targeted training, peer influence, system integration, and contextual support, we can achieve the engagement goals while delivering measurable ROI through increased platform adoption and reduced support costs.

## Strategic Framework

### 1. Pre-Semester Engagement Blitz (Weeks 1-4)

#### Faculty Activation Campaign
* **Department-Specific Workshops** (Priority: High)
  * Schedule 45-minute hands-on sessions for each department
  * Focus on discipline-specific use cases and benefits
  * Target low-adoption departments (Arts, Humanities) with customized content examples
  * Measure: Attendance rate target of 40% of faculty per department

* **Course Template Program** (Priority: High)
  * Create ready-to-use video assignment templates for common course scenarios
  * Develop 5-10 templates per major discipline
  * Offer 1:1 setup assistance for first implementation
  * Measure: Template adoption rate, increase in faculty content creators

* **"Video Champions" Relaunch** (Priority: Medium)
  * Recruit influential faculty from each department (focus on respected educators, not just tech enthusiasts)
  * Provide advanced training and early access to new features
  * Incentivize with recognition and professional development credits
  * Measure: Champion-influenced adoption rates within departments

#### Student Preparation
* **Student Orientation Integration** (Priority: High)
  * Add platform introduction to all student orientation sessions
  * Create quick-start guides specific to student needs
  * Develop mobile-first tutorial for student app onboarding
  * Measure: New student activation rate in first two weeks

* **Student Ambassador Program** (Priority: Medium)
  * Recruit tech-savvy students as platform ambassadors
  * Train them to provide peer support and promote platform benefits
  * Position in high-traffic campus locations during first weeks
  * Measure: Peer support interactions, influenced activations

### 2. System & Process Integration (Weeks 1-12)

* **Learning Management System (LMS) Deep Integration** (Priority: Critical)
  * Enhance existing integration with single-click access from all course pages
  * Implement unified notification system between platforms
  * Create seamless assignment submission workflow
  * Measure: Cross-platform navigation rates, assignment submission completion rates

* **Mobile Experience Enhancement** (Priority: High)
  * Promote mobile app through targeted campaigns
  * Optimize mobile upload process (identified pain point)
  * Implement mobile push notifications for engagement
  * Measure: Mobile session increase, mobile feature utilization

* **Authentication Streamlining** (Priority: Medium)
  * Implement "remember me" functionality
  * Extend session timeouts to reduce friction
  * Add biometric login option for mobile app
  * Measure: Login success rate, authentication-related support tickets

### 3. Contextual Support Ecosystem (Ongoing)

* **In-Platform Guidance System** (Priority: High)
  * Implement contextual help tooltips for complex features
  * Create feature spotlight system highlighting underutilized capabilities
  * Develop progressive onboarding for advanced features
  * Measure: Help system utilization, feature discovery rates

* **Knowledge Base Transformation** (Priority: Medium)
  * Restructure help documentation as task-based guides
  * Add video tutorials for common workflows (under 2 minutes each)
  * Implement searchable FAQ based on common help desk tickets
  * Measure: Knowledge base utilization, self-service resolution rate

* **Proactive Support Model** (Priority: Medium)
  * Implement usage pattern monitoring to identify struggling users
  * Create triggered assistance for users showing signs of difficulty
  * Develop automated check-ins for users with declining engagement
  * Measure: Intervention acceptance rate, post-intervention engagement

### 4. Engagement Sustainability (Months 3-6)

* **Success Storytelling Campaign** (Priority: Medium)
  * Document and share innovative platform uses across departments
  * Create monthly spotlight on creative implementations
  * Develop case studies showing measurable educational impact
  * Measure: Story engagement, influenced adoption of highlighted techniques

* **Gamification Elements** (Priority: Low)
  * Implement creator achievement system with badges
  * Create department-level friendly competition metrics
  * Recognize milestone achievements (views, uploads, etc.)
  * Measure: Gamification element engagement, influenced behaviors

* **Continuous Feedback Loop** (Priority: High)
  * Implement quick in-platform pulse surveys (single question)
  * Create user feedback council with representatives from key segments
  * Establish regular feature prioritization input mechanism
  * Measure: Feedback participation rates, sentiment trends

## Segment-Specific Strategies

### Power Users (10%)
* Advanced feature masterclasses
* Early access to new capabilities
* Recognition program for platform champions
* Peer mentoring opportunities

### Standard Users (35%)
* Workflow efficiency training focused on time-saving
* Contextual prompts for next-level feature adoption
* Personalized content recommendations based on usage patterns
* Department-specific best practice guides

### Occasional Users (30%)
* Simplified core workflows
* Mobile-optimized experience
* Just-in-time guidance for infrequent tasks
* Course-specific quick start guides

### Inactive Users (25%)
* Re-engagement campaign highlighting new capabilities
* Peer testimonials demonstrating concrete benefits
* Simplified activation process
* Department-specific use cases with clear value proposition

## Implementation Timeline

### Immediate (Weeks 1-2)
* Launch faculty workshop schedule
* Implement LMS quick-access integration
* Deploy mobile optimization enhancements
* Recruit initial video champions and student ambassadors

### Short-Term (Weeks 3-6)
* Complete department workshops
* Launch course template program
* Implement contextual help system
* Begin success storytelling campaign

### Mid-Term (Weeks 7-12)
* Deploy in-platform guidance system
* Launch proactive support model
* Complete knowledge base transformation
* Implement feedback mechanisms

### Long-Term (Months 4-6)
* Roll out gamification elements
* Expand success storytelling
* Refine strategies based on initial results
* Develop sustainability plan for year-long engagement

## Measurement Framework

### Key Performance Indicators
* Active user percentage (target: 60%)
* Content creator percentage (target: 35% of faculty/staff)
* User satisfaction score (target: 4.2/5)
* Advanced feature utilization (target: 40%)
* Help desk tickets (target: 25% reduction)
* Mobile usage (target: 50% of sessions)

### Leading Indicators
* Workshop attendance rates
* Template adoption metrics
* LMS integration utilization
* Knowledge base self-service rate
* Feature discovery metrics
* Re-engagement campaign response rate

## Resource Requirements

### Personnel
* Faculty engagement coordinator (0.5 FTE)
* Student ambassador program manager (0.25 FTE)
* Instructional designers for templates (80 hours)
* Technical integration specialist (40 hours)

### Technology
* In-platform guidance system implementation
* Enhanced analytics dashboard for engagement metrics
* Mobile experience optimization

### Budget Justification
* Training and workshop materials: $3,000
* Student ambassador program: $5,000
* Recognition and incentive program: $2,000
* Technical implementation: $15,000
* Total: $25,000

**ROI Calculation:**
* 25% reduction in help desk tickets = approximately $21,000 annual savings
* 15% increase in active users = approximately 1,275 new active users
* Value per active user (based on license utilization) = approximately $25
* Total ROI first year: ~$53,000 (112% return on $25,000 investment)

## Conclusion

This comprehensive engagement strategy addresses the specific needs of the university environment while targeting the defined goals for platform adoption and utilization. By focusing on the critical pre-semester period, leveraging peer influence, enhancing system integration, and providing contextual support, we can drive significant improvements in engagement metrics while delivering measurable ROI.
""",
        )

        prompt.add_required_tool("kaltura.user.get")
        prompt.add_required_resource("kaltura://users/{user_id}")

        return prompt
