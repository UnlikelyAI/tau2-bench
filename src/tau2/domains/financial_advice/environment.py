# Copyright Sierra
import json
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.financial_advice.data_model import FinancialAdviceDB
from tau2.domains.financial_advice.tools import EmptyTools
from tau2.domains.financial_advice.user_tools import FinancialAdviceUserTools
from tau2.domains.financial_advice.utils import (
    FINANCIAL_ADVICE_DB_PATH,
    FINANCIAL_ADVICE_POLICY_PATH,
    FINANCIAL_ADVICE_TASK_SET_PATH,
)
from tau2.environment.environment import Environment


def get_environment(
    db: Optional[FinancialAdviceDB] = None,
    solo_mode: bool = False,
) -> Environment:
    if solo_mode:
        raise ValueError("Financial advice domain does not support solo mode")
    if db is None:
        db = FinancialAdviceDB.load(FINANCIAL_ADVICE_DB_PATH)
    tools = EmptyTools(db)
    user_tools = FinancialAdviceUserTools(db)
    with open(FINANCIAL_ADVICE_POLICY_PATH, "r") as fp:
        policy = fp.read()
    return Environment(
        domain_name="financial-advice",
        policy=policy,
        tools=tools,
        user_tools=user_tools,
    )


def get_tasks() -> list[Task]:
    with open(FINANCIAL_ADVICE_TASK_SET_PATH, "r") as fp:
        tasks = json.load(fp)
    return [Task.model_validate(task) for task in tasks]
