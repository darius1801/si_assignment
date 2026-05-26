from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from si_project.tools.icd_tool import fetch_icd11_disease_data

class DatasetEntry(BaseModel):
    icd11_code: str = Field(description="The ICD-11 code of the disease.")
    disease_name: str = Field(description="The official name of the disease.")
    patient_description: str = Field(description="The colloquial patient-style description of symptoms.")
    doctor_description: str = Field(description="The formal clinical note description of symptoms.")

@CrewBase
class SiProject():
    """SiProject crew pentru generare dataset medical"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def medical_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['medical_extractor'],
            tools=[fetch_icd11_disease_data],
            verbose=True,
            max_rpm=1,
            max_iter=3
        )

    @agent
    def clinical_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['clinical_generator'],
            verbose=True,
            max_rpm=1,
            max_iter=3
        )

    @agent
    def medical_critic(self) -> Agent:
        return Agent(
            config=self.agents_config['medical_critic'],
            verbose=True,
            max_rpm=1,
            max_iter=3
        )

    @task
    def extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['extraction_task'],
            agent=self.medical_extractor()
        )

    @task
    def generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['generation_task'],
            agent=self.clinical_generator()
        )

    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['validation_task'],
            agent=self.medical_critic(),
            output_pydantic=DatasetEntry
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=2
        )