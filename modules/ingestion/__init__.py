from contracts import Expert, OnboardingPath, ReadingItem, Role


def build_corpus() -> None:
    return None


def find_experts(topic: str, role: Role) -> list[Expert]:
    return [Expert(name='Priya Rao', role='QA Lead', evidence_count=9, topics=['deviation'], sample_source='SOP-001 Deviation Handling')]


def onboarding_path(job_role: str, role: Role) -> OnboardingPath:
    item = ReadingItem(order=1, doc_id='QM-001', title='Quality Manual', why='Start here for the quality system overview', est_minutes=20)
    return OnboardingPath(job_role=job_role, days={'Day 1': [item]})
