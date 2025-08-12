# Copyright Sierra
import json
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.financial_advice.tools import FinancialAdviceTools
from tau2.domains.financial_advice.utils import (
    FINANCIAL_ADVICE_DB_PATH,
    FINANCIAL_ADVICE_POLICY_PATH,
    FINANCIAL_ADVICE_TASK_SET_PATH,
)
from tau2.environment.environment import Environment


def get_environment(
    solo_mode: bool = False,
) -> Environment:
    if solo_mode:
        raise ValueError("Financial advice domain does not support solo mode")
    tools = FinancialAdviceTools()
    with open(FINANCIAL_ADVICE_POLICY_PATH, "r") as fp:
        policy = fp.read()
    return Environment(
        domain_name="financial-advice",
        policy=policy,
        tools=tools,
    )


def get_tasks() -> list[Task]:
    with open(FINANCIAL_ADVICE_TASK_SET_PATH, "r") as fp:
        tasks = json.load(fp)
    return [Task.model_validate(task) for task in tasks]
