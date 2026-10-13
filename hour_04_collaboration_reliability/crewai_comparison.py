"""Six-minute live comparison: triage then Billing, read-only CSV tools."""
import os
import csv
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')


@tool('payment_lookup')
def payment_lookup() -> str:
    """Read captured payments for the fixed classroom case ORD1001 belonging to C001."""
    with (ROOT / 'data/payments.csv').open() as f:
        return str([r for r in csv.DictReader(f) if r['order_id'] == 'ORD1001'])


def build():
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY in the root .env. This optional comparison uses real LLM calls.')
    llm = LLM(model='openai/' + os.getenv('LLM_MODEL', 'gpt-4.1-mini'), temperature=0)
    triage = Agent(role='Support triage', goal='Identify the correct specialist for the ticket',
                   backstory='Route payment questions to Billing.', llm=llm, verbose=True)
    billing = Agent(role='Billing specialist', goal='Verify duplicate payments using the read-only tool',
                    backstory='You only investigate; never execute a refund.', tools=[payment_lookup],
                    llm=llm, verbose=True)
    classify = Task(description='Classify: I was charged twice for order ORD1001.',
                    expected_output='A team name and reason.', agent=triage)
    investigate = Task(description='Use payment_lookup to verify the duplicate charge for ORD1001. '
                       'State the duplicate amount and that a reviewer must approve above INR 1000.',
                       expected_output='Evidence-based refund proposal; no executed action.',
                       agent=billing, context=[classify])
    return Crew(agents=[triage, billing], tasks=[classify, investigate], process=Process.sequential, verbose=True)


if __name__ == '__main__':
    print(build().kickoff())
