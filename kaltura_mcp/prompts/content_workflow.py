"""
Content workflow prompts for the Kaltura-MCP Server intelligent prompting library.

This module provides prompts for common content workflow tasks such as moderation,
tagging, categorization, and distribution workflows.
"""

from .base import BasePrompt


class ContentWorkflowPrompts:
    """Collection of content workflow prompts."""

    @staticmethod
    def moderation_review() -> BasePrompt:
        """Create a prompt for content moderation review."""
        prompt = BasePrompt(name="content_moderation_review", description="Review content for moderation issues")

        prompt.set_system_message(
            """
You are a content moderation assistant for a video platform. Your task is to review video metadata
and identify any potential moderation issues. You should check for:

1. Inappropriate content or language in titles, descriptions, or tags
2. Misleading or deceptive content descriptions
3. Copyright or intellectual property concerns
4. Age-appropriate content classification
5. Compliance with platform policies

For each issue you identify, provide:
- The specific issue and why it's problematic
- A recommendation for how to address it
- A severity level (Low, Medium, High)

Be thorough but fair in your assessment. Focus on clear policy violations rather than subjective judgments.
"""
        )

        prompt.set_user_message_template(
            """
Please review the following video content for moderation issues:

Title: {title}
Description: {description}
Tags: {tags}
Duration: {duration} seconds
Created by: {user_id}
Category: {category_name}

Additional context: {additional_context}
"""
        )

        prompt.add_example(
            user_message="""
Please review the following video content for moderation issues:

Title: How to Hack Any Website in 5 Minutes
Description: This tutorial shows you the easiest ways to break into websites and access admin accounts. Works on all major sites including banks and government websites.
Tags: hacking, security, tutorial, hack, website, admin access
Duration: 325 seconds
Created by: user123
Category: Education
            
Additional context: This is a new upload from a user with no previous violations.
""",
            assistant_message="""
# Moderation Review

I've identified several moderation issues with this content:

## Issue 1: Promotion of Illegal Activities
- **Description**: The title and description explicitly promote hacking websites, which is illegal in most jurisdictions.
- **Recommendation**: Reject the video and notify the user that content promoting illegal activities violates platform policies.
- **Severity**: High

## Issue 2: Misleading Category
- **Description**: The video is categorized as "Education" but appears to be promoting illegal activities rather than educational content about cybersecurity.
- **Recommendation**: If the video is allowed with modifications, it should be recategorized or include clear disclaimers about legal educational purposes only.
- **Severity**: Medium

## Issue 3: Potentially Harmful Tags
- **Description**: Tags like "hack," "admin access" in combination with the content suggest intent to provide actual hacking instructions.
- **Recommendation**: If the content is modified to be educational about security vulnerabilities (rather than exploitation), suggest alternative tags focused on cybersecurity education.
- **Severity**: Medium

## Overall Recommendation
This content should be rejected as it currently stands, as it appears to violate platform policies against promoting illegal activities. The user should be informed about acceptable content guidelines for cybersecurity education that focus on ethical hacking, security research, or vulnerability disclosure with proper context and disclaimers.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def auto_tagging() -> BasePrompt:
        """Create a prompt for automatic content tagging."""
        prompt = BasePrompt(
            name="content_auto_tagging",
            description="Automatically generate relevant tags for content",
        )

        prompt.set_system_message(
            """
You are a content tagging assistant for a video platform. Your task is to analyze video metadata
and generate relevant tags that will improve discoverability and categorization.

When generating tags:
1. Include a mix of general and specific tags
2. Focus on the main topics, themes, and entities in the content
3. Consider the target audience and category
4. Avoid overly generic tags that don't add value
5. Limit to 10-15 high-quality tags
6. Format as comma-separated values

Generate tags based on the title, description, existing tags, and category information.
"""
        )

        prompt.set_user_message_template(
            """
Please generate relevant tags for the following video content:

Title: {title}
Description: {description}
Existing Tags: {tags}
Duration: {duration} seconds
Category: {category_name}
"""
        )

        prompt.add_example(
            user_message="""
Please generate relevant tags for the following video content:

Title: Introduction to Python Programming for Beginners
Description: This tutorial covers the basics of Python programming language, including variables, data types, control structures, and functions. Perfect for absolute beginners with no prior programming experience.
Existing Tags: python, programming
Duration: 1845 seconds
Category: Education
""",
            assistant_message="""
python, programming, beginner programming, python tutorial, coding, learn python, python basics, programming tutorial, python for beginners, variables, data types, control structures, functions, coding tutorial, computer science
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def category_suggestion() -> BasePrompt:
        """Create a prompt for suggesting appropriate categories."""
        prompt = BasePrompt(
            name="content_category_suggestion",
            description="Suggest appropriate categories for content",
        )

        prompt.set_system_message(
            """
You are a content categorization assistant for a video platform. Your task is to analyze video metadata
and suggest the most appropriate category or categories for the content.

When suggesting categories:
1. Consider the primary topic and purpose of the content
2. Look at the title, description, and existing tags
3. Consider the target audience
4. Provide reasoning for your suggestions
5. If multiple categories could apply, rank them in order of relevance

Use only categories that exist in the platform's category system.
"""
        )

        prompt.set_user_message_template(
            """
Please suggest appropriate categories for the following video content:

Title: {title}
Description: {description}
Tags: {tags}
Duration: {duration} seconds

Available Categories:
{available_categories}
"""
        )

        prompt.add_example(
            user_message="""
Please suggest appropriate categories for the following video content:

Title: 10 Minute Full Body HIIT Workout - No Equipment Needed
Description: This high-intensity interval training workout targets your entire body and can be done at home with no equipment. Perfect for busy people who want to maximize their workout efficiency.
Tags: workout, fitness, hiit, exercise, home workout, no equipment, full body, interval training
Duration: 612 seconds

Available Categories:
- Sports
- Health & Fitness
- Education
- How-to & Style
- Entertainment
- People & Blogs
""",
            assistant_message="""
# Category Recommendations

## Primary Recommendation: Health & Fitness
This is clearly the most appropriate category for this content. The video is specifically a workout routine focused on physical fitness and exercise, which is the core purpose of the Health & Fitness category.

## Secondary Recommendation: How-to & Style
This could be a secondary category as the content is instructional in nature, showing people how to perform specific exercises. However, it's less specific than Health & Fitness for this particular content.

## Not Recommended
- Sports: While related to physical activity, this video is about personal fitness rather than competitive sports or sporting events
- Education: While there is educational value, the primary purpose is fitness instruction rather than academic education
- Entertainment: The primary purpose is instructional rather than entertainment
- People & Blogs: Too general for this specific fitness-focused content

I recommend categorizing this video under "Health & Fitness" as it most accurately represents the content and will help the target audience discover it.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_tool("kaltura.category.list")
        prompt.add_required_resource("kaltura://media/{entry_id}")
        prompt.add_required_resource("kaltura://categories/list")

        return prompt

    @staticmethod
    def distribution_planning() -> BasePrompt:
        """Create a prompt for content distribution planning."""
        prompt = BasePrompt(
            name="content_distribution_planning",
            description="Plan optimal distribution strategy for content",
        )

        prompt.set_system_message(
            """
You are a content distribution strategist for a video platform. Your task is to analyze video content
and suggest the optimal distribution strategy to maximize reach and engagement.

When creating a distribution plan:
1. Consider the content type, topic, and target audience
2. Suggest appropriate distribution channels (website, social media, email, etc.)
3. Recommend optimal publishing times and frequency
4. Suggest promotional tactics and cross-promotion opportunities
5. Consider SEO and discoverability optimizations
6. Provide a timeline and key performance indicators (KPIs) to track

Be specific and practical in your recommendations, focusing on actionable steps.
"""
        )

        prompt.set_user_message_template(
            """
Please create a distribution plan for the following video content:

Title: {title}
Description: {description}
Tags: {tags}
Duration: {duration} seconds
Category: {category_name}
Target Audience: {target_audience}
Key Message: {key_message}
Call to Action: {call_to_action}

Additional context: {additional_context}
"""
        )

        prompt.add_example(
            user_message="""
Please create a distribution plan for the following video content:

Title: 5 Essential Tax Saving Tips for Small Business Owners
Description: Learn five proven strategies to legally minimize your tax burden as a small business owner. This video covers deductions you might be missing, entity structure considerations, retirement planning, timing strategies, and record-keeping best practices.
Tags: taxes, small business, tax deductions, tax planning, business finance, accounting, tax season
Duration: 845 seconds
Category: Business
Target Audience: Small business owners, entrepreneurs, self-employed professionals
Key Message: Proper tax planning can save small businesses thousands of dollars annually
Call to Action: Schedule a tax planning consultation with our experts

Additional context: This is part of our Q1 financial planning series, released 6 weeks before the tax filing deadline.
""",
            assistant_message="""
# Content Distribution Plan: 5 Essential Tax Saving Tips for Small Business Owners

## Channel Strategy

### Primary Channels
1. **Website/Blog**
   - Feature prominently on the homepage during tax season (now through filing deadline)
   - Create a dedicated landing page with additional resources and consultation sign-up form
   - Include in your "Essential Business Resources" section permanently

2. **Email Marketing**
   - Send dedicated email to small business subscriber segment
   - Include in weekly newsletter for next 6 weeks
   - Create an automated email sequence for new subscribers interested in business finance

3. **Social Media**
   - LinkedIn: Primary platform for this content
   - Facebook: Business groups and small business owner communities
   - Twitter: Share with relevant hashtags during peak business hours
   - Instagram: Create 3-5 key tip graphics from the video content

### Secondary Channels
1. **Partner Distribution**
   - Share with accounting/bookkeeping partners for their clients
   - Provide to small business associations and chambers of commerce
   - Offer to local business networking groups

2. **Paid Promotion**
   - LinkedIn Ads targeting small business owners and financial decision-makers
   - Google Ads with tax planning and small business keywords
   - Retargeting campaign for website visitors who viewed business content

## Timing Strategy

### Immediate Release (6 weeks before tax deadline)
- Initial push across all primary channels
- Highest promotion budget allocation

### Weeks 1-3
- Focus on awareness and reach
- Emphasize the "don't miss these deductions" angle
- Heavy social sharing and partner distribution

### Weeks 4-6 (approaching deadline)
- Shift to urgency messaging
- Increase CTA focus on consultation bookings
- Boost paid promotion

### Post-Tax Season
- Transition to evergreen content
- Update metadata to include "planning for next year"
- Reduce promotion but maintain in resource libraries

## Content Optimization

### SEO Recommendations
- Primary keyword: "small business tax saving tips"
- Secondary keywords: "tax deductions for business owners," "self-employed tax strategies"
- Update video description with timestamps for each tip
- Create transcript for search indexing

### Engagement Tactics
- Create 60-second highlight version for social media
- Extract each tip as a standalone short video
- Develop a downloadable checklist as a lead magnet
- Set up a Q&A follow-up session to address viewer questions

## Performance Tracking

### Key Performance Indicators
1. **Reach Metrics**
   - Video views and watch time
   - Social media impressions
   - Email open and click rates

2. **Engagement Metrics**
   - Comments and shares
   - Average view duration
   - Click-through to consultation page

3. **Conversion Metrics**
   - Consultation bookings
   - Checklist downloads
   - New client acquisitions

### Measurement Timeline
- Weekly reporting during tax season
- Comprehensive performance review post-tax deadline
- Quarterly review for evergreen performance

## Additional Recommendations
- Create a "Tax Tips" playlist grouping all related content
- Consider a webinar expansion of this topic for deeper engagement
- Develop relationships with business publications for content sharing
- Test different thumbnails to optimize click-through rate

This distribution plan maximizes the timely nature of the content while creating pathways for continued relevance beyond tax season.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def content_approval_workflow() -> BasePrompt:
        """Create a prompt for content approval workflow."""
        prompt = BasePrompt(
            name="content_approval_workflow",
            description="Guide content through an approval workflow",
        )

        prompt.set_system_message(
            """
You are a content workflow assistant for a video platform. Your task is to guide content through
the approval process, ensuring all necessary steps are completed and requirements are met.

For each piece of content in the approval workflow:
1. Verify that all required metadata is present and complete
2. Check that the content meets quality standards and guidelines
3. Identify any missing approvals or reviews
4. Suggest next steps in the workflow
5. Provide a summary of the content's current status
6. Recommend actions to move the content forward

Be thorough in your assessment and clear in your recommendations.
"""
        )

        prompt.set_user_message_template(
            """
Please review the following content in the approval workflow:

Title: {title}
Description: {description}
Tags: {tags}
Duration: {duration} seconds
Created by: {user_id}
Category: {category_name}
Current Status: {status}

Required Metadata:
{required_metadata}

Required Approvals:
{required_approvals}

Additional context: {additional_context}
"""
        )

        prompt.add_example(
            user_message="""
Please review the following content in the approval workflow:

Title: Q2 Product Roadmap Presentation
Description: Detailed overview of our product development plans for Q2 2023, including feature releases, bug fixes, and strategic initiatives.
Tags: roadmap, product, development, Q2, strategy, internal
Duration: 1245 seconds
Created by: sarah.product
Category: Internal Communications
Current Status: Pending Legal Review

Required Metadata:
- Title: ✓
- Description: ✓
- Category: ✓
- Tags: ✓
- Thumbnail: ✓
- Access Control: ❌ (Not set)
- Distribution Rights: ❌ (Not specified)
- Expiration Date: ❌ (Not set)

Required Approvals:
- Department Manager: ✓ (approved by john.manager on 2023-03-10)
- Content Review: ✓ (approved by content.team on 2023-03-11)
- Legal Review: ❌ (pending since 2023-03-11)
- Executive Approval: ❌ (not started)

Additional context: This video contains pre-release product information and should be restricted to internal employees only. Legal review was requested 5 days ago but has not been completed yet.
""",
            assistant_message="""
# Content Approval Workflow Review

## Current Status: Pending Legal Review

### Metadata Assessment
The content has several metadata issues that need to be addressed:

1. **Access Control**: ❌ MISSING
   - This is critical given the internal nature of the content
   - Recommendation: Set access control to "Internal Employees Only"

2. **Distribution Rights**: ❌ MISSING
   - Required for all content, even internal
   - Recommendation: Set to "Internal Distribution Only - No External Sharing"

3. **Expiration Date**: ❌ MISSING
   - Important for time-sensitive roadmap information
   - Recommendation: Set expiration date to end of Q2 or specify if this should be archived permanently

### Approval Status
The content is currently awaiting legal review with two outstanding approvals:

1. **Legal Review**: ❌ PENDING (5 days)
   - This approval is overdue based on standard SLA (3 business days)
   - Recommendation: Escalate to legal department head with priority flag

2. **Executive Approval**: ❌ NOT STARTED
   - Cannot proceed until legal review is complete
   - Will be the final step in the approval process

### Next Steps

1. **Immediate Actions**:
   - Complete the missing metadata fields (Access Control, Distribution Rights, Expiration Date)
   - Send reminder to legal team with escalation to department head
   - Prepare briefing for executive approval once legal review is complete

2. **Timeline Recommendation**:
   - Target completion of legal review by end of day tomorrow
   - Schedule executive review within 24 hours of legal approval
   - Aim for full publication approval within 2 business days

3. **Additional Recommendations**:
   - Add watermark indicating "Internal Use Only - Confidential"
   - Prepare distribution list for controlled release once fully approved
   - Document any legal concerns raised during review for future roadmap presentations

The content meets quality standards and has appropriate departmental and content approvals, but cannot proceed to publication until the metadata issues are resolved and remaining approvals are obtained.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt
