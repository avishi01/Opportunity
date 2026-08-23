from typing import List
from backend.ai_engine.schemas import StudentProfile, RawListing, CategoryEnum

def get_sample_student_profiles() -> List[StudentProfile]:
    return [
        StudentProfile(
            id="std_101",
            name="Alex Chen",
            degree="B.S.",
            major="Computer Science",
            gpa=3.85,
            graduation_year=2027,
            location="San Francisco, CA",
            skills=["Python", "PyTorch", "React", "TypeScript", "FastAPI", "Git", "SQL"],
            interests=["AI/ML", "Web Dev", "Hackathons", "Generative AI"],
            citizenship_or_authorization=["US Citizen"],
            preferred_categories=[CategoryEnum.INTERNSHIP, CategoryEnum.HACKATHON, CategoryEnum.SCHOLARSHIP]
        ),
        StudentProfile(
            id="std_102",
            name="Maya Patel",
            degree="B.S.",
            major="Electrical Engineering",
            gpa=3.40,
            graduation_year=2026,
            location="Austin, TX",
            skills=["C++", "C#", "Linux", "ROS", "Python", "Embedded Systems"],
            interests=["Robotics", "Cloud & DevOps", "Systems Programming"],
            citizenship_or_authorization=["US Citizen", "Permanent Resident"],
            preferred_categories=[CategoryEnum.INTERNSHIP, CategoryEnum.RESEARCH]
        ),
        StudentProfile(
            id="std_103",
            name="Jordan Taylor",
            degree="M.S.",
            major="Data Science",
            gpa=3.92,
            graduation_year=2026,
            location="Boston, MA",
            skills=["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "SQL", "Docker"],
            interests=["Research", "AI/ML", "NLP", "Bioinformatics"],
            citizenship_or_authorization=["F-1 OPT"],
            preferred_categories=[CategoryEnum.RESEARCH, CategoryEnum.SCHOLARSHIP, CategoryEnum.INTERNSHIP]
        )
    ]

def get_sample_raw_listings() -> List[RawListing]:
    return [
        RawListing(
            id="raw_201",
            source_name="Google Careers Portal",
            source_url="https://careers.google.com/jobs/results/sw-eng-intern-2027",
            raw_text="""
Title: Software Engineering Intern, Summer 2027
Company: Google
Location: Mountain View, CA, USA (Hybrid / Remote options available)

About the role:
As a Software Engineering Intern at Google, you will work on core infrastructure, AI products, or cloud solutions. 

Minimum Qualifications:
- Currently enrolled in a Bachelor's degree program in Computer Science, Software Engineering, or related technical field.
- Expected graduation date between December 2026 and June 2028 (Graduation year 2027 or 2028).
- Minimum GPA: 3.5 cumulative.
- Experience in one or more general purpose programming languages including Python, C++, Java, or Go.

Preferred Qualifications:
- Familiarity with AI/ML frameworks like PyTorch or TensorFlow.
- Experience with web technologies (React, Node) or systems development.

Deadline: October 15, 2026.
Apply at https://careers.google.com/apply
            """,
            ingested_at="2026-08-21T10:00:00Z"
        ),
        RawListing(
            id="raw_202",
            source_name="Generative AI Foundation Portal",
            source_url="https://genai-foundation.org/scholarships/2026",
            raw_text="""
Opportunity Title: Generative AI Pioneers Student Scholarship & Award
Organization: Generative AI Foundation
Category: Scholarship Grant
Location: Remote / Global

Award details:
$10,000 cash grant towards academic tuition + mentorship from top AI researchers.

Eligibility Criteria:
- Enrolled in B.S., M.S., or Ph.D. programs in Computer Science, Data Science, or AI.
- Open to students worldwide (all citizenship statuses eligible).
- Minimum GPA requirement: 3.0 out of 4.0.
- Applicants must submit a 500-word statement on how they plan to use LLMs or Agentic AI to solve real-world problems.

Required tags: AI/ML, Research, Generative AI, Diversity.
Deadline: November 30, 2026.
            """,
            ingested_at="2026-08-21T11:00:00Z"
        ),
        RawListing(
            id="raw_203",
            source_name="Devpost Platform",
            source_url="https://devpost.com/hackathons/global-agentic-ai-2026",
            raw_text="""
Event Name: Global Agentic AI Hackathon 2026
Host: Agentic AI Labs & Tech Partners
Location: Remote (Online virtual hackathon)

Build the future of autonomous software agents! $50,000 in total prizes.
Categories:
- Best Autonomous Coding Agent
- Best Multi-Agent System
- Student Special Track ($5,000 prize)

Who can participate:
Students of all degree levels (Undergraduate, Graduate, PhD) and majors.
Tech Stack: Python, TypeScript, React, Next.js, FastAPI, LangChain, PyTorch.

Event Dates: November 1-3, 2026.
Registration Closing Date: October 28, 2026.
            """,
            ingested_at="2026-08-21T12:00:00Z"
        ),
        RawListing(
            id="raw_204",
            source_name="MIT CSAIL Lab Postings",
            source_url="https://csail.mit.edu/opportunities/nlp-vision-ra",
            raw_text="""
Position: AI Research Assistant (Graduate / Senior Undergraduate)
Laboratory: MIT CSAIL - Natural Language Processing & Vision Group
Location: Cambridge, MA (On-site / Hybrid)

Role overview:
We are seeking motivated M.S. or Ph.D. students (or exceptional B.S. Seniors with high GPA 3.7+) to work on multi-modal LLM alignment and agentic reasoning architectures.

Requirements:
- Strong background in Python, PyTorch, Deep Learning, and NLP.
- Demonstrated research experience or published papers in AI conferences is a major plus.
- Degree path: M.S. or Ph.D. candidate (or graduating Senior 2026).
- Minimum GPA: 3.7.

Deadline: December 1, 2026.
            """,
            ingested_at="2026-08-21T13:00:00Z"
        ),
        RawListing(
            id="raw_205",
            source_name="Jane Street Careers",
            source_url="https://janestreet.com/join-jane-street/position/quant-sw-eng",
            raw_text="""
Role: Quantitative Software Engineer Intern
Company: Jane Street
Location: New York, NY

Overview:
We are looking for elite engineering talent to build high-frequency trading systems and low-latency algorithmic platforms.

Strict Eligibility:
- Must be enrolled in a B.S. or M.S. in Computer Science, Electrical Engineering, Mathematics, or Physics.
- Graduation Year: 2026 or 2027 only.
- Strict GPA Minimum: 3.75 out of 4.0.
- Deep expertise in C++, OCaml, Systems Programming, Algorithms, and Linux.

Deadline: October 1, 2026.
            """,
            ingested_at="2026-08-21T14:00:00Z"
        )
    ]
