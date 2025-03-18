"""
Content enrichment prompts for the Kaltura-MCP Server intelligent prompting library.

This module provides prompts for content enrichment tasks such as generating video summaries,
descriptions, AI-driven subtitles, and translations.
"""

from .base import BasePrompt


class ContentEnrichmentPrompts:
    """Collection of content enrichment prompts."""

    @staticmethod
    def video_summary() -> BasePrompt:
        """Create a prompt for generating video summaries."""
        prompt = BasePrompt(
            name="video_summary_generation",
            description="Generate concise and informative summaries of video content",
        )

        prompt.set_system_message(
            """
You are a video content summarization assistant. Your task is to create concise, informative summaries
of video content based on available metadata, transcripts, or descriptions.

When creating video summaries:
1. Capture the main topics, themes, and key points
2. Maintain a neutral, informative tone
3. Include relevant details while being concise
4. Structure the summary in a logical flow
5. Avoid subjective opinions or evaluations
6. Focus on factual information from the content

Create summaries that help viewers quickly understand what the video is about and decide if they want to watch it.
"""
        )

        prompt.set_user_message_template(
            """
Please generate a concise summary for the following video:

Title: {title}
Duration: {duration} seconds
Category: {category_name}
Tags: {tags}

Description:
{description}

Transcript/Content:
{transcript}

Additional context: {additional_context}

Please provide a summary of approximately 3-5 sentences that captures the main points and purpose of this video.
"""
        )

        prompt.add_example(
            user_message="""
Please generate a concise summary for the following video:

Title: Understanding Climate Change: Causes, Effects, and Solutions
Duration: 1245 seconds
Category: Education
Tags: climate change, global warming, environment, science, sustainability, carbon emissions

Description:
This educational video explores the science behind climate change, its observed and projected impacts on our planet, and potential solutions to mitigate its effects. We break down complex scientific concepts into easy-to-understand explanations suitable for general audiences.

Transcript/Content:
Welcome to our educational series on climate science. Today we're discussing climate change - what it is, why it's happening, and what we can do about it.

First, let's understand the basics. Climate change refers to significant changes in global temperature, precipitation, wind patterns, and other measures of climate that occur over several decades or longer. While the Earth's climate has changed throughout history, the current trend is concerning because of its rapid pace and clear connection to human activities.

The primary cause of current climate change is the greenhouse effect enhanced by human activities. When we burn fossil fuels like coal, oil, and natural gas, we release carbon dioxide and other greenhouse gases into the atmosphere. These gases trap heat from the sun, preventing it from escaping back into space. This is similar to how a greenhouse works, hence the name.

The evidence for climate change is compelling. Global temperature has risen about 1.1 degrees Celsius since the pre-industrial era. We're seeing melting ice sheets, rising sea levels, more intense heat waves, and changing precipitation patterns. These aren't just predictions - they're measurable changes happening now.

The effects of climate change are far-reaching. Rising sea levels threaten coastal communities. Changing precipitation patterns affect agriculture and food security. More frequent extreme weather events like hurricanes and wildfires cause destruction and displacement. Ecosystems and biodiversity are also at risk as species struggle to adapt to rapidly changing conditions.

But there is hope. We have solutions available today that can help mitigate climate change. Transitioning to renewable energy sources like solar and wind power reduces carbon emissions. Improving energy efficiency in buildings, transportation, and industry can make a significant difference. Protecting and restoring forests helps absorb carbon dioxide from the atmosphere.

Individual actions matter too. Reducing meat consumption, minimizing food waste, using public transportation, and being mindful of our energy use all contribute to the solution. But systemic change through policy and business practices is equally important.

In conclusion, climate change is a complex but well-understood scientific phenomenon with serious implications for our planet. By understanding its causes and effects, we can work together on solutions that create a more sustainable future for all.

Additional context: This is part of an educational series aimed at high school and college students, but designed to be accessible to general audiences.

Please provide a summary of approximately 3-5 sentences that captures the main points and purpose of this video.
""",
            assistant_message="""
This educational video provides a comprehensive overview of climate change, explaining its scientific basis as the enhanced greenhouse effect caused by human activities that release carbon dioxide and other gases into the atmosphere. It presents evidence of climate change including rising global temperatures, melting ice sheets, and changing weather patterns, while detailing the consequences such as threats to coastal communities, agriculture, and ecosystems. The video concludes with actionable solutions at both individual and systemic levels, including transitioning to renewable energy, improving efficiency, and protecting forests, emphasizing that while climate change is a serious challenge, we have the knowledge and tools to address it effectively.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def description_generation() -> BasePrompt:
        """Create a prompt for generating video descriptions."""
        prompt = BasePrompt(
            name="video_description_generation",
            description="Generate engaging and informative video descriptions",
        )

        prompt.set_system_message(
            """
You are a video description specialist. Your task is to create engaging, informative, and SEO-friendly
descriptions for video content based on available metadata, transcripts, or summaries.

When creating video descriptions:
1. Start with a compelling hook or overview sentence
2. Include key topics and information covered in the video
3. Incorporate relevant keywords naturally for discoverability
4. Use clear, concise language with proper formatting
5. Include timestamps for longer videos to highlight key sections
6. End with a clear call-to-action when appropriate

Create descriptions that accurately represent the content while encouraging viewers to watch the video.
"""
        )

        prompt.set_user_message_template(
            """
Please generate an engaging description for the following video:

Title: {title}
Duration: {duration} seconds
Category: {category_name}
Tags: {tags}
Target Audience: {target_audience}

Summary/Content:
{summary}

Key Points to Include:
{key_points}

Additional context: {additional_context}

Please provide a description of approximately 150-200 words that will engage viewers and improve discoverability.
"""
        )

        prompt.add_example(
            user_message="""
Please generate an engaging description for the following video:

Title: Mastering Python: 10 Advanced Techniques for Experienced Developers
Duration: 1845 seconds
Category: Education
Tags: python, programming, advanced python, software development, coding techniques, developer tips
Target Audience: Intermediate to advanced Python developers

Summary/Content:
This tutorial covers ten advanced Python techniques that experienced developers can use to write more efficient, maintainable, and elegant code. The video explores decorators, context managers, metaclasses, descriptors, generators, coroutines, and other advanced features of the Python language. Each technique is explained with practical examples and real-world use cases.

Key Points to Include:
- The video covers Python 3.8+ features
- Each technique includes downloadable code examples
- The instructor has 15 years of Python development experience
- This is part 3 of our Advanced Python series
- Viewers should have at least 1-2 years of Python experience

Additional context: This video has accompanying code samples available on GitHub. We want to emphasize the practical applications rather than just theoretical concepts.

Please provide a description of approximately 150-200 words that will engage viewers and improve discoverability.
""",
            assistant_message="""
Ready to take your Python skills to the next level? In this comprehensive tutorial, we dive deep into 10 powerful advanced techniques that separate novice programmers from Python experts.

🔹 00:45 - Mastering decorators for cleaner function modifications
🔹 05:12 - Building custom context managers for resource management
🔹 10:30 - Harnessing the power of metaclasses for framework development
🔹 16:25 - Using descriptors to control attribute access
🔹 22:10 - Advanced generator patterns for memory-efficient data processing

Designed specifically for developers with 1-2+ years of Python experience, this tutorial focuses on practical applications you can implement immediately in your projects. All examples target Python 3.8+ and showcase modern best practices used in production environments.

This is Part 3 of our Advanced Python series, taught by an instructor with 15 years of professional Python development experience. Each technique comes with downloadable code examples that demonstrate real-world implementations, not just theoretical concepts.

👉 All code samples available on our GitHub repository (link in comments)

Whether you're building complex applications, optimizing performance, or just wanting to write more elegant Python code, these advanced techniques will transform how you approach Python development.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def subtitle_generation() -> BasePrompt:
        """Create a prompt for generating video subtitles."""
        prompt = BasePrompt(
            name="subtitle_generation",
            description="Generate accurate and well-formatted subtitles for video content",
        )

        prompt.set_system_message(
            """
You are a subtitle generation assistant. Your task is to create accurate, well-formatted subtitles
for video content based on audio transcripts or descriptions.

When creating subtitles:
1. Break text into appropriate subtitle segments (1-2 lines, max 42 characters per line)
2. Time subtitles appropriately (display for 1-7 seconds depending on length)
3. Include speaker identification when multiple speakers are present
4. Include relevant non-speech audio cues in brackets [applause], [music], etc.
5. Ensure proper punctuation and capitalization
6. Maintain the original meaning and tone of the speech

Format subtitles in SRT format with sequential numbering, timecodes (HH:MM:SS,MS), and subtitle text.
"""
        )

        prompt.set_user_message_template(
            """
Please generate subtitles for the following video content:

Title: {title}
Duration: {duration} seconds
Number of Speakers: {num_speakers}

Transcript:
{transcript}

Audio Cues:
{audio_cues}

Additional context: {additional_context}

Please provide subtitles in SRT format, with appropriate timing and formatting.
"""
        )

        prompt.add_example(
            user_message="""
Please generate subtitles for the following video content:

Title: Introduction to Machine Learning Concepts
Duration: 180 seconds
Number of Speakers: 2

Transcript:
SARAH: Welcome to our introduction to machine learning concepts. I'm Sarah Chen, and I'm joined today by Dr. Michael Rodriguez, an AI researcher at Tech University.

MICHAEL: Thanks for having me, Sarah. I'm excited to break down some of these complex concepts for your audience.

SARAH: Let's start with the basics. Michael, how would you define machine learning for someone who's completely new to the field?

MICHAEL: That's a great question. At its core, machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Instead of writing specific instructions for every scenario, we provide data and let the algorithms find patterns and make decisions.

SARAH: So it's like teaching a computer to learn on its own?

MICHAEL: Exactly. Think of it like teaching a child. You don't program a child with rules for recognizing every possible dog they might encounter. Instead, you show them examples of dogs, and they learn to recognize the patterns and features that make a dog a dog.

SARAH: That's a helpful analogy. What are some common applications of machine learning that people might encounter in their daily lives?

MICHAEL: They're everywhere! Recommendation systems on streaming platforms and online stores, voice assistants like Siri and Alexa, email spam filters, fraud detection for your credit cards, and even the autocorrect feature on your smartphone.

Audio Cues:
[0:00-0:05] Intro music
[0:58-1:02] Michael laughs
[2:55-3:00] Outro music

Additional context: This is the opening segment of a longer educational video. Sarah is on the left side of the screen, and Michael is on the right.

Please provide subtitles in SRT format, with appropriate timing and formatting.
""",
            assistant_message="""
1
00:00:00,000 --> 00:00:05,000
[Intro music]

2
00:00:05,000 --> 00:00:09,500
SARAH: Welcome to our introduction to
machine learning concepts.

3
00:00:09,500 --> 00:00:14,000
SARAH: I'm Sarah Chen, and I'm joined today by
Dr. Michael Rodriguez,

4
00:00:14,000 --> 00:00:17,000
SARAH: an AI researcher at Tech University.

5
00:00:17,000 --> 00:00:20,500
MICHAEL: Thanks for having me, Sarah.

6
00:00:20,500 --> 00:00:25,000
MICHAEL: I'm excited to break down some of these
complex concepts for your audience.

7
00:00:25,000 --> 00:00:28,000
SARAH: Let's start with the basics.

8
00:00:28,000 --> 00:00:32,500
SARAH: Michael, how would you define machine learning
for someone who's completely new to the field?

9
00:00:32,500 --> 00:00:35,500
MICHAEL: That's a great question.

10
00:00:35,500 --> 00:00:39,000
MICHAEL: At its core, machine learning is a
subset of artificial intelligence

11
00:00:39,000 --> 00:00:43,000
MICHAEL: that enables systems to learn and
improve from experience

12
00:00:43,000 --> 00:00:46,000
MICHAEL: without being explicitly programmed.

13
00:00:46,000 --> 00:00:50,000
MICHAEL: Instead of writing specific instructions
for every scenario,

14
00:00:50,000 --> 00:00:54,000
MICHAEL: we provide data and let the algorithms
find patterns and make decisions.

15
00:00:54,000 --> 00:00:58,000
SARAH: So it's like teaching a computer
to learn on its own?

16
00:00:58,000 --> 00:01:02,000
MICHAEL: Exactly. [laughs]

17
00:01:02,000 --> 00:01:06,000
MICHAEL: Think of it like teaching a child.

18
00:01:06,000 --> 00:01:10,000
MICHAEL: You don't program a child with rules for
recognizing every possible dog they might encounter.

19
00:01:10,000 --> 00:01:14,000
MICHAEL: Instead, you show them examples of dogs,

20
00:01:14,000 --> 00:01:18,000
MICHAEL: and they learn to recognize the patterns
and features that make a dog a dog.

21
00:01:18,000 --> 00:01:22,000
SARAH: That's a helpful analogy.

22
00:01:22,000 --> 00:01:26,000
SARAH: What are some common applications of
machine learning that people might encounter

23
00:01:26,000 --> 00:01:28,000
SARAH: in their daily lives?

24
00:01:28,000 --> 00:01:31,000
MICHAEL: They're everywhere!

25
00:01:31,000 --> 00:01:35,000
MICHAEL: Recommendation systems on streaming
platforms and online stores,

26
00:01:35,000 --> 00:01:39,000
MICHAEL: voice assistants like Siri and Alexa,
email spam filters,

27
00:01:39,000 --> 00:01:43,000
MICHAEL: fraud detection for your credit cards,

28
00:01:43,000 --> 00:01:47,000
MICHAEL: and even the autocorrect feature
on your smartphone.

29
00:02:55,000 --> 00:03:00,000
[Outro music]
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def content_translation() -> BasePrompt:
        """Create a prompt for translating video content."""
        prompt = BasePrompt(
            name="content_translation",
            description="Translate video content while preserving meaning and context",
        )

        prompt.set_system_message(
            """
You are a video content translation specialist. Your task is to translate video content
(titles, descriptions, subtitles) from one language to another while preserving the original
meaning, context, and tone.

When translating content:
1. Maintain the original meaning and intent
2. Adapt cultural references when necessary for understanding
3. Preserve formatting, structure, and style where appropriate
4. Consider the target audience and cultural context
5. Maintain specialized terminology and jargon appropriately
6. Preserve the emotional tone and impact of the original

Provide translations that feel natural to native speakers of the target language while staying true to the source content.
"""
        )

        prompt.set_user_message_template(
            """
Please translate the following video content from {source_language} to {target_language}:

Title: {title}
Description: {description}
Tags: {tags}

Content to translate:
{content}

Special terminology or proper nouns (do not translate):
{special_terms}

Additional context: {additional_context}

Please provide the translation with appropriate formatting and structure for the target language.
"""
        )

        prompt.add_example(
            user_message="""
Please translate the following video content from English to Spanish:

Title: The Future of Renewable Energy: Breakthroughs and Challenges
Description: This video explores recent technological breakthroughs in renewable energy, including advances in solar efficiency, wind turbine design, and energy storage solutions. We also discuss the remaining challenges for widespread adoption and the policy changes needed to accelerate the transition to clean energy.
Tags: renewable energy, solar power, wind energy, clean energy, energy storage, climate change, sustainability

Content to translate:
The global energy landscape is undergoing a profound transformation. Renewable energy sources, once considered alternative or supplementary, are now becoming mainstream. In this video, we'll explore the cutting-edge innovations driving this change and the obstacles that still need to be overcome.

First, let's look at solar technology. The efficiency of commercial solar panels has improved dramatically, with some new designs achieving over 25% efficiency - a significant improvement from the 15% standard just a decade ago. Perovskite solar cells represent one of the most exciting breakthroughs, potentially offering higher efficiency at lower manufacturing costs. However, challenges with durability and scaling up production remain.

Wind energy has also seen remarkable advances. Modern turbines are taller, with longer blades and more sophisticated control systems, allowing them to generate electricity even in low-wind conditions. Offshore wind farms are expanding rapidly, taking advantage of stronger and more consistent wind patterns over open water.

Perhaps the most critical breakthrough has been in energy storage. Advanced battery technologies, including solid-state batteries and flow batteries, are addressing the intermittency issue of renewable sources. These storage solutions enable renewable energy to provide reliable power even when the sun isn't shining or the wind isn't blowing.

Despite these advances, significant challenges remain. The intermittent nature of renewables still poses grid integration challenges. Materials for batteries and solar panels face supply constraints. And the existing energy infrastructure was built around fossil fuels, requiring substantial investments to transition to a renewable-based system.

Policy support will be crucial for accelerating this transition. Carbon pricing, renewable portfolio standards, and targeted research funding can all help overcome these barriers. The countries and companies that lead this transition won't just help address climate change – they'll also position themselves at the forefront of the next energy revolution.

Special terminology or proper nouns (do not translate):
- Perovskite
- Solid-state batteries
- Flow batteries

Additional context: This is an educational video aimed at general audiences with some interest in energy and environmental issues. The translation should maintain the informative tone while being accessible to Spanish speakers who may not be experts in the field.

Please provide the translation with appropriate formatting and structure for the target language.
""",
            assistant_message="""
Título: El Futuro de la Energía Renovable: Avances y Desafíos
Descripción: Este video explora los recientes avances tecnológicos en energía renovable, incluyendo mejoras en la eficiencia solar, diseño de turbinas eólicas y soluciones de almacenamiento de energía. También discutimos los desafíos pendientes para su adopción generalizada y los cambios de política necesarios para acelerar la transición hacia la energía limpia.
Etiquetas: energía renovable, energía solar, energía eólica, energía limpia, almacenamiento de energía, cambio climático, sostenibilidad

Contenido traducido:
El panorama energético global está experimentando una transformación profunda. Las fuentes de energía renovable, antes consideradas alternativas o complementarias, ahora se están volviendo predominantes. En este video, exploraremos las innovaciones de vanguardia que impulsan este cambio y los obstáculos que aún deben superarse.

Primero, veamos la tecnología solar. La eficiencia de los paneles solares comerciales ha mejorado dramáticamente, con algunos nuevos diseños alcanzando más del 25% de eficiencia - una mejora significativa desde el estándar del 15% de hace apenas una década. Las células solares de Perovskite representan uno de los avances más emocionantes, ofreciendo potencialmente mayor eficiencia a costos de fabricación más bajos. Sin embargo, persisten desafíos con la durabilidad y el aumento de la producción a escala.

La energía eólica también ha experimentado avances notables. Las turbinas modernas son más altas, con palas más largas y sistemas de control más sofisticados, permitiéndoles generar electricidad incluso en condiciones de viento bajo. Los parques eólicos marinos se están expandiendo rápidamente, aprovechando patrones de viento más fuertes y constantes sobre aguas abiertas.

Quizás el avance más crítico ha sido en el almacenamiento de energía. Las tecnologías avanzadas de baterías, incluyendo las solid-state batteries y flow batteries, están abordando el problema de la intermitencia de las fuentes renovables. Estas soluciones de almacenamiento permiten que la energía renovable proporcione energía confiable incluso cuando el sol no brilla o el viento no sopla.

A pesar de estos avances, persisten desafíos significativos. La naturaleza intermitente de las renovables todavía plantea retos de integración a la red. Los materiales para baterías y paneles solares enfrentan limitaciones de suministro. Y la infraestructura energética existente fue construida en torno a los combustibles fósiles, requiriendo inversiones sustanciales para la transición hacia un sistema basado en renovables.

El apoyo político será crucial para acelerar esta transición. La fijación de precios del carbono, los estándares de cartera renovable y la financiación dirigida a la investigación pueden ayudar a superar estas barreras. Los países y empresas que lideren esta transición no solo ayudarán a abordar el cambio climático, sino que también se posicionarán a la vanguardia de la próxima revolución energética.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_tool("kaltura.media.update")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt

    @staticmethod
    def thumbnail_suggestion() -> BasePrompt:
        """Create a prompt for suggesting video thumbnails."""
        prompt = BasePrompt(
            name="thumbnail_suggestion",
            description="Suggest effective thumbnail concepts for video content",
        )

        prompt.set_system_message(
            """
You are a thumbnail design consultant for a video platform. Your task is to suggest effective
thumbnail concepts that will maximize viewer engagement and click-through rates.

When suggesting thumbnail concepts:
1. Consider the video's content, tone, and target audience
2. Focus on visually striking and attention-grabbing elements
3. Ensure the concept clearly relates to the video content
4. Include text recommendations when appropriate (keep text minimal)
5. Consider color psychology and visual hierarchy
6. Provide specific, actionable design recommendations

Your suggestions should be detailed enough for a designer to create the thumbnail based on your description.
"""
        )

        prompt.set_user_message_template(
            """
Please suggest thumbnail concepts for the following video:

Title: {title}
Description: {description}
Category: {category_name}
Target Audience: {target_audience}
Key Visual Elements: {key_visual_elements}

Video Content Summary:
{content_summary}

Additional context: {additional_context}

Please provide 3 distinct thumbnail concepts with detailed descriptions.
"""
        )

        prompt.add_example(
            user_message="""
Please suggest thumbnail concepts for the following video:

Title: 7 Habits That Transformed My Productivity
Description: In this video, I share the seven daily habits that completely changed my productivity and helped me accomplish more while feeling less stressed. These practical strategies can be implemented immediately and don't require any special tools or apps.
Category: Education
Target Audience: Young professionals, students, and anyone looking to improve their productivity
Key Visual Elements: Desk setup, productivity tools, morning routine, planning session

Video Content Summary:
The video walks through seven specific habits: 1) Morning planning ritual, 2) Time blocking, 3) The 2-minute rule for small tasks, 4) Strategic breaks using the Pomodoro technique, 5) Single-tasking instead of multitasking, 6) Digital minimalism and notification management, 7) Evening reflection and shutdown ritual. Each habit is explained with practical examples and the science behind why it works. The presenter demonstrates some of the habits in their home office environment.

Additional context: This video has a motivational but practical tone. The presenter has a clean, minimalist aesthetic. Previous thumbnails that performed well for this channel featured bright colors, clear text, and before/after concepts.

Please provide 3 distinct thumbnail concepts with detailed descriptions.
""",
            assistant_message="""
# Thumbnail Concept 1: "Before/After Split Screen"

**Visual Description:**
A split-screen design with a clear contrast between "before" and "after" implementing the seven habits. 

**Left side (Before):**
- Chaotic desk with scattered papers, multiple open devices, coffee spills
- Desaturated colors (slightly grayish/blue tint)
- Person looking stressed/overwhelmed with head in hands
- Small clock showing late afternoon time (4:30 PM)
- Minimal progress shown on laptop screen

**Right side (After):**
- Organized, minimalist desk with thoughtfully arranged items
- Vibrant, warm colors (slight orange/yellow tint for energy)
- Person looking accomplished and calm
- Small clock showing earlier time (2:00 PM)
- Clear progress/completion shown on laptop screen

**Text overlay:**
"7 HABITS" in bold, capital letters at the top
"THAT TRANSFORMED MY PRODUCTIVITY" in smaller text below

**Color scheme:** 
Contrast between cool blues (before) and warm oranges/yellows (after) to emphasize transformation

**Focal point:**
The dramatic difference between the two sides, with the subject's contrasting expressions as the central element

# Thumbnail Concept 2: "Numbered Visual Grid"

**Visual Description:**
A clean, visually organized grid showing all seven habits in a single powerful image.

**Layout:**
- 3×3 grid with the center square featuring the presenter's face with a confident expression
- Surrounding 7 squares each represent one habit with a simple, iconic visual:
  1. Morning planning: Coffee cup with small notebook
  2. Time blocking: Calendar with color-coded blocks
  3. 2-minute rule: Stopwatch showing 2:00
  4. Strategic breaks: Timer with work/break segments
  5. Single-tasking: One highlighted task among faded tasks
  6. Digital minimalism: Phone with notifications turned off
  7. Evening reflection: Sunset with small journal

**Text overlay:**
"7 HABITS" in large text at the top
"300% MORE PRODUCTIVE" in smaller text at the bottom

**Color scheme:**
Clean white background with each habit icon using a different color from a cohesive bright palette (blues, greens, oranges)

**Focal point:**
The central face surrounded by the organized habit icons, creating a wheel-like effect that draws the eye inward

# Thumbnail Concept 3: "Dramatic Transformation Moment"

**Visual Description:**
A dynamic, action-oriented single image capturing the moment of transformation.

**Main elements:**
- Presenter in mid-action, dramatically throwing papers into the air
- Papers visibly transforming into organized digital task cards as they fall
- Split lighting effect: left side of frame in cool, dim lighting; right side in warm, bright lighting
- Desk transitioning from cluttered to organized across the frame
- Digital devices showing increased productivity metrics

**Text overlay:**
"I TRIED 7 PRODUCTIVITY HABITS FOR 30 DAYS..." in large text
"...THIS HAPPENED" in bright accent color

**Color scheme:**
Gradient effect from blue-gray to vibrant orange-yellow across the image

**Focal point:**
The presenter's enthusiastic expression and the papers transforming in mid-air, creating a sense of motion and excitement

---

**Recommendation:**
Based on your channel's previous success with before/after concepts and bright colors, Concept 1 would likely perform best as it clearly communicates transformation while maintaining your minimalist aesthetic. The split-screen approach instantly communicates value to viewers scanning through videos, and the contrasting colors will stand out in recommendation feeds.
""",
        )

        prompt.add_required_tool("kaltura.media.get")
        prompt.add_required_resource("kaltura://media/{entry_id}")

        return prompt
